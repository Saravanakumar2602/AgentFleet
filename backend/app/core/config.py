from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "AgentFleet API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Supabase credentials
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_DB_URL: Optional[str] = None

    # Route Baseline Configurations
    ROUTE_DEFAULT_SPEED_KMH: float = 61.26
    ROUTE_FUEL_L_PER_100KM: float = 14.266

    # CORS Configurations
    CORS_ORIGINS: list[str] = ["*"]

    # SMTP Configuration for Outbound Email Alerts
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "notifications@agentfleet.com"

    # Fallback Demo Target Emails
    DEMO_DRIVER_EMAIL: Optional[str] = "saravanaegs2602@gmail.com"
    DEMO_CUSTOMER_EMAIL: Optional[str] = "saravanakumar26022007@gmail.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
