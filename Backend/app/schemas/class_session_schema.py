import enum

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime

# We need the TrainerResponse to nest it inside the session response
from .trainer_schema import TrainerResponse


class SessionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
# --- Base Schema ---
class ClassSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

    # Validates that capacity must be greater than 0.
    capacity: int = Field(..., gt=0)

    # --- Validators (Logic) ---

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.title()

    # This validator checks TWO fields together: start_time and end_time.
    @model_validator(mode='after')
    def check_time_logic(self):
        # self is the full object with all data
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


# --- Create Schema ---
class ClassSessionCreate(ClassSessionBase):
    title: str = Field(..., min_length=2, description="Class name, e.g., 'Pilates'")
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    capacity: int = Field(..., gt=0)
    trainer_id: Optional[int] = None
    status: SessionStatus = SessionStatus.SCHEDULED

    # Validator to ensure we don't schedule classes in the past
    @field_validator('start_time')
    @classmethod
    def validate_future_date(cls, v: datetime):
        # Note: We use datetime.now() without timezone for simplicity,
        # ensure your DB and App use the same timezone logic.
        if v < datetime.now():
            raise ValueError("Cannot schedule a class in the past")
        return v


# --- Update Schema ---
class ClassSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = Field(None, gt=0)
    trainer_id: Optional[int] = None
    status: Optional[str] = None  # e.g., "CANCELLED"

    # Validator for Status Enum
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]):
        if v:
            allowed_statuses = ["SCHEDULED", "CANCELLED", "COMPLETED"]
            if v.upper() not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
            return v.upper()

    # Note: Validating start_time < end_time in Update is tricky
    # because the user might send only one of them.
    # Usually, we handle that complex logic in the Service layer,
    # or strictly require both times if one is changed.


# --- Response Schema ---
class ClassSessionResponse(ClassSessionBase):
    id: int

    # Returns the full trainer object inside the session
    trainer: Optional[TrainerResponse] = None

    class Config:
        from_attributes = True