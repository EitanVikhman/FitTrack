from sqlalchemy.orm import Session  # Import Session to handle database transactions
from sqlalchemy.exc import SQLAlchemyError  # Import base exception for all SQLAlchemy errors
from typing import List  # Import List for type hinting return values

# Repositories
# Import specific data access layers (repositories) for Workout Plans, Members, and Trainers
# Ensure these files exist in your 'repositories' folder
from app.repositories.workout_plan_repository import WorkoutPlanRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.trainer_repository import TrainerRepository

# Schemas
# Import Pydantic models for data validation (Input) and serialization (Output)
from app.schemas.workout_plan_schema import WorkoutPlanCreate, WorkoutPlanResponse

# Exceptions
# Import custom exceptions to handle specific business errors (404, 500, etc.)
from app.exceptions.exceptions import (
    ResourceNotFoundException,
    MemberNotFoundException,
    UserIsNotExistException,
    DatabaseErrorException
)


class WorkoutPlanService:
    def __init__(self, db: Session):
        # Initialize the service with the active database session
        self.db = db
        # Initialize the repository for workout plan operations
        self.plan_repo = WorkoutPlanRepository(db)
        # Initialize the repository for member operations
        self.member_repo = MemberRepository(db)
        # Initialize the repository for trainer operations
        # If the 'TrainerRepository' file doesn't exist yet, you might need to comment this out temporarily
        self.trainer_repo = TrainerRepository(db)

    # =========================================================================
    # Logic 1: Create Workout Plan (With Archiving)
    # =========================================================================
    def create_workout_plan(self, plan_data: WorkoutPlanCreate) -> WorkoutPlanResponse:
        """
        Creates a new workout plan container.
        Critically: It archives any existing active plans for this member first.
        """
        # 1. Validate Member
        # Check if the member exists in the database before assigning a plan
        if not self.member_repo.get_by_id(plan_data.member_id):
            raise MemberNotFoundException(f"Member ID {plan_data.member_id} not found.")

        # 2. Validate Trainer (The Critical Fix)
        # Check the trainer ONLY if a trainer_id was actually provided (since it can be None/Null)
        if plan_data.trainer_id is not None:
            # If an ID is provided, verify it exists in the database
            if not self.trainer_repo.get_by_id(plan_data.trainer_id):
                raise UserIsNotExistException(f"Trainer ID {plan_data.trainer_id} not found.")

        try:
            # 3. Archive old plans (Business Logic)
            # We enforce a rule that a member can have only ONE active plan at a time.
            # This method marks any currently 'ACTIVE' plans as 'ARCHIVED'.
            self.plan_repo.archive_current_plans(plan_data.member_id)

            # 4. Create the new plan
            # Use the repository to insert the new plan into the database
            new_plan = self.plan_repo.create(plan_data)
            return new_plan

        except SQLAlchemyError as e:
            # If the database operation fails, rollback the transaction to maintain data integrity
            self.db.rollback()
            # Raise a custom generic database error
            raise DatabaseErrorException(f"Database error creating workout plan: {str(e)}")

    # =========================================================================
    # Logic 2: Get Active Plan
    # =========================================================================
    def get_member_active_plan(self, member_id: int) -> WorkoutPlanResponse:
        """
        Fetches the single currently active plan for a member.
        """
        # First, validate that the member actually exists
        if not self.member_repo.get_by_id(member_id):
            raise MemberNotFoundException("Member not found.")

        # Query the repository for the plan with status='ACTIVE'
        plan = self.plan_repo.get_active_plan(member_id)

        # If no active plan is found, raise a 404 Resource Not Found exception
        if not plan:
            raise ResourceNotFoundException("No active workout plan found.")

        # Return the plan object
        return plan

    # =========================================================================
    # Logic 3: Get History
    # =========================================================================
    def get_plan_history(self, member_id: int) -> List[WorkoutPlanResponse]:
        """
        Returns all past plans (Archived).
        """
        # Validate that the member exists
        if not self.member_repo.get_by_id(member_id):
            raise MemberNotFoundException("Member not found.")

        # Return the list of all historical plans for this member
        return self.plan_repo.get_member_history(member_id)