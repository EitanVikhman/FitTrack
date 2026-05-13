import sys
import os
from datetime import datetime, timedelta, date

# --- Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'Backend')
sys.path.append(backend_dir)

from app.database.db import SessionLocal, engine, Base
from app.models.member import Member
from app.models.trainer import Trainer
from app.models.plan import Plan
from app.models.exercise import Exercise

db = SessionLocal()

def reset_database():
    print("🗑️  Dropping and creating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset complete.")

def seed_data():
    try:
        print("--- Starting data seeding ---")



        trainer1 = Trainer(
            first_name="Danny",
            last_name="Trainer",
            full_name="Danny Trainer", # שדה חובה ממודל User
            email="dani@gym.com",
            hashed_password="pass", # שדה חובה ממודל User
            phone_number="050-0000000",
            specialization="Strength"
        )
        db.add(trainer1)


        member1 = Member(
            first_name="Avi",
            last_name="Cohen",
            full_name="Avi Cohen", # שדה חובה ממודל User
            email="avi@test.com",
            hashed_password="StrongPassword123!", # שדה חובה ממודל User
            phone="052-1234567", # שם השדה המדויק מהמודל שלך
            membership_type="VIP",
            status="ACTIVE",
            height=180.0,
            weight=80.0,
            join_date=date.today()
        )
        db.add(member1)
        db.commit()

        print("🚀 Seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
    seed_data()