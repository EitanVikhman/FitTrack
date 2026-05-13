from pydantic import BaseModel, EmailStr, Field, field_validator  # Import Pydantic tools for data validation and schema definition
from typing import Optional  # Import Optional for fields that can be None
from datetime import datetime  # Import datetime for timestamp fields

# We assume that the file utils/validators.py exists at this path
# Import custom helper functions to validate password strength and Israeli phone numbers
from app.utils.validators import validate_password_strength, validate_israeli_phone


# --- Base Schema ---
# Define a base model with shared attributes for User creation and retrieval
class UserBase(BaseModel):
    email: EmailStr  # Pydantic automatically validates that this string is a valid email format
    first_name: str  # Standard string field
    last_name: str   # Standard string field

    # Validation for names: Ensures no numbers are used and fixes capitalization
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name_content(cls, v: str):
        # Check that the name contains only alphabetic characters (no numbers or symbols)
        # Note: If you want to allow hyphens (like "Ben-Gurion"), this check needs modification
        if not v.isalpha():
            raise ValueError("Name must contain only alphabetic characters")

        # Ensure the name is not too short
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")

        # Automatically capitalize the name (e.g., "yossi" -> "Yossi") before saving
        return v.title()


# --- Create Schema ---
# Schema used specifically when creating a new user (extends UserBase)
class UserCreate(UserBase):
    # We removed Field(min_length) because our custom validator in 'utils' is stronger and more precise
    password: str

    # Validator to enforce password complexity rules
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str):
        # Use the imported utility function to check strength
        if not validate_password_strength(v):
            raise ValueError(
                "Password is too weak. Must contain: 8+ chars, uppercase, lowercase, number, special char."
            )
        return v


# --- Update Schema ---
# Schema for updating user details; all fields are optional
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

    # Validation for phone number (runs only if the user provided it)
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        # If the value is None, skip validation
        if v is None:
            return v
        # Use the imported utility to check if it matches Israeli format
        if not validate_israeli_phone(v):
            raise ValueError("Phone number must be a valid Israeli mobile number (05X-XXXXXXX)")
        return v

    # Validation for password during update (runs only if provided)
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: Optional[str]):
        # If the value is None, skip validation
        if v is None:
            return v
        # Check strength
        if not validate_password_strength(v):
            raise ValueError(
                "Password is too weak. Must contain: 8+ chars, uppercase, lowercase, number, special char."
            )
        return v

    # Validation for names during update
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name_content(cls, v: Optional[str]):
        # If the value is None, skip validation
        if v is None:
            return v
        # Check for alphabetic characters only
        if not v.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        # Return capitalized version
        return v.title()


# --- Response Schema ---
# Schema defines what data is returned to the client (frontend)
class UserResponse(BaseModel):
    id: int  # The unique database ID
    # Return basic fields so the frontend knows who was created/retrieved
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime  # Timestamp of creation

    # Config must be inside the class
    class Config:
        # Allows Pydantic to read data from SQLAlchemy ORM objects (not just dictionaries)
        from_attributes = True