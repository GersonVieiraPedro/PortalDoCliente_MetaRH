from fastapi import FastAPI
from backend.routers import usuarios, auth

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(auth.router)

print(usuarios)
@app.get("/")
def home():
    return {"msg": "tudo certo!"}