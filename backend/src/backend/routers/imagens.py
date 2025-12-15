from http import HTTPStatus
import os
import traceback  # Para logs detalhados de erro
from ..database import AtivarSession
from ..models import TB_Usuarios
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy import select
from ..aruze_storage import (
    convert_to_png,
    delete_image,
    image_exists,
    upload_image,
    upload_pdf,
    azure_container
)

# Define prefixo e tag para o grupo de rotas de imagens
router = APIRouter(prefix="/imagens", tags=["Imagens"])


@router.post("/usuario")
async def create_image(email: str, session=Depends(AtivarSession), file: UploadFile = File(...)):
    """
    Faz upload de uma imagem de perfil de usuário.
    - Busca o usuário no banco de dados pelo e-mail.
    - Converte para PNG se necessário.
    - Faz upload para o Azure Blob Storage usando azure_container().
    """
    try:
        print(f"[LOG] Iniciando upload de imagem de perfil. E-mail recebido: {email}")

        usuario_db = session.scalar(select(TB_Usuarios).where(TB_Usuarios.Email == email))
        if not usuario_db:
            print("[ERRO] Nenhum usuário encontrado com esse e-mail.")
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail={"status": "Erro", "mensagem": "Nenhum registro encontrado"}
            )

        print(f"[LOG] Usuário encontrado: ID={usuario_db.ID}, Nome={usuario_db.Nome}")

        # Lê o conteúdo do arquivo enviado
        content = await file.read()
        _, ext = os.path.splitext(file.filename)
        print(f"[LOG] Arquivo recebido: {file.filename} (extensão: {ext})")

        # Converte para PNG se não for PNG
        if ext.lower() != ".png":
            print(f"[LOG] Convertendo imagem '{file.filename}' para PNG...")
            content = convert_to_png(content)
        else:
            print("[LOG] Imagem já está em formato PNG, nenhuma conversão necessária.")

        file_name = f"fotos/usuarios/{usuario_db.ID}.png"
        print(f"[LOG] Nome final do arquivo no Azure: {file_name}")

        async with azure_container() as container_client:
            print("[LOG] Conexão com Azure Blob Storage estabelecida com sucesso.")
            url = await upload_image(file_name, content, container_client)
            print(f"[LOG] Upload concluído com sucesso. URL: {url}")
            return {"url": url}

    except HTTPException:
        raise
    except Exception as e:
        print("[ERRO] Falha inesperada ao fazer upload da imagem:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao fazer upload da imagem")


@router.get("/usuario/existe/{id}.png")
async def existe_image(id: int):
    """
    Verifica se a imagem de perfil de um usuário existe no Azure Blob Storage.
    Retorna {"exists": true} ou {"exists": false}.
    """
    try:
        print(f"[LOG] Verificando existência da imagem para usuário ID={id}")
        async with azure_container() as container_client:
            exists = await image_exists(f"fotos/usuarios/{id}.png", container_client)
            print(f"[LOG] Resultado da verificação: {'EXISTE' if exists else 'NÃO EXISTE'}")
            return {"exists": exists}

    except Exception as e:
        print("[ERRO] Falha ao verificar existência da imagem:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao verificar existência da imagem")


@router.put("/usuario/{filename}")
async def update_image(filename: str, file: UploadFile = File(...)):
    """
    Atualiza (substitui) uma imagem existente no Azure Blob Storage.
    Se o arquivo não existir, retorna 404.
    """
    try:
        print(f"[LOG] Iniciando atualização de imagem: {filename}")
        content = await file.read()

        async with azure_container() as container_client:
            print("[LOG] Conexão com Azure estabelecida para atualização.")

            # Verifica se o arquivo existe antes de substituir
            if not await image_exists(filename, container_client):
                print("[ERRO] Imagem não encontrada no Azure para atualização.")
                raise HTTPException(status_code=404, detail="Imagem não encontrada")

            print("[LOG] Imagem existente encontrada, prosseguindo com atualização...")
            url = await upload_image(filename, content, container_client)
            print(f"[LOG] Imagem atualizada com sucesso. Nova URL: {url}")
            return {"url": url}

    except HTTPException:
        raise
    except Exception as e:
        print("[ERRO] Falha inesperada ao atualizar imagem:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao atualizar imagem")


@router.delete("/usuario/{filename}")
async def delete_image_endpoint(filename: str):
    """
    Exclui uma imagem específica do Azure Blob Storage.
    Se a imagem não existir, retorna 404.
    """
    try:
        print(f"[LOG] Iniciando exclusão da imagem: {filename}")
        async with azure_container() as container_client:
            print("[LOG] Conexão com Azure estabelecida para exclusão.")
            
            # Verifica se a imagem existe
            if not await image_exists(filename, container_client):
                print("[ERRO] Imagem não encontrada para exclusão:", filename)
                raise HTTPException(status_code=404, detail="Imagem não encontrada")

            print("[LOG] Imagem encontrada, executando exclusão...")
            await delete_image(filename, container_client)
            print("[LOG] Imagem deletada com sucesso:", filename)
            return {"message": "Imagem deletada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        print("[ERRO] Falha inesperada ao deletar imagem:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao deletar imagem")


@router.post("/upload-pdf")
async def upload_pdf_endpoint(file: UploadFile = File(...)):
    """
    Endpoint de upload de PDF.
    - Faz upload de arquivos PDF para o Azure Blob Storage.
    - Retorna a URL pública do arquivo.
    """
    try:
        print(f"[LOG] Iniciando upload de PDF: {file.filename}, tipo: {file.content_type}")

        # Lê o conteúdo do PDF
        content = await file.read()
        filename = file.filename

        async with azure_container() as container_client:
            print("[LOG] Conexão com Azure estabelecida para upload de PDF.")
            await upload_pdf(filename, content, container_client)

            url = (
                f"https://{os.getenv('AZURE_STORAGE_ACCOUNT_NAME')}.blob.core.windows.net/"
                f"{os.getenv('CONTAINER_NAME')}/{filename}"
            )

            print(f"[LOG] Upload de PDF concluído com sucesso. URL: {url}")
            return {"url": url}

    except Exception as e:
        print("[ERRO] Falha ao fazer upload do PDF:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao fazer upload do PDF")
