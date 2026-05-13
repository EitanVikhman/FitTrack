from sqlalchemy import Column, Integer, DateTime, ForeignKey, String  # Import SQLAlchemy column types and constraints
from sqlalchemy.orm import relationship  # Import relationship to define links between tables
from app.database.db import Base  # Import the declarative base class for models
from datetime import datetime  # Import datetime to handle timestamps


class EntryLog(Base):
    # Define the EntryLog model, which records every check-in attempt at the gym
    __tablename__ = "entry_logs"  # The name of the table in the database

    # Unique identifier for each log entry
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking to the 'id' column in the 'members' table; cannot be null
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    # Timestamp of when the entry attempt occurred; defaults to the current server time
    entry_time = Column(DateTime, default=datetime.now)

    # The outcome of the entry attempt (e.g., "APPROVED" or "DENIED"); cannot be null
    status = Column(String, nullable=False)

    # Explanation if the entry was denied (e.g., "MEMBER_BANNED" or "SUBSCRIPTION_EXPIRED"); can be null if approved
    rejection_reason = Column(String, nullable=True)

    # ORM relationship to access the associated Member object directly (e.g., log.member)
    # 'backref="entry_logs"' automatically adds a list of entry logs to the Member model
    member = relationship("Member", backref="entry_logs")