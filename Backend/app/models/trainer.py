from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.user import User  # Inheriting from the base User model


class Trainer(User):
    """
    Represents a gym trainer/coach.
    Inherits identity fields (ID, Email, Password, Full Name) from 'User'.
    """
    __tablename__ = "trainers"

    # --- Specific Trainer Fields ---

    # We keep first/last name for display purposes (e.g. on the schedule)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # Phone number for contact
    phone_number = Column(String, nullable=True)

    # Professional expertise (e.g., "Yoga Instructor", "Weightlifting Coach")
    specialization = Column(String, nullable=True)

    # --- Relationships ---

    # A trainer can teach many class sessions.
    # On the 'ClassSession' model, there must be a 'trainer' field.
    class_sessions = relationship("ClassSession", back_populates="trainer")

    # A trainer can design many workout plans for members.
    # On the 'WorkoutPlan' model, there must be a 'trainer' field.
    created_plans = relationship("WorkoutPlan", back_populates="trainer")