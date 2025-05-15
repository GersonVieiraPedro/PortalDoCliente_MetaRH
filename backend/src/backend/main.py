from backend.TabelasGI import TabelaFuncionarios
from fastapi import FastAPI
from backend.routers import organizacao, usuarios, auth, requisicoes

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(organizacao.router)
app.include_router(requisicoes.router)

print(usuarios)
@app.get("/")
def home():
    
    res = TabelaFuncionarios(CNPJ=['00.331.788/0021-62','00.331.788/0083-65'])   

    
    return  res.to_dict(orient="records") #{"msg": "tudo certo!"}