from io import StringIO
import json
import os
import numpy as np
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
import pyodbc
from .settings import Settings

_settings = Settings()

# Configurar engine com pool de conexões robusto
engine = create_engine(
    _settings.DATABASE_URL,
    # Pool de conexões
    pool_size=5,                    # Número de conexões mantidas no pool
    max_overflow=10,                # Conexões extras além do pool_size
    pool_recycle=3600,              # Reciclar conexões a cada 1 hora (evita timeout do SQL Server)
    pool_pre_ping=True,             # CRÍTICO: Testa conexão antes de usar (evita erro 10054)
    # Timeouts
    connect_args={
        "timeout": 30,              # Timeout de conexão em segundos
    },
    # Logging (descomente para debug)
    # echo=True,                    # Log de todas as queries SQL
)

def AtivarSession():
    """Cria uma nova sessão do banco de dados."""
    with Session(engine) as session:
        yield session




def TB_Persons():
    

    service_client = DataLakeServiceClient(account_url=Settings().ACCOUTE_URL, credential=Settings().KEY)
    file_system_client = service_client.get_file_system_client(Settings().CONTAINER)

    # Baixando o arquivo CSV
    file_client = file_system_client.get_file_client('workspace/pipedrive/persons.csv')
    downloaded_file = file_client.download_file()

    # Lendo o conteúdo do arquivo CSV em um DataFrame
    csv_data = downloaded_file.readall().decode("utf-8")
    df = pd.read_csv(StringIO(csv_data), delimiter="|", dtype={"COD Contrato G.I": str})
    df = df.replace([np.inf, -np.inf, np.nan], None)

    # Aqui o DataFrame já está limpo
    TB_Organizacao_Completo = df.to_dict(orient="records")  # agora é uma lista de dicts

    return TB_Organizacao_Completo

