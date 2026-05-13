import enum  # Import the standard enum module for defining enumerations
# Import necessary SQLAlchemy components for column definitions and relationships
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum, String
from sqlalchemy.sql import func  # Import SQL functions (like now())
from sqlalchemy.orm import relationship  # Import relationship for ORM navigation
from app.database.db import Base  # Import the declarative base for the models
from datetime import datetime  # Import datetime to handle timestamps


class EnrollmentStatus(enum.Enum):
    # Define an enumeration for the possible statuses of an enrollment
    CONFIRMED = "CONFIRMED"  # The member is successfully registered for the class
    WAITLIST = "WAITLIST"  # The class is full, and the member is waiting for a spot
    CANCELLED = "CANCELLED"  # The enrollment was cancelled


class CancellationSource(enum.Enum):
    # Define an enumeration to track who initiated a cancellation
    MEMBER = "MEMBER"  # The member cancelled it themselves
    ADMIN = "ADMIN"  # An administrator cancelled it
    SYSTEM = "SYSTEM"  # Automated system cancellation (e.g., payment failure)
    TRAINER = "TRAINER"  # The trainer cancelled the class/enrollment


class Enrollment(Base):
    # Define the Enrollment model, representing the link between a Member and a ClassSession
    __tablename__ = "enrollments"  # The name of the table in the database

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each enrollment record

    # --- Foreign Keys ---
    # Link to the Member who is enrolling
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    # Link to the specific Class Session being booked
    class_session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)

    # --- Status & Meta Data ---
    # Current status of the enrollment (e.g., 'ENROLLED', 'WAITLIST').
    # Defaults to 'ENROLLED' when created.
    status = Column(String, default="ENROLLED")

    # Timestamp of when the enrollment record was created (defaults to current UTC time)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Relationships ---
    # ORM relationship to access the Member object directly (enrollment.member)
    member = relationship("Member", back_populates="enrollments")
    # ORM relationship to access the ClassSession object directly (enrollment.class_session)
    class_session = relationship("ClassSession", back_populates="enrollments")