from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trips_planner"
    session_secret: str = "change-me"
    session_cookie_name: str = "trip_session"
    session_cookie_domain: str | None = None
    session_cookie_secure: bool = False
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    session_max_age_seconds: int = 60 * 60 * 24 * 7
    oauth_state_cookie_name: str = "trip_oauth_state"
    oauth_state_max_age_seconds: int = 600
    google_client_id: str = ""
    google_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/api/routes/auth/google/callback"
    google_maps_api_key: str = ""

    @property
    def frontend_origin(self) -> str:
        return self.app_url.rstrip("/")

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.app_env.lower() == "production":
            if self.session_secret == "change-me":
                raise ValueError("SESSION_SECRET must be set to a strong random value in production")
            if not self.session_cookie_secure:
                raise ValueError("SESSION_COOKIE_SECURE must be true in production")
            if self.session_cookie_samesite != "none":
                raise ValueError("SESSION_COOKIE_SAMESITE must be 'none' for cross-origin production deployments")
        return self


settings = Settings()
