from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

# Repository
from app.repositories.exercise_repository import ExerciseRepository

# Schemas
from app.schemas.exercise_schema import ExerciseCreate, ExerciseUpdate, ExerciseResponse

# Exceptions
from app.exceptions.exceptions import (
    ResourceNotFoundException,
    DuplicateErrorException,
    DatabaseErrorException
)


class ExerciseService:
    def __init__(self, db: Session):
        self.db = db
        self.exercise_repo = ExerciseRepository(db)

    # =========================================================================
    # Logic 1: Create New Exercise
    # =========================================================================
    def create_exercise(self, exercise_data: ExerciseCreate) -> ExerciseResponse:
        """
        Adds a new exercise to the database.
        Checks if an exercise with the same name already exists to avoid duplicates.
        """
        # 1. Check for duplicates (Case-insensitive check)
        # We use the search function to see if something similar exists
        existing_exercises = self.exercise_repo.search_by_name(exercise_data.name)

        # We iterate to find an exact match
        for exercise in existing_exercises:
            if exercise.name.lower() == exercise_data.name.lower():
                raise DuplicateErrorException(f"Exercise '{exercise_data.name}' already exists.")

        # 2. Create via Repository
        try:
            new_exercise = self.exercise_repo.create(exercise_data)
            return new_exercise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error creating exercise: {str(e)}")

    # =========================================================================
    # Logic 2: Get Exercises (Read & Filter)
    # =========================================================================
    def get_exercise_by_id(self, exercise_id: int) -> ExerciseResponse:
        """
        Fetch a single exercise by ID.
        """
        exercise = self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise ResourceNotFoundException(f"Exercise with ID {exercise_id} not found.")
        return exercise

    def get_all_exercises(self) -> List[ExerciseResponse]:
        """
        Fetch all exercises available in the system.
        """
        return self.exercise_repo.get_all()

    def get_exercises_by_muscle_group(self, muscle_group: str) -> List[ExerciseResponse]:
        """
        Filter exercises by muscle group (e.g., Chest, Legs, Back).
        Useful for the Workout Builder UI.
        """
        # Note: The Repository expects the Enum value or string depending on implementation.
        # Assuming the Repo handles the string conversion or filter correctly.
        return self.exercise_repo.get_by_muscle_group(muscle_group)

    def search_exercises(self, query: str) -> List[ExerciseResponse]:
        """
        Search for exercises by name (Partial match).
        Useful for Autocomplete fields.
        """
        if not query:
            return []
        return self.exercise_repo.search_by_name(query)

    # =========================================================================
    # Logic 3: Update & Delete
    # =========================================================================
    def update_exercise(self, exercise_id: int, update_data: ExerciseUpdate) -> ExerciseResponse:
        """
        Update exercise details (e.g., change description or video URL).
        """
        exercise = self.get_exercise_by_id(exercise_id)  # Raises Error if not found

        try:
            updated_exercise = self.exercise_repo.update(exercise, update_data)
            return updated_exercise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Failed to update exercise: {str(e)}")

    def delete_exercise(self, exercise_id: int):
        """
        Delete an exercise from the bank.
        Note: This might fail if the exercise is already used in workout plans (Foreign Key constraint).
        """
        self.get_exercise_by_id(exercise_id)  # Check existence

        try:
            self.exercise_repo.delete(exercise_id)
            return {"message": "Exercise deleted successfully"}
        except SQLAlchemyError as e:
            self.db.rollback()
            # If DB prevents deletion because it's used in history:
            raise DatabaseErrorException(
                f"Cannot delete exercise (it might be part of existing workout plans): {str(e)}")