
from http import HTTPStatus
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from ..models import TB_Usuarios
from ..schema import Token
from ..database import AtivarSession
from ..security import Criar_Token_Acesso, UsuarioAtual, Verificar_Senha


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/token/', response_model=Token)
def login_for_acess_token(
     form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(AtivarSession)
):
    UsuarioDB = session.scalar(
        select(TB_Usuarios).where(TB_Usuarios.Email == form_data.username)
    )
    if not UsuarioDB or not Verificar_Senha(form_data.password, UsuarioDB.Senha):
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")
    
    access_token = Criar_Token_Acesso(data={"nome": UsuarioDB.Nome , "email": UsuarioDB.Email, "sub": UsuarioDB.TipoAcesso})

    return {"access_token": access_token, "token_type": "Bearer"}


@router.post('/refresh_token/', response_model=Token)
def refresh_token(
    user: TB_Usuarios = Depends(UsuarioAtual),
):
    new_acess_token = Criar_Token_Acesso(data={"nome": user.Nome , "email": user.Email, "sub": user.TipoAcesso})
    return {"access_token": new_acess_token, "token_type": "Bearer"}
