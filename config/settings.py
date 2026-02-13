import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Global configuration settings for Alpha-Omega."""
    
    # Project Info
    PROJECT_NAME: str = "Alpha-Omega System"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API Key")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google API Key")
    ALPACA_API_KEY: Optional[str] = Field(default=None, description="Alpaca API Key")
    ALPACA_SECRET_KEY: Optional[str] = Field(default=None, description="Alpaca Secret Key")
    BLOOMBERG_API_KEY: Optional[str] = Field(default=None, description="Bloomberg API Key")
    POLYGON_API_KEY: Optional[str] = Field(default=None, description="Polygon.io API Key")

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")

    # Model Configuration
    DEFAULT_LLM_MODEL: str = "gemini-pro"
    FAST_LLM_MODEL: str = "gemini-pro"
    REASONING_LLM_MODEL: str = "claude-3-opus-20240229"

    # Risk Management
    MAX_DRAWDOWN_LIMIT: float = 0.15 # 15%
    CONFIDENCE_THRESHOLD: float = 0.85 # 85%

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

def get_settings() -> Settings:
    return Settings()

settings = get_settings()
