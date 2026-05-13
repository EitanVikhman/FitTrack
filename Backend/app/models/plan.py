from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


class Plan(Base):
    """
    Represents a subscription plan or product in the gym's catalog.
    Examples: "Monthly Membership", "10-Entry Punch Card", "Annual VIP".
    """
    __tablename__ = "plans"

    # --- Identity ---
    id = Column(Integer, primary_key=True, index=True)

    # The marketing name of the plan.
    # unique=True ensures we don't accidentally create two "Gold" plans.
    name = Column(String, unique=True, nullable=False)

    # Detailed explanation of what the plan includes.
    # We use 'Text' instead of 'String' to allow for longer content (unlimited length).
    description = Column(Text, nullable=True)

    # --- Pricing & Terms ---
    price = Column(Float, nullable=False)  # The cost in local currency

    # How long the subscription is valid (in days).
    # e.g., 30 for monthly, 365 for yearly.
    duration_days = Column(Integer, nullable=False)

    # Limits the number of gym visits.
    # If NULL -> Unlimited entries (Time-based subscription).
    # If INT (e.g., 10) -> Punch card style (limited entries).
    max_entries = Column(Integer, nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<Plan(name={self.name}, price={self.price})>"