from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from app.models.payment import Payment
from .base_repository import BaseRepository


class PaymentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Payment)

    def get_by_member(self, member_id: int) -> List[Payment]:
        """
        Get payment history for a specific member.
        Sorted by payment date (newest first).
        """
        return self.db.query(Payment).filter(
            Payment.member_id == member_id
        ).order_by(Payment.payment_date.desc()).all()

    def get_total_revenue(self, start_date: date, end_date: date) -> float:
        """
        Calculate total revenue between two dates.
        CRITICAL for the Admin Dashboard and monthly reports.
        Uses SQL SUM() for efficiency.
        """
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).scalar()

        # If no payments found, return 0.0 instead of None
        return result if result \
            else 0.0