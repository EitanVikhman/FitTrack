from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Import nested schemas for the detailed response
from .member_schema import MemberResponse
from .class_session_schema import ClassSessionResponse


# --- Base Schema ---
class EnrollmentBase(BaseModel):
    # Usually empty because status and time are handled automatically by the logic.
    pass


# --- Create Schema ---
# Used when a user clicks "Book Class"
class EnrollmentCreate(BaseModel):
    # Validation: IDs must be positive integers
    member_id: int = Field(..., gt=0, description="The ID of the member booking the class")
    class_session_id: int = Field(..., gt=0, description="The ID of the session to book")


# --- Update Schema ---
# Used mainly for cancellations or admin updates
class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None

    # Matches the 'cancellation_source' column in the DB.
    cancellation_source: Optional[str] = None

    # --- Validators ---

    @field_validator('status')
    @classmethod
    def validate_status_enum(cls, v: Optional[str]):
        if v:
            allowed_statuses = ["REGISTERED", "CANCELLED", "WAITLIST", "ATTENDED", "NOSHOW"]
            if v.upper() not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
            return v.upper()

    @field_validator('cancellation_source')
    @classmethod
    def validate_source_enum(cls, v: Optional[str]):
        if v:
            allowed_sources = ["MEMBER", "ADMIN", "SYSTEM"]
            if v.upper() not in allowed_sources:
                raise ValueError(f"Cancellation source must be one of: {', '.join(allowed_sources)}")
            return v.upper()


# --- Response Schema ---
class EnrollmentResponse(BaseModel):
    id: int
    created_at: datetime
    status: str

    # Optional: Return who cancelled it, if relevant
    cancellation_source: Optional[str] = None

    # --- Nested Objects (Detailed) ---
    # Returning the full objects allows the UI to show:
    # "Confirmed for Pilates with Yossi" immediately.
    member: MemberResponse
    class_session: ClassSessionResponse

    class Config:
        from_attributes = True