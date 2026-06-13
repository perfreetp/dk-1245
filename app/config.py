from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./running_training.db"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RunPlan API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
