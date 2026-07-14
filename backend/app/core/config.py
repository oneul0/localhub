from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./localhub.db", env="DATABASE_URL")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    allowed_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
