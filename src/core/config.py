from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "LoveKuhnya Tenant CRM"
    API_V1_STR: str = "/api/v1"

    # Database
    #
    # DB_HOST/DB_PORT приходят из .env.example и docker-compose.
    # Внутри Docker-сети Postgres слушает на 5432, снаружи на DB_PORT (по умолчанию 5437).
    DB_HOST: str = "db"
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "crm"
    DB_PORT: int = 5437

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Если работаем внутри docker-compose (DB_HOST = "db"),
        # всегда ходим на внутренний порт 5432.
        # Если DB_HOST изменён (например, localhost), используем DB_PORT.
        port = 5432 if self.DB_HOST == "db" else self.DB_PORT
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{port}/{self.DB_NAME}"
        )

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
