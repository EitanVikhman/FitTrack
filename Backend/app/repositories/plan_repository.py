from sqlalchemy.orm import Session
from typing import Optional
from app.models.plan import Plan
from .base_repository import BaseRepository

class PlanRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Plan)

    def get_by_name(self, name: str) -> Optional[Plan]:
        """
        Get a plan by its name (e.g., 'Gold Membership').
        Useful for validation to prevent duplicate plan names.
        """
        return self.db.query(Plan).filter(Plan.name == name).first()