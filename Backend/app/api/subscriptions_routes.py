from flask import Blueprint, request, jsonify  # Import Flask utilities
from http import HTTPStatus  # Import standard HTTP status codes

from app.database.db import SessionLocal  # Correct path to your database session factory
from app.services.subscription_service import SubscriptionService  # Import the business logic service
from app.schemas.subscription_schema import SubscriptionResponse  # Import the response schema

# Define the blueprint with the correct name used in main.py
subscription_bp = Blueprint('subscription_bp', __name__)


# =========================================================================
# FREEZE SUBSCRIPTION
# =========================================================================

# Route: PUT /api/subscriptions/<subscription_id>/freeze
@subscription_bp.route('/<int:subscription_id>/freeze', methods=['PUT'])
def freeze_subscription(subscription_id):
    """
    Suspends a subscription by changing its status to 'FROZEN'.
    """
    db = SessionLocal()  # Open a database connection
    try:
        service = SubscriptionService(db)  # Initialize the service

        # Execute the freeze logic in the service
        updated_sub = service.freeze_subscription(subscription_id)

        # Convert ORM object to Pydantic schema for validation
        response = SubscriptionResponse.model_validate(updated_sub)

        # Return serialized JSON with 200 OK status
        return jsonify(response.model_dump()), HTTPStatus.OK

    except Exception as e:
        # Return error message if subscription not found or DB fails
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        db.close()  # Always close the session


# =========================================================================
# UNFREEZE SUBSCRIPTION
# =========================================================================

# Route: PUT /api/subscriptions/<subscription_id>/unfreeze
@subscription_bp.route('/<int:subscription_id>/unfreeze', methods=['PUT'])
def unfreeze_subscription(subscription_id):
    """
    Reactivates a frozen subscription by changing its status back to 'ACTIVE'.
    """
    db = SessionLocal()  # Open a database connection
    try:
        service = SubscriptionService(db)  # Initialize the service

        # Execute the unfreeze logic in the service
        updated_sub = service.unfreeze_subscription(subscription_id)

        # Convert ORM object to Pydantic schema
        response = SubscriptionResponse.model_validate(updated_sub)

        # Return serialized JSON with 200 OK status
        return jsonify(response.model_dump()), HTTPStatus.OK

    except Exception as e:
        # Return error message with 400 Bad Request
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    finally:
        db.close()  # Always close the session