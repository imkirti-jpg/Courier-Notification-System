from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_DATABASE_URL: str 


    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@notifications.com"

    # Production only — leave empty for local dev
    SENDGRID_API_KEY: str = ""
      
    CACHE_TTL: int = 3600

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Setting()