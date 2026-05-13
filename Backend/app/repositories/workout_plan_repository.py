from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.workout_plan import WorkoutPlan
from .base_repository import BaseRepository


class WorkoutPlanRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, WorkoutPlan)

    def get_active_plan(self, member_id: int) -> Optional[WorkoutPlan]:
        """
        Fetch the currently active workout plan for a member.
        There should ideally be only one active plan at a time.
        """
        return self.db.query(WorkoutPlan).filter(
            WorkoutPlan.member_id == member_id,
            WorkoutPlan.status == "ACTIVE"
        ).first()

    def archive_current_plans(self, member_id: int):
        """
        Sets all currently 'ACTIVE' plans for a member to 'ARCHIVED'.
        This is called via the Service layer right before creating a new plan.

        Optimization: Uses bulk update instead of looping through objects.
        """
        self.db.query(WorkoutPlan).filter(
            WorkoutPlan.member_id == member_id,
            WorkoutPlan.status == "ACTIVE"
        ).update({"status": "ARCHIVED"})

        self.db.commit()

    def get_member_history(self, member_id: int) -> List[WorkoutPlan]:
        """
        Get all past and present plans for a member, sorted by date (newest first).
        """
        return self.db.query(WorkoutPlan).filter(
            WorkoutPlan.member_id == member_id
        ).order_by(WorkoutPlan.start_date.desc()).all()