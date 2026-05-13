from flask import Blueprint, request, jsonify # Import Flask utilities
from http import HTTPStatus # Import standard HTTP status codes
from pydantic import ValidationError # Import Pydantic for validation error handling

from app.database import SessionLocal # Correct path to database session
from app.services.workout_item_service import WorkoutItemService # Import the specialized workout service
from app.schemas.workout_plan_schema import WorkoutPlanCreate, WorkoutPlanResponse # Import Pydantic schemas
from app.schemas.workout_item_schema import WorkoutItemUpdate # Import item update schema

# Define the blueprint with the name 'workout_bp' to match main.py registration
workout_bp = Blueprint('workout_bp', __name__)

# =========================================================================
# CREATE WORKOUT PLAN (Trainer for Member)
# Route: POST /api/members/<member_id>/workout-plans
# =========================================================================
@workout_bp.route('/members/<int:member_id>/workout-plans', methods=['POST'])
def create_workout_plan(member_id):
    """
    Allows a trainer to create a structured workout plan for a specific member.
    """
    db = SessionLocal() # Open database session
    try:
        data = request.get_json() # Get JSON data from request

        # Validate input using Pydantic
        plan_dto = WorkoutPlanCreate(**data)
        plan_dto.member_id = member_id  # Ensure the URL ID overrides body ID

        # Extract trainer_id from data (usually would come from Auth Token)
        trainer_id = data.get('trainer_id')
        if not trainer_id:
            return jsonify({"error": "trainer_id is required"}), HTTPStatus.BAD_REQUEST

        service = WorkoutItemService(db) # Initialize service
        new_plan = service.create_workout_plan(trainer_id, plan_dto) # Execute business logic

        # Return the created plan using WorkoutPlanResponse schema
        return jsonify(WorkoutPlanResponse.model_validate(new_plan).model_dump()), HTTPStatus.CREATED

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        db.close() # Close session

# =========================================================================
# GET ACTIVE PLAN (Member view)
# Route: GET /api/members/<member_id>/workout-plans/active
# =========================================================================
@workout_bp.route('/members/<int:member_id>/workout-plans/active', methods=['GET'])
def get_active_plan(member_id):
    """
    Retrieves the current active workout plan including all exercises (items).
    """
    db = SessionLocal() # Open database session
    try:
        service = WorkoutItemService(db) # Initialize service
        plan = service.get_my_active_plan(member_id) # Fetch plan from service

        # Validate and return plan data
        return jsonify(WorkoutPlanResponse.model_validate(plan).model_dump()), HTTPStatus.OK
    except Exception as e:
        # Returns 404 if no active plan is found
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    finally:
        db.close() # Close session

# =========================================================================
# UPDATE PERFORMANCE (Member recording progress)
# Route: PUT /api/workout-items/<item_id>
# =========================================================================
@workout_bp.route('/workout-items/<int:item_id>', methods=['PUT'])
def update_performance(item_id):
    """
    Allows a member to update actual weight/reps performed for a specific exercise item.
    """
    db = SessionLocal() # Open database session
    try:
        data = request.get_json() # Get update data
        performance_dto = WorkoutItemUpdate(**data) # Validate with update schema

        # Verification of member ownership
        member_id = data.get('member_id')
        if not member_id:
            return jsonify({"error": "member_id verification required"}), HTTPStatus.BAD_REQUEST

        service = WorkoutItemService(db) # Initialize service
        updated_item = service.update_performance(member_id, item_id, performance_dto)

        # Return only the updated item data
        return jsonify(updated_item.model_dump()), HTTPStatus.OK
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        db.close() # Close session