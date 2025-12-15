import datetime, json, os, logging
from http import HTTPStatus
from typing import Optional, List
from fastapi import APIRouter, Query, UploadFile, File, Form, Depends, Request # type: ignore
from fastapi.responses import HTMLResponse #type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from pydantic import BaseModel, EmailStr # type: ignore
from sqlalchemy.orm import Session
from ..database import AtivarSession
from ..email_utils import enviar_email  # função utilitária que criamos antes
from ..email_templates import render_encerramento_email_jinja
from ..models import TB_Destinatario, DIM_Funcionalidade, DIM_Proprietario, model_dinamico
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL") or os.environ.get("API_BASE_URL")

templates = Jinja2Templates(directory="src/backend/templates/email")

router = APIRouter(prefix="/mensageria", tags=["Mensageria"])

logger = logging.getLogger(__name__)


# --- Modelo Pydantic para dados do e-mail ---
class EmailRequest(BaseModel):
    para: List[EmailStr]                     # destinatários principais (To)
    assunto: str                             # assunto do e-mail
    corpo: str                               # corpo em HTML ou texto simples
    remetente: Optional[EmailStr] = None     # remetente (opcional)
    nome_remetente: Optional[str] = None     # nome exibido no remetente
    copia: Optional[List[EmailStr]] = None   # cópia (Cc)
    copia_oculta: Optional[List[EmailStr]] = None  # cópia oculta (Bcc)

# --- Rota principal para envio de e-mail ---


@router.post("/enviarEmail")
async def enviar_email_router(
    para: str = Form(...),                # string JSON com array de e-mails
    assunto: str = Form(...),
    corpo: str = Form(...),
    copia: Optional[str] = Form(None),    # string JSON opcional
    copia_oculta: Optional[str] = Form(None),
    arquivo: Optional[UploadFile] = File(None),
):

    # Converte strings JSON em listas
    para_list = json.loads(para)
    copia_list = json.loads(copia) if copia else []
    copia_oculta_list = json.loads(copia_oculta) if copia_oculta else []

    arquivo_bytes = await arquivo.read() if arquivo else None
    nome_arquivo = arquivo.filename if arquivo else None

    enviar_email(
        destinatarios=para_list,
        assunto=assunto,
        html_corpo=corpo,
        arquivo_bytes=arquivo_bytes,
        nome_arquivo=nome_arquivo,
        copia=copia_list,
        copia_oculta=copia_oculta_list,
    )

    return {"status": "sucesso", "mensagem": f"E-mail enviado para {', '.join(para_list)}"}






@router.get("/processo", response_class=HTMLResponse)
def processo(
    request: Request,
    id: int = Query(...),        # ID do registro na tabela dinâmica
    a: int = Query(...),         # Ação: 1 = iniciar, 2 = finalizar, 3 = cancelar
    f: int = Query(...),         # ID da funcionalidade
    p: int = Query(...),         # ID do proprietário (usuário)
    session: Session = Depends(AtivarSession)
):
    """
    Rota responsável por controlar o processo de início, finalização e cancelamento
    de uma solicitação. Totalmente comentada e com logs estruturados.
    """

    try:
        agora = datetime.datetime.now()

        # Dicionário para mapear ações a textos legíveis
        acoes = {1: "Iniciado", 2: "Finalizado", 3: "Cancelado"}

        logger.info(
            "Ação recebida",
            extra={"id": id, "acao": a, "funcionalidade_id": f, "proprietario_id": p}
        )

        # 1️ Buscar funcionalidades e proprietário
        funcionalidade = (
            session.query(DIM_Funcionalidade)
            .filter(DIM_Funcionalidade.ID == f)
            .first()
        )
        proprietario = (
            session.query(DIM_Proprietario)
            .filter(DIM_Proprietario.ID == p)
            .first()
        )

        if not funcionalidade:
            logger.error("Funcionalidade não encontrada", extra={"funcionalidade_id": f})
            raise ValueError(f"Funcionalidade com ID {f} não encontrada.")

        if not proprietario:
            logger.error("Proprietário não encontrado", extra={"proprietario_id": p})
            raise ValueError(f"Proprietário com ID {p} não encontrado.")

        logger.info("Funcionalidade e proprietário encontrados")

        # 2️ Carregar modelo dinâmico baseado no nome da tabela
        model = model_dinamico(funcionalidade.Tabela)
        if not model:
            logger.error(
                "Modelo dinâmico não encontrado",
                extra={"tabela": funcionalidade.Tabela}
            )
            raise ValueError(f"Modelo dinâmico para tabela {funcionalidade.Tabela} não encontrado.")

        # 3️ Buscar o registro
        registro = session.query(model).filter(model.ID == id).first()

        if not registro:
            logger.error("Registro não encontrado", extra={"registro_id": id})
            raise ValueError(f"Registro com ID {id} não encontrado.")

        logger.info("Registro carregado com sucesso")

        # ============================================
        # 4️ PROCESSAR AÇÃO DE INÍCIO
        # ============================================
        if a == 1:
            logger.info("Processando ação de início")

            # Verifica se alguém já iniciou
            if registro.IDProprietario:
                logger.warning(
                    "Tentativa de iniciar solicitação já iniciada",
                    extra={"registro_id": id, "proprietario_atual": registro.IDProprietario}
                )
                return templates.TemplateResponse(
                    "em_andamento.html",
                    {"request": request, "mensagem": "Esta solicitação já foi iniciada por outro usuário."}
                )

            registro.IDProprietario = p
            registro.DataInicio = agora
            registro.Status = acoes[a]

            session.commit()

            logger.info("Processo iniciado com sucesso")

            # ============================================
            # 4.5 Enviar E-MAIL DE FINALIZAÇÃO
            # ============================================
            logger.info("Gerando e-mail para proprietário", extra={"email": proprietario.Email})

            mensagem_email = (
                "Sua solicitação foi processada com sucesso,\n"
                "ao concluir a atividade precisa ser finalizada ou cancelada."
            )

            # Monta link base
            link_base = (
                f"{API_BASE_URL}/mensageria/processo"
                f"?id={id}&p={proprietario.ID}&f={funcionalidade.ID}"
            )

            html_final = render_encerramento_email_jinja(
                titulo=f"#{registro.ID:04d} - {funcionalidade.Nome}",
                mensagem=mensagem_email,
                link_cancelar=link_base + "&a=3",
                link_finalizar=link_base + "&a=2"
            )

            enviar_email(
                assunto=f"#{registro.ID:04d} - {funcionalidade.Nome}",
                destinatarios=[proprietario.Email],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )

            logger.info("E-mail enviado com sucesso")

            return templates.TemplateResponse(
                "iniciado.html",
                {"request": request, "acao": a}
            )

        # ============================================
        # 5️ PROCESSAR AÇÃO DE FINALIZAR OU CANCELAR
        # ============================================
        elif a in [2, 3]:
            logger.info("Processando finalização/cancelamento")

            if not registro.IDProprietario:
                logger.error("Registro sem proprietário")
                raise ValueError("Registro não possui proprietário.")

            if registro.IDProprietario != p:
                logger.error(
                    "Proprietário inválido",
                    extra={"esperado": registro.IDProprietario, "recebido": p}
                )
                raise ValueError("Proprietário inválido.")

            if registro.Status != "Iniciado":
                logger.error(
                    "Processo já finalizado ou cancelado",
                    extra={"status_atual": registro.Status}
                )
                raise ValueError("Processo já finalizado ou cancelado.")

            registro.DataConclusao = agora
            registro.Status = acoes[a]

            session.commit()

            logger.info("Processo concluído", extra={"nova_acao": acoes[a]})

    
        return templates.TemplateResponse(
            "sucesso.html",
            {"request": request, "acao": a}
        )

    except Exception as e:
        logger.exception("Erro inesperado durante o processamento da rota")
        return templates.TemplateResponse(
            "erro.html",
            {"request": request}
        )
