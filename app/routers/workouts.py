from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models import Workout, TrainingPlan, User, CheckIn
from app.schemas import WorkoutUpdate, WorkoutComplete, WorkoutResponse, NextWeekFocus
from app.services import PaceCalculator

router = APIRouter(prefix="/workouts", tags=["训练记录"])


@router.get("/plan/{plan_id}", response_model=List[WorkoutResponse])
def get_plan_workouts(plan_id: str, db: Session = Depends(get_db)):
    """获取计划所有训练课次"""
    workouts = db.query(Workout).filter(Workout.plan_id == plan_id).order_by(Workout.date).all()
    return workouts


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(workout_id: str, db: Session = Depends(get_db)):
    """获取训练课次详情"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="训练课次不存在")
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout(workout_id: str, workout_update: WorkoutUpdate, db: Session = Depends(get_db)):
    """更新训练课次"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="训练课次不存在")

    update_data = workout_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workout, key, value)

    db.commit()
    db.refresh(workout)
    return workout


@router.post("/{workout_id}/complete", response_model=WorkoutResponse)
def complete_workout(workout_id: str, completion_data: WorkoutComplete, db: Session = Depends(get_db)):
    """完成训练"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="训练课次不存在")

    if completion_data.actual_distance <= 0 or completion_data.actual_duration <= 0:
        raise HTTPException(status_code=400, detail="距离和时长必须大于0")

    actual_pace = (completion_data.actual_duration * 60) / completion_data.actual_distance

    workout.actual_distance = completion_data.actual_distance
    workout.actual_duration = completion_data.actual_duration
    workout.actual_pace = actual_pace
    workout.fatigue_level = completion_data.fatigue_level
    workout.notes = completion_data.notes
    workout.status = "completed"
    workout.completed_at = datetime.utcnow()

    checkin = CheckIn(
        workout_id=workout_id,
        user_id=workout.plan.user_id,
        distance=completion_data.actual_distance,
        duration=completion_data.actual_duration,
        pace=actual_pace,
        notes=completion_data.notes
    )
    db.add(checkin)
    db.commit()
    db.refresh(workout)

    return workout


@router.get("/next-week", response_model=NextWeekFocus)
def get_next_week_focus(
    user_id: str = Query(...),
    plan_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取下周训练重点"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.id == plan_id,
        TrainingPlan.user_id == user_id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    today = date.today()
    days_until_sunday = (6 - today.weekday()) % 7
    next_sunday = today + timedelta(days=days_until_sunday)
    next_monday = next_sunday + timedelta(days=1)

    next_week_workouts = db.query(Workout).filter(
        Workout.plan_id == plan_id,
        Workout.date >= next_monday,
        Workout.date < next_monday + timedelta(days=7)
    ).order_by(Workout.date).all()

    if not next_week_workouts:
        current_week = today.isocalendar()[1]
        next_week_workouts = db.query(Workout).filter(
            Workout.plan_id == plan_id,
            Workout.week_number == current_week + 1
        ).order_by(Workout.date).all()

    total_distance = sum(w.distance for w in next_week_workouts)
    workout_types = [w.workout_type for w in next_week_workouts]

    focus = "提升跑步能力"
    if "INTERVAL" in workout_types:
        focus = "本周重点：间歇训练，提升速度"
    elif "LONG_RUN" in workout_types:
        focus = "本周重点：长距离跑，提升耐力"
    elif "TEMPO_RUN" in workout_types:
        focus = "本周重点：节奏跑，提升乳酸阈值"
    else:
        focus = "本周重点：有氧基础训练，保持稳定"

    gear_reminders = list(set([w.gear_reminder for w in next_week_workouts if w.gear_reminder]))
    nutrition_tips = list(set([w.nutrition_tip for w in next_week_workouts if w.nutrition_tip]))

    week_number = next_week_workouts[0].week_number if next_week_workouts else 1

    return NextWeekFocus(
        week_number=week_number,
        focus=focus,
        total_distance=round(total_distance, 1),
        workouts=next_week_workouts,
        gear_reminder="; ".join(gear_reminders[:2]) if gear_reminders else None,
        nutrition_tip="; ".join(nutrition_tips[:2]) if nutrition_tips else None
    )


from datetime import timedelta
