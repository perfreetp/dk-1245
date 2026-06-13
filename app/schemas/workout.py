from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class WorkoutBase(BaseModel):
    week_number: int
    day_number: int
    workout_type: str
    distance: float = 0.0
    duration: int = 0
    target_pace: Optional[str] = None
    pace_zones: List[dict] = Field(default_factory=list)
    description: Optional[str] = None
    notes: Optional[str] = None
    gear_reminder: Optional[str] = None
    nutrition_tip: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    plan_id: str
    date: date


class WorkoutUpdate(BaseModel):
    distance: Optional[float] = None
    duration: Optional[int] = None
    target_pace: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    gear_reminder: Optional[str] = None
    nutrition_tip: Optional[str] = None
    status: Optional[str] = None


class WorkoutComplete(BaseModel):
    actual_distance: float
    actual_duration: int
    fatigue_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class WorkoutResponse(WorkoutBase):
    id: str
    plan_id: str
    date: date
    status: str
    actual_distance: Optional[float] = None
    actual_duration: Optional[int] = None
    actual_pace: Optional[float] = None
    fatigue_level: Optional[int] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CheckInCreate(BaseModel):
    workout_id: str
    user_id: str
    distance: float
    duration: int
    pace: float
    heart_rate: Optional[int] = None
    calories: Optional[int] = None
    feeling: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    photo_url: Optional[str] = None


class CheckInUpdate(BaseModel):
    distance: Optional[float] = None
    duration: Optional[int] = None
    pace: Optional[float] = None
    heart_rate: Optional[int] = None
    calories: Optional[int] = None
    feeling: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    photo_url: Optional[str] = None


class CheckInResponse(BaseModel):
    id: str
    workout_id: str
    user_id: str
    distance: float
    duration: int
    pace: float
    heart_rate: Optional[int] = None
    calories: Optional[int] = None
    feeling: Optional[int] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NextWeekFocus(BaseModel):
    week_number: int
    focus: str
    total_distance: float
    workouts: List[WorkoutResponse]
    gear_reminder: Optional[str] = None
    nutrition_tip: Optional[str] = None
