import pyodbc
import pandas as pd
import numpy as np
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

def TabelaFuncionarios(CodigoCliente=None, CNPJ=None, Ativo: str = "Tudo"):
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
            Funcionario.CodigoFuncionario,
            Funcionario.CodigoContrato,
            TipoFat,
            Funcionario.CodigoCliente,
            Cliente.RazaoSocial,
            Cliente.CGC,
            Funcionario.CodigoCentroCusto,
            NomeCentroCusto,
            Centro.Endereco,
            Funcionario.CodigoFuncao,
            Func.Descricao AS Funcao,
            Nome,
            DataNascimento,
            DataAdmissao,
            DataDemissao,
            Sexo,
            Salario,
            EstadoCivil,
            Nacionalidade,
            CidadeResid,
            CASE
                WHEN DataAdmissao <= GETDATE() AND DataDemissao IS NULL
                THEN 'Sim'
                ELSE 'Não'
            END AS Ativo
        FROM TB_Funcionario AS Funcionario
        LEFT JOIN TB_Funcao AS Func ON Funcionario.CodigoFuncao = Func.CodigoFuncao
        LEFT JOIN TB_Cliente AS Cliente ON Funcionario.CodigoCliente = Cliente.CodigoCliente
        LEFT JOIN  TB_CentroCusto AS Centro ON 
                    Funcionario.CodigoCliente = Centro.CodigoCliente AND
                    Funcionario.CodigoCentroCusto = Centro.CodigoCentroCusto
        {where_sql}
    """

    df = pd.read_sql(sql, conn, params=params)

    df["Salario"] = df["Salario"].astype(float).round(2)




    conn.close()
    #Aplica filtro só depois que trouxe do banco
    if Ativo in ("Sim", "Não"):
        df = df[df["Ativo"] == Ativo]

    return df

def TabelaContrato(CodigoCliente=None):
    conn = Conectar()

    where_clause = "WHERE Ativo = 1"
    params = []
    if CodigoCliente:
        placeholders = ','.join('?' for _ in CodigoCliente)
        where_clause += f" AND CodigoCliente IN ({placeholders})"
        params.extend(CodigoCliente)

    sql = f"""
    SELECT
        CodigoContrato,
        TipoFat AS 'TipoFaturamento',
        CodigoCliente,
        RazaoSocial,
        DataIniContrato,
        DataFimContrato,
        DataUltFat,
        TaxaFatur,
        Ativo
    FROM TB_Contrato
    {where_clause}
    """

    df = pd.read_sql(sql, conn, params=params, dtype={"RazaoSocial": str})
    conn.close()

    # Converte os tipos problemáticos
    df = df.replace({np.nan: None})  # None no lugar de NaN
    df = df.astype(object)  # força tipos nativos
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: int(x) if isinstance(x, (np.integer,)) else
                      float(x) if isinstance(x, (np.floating,)) else
                      x.isoformat() if isinstance(x, (pd.Timestamp,)) else
                      x
        )


    return df.to_dict(orient="records")

