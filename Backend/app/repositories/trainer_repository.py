from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.trainer import Trainer
from .base_repository import BaseRepository

class TrainerRepository(BaseRepository):
    def __init__(self, db: Session):
        # Pass the DB session and the Trainer model to the parent
        super().__init__(db, Trainer)

    def get_by_email(self, email: str) -> Optional[Trainer]:
        """
        Find a trainer by email.
        """
        return self.db.query(Trainer).filter(Trainer.email == email).first()

    def get_by_phone(self, phone: str) -> Optional[Trainer]:
        """
        Find a trainer by phone number.
        Note: The field in Trainer model is 'phone_number', not 'phone'.
        """
        return self.db.query(Trainer).filter(Trainer.phone_number == phone).first()

    def get_by_specialization(self, specialization: str) -> List[Trainer]:
        """
        Get all trainers with a specific specialization (e.g., 'Yoga', 'HIIT').
        """
        return self.db.query(Trainer).filter(Trainer.specialization == specialization).all()