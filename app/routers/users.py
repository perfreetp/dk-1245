from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, TrainingPlan, Workout
from app.schemas import UserCreate, UserUpdate, UserResponse, UserProfile

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(user)
    db.commit()
    return None


@router.get("/{user_id}/profile", response_model=UserProfile)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """获取用户训练档案"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    plans = db.query(TrainingPlan).filter(TrainingPlan.user_id == user_id).all()
    workouts = db.query(Workout).join(TrainingPlan).filter(TrainingPlan.user_id == user_id).all()

    total_distance = sum(w.actual_distance or w.distance for w in workouts)
    completed_plans = sum(1 for p in plans if p.status == "completed")

    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        height=user.height,
        weight=user.weight,
        age=user.age,
        gender=user.gender,
        current_pace=user.current_pace,
        weekly_mileage=user.weekly_mileage,
        injury_history=user.injury_history or [],
        available_days=user.available_days or [],
        total_plans=len(plans),
        completed_plans=completed_plans,
        total_workouts=len(workouts),
        total_distance=total_distance
    )
