from flask import Flask, jsonify  # Import Flask to create the web app and jsonify to format JSON responses
from flask_cors import CORS  # Import CORS to allow cross-origin requests (e.g., from a React frontend)
from http import HTTPStatus  # Import standard HTTP status codes

# Import database connection tools (SessionLocal is needed to execute queries like creating the plan)
from app.database.db import engine, Base, SessionLocal
# Import the Plan model to interact with the 'plans' table
from app.models.plan import Plan

# --- Import Blueprints (Route Modules) ---
from app.api.members_routes import member_bp
from app.api.classes_routes import class_bp
from app.api.subscriptions_routes import subscription_bp

# Initialize the Flask application instance
app = Flask(__name__)
# Enable CORS for the application to allow requests from other domains
CORS(app)


# =========================================================================
# Helper Function: Create Default Plan (Solves the "No Plan" issue!)
# =========================================================================
def seed_default_plan():
    """
    Automatically creates a default subscription plan (ID: 1) if it doesn't exist.
    This prevents errors when trying to create a subscription for a member.
    """
    # Initialize a new database session
    db = SessionLocal()
    try:
        # Check if a plan with ID 1 already exists in the database
        existing_plan = db.query(Plan).filter(Plan.id == 1).first()

        # If it does not exist, create it
        if not existing_plan:
            print("⚙️  Seeding database: Creating default Plan (ID: 1)...")
            # Create a new Plan object with default values
            default_plan = Plan(
                name="Monthly Standard",
                price=250.0,
                duration_days=30,
                description="Auto-generated default plan",
                max_entries=None  # 'None' implies unlimited entries for this plan
            )
            # Add the new plan to the session
            db.add(default_plan)
            # Commit the transaction to save it to the database
            db.commit()
            print("✅ Default Plan created successfully!")
        else:
            # If it already exists, log a message and do nothing
            print("ℹ️  Default Plan (ID: 1) already exists.")

    except Exception as e:
        # Catch and print any errors that occur during the seeding process
        print(f"❌ Error seeding plan: {e}")
    finally:
        # Always close the database session to release the connection
        db.close()


# =========================================================================
# Server and Database Initialization
# =========================================================================
# Use the application context to access configuration and database settings
with app.app_context():
    try:
        # 1. Create Tables
        # This looks at all imported models and creates the tables in the database if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")

        # 2. Run Seed
        # Call the helper function to ensure the default plan exists
        seed_default_plan()

    except Exception as e:
        # Print an error message if initialization fails
        print(f"❌ Error initializing DB: {e}")

# --- Register Blueprints ---
# Register the member routes under the '/members' prefix
app.register_blueprint(member_bp, url_prefix='/members')
# Register the subscription routes under the '/subscriptions' prefix
app.register_blueprint(subscription_bp, url_prefix='/subscriptions')
# Register the class routes under the '/classes' prefix
app.register_blueprint(class_bp, url_prefix='/classes')


# --- Error Handling ---
# Define a custom handler for 404 Not Found errors
@app.errorhandler(404)
def not_found(e):
    # Return a JSON response with the error details
    return jsonify({"error": "Not Found", "message": "The requested URL was not found"}), HTTPStatus.NOT_FOUND


# Define a generic handler for all other exceptions (Internal Server Error)
@app.errorhandler(Exception)
def handle_exception(e):
    # Return a JSON response with the specific error message
    return jsonify({"error": "Internal Server Error", "message": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


# Define the root route (Health Check)
@app.route('/')
def home():
    # Return a simple status message to verify the server is running
    return jsonify({
        "status": "Online",
        "message": "Welcome to FitTrack API",
        "version": "1.0.0"
    }), HTTPStatus.OK


# Main entry point: Run the server if executed directly
if __name__ == "__main__":
    # Start the Flask development server on port 5000 with debug mode enabled
    app.run(debug=True, port=5000)