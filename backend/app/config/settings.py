from pydantic_settings import BaseSettings
from pydantic import ConfigDict
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
    openai_model: str = "gpt-3.5-turbo"
    
    # External API Configuration (MISSING FIELDS - ADDING NOW)
    external_api_base_url: str = "https://api.example.com"
    external_api_key: str = "your_external_api_key_here"
    
    # Application Configuration (MISSING FIELD - ADDING NOW)
    debug: bool = True
    
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
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # This allows extra environment variables to be ignored
    )


# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings