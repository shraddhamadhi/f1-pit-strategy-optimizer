from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from models import Base

# Load environment vars from .env
load_dotenv()

# Creates/returns a SQLAlchemy engine connected to the f1_strategy PostgreSQL database
def get_engine():
    # Build PostgreSQL connection URL using password from .env
    url = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/f1_strategy"
    engine = create_engine(url, echo = False)
    return engine

# Create instance of engine
engine = get_engine()

# Temporarily opens a connection to PostgreSQL
# DELETE LATER
def test_connection():
    with engine.connect() as connection:
        print("Connection successful")

test_connection()

# Creates all tables in PostgreSQL if they don't already exist
Base.metadata.create_all(engine)