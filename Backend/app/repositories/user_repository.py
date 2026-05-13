from sqlalchemy.orm import Session  # Import Session to handle database transactions
from app.models.user import User  # Import the User model to interact with the users table
from .base_repository import BaseRepository  # Import the generic BaseRepository class

class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        # Initialize the repository with the database session
        # Call the parent constructor, passing the session and the User model to set up the repository
        super().__init__(db, User)

    def get_by_email(self, email: str):
        """
        Custom method to retrieve a user by their email address.
        Crucial for authentication (Login) and checking for duplicate registrations.
        Returns the User object if found, otherwise returns None.
        """
        # Query the database table associated with 'self.model' (User),
        # filter records where the email matches the input, and return the first result.
        return self.db.query(self.model).filter(self.model.email == email).first()