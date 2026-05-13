from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.class_session import ClassSession
from .base_repository import BaseRepository


class ClassSessionRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, ClassSession)

    # Note: We use the BaseRepository's create/update/delete methods.
    # Pydantic handles the datetime conversion automatically before it reaches here.

    def get_upcoming_classes(self, limit: int = 10) -> List[ClassSession]:
        """
        Get specific number of future classes, sorted by start time.
        Useful for 'Next Classes' widget on the dashboard.
        """
        now = datetime.now()
        return self.db.query(ClassSession).filter(
            ClassSession.start_time >= now,
            ClassSession.status != "CANCELLED"
        ).order_by(ClassSession.start_time.asc()).limit(limit).all()

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ClassSession]:
        """
        Get all classes between two dates.
        CRITICAL for the Calendar View (Weekly/Monthly view).
        """
        return self.db.query(ClassSession).filter(
            ClassSession.start_time >= start_date,
            ClassSession.start_time <= end_date
        ).order_by(ClassSession.start_time.asc()).all()

    def get_by_trainer(self, trainer_id: int) -> List[ClassSession]:
        """
        Get all classes assigned to a specific trainer.
        """
        return self.db.query(ClassSession).filter(
            ClassSession.trainer_id == trainer_id
        ).order_by(ClassSession.start_time.desc()).all()