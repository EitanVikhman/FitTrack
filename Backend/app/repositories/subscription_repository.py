from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.subscription import Subscription
from .base_repository import BaseRepository

class SubscriptionRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Subscription)

    # Note: We DO NOT override 'create' here.
    # The BaseRepository handles it automatically because our Pydantic Schema
    # (SubscriptionCreate) already uses the correct field name 'price_paid'.
    # This ensures we keep the error handling (try/except) from the Base.

    def get_active_subscription(self, member_id: int) -> Optional[Subscription]:
        """
        Fetch the current active subscription for a member.
        Logic: Status is ACTIVE and End Date is in the future.
        """
        today = date.today()
        return self.db.query(Subscription).filter(
            Subscription.member_id == member_id,
            Subscription.status == "ACTIVE",
            Subscription.end_date >= today
        ).first()

    def get_all_by_member(self, member_id: int) -> List[Subscription]:
        """
        Get full subscription history for a specific member.
        """
        return self.db.query(Subscription).filter(
            Subscription.member_id == member_id
        ).order_by(Subscription.start_date.desc()).all() # Ordered by newest first