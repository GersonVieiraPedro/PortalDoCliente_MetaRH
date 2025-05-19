from http import HTTPStatus
from typing import List
from backend.database import AtivarSession
from backend.models import TB_Usuarios, TB_Admissao
from backend.schema import AdmissaoSchema, Resposta
from fastapi import APIRouter
from fastapi import HTTPException, Depends, Body
from sqlalchemy import String
from sqlalchemy.future import select


router = APIRouter(prefix='/requisicoes', tags=['Requisições'])


@router.post('/Admissao/Cadastro', status_code=HTTPStatus.CREATED, response_model=Resposta)
def Cadastrar_Admissao(
    Email: str,
    Admissao: AdmissaoSchema,
    Session = Depends(AtivarSession)
):
    # Verifica se o usuário já existe
    UsuarioDB = Session.scalar(
        select(TB_Usuarios).where(TB_Usuarios.Email == Email)
    )

    print(UsuarioDB)
    print(Admissao)
    
    if(UsuarioDB == None):
        return Resposta(status='Erro', mensagem='Usúario não cadastrado')
    else:
        Cadastro = TB_Admissao(
            TipoVaga= Admissao.TipoVaga,
            Cargo= Admissao.Cargo,
            CentroCusto= Admissao.CentroCusto,
            SetorTrabalho= Admissao.SetorTrabalho,
            ModalidadeTrabalho= Admissao.ModalidadeTrabalho,
            MotivoContratacao= Admissao.MotivoContratacao,
            EscalaTrabalho= Admissao.EscalaTrabalho,
            LocalTrabalho= Admissao.LocalTrabalho,
            Salario= Admissao.Salario,
            DescricaoCargo= Admissao.DescricaoCargo,
            PrecisaEPI= Admissao.PrecisaEPI or None,
            DescricaoEPI= Admissao.DescricaoEPI or None,
            NomeSubstituido= Admissao.NomeSubstituido or None,
            CPFSubstituido= Admissao.CPFSubstituido or None,
            MotivoSubstituido= Admissao.MotivoSubstituido or None,
            NomeResponsavelRH= Admissao.NomeResponsavelRH,
            EmailResponsavelRH= Admissao.EmailResponsavelRH,
            TelefoneResponsavelRH= Admissao.TelefoneResponsavelRH,
            NomeGestorPonto= Admissao.NomeGestorPonto,
            EmailGestorPonto= Admissao.EmailGestorPonto,
            TelefoneGestorPonto= Admissao.TelefoneGestorPonto,
            NomePessoaPrimeiroDia= Admissao.NomePessoaPrimeiroDia,
            DepartamentoPrimeiroDia= Admissao.DepartamentoPrimeiroDia,
            HorarioPrimeiroDia= Admissao.HorarioPrimeiroDia,
        )     
        Cadastro.ID_Usuario = UsuarioDB.ID

        Session.add(Cadastro)
        Session.commit()

        return Resposta(status='Sucesso', mensagem='Recebemos sua solicitação de admissão')