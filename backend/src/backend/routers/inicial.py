from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional, List

import requests
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from pydantic import BaseModel, EmailStr # type: ignore
from bs4 import BeautifulSoup
from sqlalchemy.future import select
from ..database import AtivarSession
from ..models import VW_Solicitacoes
from ..schema import VWSolicitacaoSchema # type: ignore


router = APIRouter(prefix="/inicial", tags=["Página Inicial"])


# Cache simples em memória (30 min)
CACHE = {"data": None, "expires": None}

@router.get("/blogProxy")
async def blog_proxy_router():
    """
    Extrai imagem e link dos posts do blog da Meta RH
    e retorna como JSON estruturado.
    """

    # verifica cache
    if CACHE.get("data") and CACHE.get("expires") and CACHE["expires"] > datetime.now():
        return CACHE["data"]

    try:
        url = "https://metarh.com.br/metarhnews/blog/"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {"status": "erro", "mensagem": "Não foi possível acessar o blog."}

        soup = BeautifulSoup(response.text, "html.parser")

        # encontra todas as divs de post
        divs = soup.find_all("div", class_="premium-blog-thumb-effect-wrapper")

        posts = []

        for div in divs:
            # pega imagem e link
            img_tag = div.find("img")
            link_tag = div.find("a", href=True)

            if img_tag and link_tag:
                imagem = img_tag.get("src")
                link = link_tag["href"]

                posts.append({
                    "imagem": imagem,
                    "link": link
                })

        resultado = {
            "status": "sucesso",
            "quantidade": len(posts),
            "posts": posts
        }

        # salva no cache
        CACHE["data"] = resultado
        CACHE["expires"] = datetime.now() + timedelta(minutes=30)

        return resultado

    except Exception as e:
        return {"status": "erro", "mensagem": f"Ocorreu um erro: {str(e)}"}



@router.get("/solicitacoes",response_model=list[VWSolicitacaoSchema])
def listar_solicitacoes(
    id: Optional[int] = None,
    session=Depends(AtivarSession)
):
    stmt = (
        select(VW_Solicitacoes)
        .where(VW_Solicitacoes.Visivel == True if id is None else VW_Solicitacoes.ID == id)
        .order_by(VW_Solicitacoes.DataCadastro.desc())
    )

    return session.scalars(stmt).all()