from http import HTTPStatus
import os
from backend.database import AtivarSession
from backend.models import TB_Usuarios
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from requests import session
from sqlalchemy import String, select
from ..aruze_storage import convert_to_png, get_image_url, delete_image, image_exists, list_images, upload_image

router = APIRouter(prefix="/imagens", tags=["Imagens"])

@router.post("/usuario")
async def create_image(email:str, session = Depends(AtivarSession), file: UploadFile = File(...)):
    # Verifica se o usuário já existe
    UsuarioDB = session.scalar( 
        select(TB_Usuarios).where(TB_Usuarios.Email == email)
    )

    if UsuarioDB:

        content = await file.read()
        # Recupera a extensão do nome original (ex: .jpg, .png)
        _, ext = os.path.splitext(file.filename)
        if ext !=".png":
          print(ext)
          content = convert_to_png(content)
            

        file_name = f"fotos/usuarios/{UsuarioDB.ID}.png"
        url = upload_image(file_name, content)
        return {"url": url}
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"status": "Erro", "mensagem": "Nenhum registro encontrado!"}
        )
    

@router.get("/usuario/existe/{id}.png")
async def existe_image(id: int):
  return  image_exists(f"{id}.png") 



@router.put("/usuario/{filename}")
async def update_image(filename: str, file: UploadFile = File(...)):
    content = await file.read()
    if not image_exists(filename):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    url = upload_image(filename, content)
    return {"url": url}

@router.delete("/usuario/{filename}")
def delete_image(filename: str):
    if not image_exists(filename):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    delete_image(filename)
    return {"message": "Imagem deletada com sucesso"}

