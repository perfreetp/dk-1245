from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class CoachComment(Base):
    __tablename__ = "coach_comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("training_plans.id"), nullable=False)
    workout_id = Column(String, ForeignKey("workouts.id"), nullable=True)
    coach_id = Column(String, nullable=False)
    content = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("TrainingPlan", back_populates="coach_comments")
    workout = relationship("Workout", back_populates="coach_comments")


class PhaseReport(Base):
    __tablename__ = "phase_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("training_plans.id"), nullable=False)
    phase = Column(String, nullable=False)
    week_number = Column(Integer, nullable=False)
    total_distance = Column(Float, default=0.0)
    completed_distance = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    average_pace = Column(Float, nullable=True)
    fatigue_trend = Column(String, nullable=True)
    improvement_notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("TrainingPlan", back_populates="phase_reports")
