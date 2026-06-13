from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from app.database import get_db
from app.models import CoachComment, TrainingPlan, Workout

router = APIRouter(prefix="/coach", tags=["教练端"])


class CoachCommentCreate(BaseModel):
    plan_id: str
    workout_id: str = None
    coach_id: str
    content: str
    rating: int = Field(None, ge=1, le=5)


class CoachCommentResponse(BaseModel):
    id: str
    plan_id: str
    workout_id: str = None
    coach_id: str
    content: str
    rating: int = None
    created_at: str

    class Config:
        from_attributes = True


@router.post("/comments", response_model=CoachCommentResponse, status_code=201)
def create_comment(comment: CoachCommentCreate, db: Session = Depends(get_db)):
    """追加教练点评"""
    if comment.workout_id:
        workout = db.query(Workout).filter(Workout.id == comment.workout_id).first()
        if not workout:
            raise HTTPException(status_code=404, detail="训练课次不存在")

    plan = db.query(TrainingPlan).filter(TrainingPlan.id == comment.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    db_comment = CoachComment(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment


@router.get("/comments/plan/{plan_id}", response_model=List[CoachCommentResponse])
def get_plan_comments(plan_id: str, db: Session = Depends(get_db)):
    """获取计划所有点评"""
    comments = db.query(CoachComment).filter(
        CoachComment.plan_id == plan_id
    ).order_by(CoachComment.created_at.desc()).all()
    return comments


@router.put("/comments/{comment_id}", response_model=CoachCommentResponse)
def update_comment(comment_id: str, content: str, rating: int = None, db: Session = Depends(get_db)):
    """更新点评"""
    comment = db.query(CoachComment).filter(CoachComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="点评不存在")

    comment.content = content
    if rating is not None:
        comment.rating = rating

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    """删除点评"""
    comment = db.query(CoachComment).filter(CoachComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="点评不存在")

    db.delete(comment)
    db.commit()
    return None


@router.get("/athletes", response_model=List[dict])
def get_coach_athletes(
    coach_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取教练管理的运动员"""
    plans = db.query(TrainingPlan).filter(
        TrainingPlan.id.in_(
            db.query(CoachComment.plan_id).filter(CoachComment.coach_id == coach_id).distinct()
        )
    ).all()

    athletes = []
    seen_users = set()
    for plan in plans:
        if plan.user_id not in seen_users:
            seen_users.add(plan.user_id)
            workouts = db.query(Workout).filter(Workout.plan_id == plan.id).all()
            completed = sum(1 for w in workouts if w.status == "completed")

            athletes.append({
                "user_id": plan.user_id,
                "plan_id": plan.id,
                "race_type": plan.race_type,
                "race_date": str(plan.race_date),
                "progress": f"{completed}/{len(workouts)}",
                "status": plan.status
            })

    return athletes
