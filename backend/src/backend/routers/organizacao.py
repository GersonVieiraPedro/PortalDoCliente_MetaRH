from http import HTTPStatus
import json
from typing import List
from backend.TabelasLocais import  limpar_dataframe
from fastapi import APIRouter
from fastapi import HTTPException, Depends, Body
import pandas as pd
from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from ..models import TB_Usuarios
from ..schema import (Organizacao)
from ..database import AtivarSession, TB_Cliente, TB_Persons
from ..security import Criar_Hash, Criar_Token_Acesso, UsuarioAtual, Verificar_Senha


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
    IDOrganizacao: str = None,
    CNPJ: list[str] = None
):

    try:
        # Usando o gerenciador de contexto 'with' para abrir o arquivo corretamente
        with open("src/Tabelas/person.json", "r") as tabela_file:
            tb_person = pd.read_json(tabela_file, dtype={"primary_email": str, 'Id da Organização': str})

        # Filtrando os dados de acordo com IDOrganizacao ou Email, se fornecidos
        if IDOrganizacao and Email:
            # Filtra linhas que correspondem a IDOrganizacao ou Email
            tb_person = tb_person[
                (tb_person["Id da Organização"].str.contains(IDOrganizacao, na=False, case=False)) |
                (tb_person["primary_email"].str.contains(Email, na=False, case=False))
            ]
        elif Email:
            # Filtra apenas pelo Email
            tb_person = tb_person[tb_person["primary_email"].str.contains(Email, na=False, case=False)]
        elif IDOrganizacao:
            # Filtra apenas pelo ID da Organização
            tb_person = tb_person[tb_person["Id da Organização"].str.contains(IDOrganizacao, na=False, case=False)]

        # Verifica se a tabela está vazia
        if tb_person.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail={"status": "Erro", "mensagem": "Nenhum registro encontrado!"}
            )

        tb_person = tb_person[["id", "Proprietário", "Nome", "org_name", "primary_email", "Id da Organização"]]
        tb_person["Id da Organização"] = tb_person["Id da Organização"].astype(float).astype(int).astype(str)

        with open("src/Tabelas/organizations.json", "r") as tabela_file:
            tb_organizations = pd.read_json(tabela_file, dtype={'id': str})

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

        tb_organizations["id"] = tb_organizations["id"].astype(float).astype(int).astype(str)

        tabela = tb_person.set_index("Id da Organização").join(tb_organizations.set_index('id'), on="Id da Organização", rsuffix="_org")

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