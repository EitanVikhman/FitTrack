class AppBaseException(Exception):
    # Define a base class for all custom application exceptions, inheriting from Python's built-in Exception class
    def __init__(self, message: str):
        # Constructor method that accepts a custom error message string
        self.message = message
        # Call the constructor of the parent Exception class to initialize it with the message
        super().__init__(self.message)

# --- General ---
class ResourceNotFoundException(AppBaseException):
    # Exception raised when a specific resource (e.g., a file or database record) cannot be found
    pass

class NotFoundErrorException(AppBaseException):
    # General exception for "Not Found" errors, potentially used for API 404 responses
    pass

class DuplicateErrorException(AppBaseException):
    # Exception raised when attempting to create a record that already exists (e.g., unique constraint violation)
    pass

class BusinessRuleException(AppBaseException):
    # Exception raised when a business logic rule is violated (e.g., "End time must be after start time")
    pass

class DatabaseErrorException(AppBaseException): # תוקן מ-Erorr
    # Exception raised when a database operation fails (e.g., connection issues or query errors)
    pass

# --- Auth & Users ---
class IncorrectPasswordException(AppBaseException):
    # Exception raised during login if the provided password does not match the stored hash
    pass

class IncorrectEmailException(AppBaseException):
    # Exception raised during login if the provided email does not exist in the system
    pass

class UserAccessDeniedException(AppBaseException):
    # Exception raised when a user tries to access a resource they don't have permission for (403 Forbidden)
    pass

class UserIsNotExistException(AppBaseException):
    # Exception raised when an operation expects a user ID that does not exist
    pass

class UserAlreadyExistsException(AppBaseException):
    # Exception raised during registration if the user (email/username) is already taken
    pass

class MemberNotFoundException(AppBaseException):
    # Specific exception for when a gym member cannot be found by their ID
    pass

class IncorrectPhoneNumberException(AppBaseException):
    # Exception raised if a provided phone number format is invalid or incorrect
    pass

# --- Gym Logic ---
class ClassIsFullException(AppBaseException):
    # Exception raised when a member tries to enroll in a class that has reached its capacity
    pass

class SubscriptionAlreadyExistException(AppBaseException):
    # Exception raised when trying to assign a subscription to a member who already has one active
    pass

class SubscriptionNotExistException(AppBaseException):
    # Exception raised when an operation requires a subscription but none is found for the member
    pass


class DatabaseErorrException:
    # Define a class named DatabaseErorrException (Note: This class does not inherit from AppBaseException)
    pass