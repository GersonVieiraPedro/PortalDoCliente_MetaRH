from datetime import datetime, date
import json
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
from io import StringIO

from .settings import Settings
import numpy as np


#'workspace/pipedrive/persons.csv'
def baixar_arquivo_azure(file_path: str, nome: str):
    # Conectando ao DataLake
    service_client = DataLakeServiceClient(account_url=Settings().ACCOUTE_URL, credential=Settings().KEY)
    file_system_client = service_client.get_file_system_client(Settings().CONTAINER)

    # Caminho do arquivo no Azure
    file_client = file_system_client.get_file_client(file_path)

    # Baixando o arquivo
    download = file_client.download_file()
    csv_data = download.readall().decode('utf-8')  # Lê o conteúdo do arquivo CSV

    # Carrega o CSV para um DataFrame
    df = pd.read_csv(StringIO(csv_data), delimiter="|", dtype={"COD Contrato G.I": str})

    # Substituindo inf e NaN por None
    df = df.replace([float('inf'), float('-inf'), float('nan')], None)  

    tabela_dict = df.to_dict(orient="records")

    with open(f"src/Tabelas/{nome}.json", "w") as f:
        json.dump(tabela_dict, f, indent=4)  
    print(f"Arquivo: {nome} atualizado e salvo localmente.")

    return df



def SalvarArquivosLocal():
    # Verifica se o arquivo já existe localmente
       
    baixar_arquivo_azure('workspace/pipedrive/persons.csv', 'person')
    baixar_arquivo_azure('workspace/pipedrive/organizations.csv', 'organizations')





def limpar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Substitui valores problemáticos
    df = df.replace([np.inf, -np.inf, np.nan], None)

    # Converte datas para string
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
        elif df[col].apply(lambda x: isinstance(x, (pd.Timestamp, datetime))).any():
            df[col] = df[col].astype(str)
    
    return df
