import enum
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.db import Base


# Define the allowed payment methods explicitly.
# This prevents typos like "Creadit Card" or "Cashh".
class PaymentMethod(enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    CASH = "CASH"
    BIT = "BIT"
    BANK_TRANSFER = "BANK_TRANSFER"


class Payment(Base):
    """
    Represents a financial transaction in the system.
    Tracks who paid, how much, when, and for what product.
    """
    __tablename__ = "payments"

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)

    # --- Who paid? ---
    # Must be linked to a member. We can't have anonymous payments.
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    # --- What for? ---
    # Linked to a specific subscription purchase.
    # nullable=True: Why? Maybe the member paid for a bottle of water,
    # a towel rental, or a debt, which isn't directly a "Subscription".
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    # --- Transaction Details ---
    amount = Column(Float, nullable=False)

    # func.now(): Uses the DATABASE server's clock, not the Python server's clock.
    # This is often more accurate for financial records.
    payment_date = Column(DateTime(timezone=True), server_default=func.now())

    # Enforces that the value must be one of the Enum options defined above.
    payment_method = Column(SQLAlchemyEnum(PaymentMethod), nullable=False)

    # Optional external ID (e.g., the confirmation number from Bit or the Credit Card slip ID)
    transaction_id = Column(String, nullable=True)

    # --- Relationships ---
    # backref="payments": This is a shortcut!
    # It automatically adds a "payments" list to the Member model,
    # even though we didn't write it explicitly in the Member file.
    member = relationship("Member", backref="payments")

    def __repr__(self):
        return f"<Payment(amount={self.amount}, member={self.member_id})>"