from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# --- Base Schema ---
class PaymentBase(BaseModel):
    # Validation: Amount must be positive (greater than 0)
    amount: float = Field(..., gt=0, description="Payment amount in NIS")

    # "CASH", "BIT", "CREDIT_CARD", "BANK_TRANSFER"
    payment_method: str

    # Optional: External transaction ID (e.g. from Bit app)
    # limit length to avoid DB overflow
    transaction_id: Optional[str] = Field(None, max_length=100)

    # Optional: What did they pay for?
    # Usually linked to a subscription, but could be None for general purchases.
    subscription_id: Optional[int] = Field(None, gt=0)

    # --- Validators ---

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v: str):
        # We enforce a strict list of allowed payment methods.
        allowed_methods = ["CASH", "BIT", "CREDIT_CARD", "BANK_TRANSFER"]

        if v.upper() not in allowed_methods:
            raise ValueError(f"Payment method must be one of: {', '.join(allowed_methods)}")

        return v.upper()  # Standardize to uppercase (Bit -> BIT)


# --- Create Schema ---
class PaymentCreate(PaymentBase):
    # We must know WHO is paying.
    member_id: int = Field(..., gt=0)


# --- Response Schema ---
class PaymentResponse(PaymentBase):
    id: int
    member_id: int


    payment_date: datetime

    class Config:
        from_attributes = True