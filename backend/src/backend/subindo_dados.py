from io import StringIO
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceNotFoundError
from src.backend.settings import Settings
import pyodbc
from sqlalchemy.exc import ProgrammingError
from typing import Optional

_settings = Settings()
engine = create_engine(
    _settings.DATABASE_URL,
    fast_executemany=True,      # ESSENCIAL PARA SQL SERVER
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    future=True
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT DB_NAME()"))
    print("Conectado ao banco:", result.scalar())


def _resolve_account_url(settings_obj) -> str:
    """
    Tentativa de encontrar o atributo correto no Settings, com fallback
    caso haja um typo no nome (ACCOUTE_URL vs ACCOUNT_URL).
    """
    for attr in ("ACCOUNT_URL", "ACCOUTE_URL", "ACCOUNTURL", "ACCOUNT_ENDPOINT", "ACCOUNT"):
        val = getattr(settings_obj, attr, None)
        if val:
            return val
    raise AttributeError(
        "Não foi possível encontrar a URL da conta nos Settings. "
        "Procure por ACCOUNT_URL ou ACCOUTE_URL em src/backend/settings.py"
    )


def safe_download_file(file_system_client, path_csv: str, debug_list_path: Optional[str] = None) -> bytes:
    """
    Tenta baixar o arquivo do Data Lake com checagens e logs adicionais.
    Em caso de falha (ResourceNotFoundError) lista o diretório pai para
    ajudar no diagnóstico.
    """
    file_client = file_system_client.get_file_client(path_csv)
    print("Tentando baixar:", getattr(file_client, "url", "<sem url>"))
    # usa exists() quando disponível (evita exceção)
    try:
        if hasattr(file_client, "exists"):
            exists = file_client.exists()
            print("exists():", exists)
            if not exists:
                raise ResourceNotFoundError("exists() retornou False (arquivo não encontrado).")
        downloader = file_client.download_file()
        content = downloader.readall()
        print("Download realizado. Bytes lidos:", len(content))
        return content
    except ResourceNotFoundError as e:
        print("Erro ao baixar arquivo (ResourceNotFoundError):", e)
        # tenta listar o diretório para ajudar no debug
        try:
            # Se o usuário forneceu explicitamente um caminho a listar, usa ele,
            # senão calcula o diretório pai do arquivo solicitado
            list_path = debug_list_path
            if not list_path:
                if "/" in path_csv:
                    list_path = "/".join(path_csv.split("/")[:-1])
                else:
                    list_path = ""  # raiz do filesystem
            print(f"Listando arquivos em '{list_path}' para ajudar no diagnóstico:")
            for p in file_system_client.get_paths(path=list_path):
                print(" -", p.name)
        except Exception as le:
            print("Falha ao listar diretório:", le)
        # relança para o chamador tratar ou encerrar
        raise


def Atualizar_Dados(
    path_csv: str,
    tabela: str,
    numeric_cols: list[str] = [],
    delimiter: str = "|",
    truncate: bool = False,
    col_names: list[str] = None
):
    """
    Insere dados a partir de um CSV do Data Lake (ou local) em uma tabela existente.
    Pode opcionalmente truncar a tabela antes da inserção.

    Args:
        path_csv (str): Caminho do CSV no Data Lake.
        tabela (str): Nome da tabela no SQL Server (schema 'dbo').
        numeric_cols (list[str]): Colunas que precisam de conversão de vírgula decimal para float.
        delimiter (str): Separador do CSV (default '|').
        truncate (bool): Se True, faz TRUNCATE TABLE antes de inserir os dados.
        col_names (list[str], optional): Lista de nomes de colunas para renomear o CSV.
    """

    print(f"Iniciando atualização da tabela {tabela}...")

    # Conecta ao Data Lake e lê o CSV
    try:
        account_url = _resolve_account_url(_settings)
    except AttributeError as ae:
        print("Erro de configuração:", ae)
        return

    service_client = DataLakeServiceClient(
        account_url=account_url,
        credential=_settings.KEY
    )
    file_system_client = service_client.get_file_system_client(_settings.CONTAINER)

    try:
        raw_bytes = safe_download_file(file_system_client, path_csv)
    except ResourceNotFoundError:
        print("Arquivo não encontrado no Data Lake. Verifique o caminho e o container.")
        return
    except Exception as e:
        print("Erro inesperado ao baixar o arquivo:", e)
        return

    # tenta decodificar com latin1, senão utf-8
    try:
        csv_data = raw_bytes.decode("latin1")
    except Exception:
        try:
            csv_data = raw_bytes.decode("utf-8")
        except Exception as e:
            print("Falha ao decodificar bytes do CSV:", e)
            return

    # Lê CSV com header condicional
    try:
        if col_names:
            df = pd.read_csv(StringIO(csv_data), delimiter=delimiter, header=None, dtype=str)


            if len(col_names) != len(df.columns):
                print(f"Erro: número de nomes de colunas ({len(col_names)}) não bate com o CSV ({len(df.columns)}).")
                return
            df.columns = col_names
        else:
            df = pd.read_csv(StringIO(csv_data), delimiter=delimiter, header=0, dtype=str)
            # --- LIMPA BOM DO CABEÇALHO ---
            df.columns = [col.replace("\ufeff", "").replace("ï»¿", "") for col in df.columns]

    except Exception as e:
        print("Erro ao ler o CSV com pandas:", e)
        return

    # Remove coluna ID se for identity
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])

    # Converte colunas numéricas com vírgula decimal para float de forma robusta
    for col in numeric_cols:
        if col in df.columns:
            # Substitui vírgula por ponto e tenta converter, forçando NaN em erros
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)

            # Converte para float
            df[col] = pd.to_numeric(df[col], errors="coerce")

            # Converte apenas valores inteiros
            df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) and float(x).is_integer() else pd.NA)

            # Usa tipo inteiro que aceita NA
            df[col] = df[col].astype("Int64")

    # Substitui valores infinitos por NaN e garante tipo apropriado
    df = df.replace([np.inf, -np.inf], np.nan)

    # Remove linhas totalmente vazias
    df = df.dropna(how="all")

    # Conta linhas carregadas
    print(f"CSV carregado com {len(df)} linhas e colunas: {list(df.columns)}")

    # Truncate se ativado
    if truncate:
        try:
            with engine.begin() as conn:
                conn.execute(text(f"TRUNCATE TABLE dbo.{tabela}"))
            print(f"Tabela {tabela} truncada com sucesso.")
        except Exception as e:
            print(f"Erro ao truncar a tabela {tabela}: {e}")
            return


    # Insere os dados na tabela
    try:
        df.to_sql(tabela, con=engine, schema="dbo", if_exists="append", index=False)
        print(f"Dados inseridos com sucesso na tabela {tabela}.")
    except ProgrammingError as e:
        print(f"Erro de programação no SQL Server. Provavelmente problemas nos nomes das colunas: {e}")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela {tabela}: {e}")

    print(f"Processo finalizado para {tabela}.")


if __name__ == "__main__":
    # chamada de exemplo quando executado como módulo
    Atualizar_Dados(
        path_csv="workspace/manual/TB_Empresa.csv",
        tabela="TB_Empresas",
        numeric_cols = [
        "CodigoCliente",
        "CodigoEmpresaFat",
        "CodigoFilialFat",
        "Ativo",
        "IDPipedrive",
        "IDSelecty",
        "IDProprietario"
        ],   
        delimiter=";",
        truncate=False
    )

"""# Exemplo de uso:

    # Exemplo 1: Inserir CSV mantendo os nomes originais das colunas do CSV
    Atualizar_Dados(
        path_csv="workspace/manual/TB_ISS.csv",
        tabela="TB_ISS",
        numeric_cols=["ISS"],  # Colunas que têm vírgula decimal
        delimiter="|",
        truncate=False  # Não limpa a tabela antes
    )

    # Exemplo 2: Inserir CSV renomeando as colunas
    Atualizar_Dados(
        path_csv="workspace/manual/TB_ISS.csv",
        tabela="TB_ISS",
        numeric_cols=["ISS"],
        delimiter="|",
        truncate=True,  # Limpa a tabela antes
        col_names=["ID", "UF", "Municipio", "Label", "ISS"]  # Nomes que devem bater com a tabela
    )

"""