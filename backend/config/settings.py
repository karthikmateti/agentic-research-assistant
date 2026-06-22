import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    openrouter_api_key: str = ""
    tavily_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    database_url: str = "sqlite:///./research_history.db"
    app_env: str = "development"
    log_level: str = "INFO"

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
    load_dotenv(PROJECT_ROOT / ".env")
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./research_history.db"),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
