from typing import List, Optional
import pyodbc
import pandas as pd
import numpy as np
import os
from .settings import Settings

def Conectar():

    SERVER = Settings().SERVER_GI or os.environ.get('SERVER_GI')
    DATABASE = Settings().DATABASE_GI or os.environ.get('DATABASE_GI')
    USER = Settings().USER_GI or os.environ.get('USER_GI')
    PASSWORD = Settings().PASSWORD_GI or os.environ.get('PASSWORD_GI')

    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USER};"
        f"PWD={PASSWORD};"
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
            Funcionario.CodigoHorario,
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
            tpJornada,
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

def TabelaBeneficios(CodigoFuncionario: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Retorna os benefícios ativos de um ou mais funcionários.
    
    Parâmetro:
        CodigoFuncionario: Lista de strings (ex: ['72542', '12345']) ou None para todos
    """
    conn = Conectar()
    
    try:
        # Montagem dinâmica e segura do WHERE
        where_parts = []
        params = []

        if CodigoFuncionario:
            # Garante que é lista e remove duplicatas/None
            codigos = [str(c).strip() for c in CodigoFuncionario if c]
            if not codigos:
                return pd.DataFrame()  # retorna vazio se não tiver códigos válidos
            
            placeholders = ','.join(['?' for _ in codigos])
            where_parts.append(f"F.CodigoFuncionario IN ({placeholders})")
            params.extend(codigos)

        where_sql = ' WHERE ' + ' AND '.join(where_parts) if where_parts else ''

        sql = f"""
            SELECT 
                F.CodigoFuncionario,
                F.CodigoEmpresa,
                F.CodigoFilial,
                FB.CodigoBeneficio,
                B.Descricao          AS DescricaoBeneficio,
                FB.TipoBeneficio,
                FB.Quantidade,
                B.ValorCusto,
                B.TipoDesconto,
                B.Inativo            AS BeneficioInativo,
                F.Nome               AS NomeFuncionario
                
            FROM TB_Funcionario AS F
            LEFT JOIN TB_FuncionarioBeneficio AS FB
                ON FB.CodigoFuncionario = F.CodigoFuncionario
                AND FB.CodigoEmpresa    = F.CodigoEmpresa
                AND FB.CodigoFilial     = F.CodigoFilial
            LEFT JOIN TB_Beneficio AS B
                ON B.CodigoBeneficio = FB.CodigoBeneficio
                AND B.Tipo = FB.TipoBeneficio
                AND B.Inativo = 0      
            {where_sql}
            AND DataDemissao IS NULL
            ORDER BY F.CodigoFuncionario DESC
        """

        df = pd.read_sql(sql, conn, params=params)
        
        # Tratamento pós-leitura (opcional, mas muito útil)
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
        df['ValorCusto'] = pd.to_numeric(df['ValorCusto'], errors='coerce').fillna(0)

        return df

    except Exception as e:
        print(f"Erro ao consultar benefícios: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()

def TabelaHorario() -> pd.DataFrame:
    """
    Retorna os Hoararios ativos de um ou mais funcionários.
    
    """
    conn = Conectar()
    
    try:

        sql = f""" 
            SELECT DISTINCT
                CodigoHorario,
                Descricao,
                EscalaDataInicio,
                EscalaDataFim,
                QtdeHorasMes
            FROM TB_Horario
            WHERE 
                Inativo = 0
            ORDER BY Descricao DESC
        """

        df = pd.read_sql(sql, conn)
        

        return df

    except Exception as e:
        print(f"Erro ao consultar horarios: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()



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

def TB_Cliente(CodigoCliente: str, CNPJ: list[str]):
    
    SERVER = Settings().SERVER_GI or os.environ.get('SERVER_GI')
    DATABASE = Settings().DATABASE_GI or os.environ.get('DATABASE_GI')
    USER = Settings().USER_GI or os.environ.get('USER_GI')
    PASSWORD = Settings().PASSWORD_GI or os.environ.get('PASSWORD_GI')

    # Conexão com o banco de dados utilizando ODBC
    StrCnxn = "DRIVER={ODBC Driver 17 for SQL Server};"+f"""SERVER={SERVER};DATABASE={DATABASE};UID={USER};PWD={PASSWORD}"""
    
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

