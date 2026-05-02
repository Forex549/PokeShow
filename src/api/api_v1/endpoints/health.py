from fastapi import APIRouter
from src.api.schemas.health import HealthCheck
from src.api.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthCheck, status_code=200)
def health_check() -> HealthCheck:
    """
    Endpoint para verificar el estado de salud de la API.
    """
    return HealthCheck(status="OK", version=settings.VERSION)
