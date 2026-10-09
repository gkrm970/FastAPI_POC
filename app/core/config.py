from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./product.db"
    otel_enabled: bool = True # Enable or disable OpenTelemetry tracing
    otel_service_name: str = "product-api"
    otel_service_version: str = "1.0.0"
    otel_environment: str = "development"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
