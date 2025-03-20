from sqlalchemy.orm import Session
from app.database import SessionLocal

# Dependency function for database sessions
def get_db():
    db: Session = SessionLocal()  # Create a new session
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close()  # Ensure session is closed after request
