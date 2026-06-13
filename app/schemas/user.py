from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    current_pace: float = Field(..., description="当前配速(秒/公里)")
    weekly_mileage: float = Field(..., description="当前周跑量(公里)")
    injury_history: List[str] = Field(default_factory=list)
    available_days: List[int] = Field(default_factory=list, description="可训练日期(0-6)")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    current_pace: Optional[float] = None
    weekly_mileage: Optional[float] = None
    injury_history: Optional[List[str]] = None
    available_days: Optional[List[int]] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    current_pace: float
    weekly_mileage: float
    injury_history: List[str]
    available_days: List[int]
    total_plans: int = 0
    completed_plans: int = 0
    total_workouts: int = 0
    total_distance: float = 0.0

    class Config:
        from_attributes = True
