import os
import logging
from io import BytesIO
from contextlib import asynccontextmanager
from fastapi import APIRouter  # type: ignore
from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from azure.storage.blob import ContentSettings
from PIL import Image
from dotenv import load_dotenv

# ============================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================
# Este formato padroniza os logs e é compatível com o Azure
# Os logs de nível INFO e ERROR aparecerão no portal do Azure (App Service)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("aruze_storage")


# ============================================================
# CARREGAMENTO DE VARIÁVEIS DE AMBIENTE
# ============================================================
# Durante desenvolvimento local, o .env será carregado.
# No Azure, as variáveis são definidas no App Service (Configurações de Aplicativo).
load_dotenv()

AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME") or os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY") or os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
CONTAINER_NAME = os.getenv("CONTAINER_NAME") or os.environ.get("CONTAINER_NAME")

# ============================================================
# VALIDAÇÃO E LOG INICIAL
# ============================================================
logger.info("Iniciando módulo de integração com Azure Blob Storage...")
logger.debug(f"AZURE_STORAGE_ACCOUNT_NAME={AZURE_STORAGE_ACCOUNT_NAME!r}")
logger.debug(f"AZURE_STORAGE_ACCOUNT_KEY existe? {'Sim' if AZURE_STORAGE_ACCOUNT_KEY else 'Não'}")
logger.debug(f"CONTAINER_NAME={CONTAINER_NAME!r}")

if not all([AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_ACCOUNT_KEY, CONTAINER_NAME]):
    logger.error("Variáveis de ambiente ausentes! Verifique as Configurações do Aplicativo no Azure Portal.")
    raise EnvironmentError(
        f"[ERRO] Variáveis ausentes:\n"
        f"AZURE_STORAGE_ACCOUNT_NAME={AZURE_STORAGE_ACCOUNT_NAME!r}\n"
        f"AZURE_STORAGE_ACCOUNT_KEY={'sim' if AZURE_STORAGE_ACCOUNT_KEY else 'não'}\n"
        f"CONTAINER_NAME={CONTAINER_NAME!r}"
    )

# ============================================================
# STRING DE CONEXÃO COM O AZURE STORAGE ACCOUNT
# ============================================================
connection_string = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={AZURE_STORAGE_ACCOUNT_NAME};"
    f"AccountKey={AZURE_STORAGE_ACCOUNT_KEY};"
    f"EndpointSuffix=core.windows.net"
)

router = APIRouter()


# ============================================================
# CONTEXTO ASSÍNCRONO PARA GERENCIAR O CLIENT DO AZURE
# ============================================================
@asynccontextmanager
async def azure_container():
    """
    Cria e gerencia automaticamente a sessão com o Azure Blob Storage.
    Fecha a conexão após o uso, evitando erros de 'Unclosed client session'.
    """
    try:
        logger.info("Abrindo conexão com o Azure Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(
            conn_str=connection_string,
            connection_timeout=30,
        )

        # Cria o client do container com base no nome configurado
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        logger.info(f"Conectado ao container '{CONTAINER_NAME}' com sucesso.")

        yield container_client

    except Exception as e:
        logger.exception(f"Falha ao conectar ao container '{CONTAINER_NAME}': {e}")
        raise

    finally:
        # Fecha a conexão para evitar vazamento de sessão
        await blob_service_client.close()
        logger.info("Conexão com o Azure Blob encerrada com sucesso.")


# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def convert_to_png(data: bytes) -> bytes:
    """
    Converte qualquer imagem para o formato PNG.
    Isso garante padronização no armazenamento das fotos.
    """
    try:
        image = Image.open(BytesIO(data)).convert("RGBA")
        output = BytesIO()
        image.save(output, format="PNG")
        logger.debug("Imagem convertida para PNG com sucesso.")
        return output.getvalue()
    except Exception as e:
        logger.exception(f"Falha ao converter imagem para PNG: {e}")
        raise


async def image_exists(filename: str, container_client: ContainerClient) -> bool:
    """
    Verifica se o arquivo existe no container Azure.
    Retorna True ou False.
    """
    try:
        logger.info(f"Verificando existência do arquivo: {filename}")
        blob_client = container_client.get_blob_client(filename)
        exists = await blob_client.exists(timeout=30)
        logger.info(f"Arquivo {'existe' if exists else 'não encontrado'}: {filename}")
        return exists
    except Exception as e:
        logger.exception(f"Erro ao verificar existência de {filename}: {e}")
        return False


async def upload_image(filename: str, data: bytes, container_client: ContainerClient):
    """
    Faz upload de uma imagem (PNG/JPEG) para o Azure Blob Storage.
    Retorna a URL pública do arquivo.
    """
    try:
        content_type = (
            "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
        )
        blob_client = container_client.get_blob_client(filename)

        logger.info(f"Iniciando upload da imagem: {filename} ({len(data)} bytes)")
        await blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

        url = await get_image_url(filename)
        logger.info(f"Upload concluído com sucesso. URL: {url}")
        return url
    except Exception as e:
        logger.exception(f"Erro ao fazer upload da imagem {filename}: {e}")
        raise


async def get_image_url(filename: str) -> str:
    """
    Retorna a URL pública do arquivo no Azure Blob.
    """
    url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{filename}"
    logger.debug(f"URL gerada: {url}")
    return url


async def delete_image(filename: str, container_client: ContainerClient):
    """
    Remove uma imagem específica do Azure Blob Storage.
    """
    try:
        logger.info(f"Deletando imagem: {filename}")
        blob_client = container_client.get_blob_client(f"fotos/usuarios/{filename}")
        await blob_client.delete_blob()
        logger.info(f"Imagem deletada com sucesso: {filename}")
    except Exception as e:
        logger.exception(f"Erro ao deletar imagem {filename}: {e}")
        raise


async def list_images(container_client: ContainerClient):
    """
    Lista todos os blobs (arquivos) presentes no container.
    """
    try:
        logger.info("Listando todos os arquivos do container...")
        blob_list = []
        async for blob in container_client.list_blobs():
            blob_list.append(blob.name)
        logger.info(f"{len(blob_list)} arquivos encontrados.")
        return blob_list
    except Exception as e:
        logger.exception(f"Erro ao listar blobs no container: {e}")
        raise


async def upload_pdf(filename: str, data: bytes, container_client: ContainerClient):
    """
    Faz upload de um arquivo PDF para o container Azure.
    Retorna a URL pública do arquivo salvo.
    """
    try:
        logger.info(f"Iniciando upload do PDF: {filename} ({len(data)} bytes)")
        blob_client = container_client.get_blob_client(filename)

        await blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type="application/pdf"),
        )

        url = await get_image_url(filename)
        logger.info(f"PDF salvo com sucesso no Azure: {url}")
        return url
    except Exception as e:
        logger.exception(f"Erro ao fazer upload do PDF {filename}: {e}")
        raise


async def upload_xlsx(filename: str, data: bytes, container_client: ContainerClient):
    """
    Faz upload de um arquivo XLSX para o container Azure.
    Retorna a URL pública do arquivo salvo.
    """
    try:
        logger.info(f"Iniciando upload do XLSX: {filename} ({len(data)} bytes)")
        blob_client = container_client.get_blob_client(filename)

        await blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        )

        url = await get_image_url(filename)
        logger.info(f"XLSX salvo com sucesso no Azure: {url}")
        return url
    except Exception as e:
        logger.exception(f"Erro ao fazer upload do XLSX {filename}: {e}")
        raise
