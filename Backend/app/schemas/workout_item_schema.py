from pydantic import BaseModel, Field, field_validator
from typing import Optional

# We need this to embed the full exercise details inside the item
from .exercise_schema import ExerciseResponse


# --- Base Schema ---
# The core instructions from the Trainer.
class WorkoutItemBase(BaseModel):
    # Order index must be non-negative (0, 1, 2...)
    order_index: int = Field(..., ge=0)

    # You cannot have a workout with 0 sets.
    sets: int = Field(..., gt=0)

    # Reps is a string to allow ranges ("12-15") or text ("Failure"),
    # but it cannot be empty.
    reps: str = Field(..., min_length=1)

    # Rest cannot be negative.
    rest_seconds: Optional[int] = Field(None, ge=0)

    weight_guideline: Optional[str] = None  # e.g. "70% 1RM"
    notes: Optional[str] = None  # Specific tips

    # --- Validators ---

    @field_validator('reps')
    @classmethod
    def validate_reps_content(cls, v: str):
        if not v.strip():
            raise ValueError("Reps field cannot be empty")
        return v


# --- Create Schema ---
# Used when adding an exercise to a plan
class WorkoutItemCreate(WorkoutItemBase):
    # We must have a valid exercise ID (positive integer)
    exercise_id: int = Field(..., gt=0)


# --- Update Schema ---
# Used by both Trainer (correction) and Member (logging execution)
class WorkoutItemUpdate(BaseModel):
    # -- Trainer Fields --
    order_index: Optional[int] = Field(None, ge=0)
    sets: Optional[int] = Field(None, gt=0)
    reps: Optional[str] = None
    rest_seconds: Optional[int] = Field(None, ge=0)
    weight_guideline: Optional[str] = None
    notes: Optional[str] = None
    exercise_id: Optional[int] = Field(None, gt=0)

    # -- Member / Execution Fields --
    actual_sets: Optional[int] = Field(None, gt=0)  # Must be positive if logged
    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None
    feedback_notes: Optional[str] = None

    @field_validator('reps', 'actual_reps')
    @classmethod
    def validate_reps_not_empty(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Reps cannot be empty")
        return v


# --- Response Schema ---
class WorkoutItemResponse(WorkoutItemBase):
    id: int
    plan_id: int
    exercise_id: int

    # --- Nested Object ---
    # The frontend gets the full exercise object (Name, Muscle Group).
    exercise: Optional[ExerciseResponse] = None

    # --- Execution History ---
    actual_sets: Optional[int] = None
    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None
    feedback_notes: Optional[str] = None

    class Config:
        from_attributes = True