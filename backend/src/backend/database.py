from io import StringIO
import json
import numpy as np
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pyodbc
from .settings import Settings

engine = create_engine(Settings().DATABASE_URL)

def AtivarSession():
    """Cria uma nova sessão do banco de dados."""
    with Session(engine) as session:
        yield session



def TB_Cliente(CodigoCliente: str, CNPJ: list[str]):
    
    # Conexão com o banco de dados utilizando ODBC
    StrCnxn = "DRIVER={ODBC Driver 17 for SQL Server};"+f"""SERVER={Settings().SERVER};DATABASE={Settings().DATABASE};UID={Settings().USER};PWD={Settings().PASSWORD}"""
    
    # Estabelecendo conexão com o banco de dados utilizando ODBC
    cnxn = pyodbc.connect(StrCnxn)

    sql = "SELECT CodigoCliente,RazaoSocial,NomeFantasia,Endereco,Bairro,Cidade,UF,CEP,Telefone,Email,CGC AS CNPJ,Contato,DataInclusao,DataAlteracao,NomeUsuario FROM TB_Cliente WHERE ClienteAtivo = 1 "


    if CodigoCliente == None and CNPJ != None:   
        # Se apenas o CNPJ for fornecido, retorna os registros correspondentes ao CNPJ
        sql = sql + f' AND CGC IN ({CNPJ})'

    elif CodigoCliente != None and CNPJ == None:    
        # Se apenas o Código do Cliente for fornecido, retorna os registros correspondentes ao Código do Cliente
        sql = sql + f' AND CodigoCliente IN ({CodigoCliente})'

    elif CodigoCliente != None and CNPJ != None:
        # Se ambos os parâmetros forem fornecidos, retorna os registros correspondentes a ambos
        sql = sql + f' AND CodigoCliente IN (${CodigoCliente}) AND CGC IN ({CNPJ})'    

    Tabela = pd.read_sql(sql, cnxn, dtype={"CodigoCliente": str})    

    cnxn.close()

    return Tabela


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

