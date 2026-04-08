import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Database URL support both Postgres and SQLite for testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./documind.db")

# Render uses 'postgres://', but SQLAlchemy 1.4+ requires 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Error creating engine: {e}")
    # Fallback to sqlite if engine creation fails (optional, but safer to let it fail or handle in main)
    engine = None
    SessionLocal = None

Base = declarative_base()

def get_db():
    if SessionLocal is None:
        raise Exception("Database session local is not initialized.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
