from typing import Any, Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trips_planner"
    session_secret: str = "change-me"
    token_encryption_secret: str | None = None
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
    auth_allowed_emails: str = ""
    auth_allowed_domains: str = ""

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        if value.startswith("postgresql+psycopg://"):
            return value
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        return value

    @staticmethod
    def _parse_csv_list(raw: str) -> list[str]:
        return [item.strip().lower() for item in raw.split(",") if item.strip()]

    @property
    def frontend_origin(self) -> str:
        return self.app_url.rstrip("/")

    @property
    def resolved_token_encryption_secret(self) -> str:
        return self.token_encryption_secret or self.session_secret

    @property
    def allowed_auth_emails(self) -> set[str]:
        return set(self._parse_csv_list(self.auth_allowed_emails))

    @property
    def allowed_auth_domains(self) -> set[str]:
        return set(self._parse_csv_list(self.auth_allowed_domains))

    def is_email_allowed_to_sign_in(self, email: str) -> bool:
        normalized_email = email.strip().lower()
        if not normalized_email:
            return False

        allowed_emails = self.allowed_auth_emails
        allowed_domains = self.allowed_auth_domains
        if not allowed_emails and not allowed_domains:
            return True

        if normalized_email in allowed_emails:
            return True

        domain = normalized_email.partition("@")[2]
        return bool(domain and domain in allowed_domains)

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.app_env.lower() == "production":
            if self.session_secret == "change-me":
                raise ValueError("SESSION_SECRET must be set to a strong random value in production")
            if self.resolved_token_encryption_secret == "change-me":
                raise ValueError("TOKEN_ENCRYPTION_SECRET must be set to a strong random value in production")
            if not self.session_cookie_secure:
                raise ValueError("SESSION_COOKIE_SECURE must be true in production")
            if self.session_cookie_samesite != "none":
                raise ValueError("SESSION_COOKIE_SAMESITE must be 'none' for cross-origin production deployments")
        return self


settings = Settings()
