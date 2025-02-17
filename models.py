# models.py
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Car(Base):
    __tablename__ = 'cars'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(String)
    location = Column(String)
    mileage = Column(String)
    description = Column(Text)
    url = Column(String, unique=True)
    status = Column(String, default='Interested')  # Interested, Contacted, Viewed, Rejected, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)