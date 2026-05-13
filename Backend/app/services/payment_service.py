from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import date

# Repositories
from app.repositories.payment_repository import PaymentRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.subscription_repository import SubscriptionRepository

# Schemas
from app.schemas.payment_schema import PaymentCreate,  PaymentResponse

# Exceptions
from app.exceptions.exceptions import (
    ResourceNotFoundException,  # For payment/subscription not found
    MemberNotFoundException,  # For member not found
    BusinessRuleException,  # For logical payment errors (e.g. invalid amount)
    DatabaseErrorException
)


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.member_repo = MemberRepository(db)
        self.sub_repo = SubscriptionRepository(db)

    # =========================================================================
    # Logic 1: Process New Payment
    # =========================================================================
    def process_payment(self, payment_data: PaymentCreate) -> PaymentResponse:
        """
        Records a new payment transaction.
        In a real system, this would interact with Stripe/PayPal API.
        Here, we simulate the process and save the record.
        """
        # 1. Validate Member
        if not self.member_repo.get_by_id(payment_data.member_id):
            raise MemberNotFoundException(f"Member ID {payment_data.member_id} not found.")

        # 2. Validate Subscription (Optional - payment might be for a product)
        if payment_data.subscription_id:
            sub = self.sub_repo.get_by_id(payment_data.subscription_id)
            if not sub:
                raise ResourceNotFoundException(f"Subscription ID {payment_data.subscription_id} not found.")

        # 3. Business Logic: Amount Validation
        if payment_data.amount <= 0:
            raise BusinessRuleException("Payment amount must be greater than zero.")

        # 4. Save Payment Record
        try:
            # We assume the schema has fields: member_id, amount, payment_method, etc.
            # The Repository handles the DB insertion.
            new_payment = self.payment_repo.create(payment_data)
            return new_payment

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error processing payment: {str(e)}")

    # =========================================================================
    # Logic 2: Payment History & Details
    # =========================================================================
    def get_payment_details(self, payment_id: int) -> PaymentResponse:
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise ResourceNotFoundException(f"Payment transaction {payment_id} not found.")
        return payment

    def get_member_payment_history(self, member_id: int) -> List[PaymentResponse]:
        """
        Returns all payments made by a specific member.
        """
        # Validate member existence first
        if not self.member_repo.get_by_id(member_id):
            raise MemberNotFoundException("Member not found.")

        return self.payment_repo.get_by_member(member_id)

    # =========================================================================
    # Logic 3: Refunds & Cancellations
    # =========================================================================
    def refund_payment(self, payment_id: int) -> PaymentResponse:
        """
        Marks a payment as REFUNDED and automatically freezes the subscription.
        """
        # 1. שליפת התשלום
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise ResourceNotFoundException(f"Payment {payment_id} not found.")

        # 2. שינוי סטטוס התשלום (לוגיקה פיננסית)
        payment.status = "REFUNDED"
        payment.refund_date = date.today()

        # 3. *** ההשפעה על הזכויות (Business Logic Trigger) ***
        # זה החלק שהבוחן מחפש: אם הוחזר הכסף, המנוי חייב להיעצר.
        if payment.subscription_id:
            subscription = self.sub_repo.get_by_id(payment.subscription_id)
            if subscription:
                # הקפאת המנוי באופן מיידי
                subscription.status = "FROZEN"
                # אופציונלי: תיעוד הסיבה בתוך המנוי או בלוג
                # subscription.notes = f"Frozen due to refund of payment {payment_id}"

        # 4. שמירת השינויים (Commit)
        try:
            self.db.add(payment)
            if payment.subscription_id and subscription:
                self.db.add(subscription)  # שמירת השינוי גם במנוי
            self.db.commit()
            self.db.refresh(payment)
            return payment

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Failed to process refund: {str(e)}")