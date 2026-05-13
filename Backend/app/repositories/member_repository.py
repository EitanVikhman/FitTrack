from sqlalchemy.orm import Session  # Import Session for database transactions
from typing import Optional  # Import Optional for type hinting (e.g., return value can be None)
from app.models.member import Member  # Import the Member model to access the members table
from .base_repository import BaseRepository  # Import the generic base repository


class MemberRepository(BaseRepository):
    def __init__(self, db: Session):
        # Initialize the parent BaseRepository with the current DB session and the Member model class
        super().__init__(db, Member)

    # --- Custom Methods specific to Members ---

    def get_by_email(self, email: str):
        # Query the database to find the first member record that matches the provided email address
        return self.db.query(Member).filter(Member.email == email).first()

    def get_by_phone(self, phone: str) -> Optional[Member]:
        """
        Find a member by phone number.
        Crucial for quick check-ins or lookups at the front desk.
        """
        # Query the database to find the first member record that matches the provided phone number
        return self.db.query(Member).filter(Member.phone == phone).first()

    def create(self, member_data):
        # Convert the Pydantic data object into a standard Python dictionary
        data = member_data.model_dump()

        # Remove the 'password' field before creating the DB record.
        # The Member SQLAlchemy model likely does not have a raw 'password' column
        # (or auth is handled separately), so we remove it to prevent an error.
        if "password" in data:
            del data["password"]

        # Create a new Member instance using the cleaned data dictionary
        new_member = Member(**data)

        # Add the new member to the database session
        self.db.add(new_member)
        # Commit the transaction to save the changes to the database
        self.db.commit()
        # Refresh the instance to get generated fields (like ID) back from the database
        self.db.refresh(new_member)
        # Return the newly created member object
        return new_member