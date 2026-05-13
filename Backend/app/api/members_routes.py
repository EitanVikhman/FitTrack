from flask import Blueprint, request, jsonify  # Import Flask utilities for routing, request handling, and JSON responses
from http import HTTPStatus  # Import standard HTTP status codes

# Correct import of the session factory to create database connections
from app.database.db import SessionLocal
# Import business logic services for Members, Workout Plans, and Subscriptions
from app.services.member_service import MemberService
from app.services.workout_plan_service import WorkoutPlanService
from app.services.subscription_service import SubscriptionService
# Import custom exception for handling "Not Found" scenarios
from app.exceptions.exceptions import ResourceNotFoundException

# Import Pydantic schemas for data validation and serialization (Requests and Responses)
from app.schemas.member_schema import MemberCreate, MemberUpdate, MemberResponse
from app.schemas.workout_plan_schema import WorkoutPlanCreate, WorkoutPlanResponse
from app.schemas.subscription_schema import SubscriptionCreate, SubscriptionResponse
# Import the SQLAlchemy Member model
from app.models.member import Member

# Define a Flask Blueprint to group member-related routes under a specific URL prefix
member_bp = Blueprint('member_bp', __name__)


# =========================================================================
# MEMBER MANAGEMENT
# =========================================================================

@member_bp.route('', methods=['GET'])
def get_all_members():
    """Fetch all members"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Query the database to retrieve all member records
        members = db.query(Member).all()
        # Convert each SQLAlchemy object to a Pydantic model, then to a dictionary for JSON response
        members_list = [MemberResponse.model_validate(m).model_dump() for m in members]
        # Return the list of members as JSON with HTTP 200 OK status
        return jsonify(members_list), HTTPStatus.OK
    finally:
        # Close the database session to release the connection
        db.close()


@member_bp.route('', methods=['POST'])
def create_member():
    """Create a new member"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Retrieve the JSON payload from the incoming request
        data = request.get_json()
        # Validate the data using the MemberCreate Pydantic schema
        member_dto = MemberCreate(**data)

        # Initialize the MemberService with the active database session
        service = MemberService(db)
        # Call the service logic to register a new member
        new_member = service.register_new_member(member_dto)

        # Return the newly created member data with HTTP 201 Created status
        return jsonify(MemberResponse.model_validate(new_member).model_dump()), HTTPStatus.CREATED
    except Exception as e:
        # Handle any errors (validation or database) and return a Bad Request response
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


@member_bp.route('/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """Get specific member profile"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Initialize the MemberService
        service = MemberService(db)
        # Fetch the profile for the specific member ID via the service
        member = service.get_member_profile(member_id)
        # Return the member profile as JSON with HTTP 200 OK status
        return jsonify(MemberResponse.model_validate(member).model_dump()), HTTPStatus.OK
    finally:
        # Close the database session
        db.close()


@member_bp.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """Update member details"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Retrieve the JSON payload from the request
        data = request.get_json()
        # Validate the update data using the MemberUpdate schema
        update_dto = MemberUpdate(**data)

        # Initialize the MemberService
        service = MemberService(db)
        # Call the service to update the member's details
        updated_member = service.update_member_details(member_id, update_dto)

        # Return the updated member data with HTTP 200 OK status
        return jsonify(MemberResponse.model_validate(updated_member).model_dump()), HTTPStatus.OK
    except Exception as e:
        # Handle errors and return Bad Request status
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


# =========================================================================
# CHECK-IN
# =========================================================================

@member_bp.route('/<int:member_id>/checkin', methods=['POST'])
def check_in(member_id):
    """Perform member check-in"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Initialize the MemberService
        service = MemberService(db)
        # Process the check-in logic (validates subscription, medical status, etc.)
        result = service.process_check_in(member_id)

        # Check the result status determined by the business logic
        if result['status'] == "APPROVED":
            # If approved, return the success result with HTTP 200 OK
            return jsonify(result), HTTPStatus.OK
        else:
            # If rejected (e.g., expired subscription), return HTTP 403 Forbidden
            return jsonify(result), HTTPStatus.FORBIDDEN
    finally:
        # Close the database session
        db.close()


# =========================================================================
# WORKOUT PLANS
# =========================================================================

@member_bp.route('/<int:member_id>/workout-plans', methods=['POST'])
def create_workout_plan(member_id):
    """Create a workout plan for a member"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Retrieve the JSON payload
        data = request.get_json()

        # --- Fix to prevent "Multiple Values" error ---
        # If 'member_id' was included in the JSON body, remove it
        if 'member_id' in data:
            del data['member_id']

        # Inject the correct 'member_id' from the URL into the data dictionary
        data['member_id'] = member_id

        # Validate the data using the WorkoutPlanCreate schema
        plan_dto = WorkoutPlanCreate(**data)

        # Initialize the WorkoutPlanService
        service = WorkoutPlanService(db)
        # Call the service to create the workout plan in the database
        new_plan = service.create_workout_plan(plan_dto)

        # Return the created plan as JSON with HTTP 201 Created status
        return jsonify(WorkoutPlanResponse.model_validate(new_plan).model_dump()), HTTPStatus.CREATED
    except Exception as e:
        # Handle errors and return Bad Request status
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


@member_bp.route('/<int:member_id>/workout-plans/active', methods=['GET'])
def get_active_workout_plan(member_id):
    """
    Get the currently active workout plan for a member.
    """
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Initialize the WorkoutPlanService
        service = WorkoutPlanService(db)

        # Call the service to fetch the single active plan for this member
        active_plan = service.get_member_active_plan(member_id)

        # Return the active plan as JSON with HTTP 200 OK
        return jsonify(WorkoutPlanResponse.model_validate(active_plan).model_dump()), HTTPStatus.OK

    except ResourceNotFoundException as e:
        # If no active plan exists, return HTTP 404 Not Found with the error message
        return jsonify({"message": str(e)}), HTTPStatus.NOT_FOUND

    except Exception as e:
        # Handle other errors (e.g., database issues) with HTTP 400 Bad Request
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


# =========================================================================
# SUBSCRIPTIONS
# =========================================================================

@member_bp.route('/<int:member_id>/subscriptions', methods=['POST'])
def create_member_subscription(member_id):
    """Assign a subscription to a member"""
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Retrieve the JSON payload
        data = request.get_json()
        # Inject the 'member_id' from the URL into the data to ensure correct association
        data['member_id'] = member_id

        # Validate the data using the SubscriptionCreate schema
        subscription_dto = SubscriptionCreate(**data)
        # Initialize the SubscriptionService
        service = SubscriptionService(db)

        # Call the service to create the new subscription record
        new_subscription = service.create_subscription(subscription_dto)

        # Return the created subscription as JSON with HTTP 201 Created status
        return jsonify(SubscriptionResponse.model_validate(new_subscription).model_dump()), HTTPStatus.CREATED
    except Exception as e:
        # Handle errors and return Bad Request status
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()


@member_bp.route('/<int:member_id>/subscription-status', methods=['GET'])
def get_subscription_status(member_id):
    """
    Get member subscription status.
    """
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Initialize the SubscriptionService
        service = SubscriptionService(db)
        # Call the service to calculate and retrieve the current subscription status
        status_result = service.get_member_subscription_status(member_id)
        # Return the status result object as JSON with HTTP 200 OK
        return jsonify(status_result), HTTPStatus.OK
    except Exception as e:
        # Handle errors and return Bad Request status
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        # Close the database session
        db.close()