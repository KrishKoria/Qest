from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "fitness_studio"
    
    # API Configuration
    api_title: str = "Fitness Studio Agent API"
    api_description: str = "CrewAI-powered agents for fitness studio management"
    api_version: str = "1.0.0"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI Configuration (for CrewAI)
    openai_api_key: Optional[str] = None
    openai_model: str = "deepseek-chat"
    
    # Crew Configuration
    crew_verbose: bool = True
    crew_memory: bool = True
    
    # External Services (Bonus Features)
    redis_url: Optional[str] = "redis://localhost:6379"
    translation_service_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    allowed_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
