from typing import Optional
from datetime import date
from pydantic import  field_validator

# We inherit from User schemas to avoid code duplication
from .user_schema import UserBase, UserCreate, UserUpdate, UserResponse
from app.utils.validators import validate_israeli_phone


# --- Base Schema ---
class MemberBase(UserBase):
    # Specific fields for Member table
    # Note: DB column is named 'phone', NOT 'phone_number'
    phone: str

    date_of_birth: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    membership_type: str = "Regular"  # Default value

    # --- Validators (Base) ---
    # These apply if we use MemberBase directly, but usually we use Create/Update

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: str):
        if not validate_israeli_phone(v):
            raise ValueError("Phone must be a valid Israeli number (05X-XXXXXXX)")
        return v

    @field_validator('date_of_birth')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]):
        if v and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator('height', 'weight')
    @classmethod
    def validate_positive_metrics(cls, v: Optional[float]):
        if v is not None and v <= 0:
            raise ValueError("Height and Weight must be positive numbers")
        return v


# --- Create Schema ---
class MemberCreate(UserCreate):
    # Inherits email/password from UserCreate
    # Adds Member specific fields:
    first_name: str
    last_name: str
    phone: str
    join_date: Optional[date] = date.today()
    membership_type: str

    # Optional physical stats
    date_of_birth: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    password: Optional[str] = None

    # --- Validators (Create) ---
    # We must explicitly include validators here because we inherit from UserCreate

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: str):
        if not validate_israeli_phone(v):
            raise ValueError("Phone must be a valid Israeli number (05X-XXXXXXX)")
        return v

    @field_validator('date_of_birth')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]):
        if v and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator('height', 'weight')
    @classmethod
    def validate_positive_metrics(cls, v: Optional[float]):
        if v is not None and v <= 0:
            raise ValueError("Height and Weight must be positive numbers")
        return v


# --- Update Schema ---
class MemberUpdate(UserUpdate):
    # Everything is optional
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    membership_type: Optional[str] = None
    join_date: Optional[date] = None
    status: Optional[str] = None

    # --- Validators (Update) ---
    # Checks are only performed if the value is not None

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]):
        if v and not validate_israeli_phone(v):
            raise ValueError("Phone must be a valid Israeli number")
        return v

    @field_validator('date_of_birth')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]):
        if v and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator('height', 'weight')
    @classmethod
    def validate_positive_metrics(cls, v: Optional[float]):
        if v is not None and v <= 0:
            raise ValueError("Height and Weight must be positive numbers")
        return v


# --- Response Schema ---
class MemberResponse(UserResponse):
    # Includes User fields (id, email, name) + Member fields
    phone: str
    join_date: date
    membership_type: str
    status: str

    date_of_birth: Optional[date]
    height: Optional[float]
    weight: Optional[float]

    class Config:
        from_attributes = True