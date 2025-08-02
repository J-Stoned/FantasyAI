"""
Configuration settings for Fantasy AI Ultimate merged project
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Fantasy AI Ultimate - Merged"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./fantasy_ai.db"
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Yahoo Fantasy API
    yahoo_client_id: Optional[str] = None
    yahoo_client_secret: Optional[str] = None
    yahoo_redirect_uri: str = "http://localhost:8000/auth/callback"
    
    # AI/ML Settings
    model_cache_dir: str = "./models"
    prediction_confidence_threshold: float = 0.7
    max_analysis_workers: int = 4
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list = ["*"]
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None  # Set to None to disable file logging for now
    
    # Override settings for production
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Disable file logging in production
        if os.getenv("ENVIRONMENT") == "production":
            self.log_file = None
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # Cache Settings
    cache_ttl_seconds: int = 3600  # 1 hour
    player_cache_ttl: int = 1800   # 30 minutes
    league_cache_ttl: int = 7200   # 2 hours
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific configurations
def get_database_url() -> str:
    """Get database URL based on environment"""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    elif os.getenv("ENVIRONMENT") == "production":
        return "postgresql+asyncpg://user:password@localhost/fantasy_ai_prod"
    else:
        return "sqlite+aiosqlite:///./fantasy_ai.db"

def get_redis_url() -> Optional[str]:
    """Get Redis URL based on environment"""
    if os.getenv("REDIS_URL"):
        return os.getenv("REDIS_URL")
    elif os.getenv("ENVIRONMENT") == "production":
        return "redis://localhost:6379"
    else:
        return None

# Update settings with environment-specific values
settings.database_url = get_database_url()
settings.redis_url = get_redis_url()

# Yahoo API credentials
settings.yahoo_client_id = os.getenv("YAHOO_CLIENT_ID")
settings.yahoo_client_secret = os.getenv("YAHOO_CLIENT_SECRET")

# Security
settings.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production") 