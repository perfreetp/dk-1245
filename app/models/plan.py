from sqlalchemy import Column, String, Date, DateTime, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    race_type = Column(String, nullable=False)
    race_date = Column(Date, nullable=False)
    target_time = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    status = Column(String, default="active")
    current_phase = Column(String, default="base")
    total_weeks = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    workouts = relationship("Workout", back_populates="plan", cascade="all, delete-orphan")
    coach_comments = relationship("CoachComment", back_populates="plan", cascade="all, delete-orphan")
    phase_reports = relationship("PhaseReport", back_populates="plan", cascade="all, delete-orphan")
