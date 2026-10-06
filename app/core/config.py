from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Geospatial File Measurement API"
    database_url: str = "sqlite:///./geomeasure.db"
    max_upload_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()