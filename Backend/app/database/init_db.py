import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)
from db import engine, Base
from app.models.trainer import Trainer
from app.models.member import Member
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.class_session import ClassSession
from app.models.enrollment import Enrollment
from app.models.checkin import CheckIn
from app.models.exercise import Exercise
from app.models.workout_plan import WorkoutPlan
from app.models.workout_item import WorkoutItem




def init_db():
    print("Creating database tables if they don't exist...")

    # הפקודה הזו היא המקבילה ל- CREATE TABLE IF NOT EXISTS
    # היא עוברת על כל המודלים שיורשים מ-Base
    # ויוצרת טבלאות רק למה שחסר בדאטה-בייס.
    Base.metadata.create_all(bind=engine)

    print("Database initialization completed successfully!")


if __name__ == "__main__":
    init_db()