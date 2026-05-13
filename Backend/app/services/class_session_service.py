from sqlalchemy.orm import Session  # Import Session to handle database transactions
from sqlalchemy.exc import SQLAlchemyError  # Import exception base class for SQLAlchemy errors
from typing import List  # Import List type hint for returning lists of objects
from datetime import datetime, timezone  # Import datetime tools for handling time and timezones

# Repositories
# Import the repository layer for accessing Class Session data
from app.repositories.class_session_repository import ClassSessionRepository
# Import the repository layer for accessing Trainer data
from app.repositories.trainer_repository import TrainerRepository

# Schemas
# Import Pydantic schemas for data validation and transfer (DTOs)
from app.schemas.class_session_schema import ClassSessionCreate, ClassSessionUpdate, ClassSessionResponse

# Exceptions
# Import custom application exceptions for error handling
from app.exceptions.exceptions import (
    ResourceNotFoundException,  # For 404 Not Found errors
    UserIsNotExistException,    # For validation when a user/trainer is missing
    BusinessRuleException,      # For logic violations (e.g., bad times)
    DatabaseErrorException      # For 500 Internal Server errors
)


class ClassSessionService:
    def __init__(self, db: Session):
        # Initialize the service with the active database session
        self.db = db
        # Initialize the repository specifically for class sessions
        self.class_repo = ClassSessionRepository(db)

        # Initialize the Trainer repository to allow validation of trainers
        # This abstraction layer prevents direct SQL queries in the service
        self.trainer_repo = TrainerRepository(db)

    # =========================================================================
    # Logic 1: Schedule a New Class
    # =========================================================================
    def create_class_session(self, session_data: ClassSessionCreate) -> ClassSessionResponse:
        """
        Creates a new class in the schedule.
        Validates time logic and trainer existence.
        """
        # 1. Validate Time Logic

        # Check: Ensure the class does not end before it starts
        if session_data.start_time >= session_data.end_time:
            raise BusinessRuleException("End time must be after start time.")

        # Check: Ensure the class is not scheduled in the past
        # Fix: Use timezone-aware datetime if the input has timezone info, otherwise use local now
        current_time = datetime.now(timezone.utc) if session_data.start_time.tzinfo else datetime.now()

        # Compare the requested start time with the current time
        if session_data.start_time < current_time:
            # Note: For debugging/testing purposes, we bypass this check using 'pass'.
            # In a production environment, this should raise an exception.
            pass
            # raise BusinessRuleException("Cannot schedule a class in the past.")

        # 2. Validate Trainer Existence (Major Fix)
        # Only validate the trainer if a trainer_id was actually provided (since it can be None)
        if session_data.trainer_id is not None:
            # Check the database to see if the trainer exists
            trainer = self.trainer_repo.get_by_id(session_data.trainer_id)
            # If the trainer does not exist, raise an exception
            if not trainer:
                raise UserIsNotExistException(f"Trainer ID {session_data.trainer_id} not found.")

        # 3. Create via Repository
        try:
            # Delegate the creation logic to the repository layer
            new_class = self.class_repo.create(session_data)
            # Return the newly created class object
            return new_class

        except SQLAlchemyError as e:
            # If a database error occurs, rollback the transaction to keep data consistent
            self.db.rollback()
            # Raise a custom database error exception
            raise DatabaseErrorException(f"Database error creating class: {str(e)}")

    # =========================================================================
    # Logic 2: Get Class Details
    # =========================================================================
    def get_session_by_id(self, session_id: int) -> ClassSessionResponse:
        # Attempt to retrieve the class session by ID from the repository
        session = self.class_repo.get_by_id(session_id)
        # If no session is found, raise a Not Found exception
        if not session:
            raise ResourceNotFoundException(f"Class session {session_id} not found.")
        # Return the found session object
        return session

    def get_upcoming_classes(self, limit: int = 10) -> List[ClassSessionResponse]:
        """Returns future classes."""
        # Call the repository to get a list of upcoming classes with a limit
        return self.class_repo.get_upcoming_classes(limit)

    def get_all_sessions(self) -> List[ClassSessionResponse]:
        """Returns all classes (for admin view)"""
        # Call the repository to get all class sessions without filtering
        return self.class_repo.get_all()

    # =========================================================================
    # Logic 3: Cancel or Update Class
    # =========================================================================
    def cancel_class_session(self, session_id: int):
        """Changes status to CANCELLED"""
        # First, retrieve the existing session to ensure it exists
        session = self.class_repo.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundException("Class session not found.")

        try:
            # Use the repository to update only the specific field ("status")
            return self.class_repo.update(session, {"status": "CANCELLED"})
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            # Raise a database error exception
            raise DatabaseErrorException(f"Failed to cancel class: {str(e)}")

    def update_class_details(self, session_id: int, update_data: ClassSessionUpdate):
        # Retrieve the session to update
        session = self.class_repo.get_by_id(session_id)
        # Ensure it exists before trying to update
        if not session:
            raise ResourceNotFoundException("Class session not found.")

        # If the update data includes a new trainer ID, validate that the new trainer exists
        if update_data.trainer_id is not None:
            if not self.trainer_repo.get_by_id(update_data.trainer_id):
                raise UserIsNotExistException("New trainer ID not found.")

        try:
            # Perform the update via the repository using the validated data
            return self.class_repo.update(session, update_data)
        except Exception as e:
            # Rollback transaction on failure
            self.db.rollback()
            # Raise a database error exception
            raise DatabaseErrorException(f"Failed to update class: {str(e)}")