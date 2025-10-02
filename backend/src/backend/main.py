from backend.TabelasGI import TabelaFuncionarios
from backend.TabelasLocais import SalvarArquivosLocal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import organizacao, usuarios, auth, requisicoes, imagens, simulacoes

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


@app.get("/")
def home():
    
    return{"msg": "tudo certo!"}





#SalvarArquivosLocal()