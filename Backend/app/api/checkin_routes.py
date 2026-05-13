from flask import Blueprint, jsonify  # Import Blueprint for routing and jsonify for JSON responses
from http import HTTPStatus  # Import HTTP status codes for standard responses

from app.database import SessionLocal  # Import the session factory to create database connections
from app.services.member_service import MemberService  # Import the service layer for member logic

# Define a separate Blueprint for Check-In functionality to keep routes organized
checkin_bp = Blueprint('checkin', __name__)


@checkin_bp.route('/members/<int:member_id>/checkin', methods=['POST'])
def check_in(member_id):
    """
    Perform a member check-in.
    This endpoint uses the MemberService logic to:
    1. Verify if the member exists.
    2. Check subscription validity and member status (Banned/Frozen).
    3. Log the entry attempt in the database (EntryLog).
    """
    # Initialize a new database session for this request
    db = SessionLocal()
    try:
        # Initialize the MemberService with the active database session
        service = MemberService(db)

        # Call the centralized service method to process the check-in
        # This handles logic for subscription validation and logging the entry
        result = service.process_check_in(member_id)

        # Check if the business logic returned an 'APPROVED' status
        if result['status'] == "APPROVED":
            # Return the success result as JSON with HTTP 200 OK status
            return jsonify(result), HTTPStatus.OK
        else:
            # If rejected (Banned, Frozen, Invalid Subscription), return HTTP 403 Forbidden
            return jsonify(result), HTTPStatus.FORBIDDEN

    except Exception as e:
        # Catch unexpected server errors and return HTTP 500 Internal Server Error
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        # Close the database session to release the connection
        db.close()