from http import HTTPStatus
import json
from typing import List, Optional, Literal
from backend.TabelasGI import TabelaFuncionarios
from backend.TabelasLocais import  limpar_dataframe
from fastapi import APIRouter, HTTPException, Depends, Body
import pandas as pd
from sqlalchemy.orm import Session
from ..schema import (Organizacao)
from ..database import AtivarSession, TB_Cliente
from ..security import UsuarioAtual


router = APIRouter(prefix="/organizacao", tags=["Organização"])


@router.post("/clientes/")
def Tabela_Clientes_GI(
    session: Session = Depends(AtivarSession),   
    user=Depends(UsuarioAtual),
    listaOrganizao: Organizacao = Body(...) 
    ):

    tabela = TB_Cliente(listaOrganizao.CodigoCliente, listaOrganizao.CNPJ)

    if tabela.empty:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"status": "Erro", "mensagem": "Nenhum registro encontrado!"}
        )
    

    return {
        "status": "Sucesso",
        "mensagem": "Registros encontrados!",
        "tabela": tabela.to_dict(orient="records")
    }
     



@router.post("/pessoas/")
def Tabela_Person_Pipedrive(
    IDOrganizacao: str = None,
    Email: str = None,
):
    try:
        # Usando o gerenciador de contexto 'with' para abrir o arquivo corretamente
        with open("src/Tabelas/person.json", "r") as tabela_file:
            tabela = pd.read_json(tabela_file, dtype={"primary_email": str, 'Id da Organização': str})

        # Filtrando os dados de acordo com IDOrganizacao ou Email, se fornecidos
        if IDOrganizacao and Email:
            # Filtra linhas que correspondem a IDOrganizacao ou Email
            tabela = tabela[
                (tabela["Id da Organização"].str.contains(IDOrganizacao, na=False, case=False)) |
                (tabela["primary_email"].str.contains(Email, na=False, case=False))
            ]
        elif Email:
            # Filtra apenas pelo Email
            tabela = tabela[tabela["primary_email"].str.contains(Email, na=False, case=False)]
        elif IDOrganizacao:
            # Filtra apenas pelo ID da Organização
            tabela = tabela[tabela["Id da Organização"].str.contains(IDOrganizacao, na=False, case=False)]

        # Verifica se a tabela está vazia
        if tabela.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail={"status": "Erro", "mensagem": "Nenhum registro encontrado!"}
            )


        tabela  = limpar_dataframe(tabela)

        return {
            "status": "Sucesso",
            "mensagem": "Registros encontrados!",
            "tabela": tabela.to_dict(orient="records")
        }
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "Erro", "mensagem": "Arquivo não encontrado!"}
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "Erro", "mensagem": "Erro ao ler o arquivo JSON!"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "Erro", "mensagem": str(e)}
        )


@router.post("/empressas/")
def Dados_Empresas_Que_Tenho_Acesso(    
    Email: str = None,
    IDOrganizacao: int = None,
    CNPJ: list[str] = None
):
    try:
        # Lê o arquivo de pessoas em formato JSON
        with open("src/Tabelas/person.json", "r") as tabela_file:
            tb_person = pd.read_json(
                tabela_file, 
                dtype={"primary_email": str, 'Id da Organização': str}
            )

                # Lê o arquivo de organizações
        with open("src/Tabelas/organizations.json", "r") as tabela_file:
            tb_organizations = pd.read_json(
                tabela_file, 
                dtype={'id': str}
            )

        # Seleciona as colunas relevantes
        tb_person = tb_person[[
            "id", 
            "Proprietário", 
            "Nome", 
            "org_name", 
            "primary_email", 
            "Id da Organização"
        ]]

        # Seleciona as colunas relevantes da organização
        tb_organizations = tb_organizations[[
            "id", 
            "Nome", 
            "Data de Criação da Organização", 
            "Razão Social", 
            "CNPJ", 
            "Grupo Econômico", 
            "Status da Organização", 
            "ID Selecty", 
            "COD Contrato G.I", 
            "Primeiro Faturamento", 
            "Último Faturamento"
        ]]

        # Cria uma nova coluna duplicando a 'id' para 'Id da Pessoa'
        #tb_person['Id da Pessoa'] = tb_person['id']


        # Converte a coluna "Id da Organização" com segurança (aceita nulos)
        tb_person["Id da Organização"] = (
            pd.to_numeric(tb_person["Id da Organização"], errors='coerce')
            .astype("Int64")  # tipo inteiro que aceita NaN
            #.astype(str)      # converte para string
        )

        # Converte a coluna 'id' com segurança
        tb_organizations["id"] = (
            pd.to_numeric(tb_organizations["id"], errors='coerce')
            .astype("Int64")
            #.astype(str)
        )

        # Junta os dois DataFrames pela chave "Id da Organização" / "id"
        tabela = tb_person.set_index("Id da Organização").join(
            tb_organizations.set_index('id'), 
            on="Id da Organização", 
            rsuffix="_org"
        ).reset_index() #para voltar o index original 

        # Corrige a tentativa de renomeação da coluna
        #tabela = tabela.rename(columns={'id': 'Id da Organização'})  # (Obs: essa linha parece desnecessária agora)

        # Aplica filtros se Email e/ou IDOrganizacao forem fornecidos
        if IDOrganizacao and Email:
            tabela = tabela[
                (tabela["Id da Organização"] == int(IDOrganizacao)) |
                (tabela["primary_email"].str.contains(Email, na=False, case=False))
            ]
        elif Email:
            tabela = tabela[
                tabela["primary_email"].str.contains(Email, na=False, case=False)
            ]
        elif IDOrganizacao:
            tabela = tabela[
                tabela["Id da Organização"] == int(IDOrganizacao)
            ]

        # Se não houver resultados após o filtro
        if tabela.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail={"status": "Erro", "mensagem": "Nenhum registro encontrado!"}
            )

        # Limpa o DataFrame (supondo que você tenha essa função definida)
        tabela = limpar_dataframe(tabela)

        # Retorna os dados convertidos em dicionário
        return {
            "status": "Sucesso",
            "mensagem": "Registros encontrados!",
            "tabela": tabela.to_dict(orient="records")
        }
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "Erro", "mensagem": "Arquivo não encontrado!"}
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "Erro", "mensagem": "Erro ao ler o arquivo JSON!"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "Erro", "mensagem": str(e)}
        )
    
@router.post('/Funcionarios')
def Funcionarios(
    Ativo: Literal["Sim", "Não", "Tudo"] = "Tudo",
    CNPJ: Optional[List[str]] | None = None,
    CodigoCliente: Optional[List[int]] | None = None,
):
    # Chamada correta com base nos parâmetros
    resultado = TabelaFuncionarios(CNPJ=CNPJ, CodigoCliente=CodigoCliente, Ativo=Ativo)

    if not resultado.empty:
        return {
            "status": "Sucesso",
            "mensagem": "Registros encontrados!",
            "tabela": resultado.to_dict(orient="records")
        }
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"status": "Erro", "mensagem": "Nenhum registro encontrado"}
        )


 