from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LendGuard AI"
    environment: str = "development"
    secret_key: str = "change-me-in-production"
    access_token_minutes: int = 60
    database_url: str = "sqlite:///./lendguard.db"
    model_path: str = "ml/artifacts/model.joblib"
    powerbi_push_url: str | None = None
    powerbi_embed_url: str | None = None
    cors_origins: str = "http://localhost:3000,http://localhost:3100,http://127.0.0.1:3100"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
