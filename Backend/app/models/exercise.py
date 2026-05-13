import enum
from sqlalchemy import Column, Integer, String, Text, Enum as SQLAlchemyEnum
from app.database.db import Base


# Defines the anatomical focus of the exercise.
# Using an Enum ensures we can easily filter by "LEGS" or "CHEST" in the app later.
class MuscleGroup(enum.Enum):
    CHEST = "CHEST"
    BACK = "BACK"
    LEGS = "LEGS"
    SHOULDERS = "SHOULDERS"
    ARMS = "ARMS"
    ABS = "ABS"
    CARDIO = "CARDIO"
    FULL_BODY = "FULL_BODY"


class Exercise(Base):
    """
    Represents a definition of a physical movement in the global library.
    This is a 'Lookup Table' - other tables refer to this one.
    """
    __tablename__ = "exercises"

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)

    # --- Content ---
    # The name must be unique. We don't want two "Bench Press" entries.
    # index=True helps when searching for an exercise by name (Autocomplete).
    name = Column(String, unique=True, nullable=False, index=True)

    # Instructions on how to perform the movement.
    description = Column(Text, nullable=True)

    # Categorization for filtering.
    # create_constraint=True (default) ensures the DB rejects invalid muscle groups.
    muscle_group = Column(SQLAlchemyEnum(MuscleGroup), nullable=False)

    # --- Relationships ---
    # Note: We do NOT define a relationship back to WorkoutItem here.
    # Why? Because an exercise is a standalone concept.
    # It doesn't need to know about every single time it was ever assigned to someone.


    def __repr__(self):
        return f"<Exercise(name={self.name}, muscle={self.muscle_group})>"