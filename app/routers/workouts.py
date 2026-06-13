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

from pydantic import BaseModel, Field


class WeeklyPlanResponse(BaseModel):
    week_number: int
    start_date: date
    end_date: date
    total_distance: float
    workout_count: int
    completed_count: int
    workouts: dict

    class Config:
        from_attributes = True


class WorkoutCompletionRequest(BaseModel):
    actual_distance: float
    actual_duration: int
    fatigue_level: int = Field(None, ge=1, le=10)
    notes: str = None


class WorkoutUndoRequest(BaseModel):
    reason: str = None


@router.get("/weekly")
def get_weekly_plan(
    plan_id: str = Query(...),
    reference_date: str = Query(..., description="任意一天的日期，格式: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """按周查看计划 - 给定计划和任意一天，返回这一周每天的训练安排"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    ref_date = date.fromisoformat(reference_date)
    start_of_week = ref_date - timedelta(days=ref_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    week_workouts = db.query(Workout).filter(
        Workout.plan_id == plan_id,
        Workout.date >= start_of_week,
        Workout.date <= end_of_week
    ).order_by(Workout.date).all()

    workouts_by_day = {}
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][i]
        workouts_on_day = [w for w in week_workouts if w.date == day_date]

        workouts_by_day[day_name] = []
        for w in workouts_on_day:
            workouts_by_day[day_name].append({
                "id": w.id,
                "workout_type": w.workout_type,
                "distance": w.distance,
                "duration": w.duration,
                "target_pace": w.target_pace,
                "description": w.description,
                "status": w.status,
                "actual_distance": w.actual_distance,
                "actual_duration": w.actual_duration,
                "actual_pace": w.actual_pace,
                "fatigue_level": w.fatigue_level,
                "gear_reminder": w.gear_reminder,
                "nutrition_tip": w.nutrition_tip
            })

    completed_count = sum(1 for w in week_workouts if w.status == "completed")
    total_distance = sum(w.distance for w in week_workouts)

    current_week_number = (ref_date - plan.start_date).days // 7 + 1

    return {
        "plan_id": plan_id,
        "current_week": current_week_number,
        "week_range": f"{start_of_week} 至 {end_of_week}",
        "start_date": str(start_of_week),
        "end_date": str(end_of_week),
        "total_distance": round(total_distance, 1),
        "workout_count": len(week_workouts),
        "completed_count": completed_count,
        "completion_rate": round(completed_count / len(week_workouts) * 100, 1) if week_workouts else 0,
        "workouts_by_day": workouts_by_day
    }


@router.post("/{workout_id}/makeup")
def makeup_workout(workout_id: str, makeup_data: WorkoutCompletionRequest, db: Session = Depends(get_db)):
    """训练补录 - 漏打卡时手动补一条真实完成记录"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="训练课次不存在")

    if workout.status == "completed":
        raise HTTPException(status_code=400, detail="该训练已完成，无需补录")

    if makeup_data.actual_distance <= 0 or makeup_data.actual_duration <= 0:
        raise HTTPException(status_code=400, detail="距离和时长必须大于0")

    actual_pace = (makeup_data.actual_duration * 60) / makeup_data.actual_distance

    workout.actual_distance = makeup_data.actual_distance
    workout.actual_duration = makeup_data.actual_duration
    workout.actual_pace = actual_pace
    workout.fatigue_level = makeup_data.fatigue_level or 5
    workout.notes = makeup_data.notes
    workout.status = "completed"
    workout.completed_at = datetime.utcnow()

    checkin = CheckIn(
        workout_id=workout_id,
        user_id=workout.plan.user_id,
        distance=makeup_data.actual_distance,
        duration=makeup_data.actual_duration,
        pace=actual_pace,
        notes=f"[补录] {makeup_data.notes}" if makeup_data.notes else "[补录]"
    )
    db.add(checkin)
    db.commit()
    db.refresh(workout)

    plan = workout.plan
    all_workouts = db.query(Workout).filter(Workout.plan_id == plan.id).all()
    completed_workouts = [w for w in all_workouts if w.status == "completed"]

    total_distance = sum(w.actual_distance or w.distance for w in all_workouts)
    completed_distance = sum(w.actual_distance or 0 for w in completed_workouts)
    completion_rate = len(completed_workouts) / len(all_workouts) * 100 if all_workouts else 0

    return {
        "message": "训练补录成功",
        "workout_id": workout_id,
        "workout_type": workout.workout_type,
        "actual_distance": workout.actual_distance,
        "actual_duration": workout.actual_duration,
        "actual_pace": round(actual_pace, 1),
        "fatigue_level": workout.fatigue_level,
        "plan_stats": {
            "total_workouts": len(all_workouts),
            "completed_workouts": len(completed_workouts),
            "completion_rate": round(completion_rate, 1),
            "total_distance": round(total_distance, 1),
            "completed_distance": round(completed_distance, 1)
        }
    }


@router.post("/{workout_id}/undo")
def undo_workout(workout_id: str, undo_data: WorkoutUndoRequest, db: Session = Depends(get_db)):
    """撤回训练 - 撤回已完成的打卡记录"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="训练课次不存在")

    if workout.status != "completed":
        raise HTTPException(status_code=400, detail="该训练未完成，无法撤回")

    checkin = db.query(CheckIn).filter(CheckIn.workout_id == workout_id).first()
    if checkin:
        db.delete(checkin)

    workout.actual_distance = None
    workout.actual_duration = None
    workout.actual_pace = None
    workout.fatigue_level = None
    workout.notes = undo_data.reason or "[已撤回]"
    workout.status = "scheduled"
    workout.completed_at = None

    db.commit()
    db.refresh(workout)

    plan = workout.plan
    all_workouts = db.query(Workout).filter(Workout.plan_id == plan.id).all()
    completed_workouts = [w for w in all_workouts if w.status == "completed"]

    total_distance = sum(w.actual_distance or w.distance for w in all_workouts)
    completed_distance = sum(w.actual_distance or 0 for w in completed_workouts)
    completion_rate = len(completed_workouts) / len(all_workouts) * 100 if all_workouts else 0

    return {
        "message": "训练撤回成功",
        "workout_id": workout_id,
        "workout_type": workout.workout_type,
        "plan_stats": {
            "total_workouts": len(all_workouts),
            "completed_workouts": len(completed_workouts),
            "completion_rate": round(completion_rate, 1),
            "total_distance": round(total_distance, 1),
            "completed_distance": round(completed_distance, 1)
        }
    }


@router.get("/calendar")
def get_monthly_calendar(
    plan_id: str = Query(...),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """按月查看训练日历 - 返回每天的训练情况"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)

    month_workouts = db.query(Workout).filter(
        Workout.plan_id == plan_id,
        Workout.date >= start_of_month,
        Workout.date <= end_of_month
    ).order_by(Workout.date).all()

    calendar = []
    current_date = start_of_month
    while current_date <= end_of_month:
        day_workouts = [w for w in month_workouts if w.date == current_date]

        day_info = {
            "date": str(current_date),
            "day_of_week": current_date.weekday(),
            "day_name": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][current_date.weekday()],
            "has_workout": len(day_workouts) > 0,
            "workout_count": len(day_workouts),
            "workouts": []
        }

        for w in day_workouts:
            day_info["workouts"].append({
                "id": w.id,
                "workout_type": w.workout_type,
                "distance": w.distance,
                "duration": w.duration,
                "target_pace": w.target_pace,
                "description": w.description,
                "status": w.status,
                "actual_distance": w.actual_distance,
                "actual_duration": w.actual_duration,
                "actual_pace": w.actual_pace,
                "fatigue_level": w.fatigue_level,
                "gear_reminder": w.gear_reminder,
                "nutrition_tip": w.nutrition_tip
            })

        calendar.append(day_info)
        current_date += timedelta(days=1)

    month_stats = {
        "total_days": len(calendar),
        "days_with_workout": sum(1 for d in calendar if d["has_workout"]),
        "total_workouts": sum(d["workout_count"] for d in calendar),
        "completed_workouts": sum(1 for d in calendar for w in d["workouts"] if w["status"] == "completed"),
        "total_distance": sum(w.distance for d in calendar for w in d["workouts"]),
        "completed_distance": sum(w["actual_distance"] or 0 for d in calendar for w in d["workouts"] if w["status"] == "completed")
    }

    return {
        "plan_id": plan_id,
        "year": year,
        "month": month,
        "month_name": f"{year}年{month}月",
        "start_date": str(start_of_month),
        "end_date": str(end_of_month),
        "calendar": calendar,
        "month_stats": month_stats
    }


@router.get("/day/{plan_id}")
def get_day_detail(
    plan_id: str,
    target_date: str = Query(..., description="目标日期，格式: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取某一天的训练详情 - 与训练列表、周视图数据一致"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    ref_date = date.fromisoformat(target_date)
    day_workouts = db.query(Workout).filter(
        Workout.plan_id == plan_id,
        Workout.date == ref_date
    ).order_by(Workout.date).all()

    if not day_workouts:
        raise HTTPException(status_code=404, detail="该日期没有训练安排")

    workouts_detail = []
    for w in day_workouts:
        workouts_detail.append({
            "id": w.id,
            "workout_type": w.workout_type,
            "distance": w.distance,
            "duration": w.duration,
            "target_pace": w.target_pace,
            "pace_zones": w.pace_zones,
            "description": w.description,
            "notes": w.notes,
            "status": w.status,
            "actual_distance": w.actual_distance,
            "actual_duration": w.actual_duration,
            "actual_pace": w.actual_pace,
            "fatigue_level": w.fatigue_level,
            "gear_reminder": w.gear_reminder,
            "nutrition_tip": w.nutrition_tip,
            "completed_at": w.completed_at.isoformat() if w.completed_at else None
        })

    day_stats = {
        "total_distance": sum(w.distance for w in day_workouts),
        "completed_distance": sum(w.actual_distance or 0 for w in day_workouts),
        "completed_count": sum(1 for w in day_workouts if w.status == "completed"),
        "total_count": len(day_workouts)
    }

    return {
        "plan_id": plan_id,
        "date": target_date,
        "day_of_week": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][ref_date.weekday()],
        "workouts": workouts_detail,
        "day_stats": day_stats
    }
