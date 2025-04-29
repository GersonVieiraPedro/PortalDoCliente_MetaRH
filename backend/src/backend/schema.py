from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class Resposta(BaseModel):
    status: str
    mensagem: str


class RespostaLista(Resposta):
    ID: int

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cnpj: str

class UsuarioPublico(BaseModel):
    ID: int
    Nome: str
    Email: EmailStr    
    CNPJ:str
    TipoAcesso: str
    PipedriveID: str
    CodigoCliente: str
    Status: bool
    DataCadastro: datetime
    DataAtualizacao: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UsarioLogin(BaseModel):
    email: EmailStr
    senha:str    


class ListaUsuarios(BaseModel):
    usuarios: list[UsuarioPublico]


class AtualizarUsuarios(BaseModel):
    Nome: Optional[str] = None
    Email: Optional[EmailStr] = None 
    CNPJ: Optional[str] = None 
    TipoAcesso: Optional[str] = None 
    PipedriveID: Optional[str] = None 
    CodigoCliente: Optional[str] = None 
    Status: Optional[bool] = None 


class AtualizarUsuariosLista(AtualizarUsuarios):
    ID: int



class Organizacao(BaseModel):
   
    CNPJ: Optional[str] = None
    CodigoCliente: Optional[str] = None
