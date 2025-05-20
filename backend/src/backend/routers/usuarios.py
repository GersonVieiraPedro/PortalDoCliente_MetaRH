
from http import HTTPStatus
from typing import List
from fastapi import APIRouter
from fastapi import HTTPException, Depends, Body
from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from ..models import TB_Usuarios
from ..schema import AtualizarUsuariosLista, ListaUsuarios, Resposta, UsuarioPublico, UsuarioSchema, UsarioLogin, Token, AtualizarUsuarios, RespostaLista
from ..database import AtivarSession
from ..security import Criar_Hash, Criar_Token_Acesso, UsuarioAtual, Verificar_Senha


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


#rota para criar o usuario no banco de dados 
@router.post('/cadastrar', status_code=HTTPStatus.CREATED, response_model=Resposta)
def Cadastrar_Usuario(
    usuario: UsuarioSchema, session = Depends(AtivarSession)
):
   # Verifica se o usuário já existe
    UsuarioDB = session.scalar(
        select(TB_Usuarios).where(TB_Usuarios.Email == usuario.email)
    )

    # Se o usuário já estiver cadastrado, retorna um erro
    if UsuarioDB:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail={"status": "Erro", "mensagem": "Usuário já cadastrado!"}
        )

    # Cria novo usuário
    UsuarioDB = TB_Usuarios(
        Nome=usuario.nome,
        Senha=Criar_Hash(usuario.senha),
        Email=usuario.email,
        CNPJ=usuario.cnpj
    )

    session.add(UsuarioDB)
    session.commit()

    
    return Resposta(status="Sucesso", mensagem="Usuário criado com sucesso!")


@router.post('/login', status_code=HTTPStatus.OK ,response_model=Token)
def Entrar(usuario: UsarioLogin, session = Depends(AtivarSession)):

    #Verifica se o usuario já existe
    UsuarioDB = session.scalar(
        select(TB_Usuarios).where(TB_Usuarios.Email == usuario.email)
    )

    if not UsuarioDB or not Verificar_Senha(usuario.senha, UsuarioDB.Senha)  :
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail={
            "titulo": "Erro",
            "msg": "Usuário ou senha inválidos!"
        })
    
    access_token = Criar_Token_Acesso(data={"nome": UsuarioDB.Nome , "email": usuario.email, "sub": UsuarioDB.TipoAcesso})

    return {"access_token": access_token, "token_type": "Bearer"}



@router.get('/listar', status_code=HTTPStatus.OK, response_model=ListaUsuarios)
def Listar_Usuarios(
    Limite: int = 100,
    Inicio: int = 0,
    TipoFiltro: str = None,
    Filtro: str = None,
    session=Depends(AtivarSession)
   # usuario=Depends(UsuarioAtual)
):
    query = select(TB_Usuarios)

    if TipoFiltro == "Geral":
        query = query.filter(
            TB_Usuarios.Nome.contains(Filtro) |
            TB_Usuarios.CNPJ.contains(Filtro) |
            TB_Usuarios.Email.contains(Filtro) |
            TB_Usuarios.DataCadastro.cast(String).contains(Filtro) |
            TB_Usuarios.ID.cast(String).contains(Filtro)
        )
    elif TipoFiltro == "Nome":
        query = query.filter(TB_Usuarios.Nome.contains(Filtro))
    elif TipoFiltro == "CNPJ":
        query = query.filter(TB_Usuarios.CNPJ.contains(Filtro))
    elif TipoFiltro == "Email":
        query = query.filter(TB_Usuarios.Email.contains(Filtro))
    elif TipoFiltro == "Data":
        query = query.filter(TB_Usuarios.DataCadastro.cast(String).contains(Filtro))
    elif TipoFiltro == "ID":
        query = query.filter(TB_Usuarios.ID.cast(String).contains(Filtro))

    # Paginação 
    query = query.offset(Inicio).limit(Limite)

    # Executa e coleta os resultados
    usuarios = session.scalars(query).all()

    return {'usuarios': usuarios}



    
@router.patch('/atualizar/lista', response_model=List[RespostaLista])
def Lista_De_Usuarios(
    session= Depends(AtivarSession),
    user=Depends(UsuarioAtual),
    listaUsuarios: List[AtualizarUsuariosLista]= Body(...)
):
    Lista = []

    for usuario in listaUsuarios:

        UsuarioDB = session.scalar(
            select(TB_Usuarios).where(TB_Usuarios.ID == usuario.ID)
        )

        if not UsuarioDB:
            Lista.append({'ID': usuario.ID, 
                          'status': 'Erro', 
                          'mensagem': 'Usuário não encontrado'
                        })
       
        else:
            Lista.append({'ID': usuario.ID, 
                          'status': 'Sucesso',
                          'mensagem': 'Usuário atualizado'
                        })

            for key, value in usuario.model_dump(exclude={"ID"}, exclude_unset=True).items():
                setattr(UsuarioDB, key, value)

            session.add(UsuarioDB)     

    session.commit()

    return Lista




@router.patch('/atualizar/{Usuario_ID}', response_model=UsuarioPublico)
def Usuario_ID(
    Usuario_ID: int, 
    session= Depends(AtivarSession),
    user=Depends(UsuarioAtual),
    usuario: AtualizarUsuarios = Body(...)
):
    UsuarioDB = session.scalar(
        select(TB_Usuarios).where(TB_Usuarios.ID == Usuario_ID)
    )

    if not UsuarioDB:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
        )
    
    for key, value in usuario.model_dump(exclude_unset=True).items():
        setattr(UsuarioDB, key, value)

    session.add(UsuarioDB)
    session.commit()
    session.refresh(UsuarioDB)

    return UsuarioDB        

