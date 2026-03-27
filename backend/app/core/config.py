from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trips_planner"
    session_secret: str = "change-me"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/api/routes/auth/google/callback"
    google_maps_api_key: str = ""


settings = Settings()
