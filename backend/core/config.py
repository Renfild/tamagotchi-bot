"""
Application configuration using Pydantic Settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Tamagotchi Bot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Telegram
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    BOT_USERNAME: str = Field(..., description="Telegram Bot Username")
    WEBAPP_URL: str = Field(..., description="Mini App URL")
    ADMIN_IDS: List[int] = Field(default_factory=list, description="Admin Telegram IDs")
    
    @validator("ADMIN_IDS", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v
    
    # Database
    POSTGRES_USER: str = "tamagotchi"
    POSTGRES_PASSWORD: str = "secret"
    POSTGRES_DB: str = "tamagotchi_db"
    DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v, values):
        if v:
            return v
        return (
            f"postgresql+asyncpg://{values.get('POSTGRES_USER')}"
            f":{values.get('POSTGRES_PASSWORD')}@postgres:5432/"
            f"{values.get('POSTGRES_DB')}"
        )
    
    # Redis
    REDIS_PASSWORD: str = "redispass"
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v, values):
        if v:
            return v
        password = values.get("REDIS_PASSWORD", "")
        return f"redis://:{password}@redis:6379/0"
    
    @validator("CELERY_BROKER_URL", pre=True)
    def assemble_celery_broker(cls, v, values):
        if v:
            return v
        password = values.get("REDIS_PASSWORD", "")
        return f"redis://:{password}@redis:6379/1"
    
    @validator("CELERY_RESULT_BACKEND", pre=True)
    def assemble_celery_backend(cls, v, values):
        if v:
            return v
        password = values.get("REDIS_PASSWORD", "")
        return f"redis://:{password}@redis:6379/2"
    
    # MinIO S3
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_PETS: str = "tamagotchi-pets"
    MINIO_BUCKET_ASSETS: str = "tamagotchi-assets"
    
    # Security
    JWT_SECRET: str = Field(..., min_length=32, description="JWT Secret Key")
    ENCRYPTION_KEY: Optional[str] = None
    
    # AI Generation
    STABILITY_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_GENERATION_ENABLED: bool = False
    
    # Payments
    PAYMENT_PROVIDER_TOKEN: Optional[str] = None
    PREMIUM_PRICE_STARS: int = 100
    
    # Feature Flags
    ENABLE_PVP: bool = True
    ENABLE_BREEDING: bool = True
    ENABLE_MARKET: bool = True
    ENABLE_GUILDS: bool = False
    ENABLE_AI_GENERATION: bool = True
    
    # Game Balance
    HUNGER_DECAY_PER_HOUR: int = 5
    HAPPINESS_DECAY_PER_HOUR: int = 3
    ENERGY_RECOVERY_PER_HOUR: int = 10
    MAX_PETS_PER_USER: int = 10
    BREEDING_COOLDOWN_HOURS: int = 168
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
