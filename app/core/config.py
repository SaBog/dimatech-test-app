from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:root@localhost:5432/dimatech_test_db"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SECRET_KEY: str = "gfdmhghif38yrf9ew0jkf32"
    JWT_SECRET: str = "jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
