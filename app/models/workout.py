from sqlalchemy import Column, String, Date, DateTime, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("training_plans.id"), nullable=False)
    date = Column(Date, nullable=False)
    week_number = Column(Integer, nullable=False)
    day_number = Column(Integer, nullable=False)
    workout_type = Column(String, nullable=False)
    distance = Column(Float, default=0.0)
    duration = Column(Integer, default=0)
    target_pace = Column(String, nullable=True)
    pace_zones = Column(JSON, default=list)
    description = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    gear_reminder = Column(String, nullable=True)
    nutrition_tip = Column(String, nullable=True)
    status = Column(String, default="scheduled")
    actual_distance = Column(Float, nullable=True)
    actual_duration = Column(Integer, nullable=True)
    actual_pace = Column(Float, nullable=True)
    fatigue_level = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    plan = relationship("TrainingPlan", back_populates="workouts")
    checkin = relationship("CheckIn", back_populates="workout", uselist=False, foreign_keys="CheckIn.workout_id")
    coach_comments = relationship("CoachComment", back_populates="workout")


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String, ForeignKey("workouts.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    distance = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)
    pace = Column(Float, nullable=False)
    heart_rate = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    feeling = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workout = relationship("Workout", back_populates="checkin", uselist=False)
    user = relationship("User", back_populates="checkins")
