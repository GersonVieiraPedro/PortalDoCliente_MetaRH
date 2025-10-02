from http import HTTPStatus
from backend.database import AtivarSession
from backend.models import TB_ISS
from backend.TabelasGI import TabelaContrato
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
import pandas as pd


router = APIRouter(prefix='/simulacoes', tags=['Simulações'])

@router.get('/iss',status_code=HTTPStatus.OK)
def Tabela_ISS(session=Depends(AtivarSession)):
    query = select(TB_ISS)
    ISS = session.scalars(query).all()
    return ISS



@router.post('/contratos-ativos', status_code=HTTPStatus.OK)
def Contratos_Ativos(CodigoCliente: list[int]):
    contratos = TabelaContrato(CodigoCliente=CodigoCliente)

    return contratos