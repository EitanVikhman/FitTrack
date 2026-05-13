from sqlalchemy.orm import Session
from typing import List

from app.models.exercise import Exercise, MuscleGroup
from .base_repository import BaseRepository

class ExerciseRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Exercise)

    def get_by_muscle_group(self, group: MuscleGroup) -> List[Exercise]:
        """
        Get all exercises for a specific muscle group (e.g., CHEST, LEGS).
        Useful for filtering in the workout builder UI.
        """
        return self.db.query(Exercise).filter(
            Exercise.muscle_group == group
        ).all()

    def search_by_name(self, query: str) -> List[Exercise]:
        """
        Search exercises by name (case-insensitive partial match).
        Example: query="bench" -> returns "Bench Press", "Incline Bench".
        """
        # ilike is case-insensitive LIKE in SQL
        return self.db.query(Exercise).filter(
            Exercise.name.ilike(f"%{query}%")
        ).all()