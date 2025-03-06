from fastapi import APIRouter
from app.api.endpoints import dashboard

router = APIRouter(prefix="/api")
router.include_router(dashboard.router, tags=["dashboard"]) 