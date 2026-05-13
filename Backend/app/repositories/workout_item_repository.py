from sqlalchemy.orm import Session
from typing import List

from app.models.workout_item import WorkoutItem
from .base_repository import BaseRepository


class WorkoutItemRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, WorkoutItem)

    def get_by_plan_id(self, plan_id: int) -> List[WorkoutItem]:
        """
        Get all exercises for a specific workout plan.
        CRITICAL: Results are sorted by 'order_index' to ensure the workout
        is displayed in the correct sequence (e.g., Warm-up first).
        """
        return self.db.query(WorkoutItem).filter(
            WorkoutItem.plan_id == plan_id
        ).order_by(WorkoutItem.order_index.asc()).all()

    def create_bulk(self, items_data: List[dict]):
        """
        Optimization: Insert multiple workout items at once.
        Instead of calling 'create()' 10 times for 10 exercises (10 commits),
        we add them all and commit once. Much faster.
        """
        db_items = [WorkoutItem(**item) for item in items_data]
        self.db.add_all(db_items)
        self.db.commit()

        # We don't refresh all items individually to save time,
        # unless explicitly needed.
        return db_items