from flask import jsonify  # Import jsonify to convert Python dictionaries to JSON responses
from . import exceptions  # Import the custom exceptions module defined in the project

# 1. Mapping Exceptions to HTTP Status Codes
# This dictionary maps specific custom exception classes to standard HTTP status codes.
# It acts as a configuration for how the API should respond to different internal errors.
EXCEPTION_STATUS_MAP = {
    # 404 - Not Found: User requested a resource that doesn't exist
    exceptions.ResourceNotFoundException: 404,
    exceptions.NotFoundErrorException: 404,
    exceptions.UserIsNotExistException: 404,
    exceptions.MemberNotFoundException: 404,
    exceptions.SubscriptionNotExistException: 404,

    # 400 - Bad Request: Client sent invalid data or violated business logic
    exceptions.BusinessRuleException: 400,
    exceptions.ClassIsFullException: 400,
    exceptions.SubscriptionAlreadyExistException: 400,
    exceptions.IncorrectPhoneNumberException: 400,
    exceptions.DuplicateErrorException: 400,
    exceptions.UserAlreadyExistsException: 400,

    # 401 - Unauthorized: Authentication failed (wrong password/email)
    exceptions.IncorrectPasswordException: 401,
    exceptions.IncorrectEmailException: 401,

    # 403 - Forbidden: Authenticated user does not have permission
    exceptions.UserAccessDeniedException: 403,

    # 500 - Internal Server Error: Unexpected system or database failures
    exceptions.DatabaseErrorException: 500,
}

def register_exception_handlers(app):
    """
    Function that accepts the Flask application instance
    and registers all the error handlers defined in the map.
    """

    # Internal factory function to create a specific handler for a given status code.
    # We use a closure here to capture the 'status_code' variable for the handler.
    def create_handler(status_code):
        def handler(error):
            # Flask expects a return value of (Response, Status Code).
            # We construct a consistent JSON error format for all exceptions.
            return jsonify({
                "error": True,  # Flag indicating an error occurred
                "type": type(error).__name__,  # The name of the exception class (e.g., "ResourceNotFoundException")
                "message": getattr(error, "message", str(error))  # The error message string
            }), status_code
        return handler

    # Iterate over the configuration map and register each exception class with Flask.
    # This tells Flask: "When X exception is raised, run the handler created with Y status code."
    for exc_class, status_code in EXCEPTION_STATUS_MAP.items():
        app.register_error_handler(exc_class, create_handler(status_code))

    # Optional: Default handler for generic 500 errors not caught by our custom exceptions.
    # This ensures the API always returns JSON, even for unexpected crashes.
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "error": True,
            "type": "InternalServerError",
            "message": "An unexpected error occurred"
        }), 500