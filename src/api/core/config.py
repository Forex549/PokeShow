from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PokeShow API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Orígenes CORS permitidos (Configurar con dominios específicos en producción)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True


settings = Settings()
