from datetime import datetime
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, registry, mapped_column



TabelaRegistro = registry()

@TabelaRegistro.mapped_as_dataclass
class TB_Usuarios:
    __tablename__  ='TB_Usuarios'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    Nome: Mapped[str]
    Email: Mapped[str] = mapped_column(unique=True)
    Senha: Mapped[str]
    CNPJ: Mapped[str]
    TipoAcesso: Mapped[str] = mapped_column(init=False, server_default=text('Cliente'))
    Acesso: Mapped[str] = mapped_column(init=False)
    PipedriveID: Mapped[str] = mapped_column(init=False, server_default=text('NãoMapeado'))
    CodigoCliente: Mapped[str] = mapped_column(init=False, server_default=text('NãoMapeado'))
    Status: Mapped[bool] = mapped_column(default=False, server_default=text("FALSE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))



@TabelaRegistro.mapped_as_dataclass
class TB_Admissao:
    __tablename__ ='TB_Admissao'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Usuario: Mapped[int] = mapped_column(ForeignKey('TB_Usuarios.ID'), init=False)
    TipoVaga: Mapped[str] 
    Cargo: Mapped[str]
    CentroCusto: Mapped[str]
    SetorTrabalho: Mapped[str]
    ModalidadeTrabalho: Mapped[str]
    MotivoContratacao: Mapped[str]
    EscalaTrabalho: Mapped[str]
    LocalTrabalho: Mapped[str]
    Salario: Mapped[str]
    DescricaoCargo: Mapped[str]
    PrecisaEPI: Mapped[bool]
    DescricaoEPI: Mapped[str]
    NomeSubstituido: Mapped[str]
    CPFSubstituido: Mapped[str]
    MotivoSubstituido: Mapped[str]
    NomeResponsavelRH: Mapped[str]
    EmailResponsavelRH: Mapped[str]
    TelefoneResponsavelRH: Mapped[str]
    NomeGestorPonto: Mapped[str]
    EmailGestorPonto: Mapped[str]
    TelefoneGestorPonto: Mapped[str]
    NomePessoaPrimeiroDia: Mapped[str]
    DepartamentoPrimeiroDia: Mapped[str]
    HorarioPrimeiroDia: Mapped[str]
    Proprietario: Mapped[str] = mapped_column(init=False)
    DataInicio: Mapped[datetime] = mapped_column(init=False)
    DataEncerramento: Mapped[datetime] = mapped_column(init=False)
    Status: Mapped[str] = mapped_column(init=False, server_default=text('Não Iniciado'))
    Visivel: Mapped[str] = mapped_column(default=False, server_default=text("TRUE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))



@TabelaRegistro.mapped_as_dataclass
class TB_Demissao:
    __tablename__ ='TB_Demissao'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Usuario: Mapped[int] = mapped_column(ForeignKey('TB_Usuarios.ID'), init=False)
    CodigoFuncionario: Mapped[int]
    NomeFuncionario: Mapped[str]
    Empresa: Mapped[str]
    Cargo: Mapped[str]
    CentroCusto: Mapped[str]
    Gestor: Mapped[str]
    Salario: Mapped[str]
    DataAdmissao: Mapped[datetime]
    DataDemissao: Mapped[datetime]
    MotivoDemissao: Mapped[str]
    FeriasVencidas: Mapped[str]
    AvisoPrevio: Mapped[str]
    ConhecimentoDesligamento: Mapped[str]
    ComunicadoPresencial: Mapped[str]
    Endereco: Mapped[str]
    Horario: Mapped[str]
    Proprietario: Mapped[str] = mapped_column(init=False)
    DataInicio: Mapped[datetime] = mapped_column(init=False)
    DataEncerramento: Mapped[datetime] = mapped_column(init=False)
    Status: Mapped[str] = mapped_column(init=False, server_default=text('Não Iniciado'))
    Visivel: Mapped[str] = mapped_column(default=False, server_default=text("TRUE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))


@TabelaRegistro.mapped_as_dataclass
class TB_ISS:
    __tablename__ = 'TB_ISS'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    UF: Mapped[str]
    Municipio: Mapped[str]
    Label: Mapped[str]
    ISS: Mapped[float]