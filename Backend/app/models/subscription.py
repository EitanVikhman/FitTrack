from sqlalchemy import Column, Integer, ForeignKey, Date, String, Float
from sqlalchemy.orm import relationship
from app.database.db import Base


class Subscription(Base):
    """
    Represents the actual purchase/contract between a Member and a Plan.
    It tracks time validity (start/end) and usage limits (entries).
    """
    __tablename__ = "subscriptions"

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys: linking the subscription to a specific member and a specific plan.
    # nullable=False means a subscription MUST belong to someone and be based on a plan.
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)

    # --- Time & Status ---
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)  # The expiration date

    # Status can be: "ACTIVE", "EXPIRED", "CANCELLED", "FROZEN"
    status = Column(String, default="ACTIVE")

    # --- Financial & Logic ---
    # We store the price paid at the moment of purchase.
    # Why? Because the Plan price might change in the future, but historical records shouldn't.
    price_paid = Column(Float, nullable=False)

    # Snapshot of the subscription type (e.g., "Monthly", "PunchCard")
    type = Column(String, nullable=True)

    # For Punch Cards: tracks how many visits are left.
    # If NULL, it implies an unlimited subscription (time-based).
    entries_remaining = Column(Integer, nullable=True)

    # --- Relationships ---
    # Connection to the Member model (bidirectional)
    member = relationship("Member", back_populates="subscriptions")

    # Connection to the Plan model (bidirectional)
    # We added 'back_populates="subscriptions"' to match the change we made in the Plan model.
    plan = relationship("Plan", back_populates="subscriptions")


    @property
    def price(self):
        return self.price_paid