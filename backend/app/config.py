from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://guardian:guardian_password@localhost:5432/it_guardian"

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_debug: bool = True
    secret_key: str = "change_this_in_production"

    # Monitoring
    monitoring_interval_seconds: int = 60
    monitoring_timeout_seconds: int = 5
    monitoring_ping_count: int = 4

    class Config:
        env_file = ".env"

settings = Settings()
