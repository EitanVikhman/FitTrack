from sqlalchemy import Column, Integer, String
from app.database.db import Base


class User(Base):
    """
    Abstract Base Class for all users in the system (Members, Trainers, Admins).

    This model will NOT create a 'users' table in the database because of
    the '__abstract__ = True' flag. instead, other models will inherit from it.
    """
    __abstract__ = True  # Tells SQLAlchemy not to create a specific table for this class

    # --- Common Fields for all users ---

    # Unique identifier for the user (Primary Key)
    # index=True makes lookups by ID very fast.
    id = Column(Integer, primary_key=True, index=True)

    # User's email address. Used for login/authentication.
    # unique=True prevents two users from having the same email.
    # nullable=False means this field is mandatory.
    email = Column(String, unique=True, index=True, nullable=False)

    # We store the HASH of the password, never the plain text (Security best practice).
    hashed_password = Column(String, nullable=False)

    # The full name of the user (e.g., "John Doe")
    full_name = Column(String, nullable=False)

    def __repr__(self):
        """
        String representation of the object.
        Helps with debugging by printing a readable format like: <User(id=1, email=user@example.com)>
        """
        return f"<{self.__class__.__name__}(id={self.id}, email={self.email})>"