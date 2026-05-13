from sqlalchemy.orm import Session  # Import Session to handle database transactions


from app.models.enrollment import Enrollment  # Import the Enrollment model to access the enrollments table
from .base_repository import BaseRepository  # Import the base repository class for common CRUD operations


class EnrollmentRepository(BaseRepository):
    def __init__(self, db: Session):
        # Initialize the repository with the database session and the Enrollment model
        super().__init__(db, Enrollment)

    def get_by_member_and_class(self, member_id: int, class_id: int):
        """
        Check if a member is already enrolled (or on the waitlist) for this class.
        Returns a result only if the status is REGISTERED or WAITLIST.
        """
        return self.db.query(Enrollment).filter(
            Enrollment.member_id == member_id,  # Filter by the specific member ID
            Enrollment.class_session_id == class_id,  # Filter by the specific class session ID
            Enrollment.status.in_(["REGISTERED", "WAITLIST"])  # Check if status is either REGISTERED or WAITLIST
        ).first()  # Return the first matching record or None if not found

    def count_active_enrollments(self, class_id: int) -> int:
        """
        Counts how many people are actually registered (occupying capacity).
        Does not include the waitlist.
        """
        return self.db.query(Enrollment).filter(
            Enrollment.class_session_id == class_id,  # Filter by the specific class session ID
            Enrollment.status == "REGISTERED"  # Only count members who are fully registered (ignore waitlist/cancelled)
        ).count()  # Return the count as an integer

    def get_waiting_list(self, class_id: int):
        """
        Retrieve the waitlist ordered by time (First In, First Out).
        This is critical for the 'fair queue management' requirement.
        """
        return self.db.query(Enrollment).filter(
            Enrollment.class_session_id == class_id,  # Filter by the specific class session ID
            Enrollment.status == "WAITLIST"  # Filter only for members currently on the waitlist
        ).order_by(Enrollment.created_at.asc()).all()  # Order results by creation time (ascending) to ensure FIFO