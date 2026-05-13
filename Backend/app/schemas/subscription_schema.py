from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import Optional


# --- Base Schema ---
# Common fields shared between Create and Response
class SubscriptionBase(BaseModel):
    member_id: int = Field(..., gt=0)
    plan_id: int = Field(..., gt=0)

    start_date: date
    end_date: date

    # "Monthly", "Yearly", "PunchCard"
    type: str

    status: Optional[str] = "ACTIVE"

    # If None -> Unlimited entries.
    # If number -> Punch card.
    entries_remaining: Optional[int] = None

    # --- Validators ---

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str):
        allowed_types = ["Monthly", "Yearly", "PunchCard"]
        # Case insensitive check, then normalize to Title Case
        if v.title() not in allowed_types:
            raise ValueError(f"Subscription type must be one of: {', '.join(allowed_types)}")
        return v.title()

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]):
        if v:
            allowed_statuses = ["ACTIVE", "EXPIRED", "CANCELLED", "FROZEN"]
            if v.upper() not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
            return v.upper()

    @field_validator('entries_remaining')
    @classmethod
    def validate_entries(cls, v: Optional[int]):
        # You cannot have -5 entries remaining
        if v is not None and v < 0:
            raise ValueError("Entries remaining cannot be negative")
        return v

    # CRITICAL: Validate that End Date is AFTER Start Date
    @model_validator(mode='after')
    def check_dates_logic(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        return self


# --- Create Schema ---
# What the frontend sends to create a subscription
class SubscriptionCreate(SubscriptionBase):

    # This allows automatic mapping in the Service layer.
    price_paid: float = Field(..., gt=0, description="Actual price paid in NIS")
    member_id: Optional[int] = None
    plan_id: Optional[int] = None
    start_date: date
    end_date: date
    status: str = "ACTIVE"


# --- Response Schema ---
# What the frontend receives back
class SubscriptionResponse(SubscriptionBase):
    id: int
    member_id: int
    plan_id: Optional[int]
    start_date: date
    end_date: date
    status: str
    #
    #  from_attributes='True' is smart enough to read that property!
    price_paid: float

    class Config:
        from_attributes = True