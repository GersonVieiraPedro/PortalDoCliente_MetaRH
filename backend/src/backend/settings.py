import os
from pathlib import Path
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict # type: ignore


class Settings(BaseSettings):
    BASE_DIR: ClassVar[str] = "C:\\Users\\GersonVieira\\Documents\\Projetos\\App"

    # Caminho absoluto para o arquivo .env (raiz do projeto)
    _ENV_FILE: ClassVar[Path] = Path(__file__).parent.parent.parent / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore',
    )

    # Database URLs - loaded from .env
    DATABASE_URL: str

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str
    EXPIRES_IN_MINUTES: int

    # Azure Storage
    ACCOUTE_URL: str
    CONTAINER: str
    KEY: str

    # Legacy ERP Database (ODBC)
    DRIVER_GI: str
    SERVER_GI: str
    DATABASE_GI: str
    USER_GI: str
    PASSWORD_GI: str

    # Email Configuration - RPS (Aprovação/Reprovação)
    EMAIL_RPS_ATIVO: bool = True  # Feature toggle: habilitar/desabilitar envio de emails
    EMAIL_RPS_REMETENTE: str = ""  # Email remetente (Gmail ou outro provedor SMTP)
    EMAIL_RPS_SENHA: str = ""  # Senha de aplicativo (App Password)
    EMAIL_DESTINATARIOS_RPS: str = ""  # Lista de emails separados por vírgula


