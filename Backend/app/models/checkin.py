import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.db import Base

# Defines exactly HOW the member entered the facility.
# Useful for security auditing and usage analytics.
class CheckInMethod(enum.Enum):
    QR_SCAN = "QR_SCAN"      # Standard app scan
    MANUAL = "MANUAL"        # Receptionist bypassed the gate
    NFC = "NFC"              # Wristband / Chip
    LOCATION = "LOCATION"    # GPS based (Geofencing)
    FACE_ID = "FACE_ID"      # Biometric entry

class CheckIn(Base):
    """
    Represents the physical event of a member attending a class.
    Acts as the 'validation' of an Enrollment.
    """
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)

    # --- The Ticket ---
    # Links the check-in to a specific class booking (Enrollment).
    # unique=True is CRITICAL: It prevents checking in twice on the same ticket.
    # nullable=False: You cannot check in without a valid booking.
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), unique=True, nullable=False)

    # --- Timing ---
    # Records the exact server time of entry.
    checked_in_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Metadata ---
    # How did they get in? Default is QR Scan.
    method = Column(SQLAlchemyEnum(CheckInMethod), default=CheckInMethod.QR_SCAN)

    # Optional notes (e.g., "Member forgot towel", "Late arrival approved")
    notes = Column(String, nullable=True)

    # --- Relationships ---

    # to the Enrollment model, allowing us to access check-in details from the enrollment object.
    enrollment = relationship("Enrollment", backref="checkin")

    def __repr__(self):
        return f"<CheckIn(enrollment={self.enrollment_id}, time={self.checked_in_at})>"