from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Vehicle Insurance Claim Management System"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./vehicle_insurance.db"

    JWT_SECRET_KEY: str = Field(
        validation_alias=AliasChoices("JWT_SECRET_KEY", "JWT_SECRET"),
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "vehicle_insurance_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
