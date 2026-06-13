from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class PlanCreate(BaseModel):
    user_id: str
    race_type: str = Field(..., description="赛事类型: 5K, HALF_MARATHON, MARATHON")
    race_date: date
    target_time: Optional[str] = Field(None, description="目标时间(HH:MM:SS)")
    current_pace: float = Field(..., description="当前配速(秒/公里)")
    weekly_mileage: float = Field(..., description="当前周跑量(公里)")
    injury_history: List[str] = Field(default_factory=list)
    available_days: List[int] = Field(default_factory=list, description="可训练日期(0-6)")


class PlanUpdate(BaseModel):
    race_date: Optional[date] = None
    target_time: Optional[str] = None
    status: Optional[str] = None
    current_phase: Optional[str] = None


class PlanResponse(BaseModel):
    id: str
    user_id: str
    race_type: str
    race_date: date
    target_time: Optional[str] = None
    start_date: date
    status: str
    current_phase: str
    total_weeks: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanOverview(BaseModel):
    id: str
    race_type: str
    race_date: date
    target_time: Optional[str] = None
    current_phase: str
    total_weeks: int
    completed_weeks: int
    completion_rate: float
    total_distance: float
    completed_distance: float
    average_pace: Optional[float] = None

    class Config:
        from_attributes = True


class RescheduleRequest(BaseModel):
    missed_workout_id: str
    target_date: date
