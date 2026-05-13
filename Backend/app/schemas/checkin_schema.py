from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# --- Base Schema ---
# Common fields shared between Create and Response
class CheckInBase(BaseModel):
    # Default is QR_SCAN, but we must validate acceptable values.
    method: str = "QR_SCAN"

    # Optional notes (e.g., "Gate didn't open, manual override")
    notes: Optional[str] = None

    # --- Validators ---

    @field_validator('method')
    @classmethod
    def validate_method_enum(cls, v: str):
        # We ensure the method is one of the allowed types in our system.
        # This prevents "Garbage Data" in the database.
        allowed_methods = ["QR_SCAN", "NFC", "MANUAL", "FACE_ID", "PIN_CODE"]

        if v.upper() not in allowed_methods:
            raise ValueError(f"Check-in method must be one of: {', '.join(allowed_methods)}")

        return v.upper()  # Standardize to uppercase

    @field_validator('notes')
    @classmethod
    def validate_notes_length(cls, v: Optional[str]):
        # Prevent huge text blobs that could fill up the DB storage
        if v and len(v) > 255:
            raise ValueError("Notes cannot exceed 255 characters")
        return v


# --- Create Schema ---
class CheckInCreate(CheckInBase):
    enrollment_id: int
    # 'method' and 'notes' are inherited from CheckInBase along with their validators


# --- Response Schema ---
class CheckInResponse(CheckInBase):
    id: int
    checked_in_at: datetime
    enrollment_id: int

    # 'method' and 'notes' are inherited and will be displayed in the response

    class Config:
        from_attributes = True