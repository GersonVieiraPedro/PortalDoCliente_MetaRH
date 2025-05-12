import pyodbc
import pandas as pd
from .settings import Settings

def Conectar():
    settings = Settings()
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={settings.SERVER};"
        f"DATABASE={settings.DATABASE};"
        f"UID={settings.USER};"
        f"PWD={settings.PASSWORD};"
        f"TrustServerCertificate=yes;"
    )

def TabelaFuncionarios(CodigoCliente=None, CNPJ=None):
    conn = Conectar()
    cursor = conn.cursor()

    where_clauses = []
    params = []

    if CodigoCliente:
        placeholders = ','.join('?' for _ in CodigoCliente)
        where_clauses.append(f"Funcionario.CodigoCliente IN ({placeholders})")
        params.extend(CodigoCliente)

    if CNPJ:
        placeholders = ','.join('?' for _ in CNPJ)
        where_clauses.append(f"Cliente.CGC IN ({placeholders})")
        params.extend(CNPJ)

    where_sql = ' WHERE ' + ' OR '.join(where_clauses) if where_clauses else ''

    sql = f"""
        SELECT
            CodigoFuncionario,
            CodigoContrato,
            TipoFat,
            Funcionario.CodigoCliente,
            RazaoSocial,
            CGC,
            Funcionario.CodigoCentroCusto,
            NomeCentroCusto,
            Endereco,
            Funcionario.CodigoFuncao,
            Funcao,
            Nome,
            DataNascimento,
            DataAdmissao,
            DataDemissao,
            Sexo,
            EstadoCivil,
            Nacionalidade,
            CidadeResid,
            CASE
                WHEN DataAdmissao <= GETDATE() AND (DataDemissao IS NULL OR DataDemissao > GETDATE()) 
                THEN 'Sim'
                ELSE 'Não'
            END AS Ativo
        FROM TB_Funcionario AS Funcionario
        LEFT JOIN (
            SELECT CodigoFuncao, Descricao AS Funcao FROM TB_Funcao
        ) AS Func ON Funcionario.CodigoFuncao = Func.CodigoFuncao
        LEFT JOIN (
            SELECT CodigoCliente, RazaoSocial, CGC FROM TB_Cliente
        ) AS Cliente ON Funcionario.CodigoCliente = Cliente.CodigoCliente
        LEFT JOIN (
            SELECT CodigoCliente, CodigoCentroCusto, NomeCentroCusto, Endereco FROM TB_CentroCusto
        ) AS Centro ON Funcionario.CodigoCliente = Centro.CodigoCliente AND
                    Funcionario.CodigoCentroCusto = Centro.CodigoCentroCusto
        {where_sql}
    """

    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df
