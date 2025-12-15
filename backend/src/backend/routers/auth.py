from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.future import select
from ..models import TB_Usuarios
from ..schema import Token
from ..database import AtivarSession
from ..security import Criar_Token_Acesso, UsuarioAtual, Verificar_Senha
from ..utils import get_logger
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("auth.login")

# -----------------------------
# OAuth2 para Swagger/OpenAPI
# -----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # deve bater com o path do login

# -----------------------------
# ROTA DE LOGIN
# -----------------------------
@router.post("/token/", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(AtivarSession)
):
    """
    Faz login do usuário e retorna JWT de acesso.
    Funciona com Swagger/Authorize.
    """
    try:
        logger.info("Tentativa de login", extra={"email": form_data.username})

        # 1️⃣ Busca usuário
        usuario_db = session.scalar(
            select(TB_Usuarios).where(TB_Usuarios.Email == form_data.username)
        )

        credenciais_invalidas = HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Usuário ou senha inválidos"
        )

        if not usuario_db:
            logger.warning("Login falhou: usuário não encontrado", extra={"email": form_data.username})
            raise credenciais_invalidas

        # 2️⃣ Valida senha
        if not Verificar_Senha(form_data.password, usuario_db.Senha):
            logger.warning("Login falhou: senha inválida", extra={"email": form_data.username, "user_id": usuario_db.ID})
            raise credenciais_invalidas

        # 3️⃣ Gera token
        access_token = Criar_Token_Acesso(data={
            "sub": str(usuario_db.ID),
            "nome": usuario_db.Nome,
            "email": usuario_db.Email,
            "tipo": usuario_db.TipoAcesso
        })

        logger.info("Login realizado com sucesso", extra={"user_id": usuario_db.ID, "email": usuario_db.Email})

        return {"access_token": access_token, "token_type": "Bearer"}

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Erro inesperado durante o login", extra={"email": form_data.username})
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar o login"
        )

# -----------------------------
# ROTA DE REFRESH TOKEN
# -----------------------------
@router.post("/refresh_token/", response_model=Token)
def refresh_token(usuario: TB_Usuarios = Depends(UsuarioAtual)):
    """
    Gera um novo token de acesso para o usuário autenticado
    """
    new_access_token = Criar_Token_Acesso(data={
        "sub": str(usuario.ID),
        "nome": usuario.Nome,
        "email": usuario.Email,
        "tipo": usuario.TipoAcesso
    })
    return {"access_token": new_access_token, "token_type": "Bearer"}

# -----------------------------
# ROTA DE VALIDAÇÃO DE TOKEN
# -----------------------------
@router.post("/validate_token/")
def validate_token(token: str = Depends(oauth2_scheme)):
    """
    Valida um JWT enviado pelo frontend ou Swagger
    """
    from ..settings import Settings
    Sett = Settings()
    try:
        payload = jwt.decode(token, Sett.SECRET_KEY, algorithms=[Sett.ALGORITHM])
        return {"valid": True, "sub": payload.get("sub"), "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expirado"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Token inválido"}
