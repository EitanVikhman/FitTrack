from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 1. Define file location
# Get the absolute path of the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the name of the SQLite database file
DB_NAME = "gym.db"
# Construct the full database URL string required by SQLAlchemy (using SQLite protocol)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"

# 2. Create the Engine (The physical connection)
# The engine is the starting point for any SQLAlchemy application; it acts as a central source of connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # "check_same_thread": False is required for SQLite when using it in a multi-threaded environment like Flask
    connect_args={"check_same_thread": False}
)

# 3. Create a "Factory" for Sessions
# SessionLocal is not an actual session but a class (factory) used to create new database sessions
# autocommit=False: We want to manually commit transactions to ensure data integrity
# autoflush=False: We want to manually flush changes to the database
# bind=engine: Connects this session factory to the engine created above
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base Model
# This function returns a base class that all our database models (tables) will inherit from
Base = declarative_base()