from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

# Repositories
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.plan_repository import PlanRepository

# Schemas
from app.schemas.subscription_schema import SubscriptionCreate,SubscriptionResponse

# Exceptions
from app.exceptions.exceptions import (
    SubscriptionAlreadyExistException,
    SubscriptionNotExistException,
    MemberNotFoundException,
    ResourceNotFoundException,  # For Plan not found
    DatabaseErrorException
)


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.sub_repo = SubscriptionRepository(db)
        self.member_repo = MemberRepository(db)
        self.plan_repo = PlanRepository(db)

    # =========================================================================
    # Logic 1: Create / Purchase Subscription
    # =========================================================================
    def create_subscription(self, subscription_data: SubscriptionCreate) -> SubscriptionResponse:
        """
        Create a new subscription.
        Validates member, plan, and checks for existing active subscriptions.
        """
        # 1. Validate Member existence
        if not self.member_repo.get_by_id(subscription_data.member_id):
            raise MemberNotFoundException(f"Member ID {subscription_data.member_id} not found.")

        # 2. Validate Plan existence
        if not self.plan_repo.get_by_id(subscription_data.plan_id):
            raise ResourceNotFoundException(f"Plan ID {subscription_data.plan_id} not found.")

        # 3. Check for existing active subscription (Business Rule)
        active_sub = self.sub_repo.get_active_subscription(subscription_data.member_id)
        if active_sub:
            raise SubscriptionAlreadyExistException("This member already has an active subscription.")

        # 4. Create via Repository
        try:
            return self.sub_repo.create(subscription_data)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error creating subscription: {str(e)}")

    # =========================================================================
    # Logic 2: Check Status
    # =========================================================================
    def get_member_subscription_status(self, member_id: int):
        """
        Analyzes the member's subscription status.
        Returns: Active, Frozen, Expired, or No Subscription.
        """
        # We fetch all subscriptions to find the latest one
        # Assuming get_all_by_member sorts by date desc (newest first)
        all_subs = self.sub_repo.get_all_by_member(member_id)

        if not all_subs:
            return {"status": "No Subscription", "message": "Member has no subscription history"}

        # Get the most recent subscription
        subscription = all_subs[0]
        today = date.today()

        # 1. Check if Frozen
        if subscription.status == "FROZEN":
            return {
                "status": "Frozen",
                "end_date": str(subscription.end_date),
                "message": "Subscription is currently frozen"
            }

        # 2. Check if Expired
        if subscription.end_date < today or subscription.status == "EXPIRED":
            return {
                "status": "Expired",
                "end_date": str(subscription.end_date),
                "message": "Subscription has expired"
            }

        # 3. Active
        days_remaining = (subscription.end_date - today).days
        return {
            "status": "Active",
            "plan_id": subscription.plan_id,
            "start_date": str(subscription.start_date),
            "end_date": str(subscription.end_date),
            "days_remaining": days_remaining
        }

    # =========================================================================
    # Logic 3: Freeze / Unfreeze
    # =========================================================================
    def freeze_subscription(self, subscription_id: int):
        """
        Updates subscription status to 'FROZEN'.
        """
        sub = self.sub_repo.get_by_id(subscription_id)
        if not sub:
            raise SubscriptionNotExistException("Subscription not found.")

        try:
            # Use Repository update method (cleaner than manual commit)
            # We assume UpdateSchema allows 'status' field or we pass dict
            return self.sub_repo.update(sub, {"status": "FROZEN"})
        except Exception as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Failed to freeze subscription: {str(e)}")

    def unfreeze_subscription(self, subscription_id: int):
        """
        Updates subscription status back to 'ACTIVE'.
        """
        sub = self.sub_repo.get_by_id(subscription_id)
        if not sub:
            raise SubscriptionNotExistException("Subscription not found.")

        try:
            return self.sub_repo.update(sub, {"status": "ACTIVE"})
        except Exception as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Failed to unfreeze subscription: {str(e)}")