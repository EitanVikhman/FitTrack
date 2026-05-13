from typing import Optional
from pydantic import BaseModel, field_validator
from .user_schema import UserBase, UserCreate, UserUpdate, UserResponse

# Import the regex validation logic
from app.utils.validators import validate_israeli_phone


# --- Base Schema ---
# Defines the fields specific to a Trainer.
class TrainerBase(BaseModel):
    # We must explicitly define these because the Trainer model splits the name.
    first_name: str
    last_name: str

    # Matches the 'phone_number' column in the Trainer model exactly.
    phone_number: Optional[str] = None

    # The unique field for trainers.
    specialization: Optional[str] = None

    # --- Validators (Base) ---

    @field_validator('phone_number')
    @classmethod
    def validate_trainer_phone(cls, v: Optional[str]):
        # If the field is not None, validate it
        if v and not validate_israeli_phone(v):
            raise ValueError("Trainer phone must be a valid Israeli number (05X-XXXXXXX)")
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name_content(cls, v: str):
        # We re-apply name validation here because we redefined the fields
        if not v.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v.title()


# --- Create Schema ---
# Used for POST /trainers
# Inherits email & password from UserCreate
class TrainerCreate(UserCreate):
    # We repeat the trainer fields here to ensure they are required/allowed during creation.
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    specialization: Optional[str] = None

    # --- Validators (Create) ---

    @field_validator('phone_number')
    @classmethod
    def validate_trainer_phone(cls, v: Optional[str]):
        if v and not validate_israeli_phone(v):
            raise ValueError("Trainer phone must be a valid Israeli number (05X-XXXXXXX)")
        return v

    # Note: Name validation is inherited from UserCreate/UserBase,
    # but since we redeclared fields, Pydantic might skip inherited validators for these specific fields.
    # It's safer to explicitly validate here too.
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name_content(cls, v: str):
        if not v.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return v.title()


# --- Update Schema ---
# Used for PATCH /trainers/{id}
# Inherits password/email update logic from UserUpdate
class TrainerUpdate(UserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    specialization: Optional[str] = None

    # --- Validators (Update) ---

    @field_validator('phone_number')
    @classmethod
    def validate_trainer_phone(cls, v: Optional[str]):
        if v and not validate_israeli_phone(v):
            raise ValueError("Trainer phone must be a valid Israeli number")
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name_content(cls, v: Optional[str]):
        if v is None:
            return v
        if not v.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return v.title()


# --- Response Schema ---
# What the frontend receives
class TrainerResponse(UserResponse):
    id: int
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    specialization: Optional[str] = None

    class Config:
        # Allows Pydantic to read data directly from the SQLAlchemy model
        from_attributes = True