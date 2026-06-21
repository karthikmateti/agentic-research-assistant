from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    tavily_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    database_url: str = "sqlite:///./research_history.db"
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def openrouter_base_url(self) -> str:
        return "https://openrouter.ai/api/v1"

    @property
    def has_openrouter_key(self) -> bool:
        return bool(self.openrouter_api_key.strip())

    @property
    def has_tavily_key(self) -> bool:
        return bool(self.tavily_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
