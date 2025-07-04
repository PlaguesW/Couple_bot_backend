from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/couple_bot"
    
    # API Security
    API_TOKEN: str = "your-secret-api-token"
    
    # Application
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()