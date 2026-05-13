from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

# Repositories
from app.repositories.workout_item_repository import WorkoutItemRepository
from app.repositories.workout_plan_repository import WorkoutPlanRepository
from app.repositories.exercise_repository import ExerciseRepository

# Schemas
from app.schemas.workout_item_schema import WorkoutItemCreate, WorkoutItemUpdate, WorkoutItemResponse

# Exceptions
from app.exceptions.exceptions import (
    ResourceNotFoundException, # If plan or exercise doesn't exist
    DatabaseErrorException     # If DB fails
)

class WorkoutItemService:
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = WorkoutItemRepository(db)
        self.plan_repo = WorkoutPlanRepository(db)
        self.exercise_repo = ExerciseRepository(db)

    # =========================================================================
    # Logic 1: Add a Single Exercise to a Plan
    # =========================================================================
    def add_item_to_plan(self, item_data: WorkoutItemCreate) -> WorkoutItemResponse:
        """
        Adds a specific exercise (e.g., 'Bench Press', 3 sets) to a plan.
        Validates that both the Plan and the Exercise exist first.
        """
        # 1. Validate: Does the Plan exist?
        plan = self.plan_repo.get_by_id(item_data.plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Workout plan ID {item_data.plan_id} not found.")

        # 2. Validate: Does the Exercise exist in our bank?
        exercise = self.exercise_repo.get_by_id(item_data.exercise_id)
        if not exercise:
            raise ResourceNotFoundException(f"Exercise ID {item_data.exercise_id} not found.")

        # 3. Create Item via Repository
        try:
            new_item = self.item_repo.create(item_data)
            return new_item

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error adding item: {str(e)}")

    # =========================================================================
    # Logic 2: Get All Items for a Plan
    # =========================================================================
    def get_items_by_plan(self, plan_id: int) -> List[WorkoutItemResponse]:
        """
        Fetches all exercises belonging to a specific plan.
        Usually sorted by order_index (from Repository).
        """
        # Ensure plan exists first
        if not self.plan_repo.get_by_id(plan_id):
            raise ResourceNotFoundException(f"Workout plan ID {plan_id} not found.")

        return self.item_repo.get_by_plan_id