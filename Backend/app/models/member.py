from sqlalchemy import Column, String, Date, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import date, datetime
from app.models.user import User  # Importing the parent class


class Member(User):
    """
    Represents a gym member.
    Inherits core identity fields (ID, Email, Password, Full Name) from the 'User' model.
    """
    __tablename__ = "members"

    # --- Specific Member Fields ---
    # Although 'full_name' is inherited from User, we keep specific name fields
    # for better sorting and filtering capabilities.
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # Contact and physical information
    phone = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    height = Column(Float, nullable=True)  # Optional field
    weight = Column(Float, nullable=True)  # Optional field

    # --- Membership Management ---
    # Default join date is set to today
    join_date = Column(Date, default=date.today)
    membership_type = Column(String, nullable=False)  # e.g., "Student", "VIP"
    status = Column(String, default="ACTIVE")  # e.g., "ACTIVE", "FROZEN"

    #
    # Tracks when the record was created and last updated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    # These define the connections to other tables in the database.
    # 'back_populates' ensures that changes on one side are immediately visible on the other.

    subscriptions = relationship("Subscription", back_populates="member")
    enrollments = relationship("Enrollment", back_populates="member")
    workout_plans = relationship("WorkoutPlan", back_populates="member")


class MemberStatus:
    pass