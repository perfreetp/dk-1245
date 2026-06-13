from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import users_router, plans_router, workouts_router, coach_router, reports_router, checkins_router
from app.models import User, TrainingPlan, Workout, CheckIn, CoachComment, PhaseReport

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="智能跑步训练计划后端服务 API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(plans_router, prefix=settings.API_V1_PREFIX)
app.include_router(workouts_router, prefix=settings.API_V1_PREFIX)
app.include_router(coach_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(checkins_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "RunPlan API - 智能跑步训练计划服务",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
