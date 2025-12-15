from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
import jwt
from jwt.exceptions import ExpiredSignatureError

from pwdlib import PasswordHash

from .database import AtivarSession
from .models import TB_Usuarios
from .settings import Settings


# -------------------------------------------------
# CONFIGURAÇÕES GERAIS
# -------------------------------------------------

# Contexto de hash de senha (recomendado)
pwd_context = PasswordHash.recommended()

# OAuth2 padrão (usado pelo FastAPI para extrair o token do header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Carrega configurações (SECRET_KEY, ALGORITHM, EXPIRES_IN_MINUTES)
Sett = Settings()


# -------------------------------------------------
# FUNÇÕES DE SENHA
# -------------------------------------------------

def Criar_Hash(senha: str) -> str:
    """
    Gera hash seguro da senha.
    """
    return pwd_context.hash(senha)


def Verificar_Senha(senha: str, hash_salvo: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash salvo.
    """
    return pwd_context.verify(senha, hash_salvo)


# -------------------------------------------------
# CRIAÇÃO DO TOKEN JWT
# -------------------------------------------------

def Criar_Token_Acesso(data: dict) -> str:
    """
    Cria token JWT de acesso.
    O campo 'sub' deve conter SEMPRE o ID do usuário.
    """
    to_encode = data.copy()

    # Define timezone do Brasil
    timezone_brasilia = ZoneInfo("America/Sao_Paulo")

    # Calcula expiração
    expire = datetime.now(tz=timezone_brasilia) + timedelta(
        minutes=Sett.EXPIRES_IN_MINUTES
    )

    # Adiciona expiração ao payload
    to_encode.update({"exp": expire})

    # Gera o token
    encoded_jwt = jwt.encode(
        to_encode,
        Sett.SECRET_KEY,
        algorithm=Sett.ALGORITHM
    )

    return encoded_jwt


# -------------------------------------------------
# DEPENDÊNCIA: USUÁRIO ATUAL (QUALQUER USUÁRIO LOGADO)
# -------------------------------------------------

def UsuarioAtual(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(AtivarSession),
):
    """
    Resolve o usuário autenticado a partir do token JWT.
    Usa EXCLUSIVAMENTE o campo 'sub' como identidade.
    """

    credenciais_invalidas = HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica o token
        payload = jwt.decode(
            token,
            Sett.SECRET_KEY,
            algorithms=[Sett.ALGORITHM],
        )

        # O 'sub' é o ID do usuário
        user_id = payload.get("sub")

        if not user_id:
            raise credenciais_invalidas

        user_id = int(user_id)

    except ExpiredSignatureError:
        # Token expirado
        raise credenciais_invalidas

    except Exception:
        # Qualquer outro erro de token
        raise credenciais_invalidas

    # Busca o usuário pela chave primária
    usuario = session.get(TB_Usuarios, user_id)

    if not usuario:
        raise credenciais_invalidas

    return usuario


# -------------------------------------------------
# DEPENDÊNCIA: USUÁRIO ATUAL (APENAS ADMIN)
# -------------------------------------------------

def UsuarioAtualAdmin(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(AtivarSession),
):
    """
    Resolve o usuário autenticado e valida se é ADMIN.
    """

    credenciais_invalidas = HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            Sett.SECRET_KEY,
            algorithms=[Sett.ALGORITHM],
        )

        user_id = payload.get("sub")
        tipo = payload.get("tipo")

        if not user_id or tipo != "Admin":
            raise credenciais_invalidas

        user_id = int(user_id)

    except ExpiredSignatureError:
        raise credenciais_invalidas

    except Exception:
        raise credenciais_invalidas

    usuario = session.get(TB_Usuarios, user_id)

    if not usuario:
        raise credenciais_invalidas

    return usuario
