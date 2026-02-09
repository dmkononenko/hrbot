from fastapi import APIRouter
from app.api.v1 import surveys, employees, responses, bot

router = APIRouter()

# Include all routers
router.include_router(surveys.router, prefix="/surveys", tags=["surveys"])
router.include_router(employees.router, prefix="/employees", tags=["employees"])
router.include_router(responses.router, prefix="/responses", tags=["responses"])
router.include_router(bot.router, prefix="/bot", tags=["bot"])
