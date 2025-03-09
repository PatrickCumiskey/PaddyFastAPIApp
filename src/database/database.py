from sqlalchemy import create_engine
# Updated import for declarative_base in SQLAlchemy 2.0
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database for simplicity
# For production, use PostgreSQL, MySQL, etc.
SQLALCHEMY_DATABASE_URL = "sqlite:///./weather_data.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use declarative_base from sqlalchemy.orm package
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()