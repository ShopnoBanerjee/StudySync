from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(Text)
    filename = Column(String)
    