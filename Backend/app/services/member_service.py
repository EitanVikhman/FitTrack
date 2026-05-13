from sqlalchemy.orm import Session  # Import Session to manage database transactions
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemy base exception for database errors
from datetime import datetime, date  # Import date/time utilities for timestamps

# Import Models and Repositories
from app.models.member import Member  # Import the Member database model
from app.models.entry_log import EntryLog  # Import the EntryLog model for tracking gym visits
from app.repositories.member_repository import MemberRepository  # Import the repository for member database operations

# Import Schemas
# Import Pydantic models for data validation (Create, Update, Response)
from app.schemas.member_schema import MemberCreate, MemberUpdate, MemberResponse

# Import Validators
# Import utility functions to validate input formats
from app.utils.validators import (
    validate_email_format,
    validate_password_strength,
    validate_israeli_phone
)

# Import Exceptions (Based on your provided list)
# Import custom exceptions to handle specific error scenarios
from app.exceptions.exceptions import (
    UserAlreadyExistsException,
    IncorrectEmailException,
    IncorrectPasswordException,
    IncorrectPhoneNumberException,
    UserIsNotExistException,
    MemberNotFoundException,
    UserAccessDeniedException,
    DatabaseErrorException
)


class MemberService:
    def __init__(self, db: Session):
        # Initialize the service with the active database session
        self.db = db
        # Initialize the MemberRepository to handle database queries
        self.member_repo = MemberRepository(db)

    # =========================================================================
    # Logic 1: Smart Registration (No Encryption)
    # =========================================================================
    def register_new_member(self, member_data: MemberCreate) -> MemberResponse:
        # 1. Validation checks
        # Validate that the email format is correct using the utility function
        if not validate_email_format(member_data.email):
            raise IncorrectEmailException("The format of the email is incorrect.")

        # Check if a user with this email already exists in the database
        if self.member_repo.get_by_email(member_data.email):
            raise UserAlreadyExistsException(f"The email {member_data.email} already exists.")

        # 2. Prepare data for the Database
        try:
            # Convert the Pydantic model to a standard dictionary
            member_dict = member_data.model_dump()


            # The DB requires 'hashed_password'. We take the password from input and map it.
            # Get the raw password from the dictionary
            raw_password = member_dict.get("password")

            if raw_password:
                # Map the raw password to the 'hashed_password' field (encryption would happen here in production)
                member_dict["hashed_password"] = raw_password
            else:
                # If password is missing (optional), set a default to prevent database NOT NULL errors
                member_dict["hashed_password"] = "default_pass_123"

            # Remove the old 'password' key from the dictionary to avoid arguments error in the SQL model
            if "password" in member_dict:
                del member_dict["password"]


            # The DB requires a 'full_name' field (inherited from User model).
            # Retrieve first and last names, defaulting to empty strings if missing
            first = member_dict.get("first_name", "")
            last = member_dict.get("last_name", "")
            # Concatenate them to create the full name
            member_dict["full_name"] = f"{first} {last}".strip()

            # --- Fix 3: Date Handling ---
            # If no join date was provided, set it to today's date
            if not member_dict.get("join_date"):
                member_dict["join_date"] = date.today()

            # 3. Create in Database
            # Create a new Member instance using the prepared dictionary
            new_member = Member(**member_dict)
            # Add the new member to the session
            self.db.add(new_member)
            # Commit the transaction to save changes
            self.db.commit()
            # Refresh the instance to get generated fields (like ID)
            self.db.refresh(new_member)

            # Return the newly created member object
            return new_member

        except SQLAlchemyError as e:
            # Rollback the transaction if a database error occurs
            self.db.rollback()
            # Raise a custom database error exception
            raise DatabaseErrorException(f"Database error: {str(e)}")
        except Exception as e:
            # Rollback for any other unexpected errors
            self.db.rollback()
            # Raise a generic database error with the exception details
            raise DatabaseErrorException(f"Unexpected error: {str(e)}")

    # =========================================================================
    # Logic 2: Check Entry Eligibility (Logic Only)
    # =========================================================================
    def check_entry_eligibility(self, member_id: int) -> bool:
        # Retrieve the member by ID
        member = self.member_repo.get_by_id(member_id)
        # If member does not exist, raise an exception
        if not member:
            raise UserIsNotExistException("The member does not exist in the system.")

        # Check status (Case Insensitive) - defaults to 'ACTIVE' if missing
        status = str(getattr(member, 'status', 'ACTIVE')).upper()

        # Check if the user is banned
        if status == "BANNED":
            raise UserAccessDeniedException("The user is banned.")

        # Check if the user is frozen
        if status == "FROZEN":
            raise UserAccessDeniedException("Access denied - the member is frozen.")

        # Return True if the member is eligible to enter
        return True

    # =========================================================================
    # Logic 3: Process Check-In (Logic + Logging)
    # =========================================================================
    def process_check_in(self, member_id: int):
        """
        Performs entry check, logs the result in EntryLog, and returns the response.
        """
        # Retrieve the member from the database
        member = self.member_repo.get_by_id(member_id)

        # Set default status to DENIED and reason to MEMBER_NOT_FOUND
        status = "DENIED"
        reason = "MEMBER_NOT_FOUND"

        # If the member exists, check their specific status
        if member:
            # Get the member's status safely, defaulting to ACTIVE
            member_status = str(getattr(member, 'status', 'ACTIVE')).upper()

            if member_status == "BANNED":
                reason = "MEMBER_BANNED"
            elif member_status == "FROZEN":
                reason = "MEMBER_FROZEN"
            elif member_status == "CANCELLED":
                reason = "MEMBER_CANCELLED"
            else:
                # If none of the negative statuses apply, approve entry
                status = "APPROVED"
                reason = None

        # --- Save Log to DB ---
        if member:
            # Create a new entry log record
            new_log = EntryLog(
                member_id=member.id,
                entry_time=datetime.now(),
                status=status,
                rejection_reason=reason
            )
            # Add log to database
            self.db.add(new_log)
            # Commit the transaction
            self.db.commit()
            # Refresh to get the ID
            self.db.refresh(new_log)

        # Return a dictionary with the check-in results for the API response
        return {
            "status": status,
            "reason": reason,
            # Return member name if found, else "Unknown"
            "member_name": f"{member.first_name} {member.last_name}" if member else "Unknown",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # =========================================================================
    # Logic 4: Get and Update Profile
    # =========================================================================
    def get_member_profile(self, member_id: int) -> MemberResponse:
        # Retrieve member by ID
        member = self.member_repo.get_by_id(member_id)
        # If not found, raise specific exception
        if not member:
            raise MemberNotFoundException("Member not found.")
        # Return the member object
        return member

    def update_member_details(self, member_id: int, member_update: MemberUpdate) -> MemberResponse:
        # 1. Fetch the member first to ensure existence
        member = self.get_member_profile(member_id)  # Raises error if not found

        # 2. Update via Repository
        try:
            # Call repository to update the member fields
            updated_member = self.member_repo.update(member, member_update)
            return updated_member
        except SQLAlchemyError as e:
            # Rollback on database failure
            self.db.rollback()
            # Raise exception detailing the update failure
            raise DatabaseErrorException(f"Failed to update member: {str(e)}")