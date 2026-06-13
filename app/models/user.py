from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    current_pace = Column(Float, nullable=False)
    weekly_mileage = Column(Float, nullable=False)
    injury_history = Column(JSON, default=list)
    available_days = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plans = relationship("TrainingPlan", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("CheckIn", back_populates="user", cascade="all, delete-orphan")
