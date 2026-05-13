from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

# Repositories
from app.repositories.trainer_repository import TrainerRepository
from app.repositories.member_repository import MemberRepository

# Schemas
from app.schemas.trainer_schema import TrainerCreate, TrainerUpdate, TrainerResponse
from app.schemas.member_schema import MemberResponse

# Validators & Utils
from app.utils.validators import (
    validate_email_format,
    validate_password_strength,
    validate_israeli_phone
)

# Exceptions
from app.exceptions.exceptions import (
    UserAlreadyExistsException,
    IncorrectEmailException,
    IncorrectPasswordException,
    IncorrectPhoneNumberException,
    DatabaseErrorException,  # Fixed spelling
    UserIsNotExistException
)


class TrainerService:
    def __init__(self, db: Session):
        self.db = db
        self.trainer_repo = TrainerRepository(db)
        self.member_repo = MemberRepository(db)

    # =========================================================================
    # Logic 1: Recruit New Trainer (Create)
    # =========================================================================
    def register_new_trainer(self, trainer_data: TrainerCreate) -> TrainerResponse:
        """
        Register a new trainer.
        Includes strict validation checks (similar to Member).
        """
        # 1. Basic Validations
        if not validate_email_format(trainer_data.email):
            raise IncorrectEmailException("Email format is incorrect.")

        if not validate_password_strength(trainer_data.password):
            raise IncorrectPasswordException("The password is too weak.")

        if trainer_data.phone_number and not validate_israeli_phone(trainer_data.phone_number):
            raise IncorrectPhoneNumberException("Incorrect phone number format.")

        # 2. Check if email or phone is taken
        if self.trainer_repo.get_by_email(trainer_data.email):
            raise UserAlreadyExistsException(f"The trainer email {trainer_data.email} already exists.")

        if self.trainer_repo.get_by_phone(trainer_data.phone_number):
            raise UserAlreadyExistsException(f"The phone number {trainer_data.phone_number} already exists.")

        # 3. Save to DB
        try:
            # We pass the data directly. The Repository handles the creation.
            new_trainer = self.trainer_repo.create(trainer_data)
            return new_trainer

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error: Cannot create trainer. {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Unexpected error: {str(e)}")

    # =========================================================================
    # Logic 2: Manage Profile (Read / Update)
    # =========================================================================
    def get_trainer_profile(self, trainer_id: int) -> TrainerResponse:
        trainer = self.trainer_repo.get_by_id(trainer_id)
        if not trainer:
            raise UserIsNotExistException("Cannot find the trainer.")
        return trainer

    def get_all_trainers(self) -> List[TrainerResponse]:
        """Fetch all trainers in the system."""
        return self.trainer_repo.get_all()

    def update_trainer_details(self, trainer_id: int, update_data: TrainerUpdate) -> TrainerResponse:
        # 1. Fetch existing trainer
        trainer = self.trainer_repo.get_by_id(trainer_id)
        if not trainer:
            raise UserIsNotExistException("Cannot find the trainer.")

        # 2. Validation if email is being updated
        if update_data.email:
            if not validate_email_format(update_data.email):
                raise IncorrectEmailException("Invalid email format.")

            # Check if new email belongs to another user
            existing = self.trainer_repo.get_by_email(update_data.email)
            if existing and existing.id != trainer_id:
                raise UserAlreadyExistsException("This email is already being used by another trainer.")

        # 3. Update via Repository
        try:
            # Note: base_repo.update expects (db_obj, obj_in)
            updated_trainer = self.trainer_repo.update(trainer, update_data)
            return updated_trainer
        except Exception as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Failed to update trainer: {str(e)}")

    # =========================================================================
    # Logic 3: Trainee Management
    # =========================================================================
    def get_my_trainees(self, trainer_id: int) -> List[MemberResponse]:
        """
        Returns all members assigned to this specific trainer.
        """
        # 1. Verify trainer exists
        trainer = self.trainer_repo.get_by_id(trainer_id)
        if not trainer:
            raise UserIsNotExistException("Trainer not found.")

        # 2. Return the list using the Relationship defined in the Model
        return trainer.members

    def assign_member_to_trainer(self, trainer_id: int, member_id: int):
        """
        Link a member to a specific trainer.
        """
        # 1. Validate existence
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise UserIsNotExistException(f"Member {member_id} not found.")

        trainer = self.trainer_repo.get_by_id(trainer_id)
        if not trainer:
            raise UserIsNotExistException(f"Trainer {trainer_id} not found.")

        # 2. Update the member using the Repository
        # We pass a dictionary with the specific field to update
        try:
            self.member_repo.update(member, {"trainer_id": trainer_id})
            return {"message": f"Member {member_id} assigned to Trainer {trainer_id} successfully"}
        except Exception as e:
            raise DatabaseErrorException(f"Assignment failed: {str(e)}")