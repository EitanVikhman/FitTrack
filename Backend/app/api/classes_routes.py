from flask import Blueprint, request, jsonify  # Import Flask tools for routing and JSON handling
from http import HTTPStatus  # Import HTTP status codes for standard responses

# Correct import of SessionLocal from the db.py file to handle database connections
from app.database.db import SessionLocal

# Services - importing the business logic layers
from app.services.class_session_service import ClassSessionService
# Note: Ensure that enrollment_service.py exists and contains the EnrollmentService class
from app.services.enrollment_service import EnrollmentService

# Schemas - importing Pydantic models for data validation and serialization
from app.schemas.class_session_schema import ClassSessionCreate, ClassSessionResponse

# Define the Blueprint for class-related routes
class_bp = Blueprint('class_bp', __name__)


# =========================================================================
# CLASS MANAGEMENT (Managing the class sessions themselves)
# =========================================================================

@class_bp.route('', methods=['POST'])
def create_class():
    """Create a new class session in the schedule"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Retrieve the JSON payload from the request
        data = request.get_json()

        # Validate the incoming data using the Pydantic schema
        class_dto = ClassSessionCreate(**data)

        # Initialize the service with the database session
        service = ClassSessionService(db)
        # Call the service to create the new class session
        new_class = service.create_class_session(class_dto)

        # Convert the result to a dictionary and return it with 201 Created status
        return jsonify(ClassSessionResponse.model_validate(new_class).model_dump()), HTTPStatus.CREATED

    except Exception as e:
        # Return a structured error message in JSON format if something goes wrong
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session to release the connection
        db.close()


@class_bp.route('', methods=['GET'])
def get_all_classes():
    """Get all scheduled classes"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Initialize the service
        service = ClassSessionService(db)
        # Fetch all class sessions from the database
        classes = service.get_all_sessions()
        # Serialize the list of class objects into a list of dictionaries and return JSON
        return jsonify([ClassSessionResponse.model_validate(c).model_dump() for c in classes]), HTTPStatus.OK
    except Exception as e:
        # Handle exceptions and return error message
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


# =========================================================================
# ENROLLMENT & PARTICIPANTS (Member enrollment for classes)
# =========================================================================

@class_bp.route('/<int:class_id>/enroll', methods=['POST'])
def enroll_member(class_id):
    """Enroll a member to a class (or add to waitlist)"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Get JSON data from request
        data = request.get_json()
        # Extract member_id from the data
        member_id = data.get('member_id')

        # Validate that member_id is provided
        if not member_id:
            return jsonify({"error": "member_id is required"}), HTTPStatus.BAD_REQUEST

        # Initialize the EnrollmentService
        service = EnrollmentService(db)
        # Call the service to register the member to the specific class
        result = service.register_to_class(member_id, class_id)

        # Return the result (Success/Waitlist message) with 201 Created status
        return jsonify(result), HTTPStatus.CREATED

    except Exception as e:
        # Handle exceptions (e.g., class full, member not found)
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


@class_bp.route('/<int:class_id>/cancel', methods=['POST'])
def cancel_enrollment(class_id):
    """Cancel enrollment for a member"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Get JSON data
        data = request.get_json()
        # Extract member_id
        member_id = data.get('member_id')

        # Validate that member_id is provided
        if not member_id:
            return jsonify({"error": "member_id is required"}), HTTPStatus.BAD_REQUEST

        # Initialize the EnrollmentService
        service = EnrollmentService(db)

        # Improved Logic: Try to let the Service handle cancellation by member_id and class_id
        try:
            # Attempt to call the specific cancellation method in the service
            result = service.cancel_registration_by_member(member_id, class_id)
            return jsonify(result), HTTPStatus.OK
        except AttributeError:
            # Fallback: If the helper method doesn't exist in the Service, try manual lookup
            # This requires access to the repository within the service
            repo = service.enrollment_repo
            # Find the specific enrollment record
            enrollment = repo.get_by_member_and_class(member_id, class_id)

            # If no enrollment is found, return 404
            if not enrollment:
                return jsonify({"error": "Enrollment not found"}), HTTPStatus.NOT_FOUND

            # Cancel using the enrollment ID
            result = service.cancel_registration(enrollment.id)
            return jsonify(result), HTTPStatus.OK

    except Exception as e:
        # Handle general exceptions
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


@class_bp.route('/<int:class_id>/participants', methods=['GET'])
def get_participants(class_id):
    """List participants and waitlist"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Initialize the EnrollmentService
        service = EnrollmentService(db)
        # Fetch the list of participants for the given class ID
        result = service.get_class_participants(class_id)
        # Return the list as JSON
        return jsonify(result), HTTPStatus.OK
    except Exception as e:
        # Handle exceptions
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()