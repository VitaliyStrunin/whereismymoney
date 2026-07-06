from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = Field(default=5433, ge=1, le=65535)
    DB_NAME: str = "expenses_db"

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    TEST_DB_USER: str = "postgres"
    TEST_DB_PASSWORD: str = "postgres"
    TEST_DB_HOST: str = "localhost"
    TEST_DB_PORT: int = Field(default=5433, ge=1, le=65535)
    TEST_DB_NAME: str = "test_expenses_db"

    @property
    def test_db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.TEST_DB_USER}:{self.TEST_DB_PASSWORD}"
            f"@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    JWT_SECRET_KEY: str = "ultrasecretkey-hide-it-in-prod-it-is-just-example-for-dev"
    JWT_ACCESS_TOKEN_TTL_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"

settings = Settings()
