
from pydantic_settings import BaseSettings

DEFAULT_SECRET_KEY = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Urban Traffic Management"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Environment: development | staging | production
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/urban_traffic"
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Camera Settings
    RTSP_TIMEOUT: int = 10
    FRAME_RATE: int = 5

    # ML Settings
    CONFIDENCE_THRESHOLD: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_security(self) -> None:
        """Fail fast on insecure configuration before serving traffic."""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == DEFAULT_SECRET_KEY:
                raise RuntimeError(
                    "SECRET_KEY must be set to a strong value in production "
                    "(generate with: openssl rand -hex 32)"
                )
            if len(self.SECRET_KEY) < 32:
                raise RuntimeError("SECRET_KEY must be at least 32 characters long")


settings = Settings()
settings.validate_security()
