from .TabelasGI import TabelaFuncionarios
from .TabelasLocais import SalvarArquivosLocal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import organizacao, usuarios, auth, requisicoes, imagens, simulacoes, mensageria, financeiro, inicial
import logging

# Reduz o nível de logs do Azure Monitor
logging.getLogger("azure.monitor.opentelemetry").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifique seu frontend: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # ou ["POST", "GET", "OPTIONS"]
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(organizacao.router)
app.include_router(requisicoes.router)
app.include_router(imagens.router)
app.include_router(simulacoes.router)
app.include_router(mensageria.router)
app.include_router(financeiro.router)
app.include_router(inicial.router)


@app.get("/")
def home():
    return {
        "msg": "tudo certo!",
        "status": "online"
    }





#SalvarArquivosLocal()