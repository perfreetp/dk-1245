from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from app.database import get_db
from app.models import User, TrainingPlan, Workout
from app.schemas import PlanCreate, PlanUpdate, PlanResponse, PlanOverview
from app.services import PlanGenerator

router = APIRouter(prefix="/plans", tags=["训练计划"])


@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(plan_data: PlanCreate, db: Session = Depends(get_db)):
    """创建训练计划"""
    user = db.query(User).filter(User.id == plan_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    race_config = {
        "5K": 12,
        "HALF_MARATHON": 16,
        "MARATHON": 20
    }
    total_weeks = race_config.get(plan_data.race_type, 16)
    start_date = plan_data.race_date - timedelta(weeks=total_weeks)

    if start_date < date.today():
        start_date = date.today()

    db_plan = TrainingPlan(
        user_id=plan_data.user_id,
        race_type=plan_data.race_type,
        race_date=plan_data.race_date,
        target_time=plan_data.target_time,
        start_date=start_date,
        total_weeks=total_weeks,
        status="active"
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    return db_plan


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str, db: Session = Depends(get_db)):
    """获取计划详情"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")
    return plan


@router.get("/user/{user_id}", response_model=List[PlanResponse])
def get_user_plans(user_id: str, db: Session = Depends(get_db)):
    """获取用户所有计划"""
    plans = db.query(TrainingPlan).filter(TrainingPlan.user_id == user_id).all()
    return plans


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: str, plan_update: PlanUpdate, db: Session = Depends(get_db)):
    """更新计划"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    update_data = plan_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: str, db: Session = Depends(get_db)):
    """删除计划"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    db.delete(plan)
    db.commit()
    return None


@router.post("/{plan_id}/generate", response_model=dict)
def generate_plan(plan_id: str, db: Session = Depends(get_db)):
    """生成训练计划"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    existing_workouts = db.query(Workout).filter(Workout.plan_id == plan_id).count()
    if existing_workouts > 0:
        raise HTTPException(status_code=400, detail="计划已生成，无法重复生成")

    user = db.query(User).filter(User.id == plan.user_id).first()

    generator = PlanGenerator(
        race_type=plan.race_type,
        race_date=plan.race_date,
        current_pace=plan.target_time if plan.target_time else user.current_pace,
        weekly_mileage=user.weekly_mileage,
        available_days=user.available_days or [1, 2, 3, 4, 5, 6],
        injury_history=user.injury_history or []
    )

    generated_plan = generator.generate_plan()

    for workout_data in generated_plan["workouts"]:
        workout = Workout(
            plan_id=plan_id,
            **workout_data
        )
        db.add(workout)

    db.commit()

    return {
        "message": generated_plan["message"],
        "total_weeks": generated_plan["total_weeks"],
        "total_workouts": len(generated_plan["workouts"]),
        "total_distance": generated_plan["total_distance"]
    }


@router.get("/{plan_id}/overview", response_model=PlanOverview)
def get_plan_overview(plan_id: str, db: Session = Depends(get_db)):
    """获取计划概览"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    workouts = db.query(Workout).filter(Workout.plan_id == plan_id).all()
    completed_workouts = [w for w in workouts if w.status == "completed"]

    completed_distance = sum(w.actual_distance or 0 for w in completed_workouts)
    total_distance = sum(w.distance for w in workouts)
    completion_rate = len(completed_workouts) / len(workouts) if workouts else 0

    completed_weeks = max([w.week_number for w in completed_workouts]) if completed_workouts else 0

    avg_pace = None
    if completed_workouts:
        paces = [w.actual_pace for w in completed_workouts if w.actual_pace]
        if paces:
            avg_pace = sum(paces) / len(paces)

    return PlanOverview(
        id=plan.id,
        race_type=plan.race_type,
        race_date=plan.race_date,
        target_time=plan.target_time,
        current_phase=plan.current_phase,
        total_weeks=plan.total_weeks,
        completed_weeks=completed_weeks,
        completion_rate=round(completion_rate, 2),
        total_distance=round(total_distance, 1),
        completed_distance=round(completed_distance, 1),
        average_pace=avg_pace
    )
