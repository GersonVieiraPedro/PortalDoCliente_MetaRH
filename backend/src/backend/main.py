from fastapi import FastAPI
from backend.routers import organizacao, usuarios, auth

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(organizacao.router)

print(usuarios)
@app.get("/")
def home():
    return {"msg": "tudo certo!"}