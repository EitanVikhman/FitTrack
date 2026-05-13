from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base


class WorkoutItem(Base):
    """
    Represents a specific exercise within a workout plan.
    It contains both the PLANNED instructions (from the trainer)
    and the ACTUAL results (from the member).
    """
    __tablename__ = "workout_items"

    id = Column(Integer, primary_key=True, index=True)

    # --- Parent Links ---
    # Links this item to the main plan container.
    plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=False)

    # Links to the library of exercises (e.g., "Bench Press", "Squat").
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    # --- The Prescription (Planned) ---
    # Defines the sequence of exercises in the app (1st, 2nd, 3rd...)
    order_index = Column(Integer, nullable=False)

    sets = Column(Integer, nullable=False)

    # Reps are stored as String to allow ranges like "10-12" or "Until Failure".
    reps = Column(String, nullable=False)

    # Rest time in seconds (e.g., 60, 90).
    rest_seconds = Column(Integer, nullable=True)

    # Specific instruction like "70% 1RM" or "RPE 8".
    weight_guideline = Column(String, nullable=True)

    # Specific tips for this exercise (e.g., "Keep elbows in").
    notes = Column(Text, nullable=True)

    # --- The Execution (Actual) ---
    # These fields start as NULL and are filled by the member during/after the workout.
    # This allows comparing Plan vs. Reality.
    actual_sets = Column(Integer, nullable=True)
    actual_reps = Column(String, nullable=True)
    actual_weight = Column(String, nullable=True)

    # Member's feedback (e.g., "Too heavy", "Felt pain in shoulder").
    feedback_notes = Column(String, nullable=True)

    # --- Relationships ---

    # Connection to the WorkoutPlan.
    # We use 'back_populates="items"' to match the parent model perfectly.
    plan = relationship("WorkoutPlan", back_populates="items")

    # Connection to the Exercise definition.
    # Note: Assuming 'Exercise' model does not strictly need a list of all items using it,
    # so a simple relationship here is sufficient.
    exercise = relationship("Exercise")

    def __repr__(self):
        return f"<WorkoutItem(id={self.id}, exercise_id={self.exercise_id})>"