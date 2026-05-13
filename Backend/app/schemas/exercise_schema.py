from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.models.exercise import MuscleGroup  # Import the Enum from  models exercise


# --- Base Schema ---
class ExerciseBase(BaseModel):
    # Validation: Name cannot be empty or too short
    name: str = Field(..., min_length=2, max_length=100)

    description: Optional[str] = None

    # POWERFUL: Pydantic validates this against the Enum values automatically.
    # If user sends "Brain", it will raise a validation error.
    # It expects strings like "CHEST", "LEGS", "BACK", "CARDIO".
    muscle_group: MuscleGroup

    # --- Validators ---

    @field_validator('name')
    @classmethod
    def validate_name_clean(cls, v: str):
        # Clean up whitespace (e.g., "  Push Up  " -> "Push Up")
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v.title()


# --- Create Schema ---
class ExerciseCreate(ExerciseBase):
    pass


# --- Update Schema ---
class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    muscle_group: Optional[MuscleGroup] = None  # Optional, but must be valid if sent

    @field_validator('name')
    @classmethod
    def validate_name_clean(cls, v: Optional[str]):
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty")
            return v.title()
        return v


# --- Response Schema ---
class ExerciseResponse(ExerciseBase):
    id: int

    class Config:
        from_attributes = True
        # Hints Pydantic to handle Enums correctly when reading from DB
        use_enum_values = True