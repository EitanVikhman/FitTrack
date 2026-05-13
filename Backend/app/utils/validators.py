import re

# --- Regex Constants ---

# Standard email format
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# Israeli Mobile Phone:
# Starts with 05, followed by a digit (0-9), optional hyphen, and 7 more digits.
# Valid: 0501234567, 050-1234567, 0548888888
PHONE_REGEX = r"^05\d-?\d{7}$"

# Israeli ID Structure:
# Basic check for 9 digits.
# (Note: Does not perform the mathematical checksum calculation, but satisfies assignment requirements)
ID_NUMBER_REGEX = r"^\d{9}$"

# Strong Password:
# 1. At least one lowercase letter (?=.*[a-z])
# 2. At least one uppercase letter (?=.*[A-Z])
# 3. At least one digit (?=.*\d)
# 4. At least one special char from the list [@$!%*?&]
# 5. Minimum 8 characters total
# Note: This restricts special chars to ONLY @$!%*?&. Chars like # or ^ are not allowed.
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


# --- Validation Functions ---

def validate_email_format(email: str) -> bool:
    """Returns True if the email matches standard format."""
    return bool(re.match(EMAIL_REGEX, email))

def validate_israeli_phone(phone: str) -> bool:
    """Returns True if the phone is a valid Israeli mobile number."""
    return bool(re.match(PHONE_REGEX, phone))

def validate_id_number(id_number: str) -> bool:
    """Returns True if the ID consists of exactly 9 digits."""
    return bool(re.match(ID_NUMBER_REGEX, id_number))

def validate_password_strength(password: str) -> bool:
    """
    Checks if password meets complexity requirements:
    - Min 8 chars
    - At least 1 Uppercase, 1 Lowercase, 1 Digit, 1 Special Char
    """
    return bool(re.match(PASSWORD_REGEX, password))