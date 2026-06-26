from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )

    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="postgres")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5433, ge=1, le=65535)
    DB_NAME: str = Field(default="expenses_db")

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    TEST_DB_USER: str = Field(default="postgres")
    TEST_DB_PASSWORD: str = Field(default="postgres")
    TEST_DB_HOST: str = Field(default="localhost")
    TEST_DB_PORT: int = Field(default=5433, ge=1, le=65535)
    TEST_DB_NAME: str = Field(default="test_expenses_db")

    @property
    def test_db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.TEST_DB_USER}:{self.TEST_DB_PASSWORD}"
            f"@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )


settings = Settings()
