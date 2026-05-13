from pydantic import BaseModel, Field, field_validator
from typing import Optional


# --- Base Schema ---
# Defines the core structure of a "Product" in the gym (e.g., Gold Membership).
class PlanBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

    # Validation: Price must be positive.
    price: float = Field(..., gt=0, description="Price in NIS")

    # Validation: A plan cannot last 0 or negative days.
    duration_days: int = Field(..., gt=0, description="Duration in days")

    # Optional: If set, it limits the number of visits (Punch Card).
    # If None, it implies unlimited visits within the duration.
    max_entries: Optional[int] = None

    # --- Validators ---

    @field_validator('name')
    @classmethod
    def validate_name_clean(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Plan name cannot be empty")
        return v.title()

    @field_validator('max_entries')
    @classmethod
    def validate_positive_entries(cls, v: Optional[int]):
        # If max_entries is provided (not None), it must be positive.
        if v is not None and v <= 0:
            raise ValueError("Max entries must be greater than 0")
        return v


# --- Create Schema ---
class PlanCreate(PlanBase):
    pass


# --- Update Schema ---
# Allows changing price or terms for future sales.
class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    max_entries: Optional[int] = None

    # --- Validators (Update) ---

    @field_validator('name')
    @classmethod
    def validate_name_clean(cls, v: Optional[str]):
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Plan name cannot be empty")
            return v.title()
        return v

    @field_validator('max_entries')
    @classmethod
    def validate_positive_entries(cls, v: Optional[int]):
        if v is not None and v <= 0:
            raise ValueError("Max entries must be greater than 0")
        return v


# --- Response Schema ---
class PlanResponse(PlanBase):
    id: int

    class Config:
        from_attributes = True