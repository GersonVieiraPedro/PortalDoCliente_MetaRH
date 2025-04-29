import os
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: ClassVar[str] = "C:\\Users\\GersonVieira\\Documents\\Projetos\\App"
    
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )
    SECRET_KEY: str
    ALGORITHM: str
    EXPIRES_IN_MINUTES: int
    ACCOUTE_URL: str
    CONTAINER: str
    KEY: str
    DRIVER: str
    SERVER: str
    DATABASE: str
    USER: str
    PASSWORD: str


