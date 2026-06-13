from app.routers.users import router as users_router
from app.routers.plans import router as plans_router
from app.routers.workouts import router as workouts_router
from app.routers.coach import router as coach_router
from app.routers.reports import router as reports_router
from app.routers.checkins import router as checkins_router

__all__ = ["users_router", "plans_router", "workouts_router", "coach_router", "reports_router", "checkins_router"]
