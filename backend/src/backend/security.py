from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import AtivarSession
from zoneinfo import ZoneInfo
import jwt
from jwt.exceptions import PyJWKError, ExpiredSignatureError
from pwdlib import PasswordHash
from .models import TB_Usuarios
from .settings import Settings





pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

Sett = Settings()


def Criar_Hash(Senha: str):
     return pwd_context.hash(Senha)

def Verificar_Senha(Senha: str, Hash: str):
     return pwd_context.verify(Senha, Hash)

def Criar_Token_Acesso(data: dict):
    to_encode = data.copy()
    timezone_brasilia = ZoneInfo("America/Sao_Paulo")
    # Define a expiração do token
    expire = datetime.now(tz=timezone_brasilia) + timedelta(minutes=Sett.EXPIRES_IN_MINUTES)
    #datetime.now(tz=ZoneInfo("Etc/UTC"))p

    to_encode.update({"exp": expire})

    # Adiciona o tempo de expiração ao payload do token
    encoded_jwt = jwt.encode(to_encode, Sett.SECRET_KEY, algorithm=Sett.ALGORITHM)
 

    return encoded_jwt

def UsuarioAtual(
    session: Session = Depends(AtivarSession),
    token: str = Depends(oauth2_scheme)
    ):

    credencial_invalidas = HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, Sett.SECRET_KEY, algorithms=[Sett.ALGORITHM])
        email = payload.get("email")
        sub = payload.get("sub")
        if not email:
            raise credencial_invalidas
        if sub !="Admin":
            raise credencial_invalidas
        

    except ExpiredSignatureError:
        raise credencial_invalidas

    except PyJWKError:
        raise credencial_invalidas
    
    user = session.scalar(
        select(TB_Usuarios).where(TB_Usuarios.Email == email)
    )

    if not user:
        raise credencial_invalidas
    
    return user