from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # App
    APP_NAME: str = "Couple Bot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()