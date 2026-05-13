from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import date


class WorkoutPlan(Base):
    """
    Represents a full training program assigned to a member.
    It acts as a container for specific exercises (WorkoutItems).
    """
    __tablename__ = "workout_plans"

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)

    # --- Ownership ---

    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)


    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)

    # --- Timeline ---
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=False)  # The plan must have a deadline/review date


    goal = Column(String, nullable=False)

    # Detailed instructions or philosophy behind the plan
    notes = Column(Text, nullable=True)

    # Status: ACTIVE (current), COMPLETED (history), ARCHIVED
    status = Column(String, default="ACTIVE")

    # --- Relationships ---

    # Link back to the Member (Consumer)
    member = relationship("Member", back_populates="workout_plans")

    # Link back to the Trainer (Creator)
    # Note: Matches 'created_plans' in the Trainer model
    trainer = relationship("Trainer", back_populates="created_plans")

    # The actual content of the plan (The exercises).
    # cascade="all, delete-orphan": If we delete the Plan, all its exercises are deleted too.
    items = relationship("WorkoutItem", back_populates="plan", cascade="all, delete-orphan")