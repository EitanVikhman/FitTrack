from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any

# Repositories
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.class_session_repository import ClassSessionRepository
from app.repositories.member_repository import MemberRepository

# External Services
from app.services.subscription_service import SubscriptionService

# Exceptions
from app.exceptions.exceptions import (
    UserAlreadyExistsException,  # For double booking
    NotFoundErrorException,  # General not found
    MemberNotFoundException,  # Specific member not found
    BusinessRuleException,  # For subscription issues
    DatabaseErrorException
)


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)
        self.class_repo = ClassSessionRepository(db)
        self.member_repo = MemberRepository(db)
        # We initialize SubscriptionService to check eligibility
        self.sub_service = SubscriptionService(db)

    # =========================================================================
    # Logic 1: Register to Class (With Waitlist Logic)
    # =========================================================================
    def register_to_class(self, member_id: int, class_id: int) -> Dict[str, Any]:
        """
        Registers a member to a class.
        Checks: Subscription status, Duplicates, Capacity.
        Result: Either REGISTERED or WAITLIST.
        """
        # 1. Validation: Existence
        class_session = self.class_repo.get_by_id(class_id)
        if not class_session:
            raise NotFoundErrorException(f"Class session {class_id} not found.")

        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise MemberNotFoundException(f"Member {member_id} not found.")

        # 2. Validation: Subscription Eligibility
        # We expect a dictionary with 'status' from the sub_service
        sub_status = self.sub_service.get_member_subscription_status(member_id)
        if sub_status.get('status') != 'Active':
            raise BusinessRuleException(f"Cannot register: Subscription is {sub_status.get('status')}")

        # 3. Validation: Duplicate Registration
        existing = self.enrollment_repo.get_by_member_and_class(member_id, class_id)
        if existing:
            status_msg = "in waiting list" if existing.status == "WAITLIST" else "already registered"
            raise UserAlreadyExistsException(f"The member is {status_msg} for this class session.")

        # 4. Capacity Check & Status Determination
        current_count = self.enrollment_repo.count_active_enrollments(class_id)

        new_status = "REGISTERED"
        message = "Successfully registered."

        # If full -> Move to Waitlist
        if current_count >= class_session.capacity:
            new_status = "WAITLIST"
            message = "Class is full. You have been added to the waiting list."

        # 5. Create Enrollment via Repository
        try:
            # We create a dictionary for the Repo
            enrollment_data = {
                "member_id": member_id,
                "class_session_id": class_id,
                "status": new_status
            }
            new_enrollment = self.enrollment_repo.create(enrollment_data)

            return {
                "enrollment_id": new_enrollment.id,
                "status": new_status,
                "message": message
            }

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error during registration: {str(e)}")

    # =========================================================================
    # Logic 2: Cancel Registration & Promote Waitlist
    # =========================================================================
    def cancel_registration(self, enrollment_id: int):
        """
        Cancels an enrollment.
        If the cancelled spot was taken (REGISTERED), it promotes the next person
        from the Waitlist automatically.
        """
        # 1. Get the enrollment
        enrollment_to_cancel = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment_to_cancel:
            raise NotFoundErrorException("Enrollment not found")

        if enrollment_to_cancel.status == "CANCELLED":
            raise BusinessRuleException("Enrollment is already cancelled.")

        class_id = enrollment_to_cancel.class_session_id
        was_registered = (enrollment_to_cancel.status == "REGISTERED")

        try:
            # 2. Cancel the current enrollment
            # Using Repo update
            self.enrollment_repo.update(enrollment_to_cancel, {"status": "CANCELLED"})

            # 3. Promote next in line (Fair Queue Management)
            if was_registered:
                self._promote_next_in_line(class_id)

            return {"message": "Enrollment successfully cancelled."}

        except Exception as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Error during cancellation: {str(e)}")

    def _promote_next_in_line(self, class_id: int):
        """
        Internal Helper: Promotes the first person in the waitlist (FIFO).
        """
        # 1. Fetch waitlist sorted by date (Repo logic)
        waitlist = self.enrollment_repo.get_waiting_list(class_id)

        # 2. If there is someone waiting, promote the first one
        if waitlist:
            lucky_member = waitlist[0]  # First come, first served
            self.enrollment_repo.update(lucky_member, {"status": "REGISTERED"})

            # Here you would typically send an Email/SMS notification
            print(f"[NOTIFICATION] Member {lucky_member.member_id} promoted to class {class_id}.")

    # =========================================================================
    # Logic 3: Queries
    # =========================================================================
    def get_class_participants(self, class_id: int):
        """
        Returns active participants and waitlist.
        """
        # We can implement a method in repo to get all by class,
        # or use logic here. Assuming we want waitlist separated:

        # This is a bit manual, but effective if we don't have a specific repo method for both
        waitlist = self.enrollment_repo.get_waiting_list(class_id)

        # You might want to add a method in Repo: get_active_participants(class_id)
        # For now, let's assume get_waiting_list is what we need for the admin view
        return {
            "waitlist_count": len(waitlist),
            "waitlist": waitlist
        }