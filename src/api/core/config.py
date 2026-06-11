from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PokeShow API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Orígenes CORS permitidos (Configurar con dominios específicos en producción)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    class Config:
        case_sensitive = True


settings = Settings()
