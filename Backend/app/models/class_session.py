import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database.db import Base


# Define the lifecycle of a class session
class SessionStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"  # The class is planned and open for booking
    CANCELLED = "CANCELLED"  # The class was removed (members should be notified)
    COMPLETED = "COMPLETED"  # The class happened in the past


class ClassSession(Base):
    """
    Represents a single event in the calendar (e.g., "Yoga on Sunday at 10:00").
    This is the entity that Members enroll in.
    """
    __tablename__ = "class_sessions"

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)

    # --- Content ---
    title = Column(String, nullable=False)  # e.g., "Pilates Reformer"
    description = Column(String, nullable=True)  # e.g., "Bring a towel and water"

    # --- Scheduling ---
    # We use timezone=True to handle daylight saving time changes correctly.
    # index=True on start_time makes filtering "today's classes" very fast.
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # --- Logic Limits ---
    # This number determines when the Waiting List kicks in.
    capacity = Column(Integer, nullable=False)

    # --- Relationships ---

    # 1. Connection to Trainer
    # nullable=True: Allows creating a schedule (e.g., "Spinning 18:00")
    # even if we haven't found a substitute trainer yet.
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)

    # Status defaults to SCHEDULED when created.
    status = Column(SQLAlchemyEnum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False)

    # --- ORM Links ---


    trainer = relationship("Trainer", back_populates="class_sessions")

    # 2. Connection to Enrollments (The people in the class)

    # If we delete this ClassSession from the DB, all associated Enrollments (bookings)
    # will be automatically deleted too. We don't want orphan bookings pointing to nowhere.
    enrollments = relationship("Enrollment", back_populates="class_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClassSession(title={self.title}, start={self.start_time}, status={self.status})>"