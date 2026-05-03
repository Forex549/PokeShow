from fastapi import APIRouter

from src.api.api_v1.endpoints import (
    battle,
    health,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(battle.router, prefix="/battle", tags=["battle"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
