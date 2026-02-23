# backend/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str

    # PostgreSQL - now built from separate variables
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "support_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgress"

    # Vector DB
    VECTOR_DB_PATH: str = "./chroma_db"

    # FastAPI
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()