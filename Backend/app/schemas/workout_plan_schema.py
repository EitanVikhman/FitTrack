from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import date

# We import the Item schema to embed the exercises inside the plan response
from .workout_item_schema import WorkoutItemResponse


# --- Base Schema ---
class WorkoutPlanBase(BaseModel):
    start_date: date
    end_date: date

    # Goal cannot be empty
    goal: str = Field(..., min_length=2)

    notes: Optional[str] = None
    status: Optional[str] = "ACTIVE"

    # --- Validators ---

    @field_validator('goal')
    @classmethod
    def validate_goal_content(cls, v: str):
        if not v.strip():
            raise ValueError("Goal cannot be empty")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]):
        if v:
            allowed_statuses = ["ACTIVE", "COMPLETED", "ARCHIVED", "CANCELLED"]
            if v.upper() not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
            return v.upper()

    # CRITICAL: Validate that End Date is AFTER Start Date
    @model_validator(mode='after')
    def check_dates_logic(self):
        # self refers to the model instance with all fields
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        return self


# --- Create Schema ---
class WorkoutPlanCreate(WorkoutPlanBase):
    # CRITICAL FIX: We must know WHO this plan is for and WHO created it.
    # IDs must be positive integers.
    member_id: Optional[int] = None
    trainer_id: Optional[int] = None


# --- Update Schema ---
# Used to change dates, update status (ACTIVE -> COMPLETED), or refine the goal.
class WorkoutPlanUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    goal: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

    # --- Validators (Update) ---

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]):
        if v:
            allowed_statuses = ["ACTIVE", "COMPLETED", "ARCHIVED", "CANCELLED"]
            if v.upper() not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
            return v.upper()

    @field_validator('goal')
    @classmethod
    def validate_goal_content(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Goal cannot be empty")
        return v


# --- Response Schema ---
class WorkoutPlanResponse(WorkoutPlanCreate):
    id: int
    status : str


    items: List[WorkoutItemResponse] = None

    class Config:
        from_attributes = True