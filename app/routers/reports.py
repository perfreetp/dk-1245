from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from app.database import get_db
from app.models import TrainingPlan, Workout, PhaseReport, User
from app.services import PredictionService, FatigueTracker, PaceCalculator
from app.utils.training_types import TRAINING_PHASES

router = APIRouter(prefix="/reports", tags=["报告与分析"])


@router.get("/{plan_id}/phase")
def get_phase_report(plan_id: str, db: Session = Depends(get_db)):
    """获取阶段报告"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    workouts = db.query(Workout).filter(Workout.plan_id == plan_id).order_by(Workout.week_number).all()

    phases = {}
    for phase_key, phase_config in TRAINING_PHASES.items():
        phase_weeks = [w for w in workouts if
            phase_config.get("start", 1) <= w.week_number <= phase_config.get("end", 20)
        ]
        if not phase_weeks:
            continue

        completed = [w for w in phase_weeks if w.status == "completed"]
        total_distance = sum(w.distance for w in phase_weeks)
        completed_distance = sum(w.actual_distance or 0 for w in completed)
        completion_rate = len(completed) / len(phase_weeks) if phase_weeks else 0

        avg_pace = None
        if completed:
            paces = [w.actual_pace for w in completed if w.actual_pace]
            if paces:
                avg_pace = sum(paces) / len(paces)

        fatigue_trend = FatigueTracker.analyze_fatigue_trend([
            {"fatigue_level": w.fatigue_level}
            for w in completed[-7:]
        ])

        phases[phase_key] = {
            "name": phase_config["name"],
            "weeks": len(phase_weeks),
            "completed_weeks": len(completed),
            "completion_rate": round(completion_rate, 2),
            "total_distance": round(total_distance, 1),
            "completed_distance": round(completed_distance, 1),
            "average_pace": PaceCalculator.seconds_to_pace(avg_pace) if avg_pace else None,
            "fatigue_trend": fatigue_trend
        }

    return {
        "plan_id": plan_id,
        "race_type": plan.race_type,
        "current_phase": plan.current_phase,
        "phases": phases
    }


@router.get("/{plan_id}/progress")
def get_progress_report(plan_id: str, db: Session = Depends(get_db)):
    """获取进度报告"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    workouts = db.query(Workout).filter(Workout.plan_id == plan_id).all()
    completed = [w for w in workouts if w.status == "completed"]

    total_distance = sum(w.distance for w in workouts)
    completed_distance = sum(w.actual_distance or 0 for w in completed)
    completion_rate = len(completed) / len(workouts) if workouts else 0

    weekly_progress = []
    for week in range(1, plan.total_weeks + 1):
        week_workouts = [w for w in workouts if w.week_number == week]
        week_completed = [w for w in week_workouts if w.status == "completed"]

        weekly_progress.append({
            "week": week,
            "total_distance": round(sum(w.distance for w in week_workouts), 1),
            "completed_distance": round(sum(w.actual_distance or 0 for w in week_completed), 1),
            "completion_rate": round(len(week_completed) / len(week_workouts) if week_workouts else 0, 2)
        })

    avg_pace = None
    if completed:
        paces = [w.actual_pace for w in completed if w.actual_pace]
        if paces:
            avg_pace = sum(paces) / len(paces)

    return {
        "plan_id": plan_id,
        "total_weeks": plan.total_weeks,
        "completed_weeks": max([w.week_number for w in completed]) if completed else 0,
        "total_distance": round(total_distance, 1),
        "completed_distance": round(completed_distance, 1),
        "completion_rate": round(completion_rate, 2),
        "average_pace": PaceCalculator.seconds_to_pace(avg_pace) if avg_pace else None,
        "weekly_progress": weekly_progress
    }


@router.get("/{user_id}/prediction")
def get_finish_prediction(
    user_id: str,
    plan_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """完赛预测"""
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.id == plan_id,
        TrainingPlan.user_id == user_id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    user = db.query(User).filter(User.id == user_id).first()
    workouts = db.query(Workout).filter(Workout.plan_id == plan_id).all()
    completed = [w for w in workouts if w.status == "completed"]

    training_completion_rate = len(completed) / len(workouts) if workouts else 0

    prediction = PredictionService.predict_finish_time(
        race_type=plan.race_type,
        current_pace=user.current_pace,
        target_time=plan.target_time,
        training_completion_rate=training_completion_rate
    )

    race_distances = {
        "5K": 5.0,
        "HALF_MARATHON": 21.0975,
        "MARATHON": 42.195
    }
    distance = race_distances.get(plan.race_type, 0)

    pace_strategy = PredictionService.generate_pace_strategy(
        plan.race_type,
        prediction["predicted_time"],
        distance
    )

    risk = PredictionService.assess_risk(
        prediction["predicted_time"],
        plan.target_time
    )

    return {
        "predicted_time": prediction["predicted_time"],
        "predicted_pace": prediction["predicted_pace"],
        "confidence": prediction["confidence"],
        "pace_strategy": pace_strategy,
        "risk_assessment": risk
    }


@router.get("/{plan_id}/fatigue")
def get_fatigue_risk(plan_id: str, db: Session = Depends(get_db)):
    """疲劳风险提示"""
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    user = db.query(User).filter(User.id == plan.user_id).first()
    workouts = db.query(Workout).filter(Workout.plan_id == plan_id).order_by(Workout.date.desc()).limit(14).all()

    recent_workouts = [
        {
            "intensity": 4 if w.workout_type in ["INTERVAL", "TEMPO_RUN"] else 1,
            "fatigue_level": w.fatigue_level or 5
        }
        for w in workouts[-7:]
    ]

    if len(workouts) > 1:
        prev_week_distance = sum(w.distance for w in workouts[-14:-7])
        current_week_distance = sum(w.distance for w in workouts[-7:])
        mileage_increase = ((current_week_distance - prev_week_distance) / prev_week_distance * 100) if prev_week_distance > 0 else 0
    else:
        mileage_increase = 0

    fatigue_risk = FatigueTracker.calculate_fatigue_risk(
        recent_workouts=recent_workouts,
        weekly_mileage_increase=mileage_increase,
        injury_history=user.injury_history or []
    )

    adjustment = FatigueTracker.suggest_adjustment(fatigue_risk, sum(w.distance for w in workouts[-7:]))

    return {
        "risk_level": fatigue_risk["risk_level"],
        "risk_score": fatigue_risk["risk_score"],
        "risk_factors": fatigue_risk["risk_factors"],
        "recommendation": fatigue_risk["recommendation"],
        "adjustment": adjustment
    }
