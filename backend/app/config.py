from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Default to local SQLite for simple local development. In docker, this is
    # overridden from environment to Postgres (docker-compose.yml).
    DATABASE_URL: str = "sqlite:///./urbancare.db"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
