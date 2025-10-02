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
    SenhaAntiga: Optional[str] = None 
    SenhaNova: Optional[str] = None 
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


class AdmissaoSchema(BaseModel):
    TipoVaga: str
    Cargo: str
    CentroCusto: str
    SetorTrabalho: str
    ModalidadeTrabalho: str
    MotivoContratacao: str
    EscalaTrabalho: str
    LocalTrabalho: str
    Salario: str
    DescricaoCargo: str
    PrecisaEPI: Optional[bool] = None
    DescricaoEPI: Optional[str] = None
    NomeSubstituido: Optional[str] = None
    CPFSubstituido: Optional[str] = None
    MotivoSubstituido: Optional[str] = None
    NomeResponsavelRH: str
    EmailResponsavelRH: str
    TelefoneResponsavelRH: str
    NomeGestorPonto: str
    EmailGestorPonto: str
    TelefoneGestorPonto: str
    NomePessoaPrimeiroDia: str
    DepartamentoPrimeiroDia: str
    HorarioPrimeiroDia: str
    Proprietario: Optional[str] = None
    DataInicio: Optional[datetime] = None
    DataEncerramento: Optional[datetime] = None

class DemissaoSchema(BaseModel):
    CodigoFuncionario: int
    NomeFuncionario: str
    Cargo: str
    CentroCusto: str
    Empresa: str
    Gestor: str
    Salario: str
    DataAdmissao: datetime
    DataDemissao: datetime
    MotivoDemissao: str
    FeriasVencidas: str
    AvisoPrevio: str
    ConhecimentoDesligamento: str
    ComunicadoPresencial: str
    Endereco: str
    Horario: str