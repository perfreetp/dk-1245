from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CheckIn, Workout

router = APIRouter(prefix="/checkins", tags=["打卡记录"])


@router.post("", status_code=201)
def create_checkin(checkin_data: dict, db: Session = Depends(get_db)):
    """创建打卡记录"""
    workout = db.query(Workout).filter(Workout.id == checkin_data.get("workout_id")).first()
    if not workout:
        raise HTTPException(status_code=404, detail="训练课次不存在")

    checkin = CheckIn(**checkin_data)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    workout.status = "completed"
    workout.actual_distance = checkin_data.get("distance", 0)
    workout.actual_duration = checkin_data.get("duration", 0)
    workout.actual_pace = checkin.pace
    db.commit()

    return checkin


@router.get("/user/{user_id}")
def get_user_checkins(user_id: str, limit: int = Query(50), db: Session = Depends(get_db)):
    """获取用户打卡记录"""
    checkins = db.query(CheckIn).filter(
        CheckIn.user_id == user_id
    ).order_by(CheckIn.created_at.desc()).limit(limit).all()
    return checkins


@router.get("/workout/{workout_id}")
def get_workout_checkin(workout_id: str, db: Session = Depends(get_db)):
    """获取课次打卡记录"""
    checkin = db.query(CheckIn).filter(CheckIn.workout_id == workout_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="打卡记录不存在")
    return checkin


@router.put("/{checkin_id}")
def update_checkin(checkin_id: str, update_data: dict, db: Session = Depends(get_db)):
    """更新打卡记录"""
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="打卡记录不存在")

    for key, value in update_data.items():
        if hasattr(checkin, key):
            setattr(checkin, key, value)

    db.commit()
    db.refresh(checkin)
    return checkin
