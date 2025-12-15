from datetime import datetime
from typing import Optional
from sqlalchemy import DECIMAL, Boolean, Column, DateTime, Float, ForeignKey, Integer, text, Numeric, String
from sqlalchemy.orm import Mapped, registry, mapped_column, relationship


TabelaRegistro = registry()

@TabelaRegistro.mapped_as_dataclass
class TB_Usuarios:
    """
    Modelo para a tabela TB_Usuarios (Usuários do sistema)
    Armazena dados cadastrais e de acesso dos usuários.
    """
    __tablename__  ='TB_Usuarios'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    Nome: Mapped[str]
    Email: Mapped[str] = mapped_column(unique=True)
    Senha: Mapped[str]
    CNPJ: Mapped[str]
    TipoAcesso: Mapped[str] = mapped_column(init=False, server_default=text('Cliente'))
    Acesso: Mapped[str] = mapped_column(init=False)
    PipedriveID: Mapped[str] = mapped_column(init=False, server_default=text('NãoMapeado'))
    CodigoCliente: Mapped[int] = mapped_column(init=False, server_default=text('NãoMapeado'))
    IDEmpresa: Mapped[Optional[int]] = mapped_column(ForeignKey('TB_Empresa.ID'), init=False, default=None)
    Status: Mapped[bool] = mapped_column(default=False, server_default=text("FALSE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

    # Relationships
    empresa: Mapped[Optional["TB_Empresa"]] = relationship(init=False, lazy="joined")



@TabelaRegistro.mapped_as_dataclass
class TB_Empresa:
    """
    Modelo para a tabela TB_Empresas (Empresas/Filiais)
    Tabela de domínio que armazena empresas e filiais do sistema.
    Utilizada para relacionar usuários com suas empresas e aplicar filtros de segurança.
    """
    __tablename__ = 'TB_Empresa'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    IDSelecty: Mapped[int | None] = mapped_column(nullable=True)
    IDPipedrive: Mapped[int | None] = mapped_column(nullable=True)
    IDProprietario: Mapped[int | None] = mapped_column(ForeignKey('DIM_Proprietario.ID'),nullable=True)
    CodigoCliente: Mapped[int]
    CodigoEmpresaFat: Mapped[int]
    CodigoFilialFat: Mapped[int]
    Nome: Mapped[str] = mapped_column(String(100))
    GrupoEconomico: Mapped[str] = mapped_column(String(100))
    RazaoSocial: Mapped[str] = mapped_column(String(200))
    CNPJ: Mapped[str] = mapped_column(String(18))
    Ativo: Mapped[bool] = mapped_column(default=True, server_default=text("1"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    usuarios: Mapped[list["TB_UsuarioEmpresa"]] = relationship(
        back_populates="empresa",
        default_factory=list,
        repr=False
    )
    proprietario: Mapped["DIM_Proprietario"] = relationship(init=False)



@TabelaRegistro.mapped_as_dataclass
class TB_UsuarioEmpresa:
    """
    Modelo para a tabela TB_UsuarioEmpresa
    Tabela de associação entre usuários e empresas/filiais.
    Permite que um usuário tenha acesso a múltiplas empresas.
    """
    __tablename__ = 'TB_UsuarioEmpresa'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    IDUsuario: Mapped[int] = mapped_column(ForeignKey('TB_Usuarios.ID'))
    IDEmpresa: Mapped[int] = mapped_column(ForeignKey('TB_Empresa.ID'))
    Ativo: Mapped[bool] = mapped_column(default=True, server_default=text("1"))
    DataVinculo: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    empresa: Mapped["TB_Empresa"] = relationship(
        back_populates="usuarios",
        init=False
    )

@TabelaRegistro.mapped_as_dataclass
class TB_Admissao:
    """
    Modelo para a tabela TB_Admissao
    Armazena informações detalhadas de admissões de colaboradores.
    """
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
    IDProprietario: Mapped[Optional[int]] = mapped_column(ForeignKey('DIM_Proprietario.ID'), nullable=True, init=False)
    DataInicio: Mapped[Optional[datetime]] = mapped_column(nullable=True, init=False)
    DataConclusao: Mapped[Optional[datetime]] = mapped_column(nullable=True, init=False)
    Status: Mapped[Optional[str]] = mapped_column(nullable=True, init=False)
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))



@TabelaRegistro.mapped_as_dataclass
class TB_Demissao:
    """
    Modelo para a tabela TB_Demissao
    Armazena informações detalhadas de desligamentos de colaboradores.
    """
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
    IDProprietario: Mapped[Optional[int]] = mapped_column(ForeignKey('DIM_Proprietario.ID'), nullable=True, init=False)
    DataInicio: Mapped[Optional[datetime]] = mapped_column(nullable=True, init=False)
    DataConclusao: Mapped[Optional[datetime]] = mapped_column(nullable=True, init=False)
    Status: Mapped[Optional[str]] = mapped_column(nullable=True, init=False)
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))


@TabelaRegistro.mapped_as_dataclass
class TB_ISS:
    """
    Modelo para a tabela TB_ISS
    Armazena informações de alíquotas de ISS por município.
    """
    __tablename__ = 'TB_ISS'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    UF: Mapped[str]
    Municipio: Mapped[str]
    Label: Mapped[str]
    ISS: Mapped[float]


@TabelaRegistro.mapped_as_dataclass
class TB_Encargo:
    """
    Modelo para a tabela TB_Encargo
    Armazena informações de encargos aplicáveis a serviços.
    """
    __tablename__ = 'TB_Encargo'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    CodigoServico: Mapped[str]
    Servico: Mapped[str]
    Grupo: Mapped[str]
    Nome: Mapped[str]
    Percentual: Mapped[float] = mapped_column(Numeric(18, 2))
    ModalidadeContrato: Mapped[str]
    Fonte: Mapped[str]
    UltimoUsuario: Mapped[str]
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))



@TabelaRegistro.mapped_as_dataclass
class TB_Beneficio:
    """
    Modelo para a tabela TB_Beneficio
    Armazena informações sobre benefícios concedidos aos colaboradores.
    """
    __tablename__ = 'TB_Beneficio'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    Nome: Mapped[str]
    Editavel: Mapped[bool]
    Frequencia: Mapped[str]
    Quantidade: Mapped[int]
    Dias: Mapped[int]
    ValorUnitario: Mapped[float]
    Desconto: Mapped[float]
    Categoria: Mapped[str]
    UltimoUsuario: Mapped[str]
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

@TabelaRegistro.mapped_as_dataclass
class TB_Orcamento:
    """
    Modelo para a tabela TB_Orcamento
    Armazena informações consolidadas de orçamentos de serviços.
    """
    __tablename__ = "TB_Orcamento"
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Usuario: Mapped[int]
    ID_Servico: Mapped[int]
    ID_Contrato: Mapped[str]
    ID_MunicipioISS: Mapped[int] 
    ModalidadeContrato: Mapped[Optional[str]] = mapped_column(nullable=True)
    TaxaAdministrativa: Mapped[float]
    Cargo: Mapped[str]
    Salario: Mapped[float]
    Quantidade: Mapped[int]
    Periculosidade: Mapped[str]
    Insalubridade: Mapped[str]
    SalarioBruto: Mapped[float]
    GrupoAPercentual: Mapped[float]
    GrupoAValor: Mapped[float]
    GrupoBPercentual: Mapped[float]
    GrupoBValor: Mapped[float]
    TotalEncargosTrabalistasPercentual: Mapped[float]
    TotalEncargosTrabalistasValor: Mapped[float]
    TotalSalarioBrutoEncargos: Mapped[float]
    TotalBeneficiosFornecido: Mapped[float]
    TotalBeneficiosRepasse: Mapped[float]
    SubtotalNotaFiscalServico:Mapped[float]
    ExameASO: Mapped[float]
    TotalEncargosTributariosPercentual: Mapped[float]
    TotalEncargosTributariosValor: Mapped[float]
    ProjecaoPorColaboradorAdministrado: Mapped[float]
    ProjecaoTotalNotaFiscalServico: Mapped[float]
    Proprietario: Mapped[Optional[str]] = mapped_column(init=False, nullable=True)
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

    
@TabelaRegistro.mapped_as_dataclass
class TB_OrcamentoEncargo:
    """
    Modelo para a tabela TB_OrcamentoEncargo
    Associa encargos a orçamentos específicos.
    """
    __tablename__ = "TB_OrcamentoEncargo"
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Orcamento: Mapped[int]
    ID_Encargo: Mapped[int]
    TipoEncargo: Mapped[str]
    Percentual: Mapped[float]
    Valor: Mapped[float]
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))

@TabelaRegistro.mapped_as_dataclass
class TB_OrcamentoBeneficio:
    """
    Modelo para a tabela TB_OrcamentoBeneficio
    Associa benefícios a orçamentos específicos.
    """
    __tablename__ = "TB_OrcamentoBeneficio"
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Orcamento: Mapped[int]
    ID_Beneficio: Mapped[int]
    Quantidade: Mapped[int]
    ValorUnitario: Mapped[float]
    Fornecido: Mapped[float]
    Repasse: Mapped[float]
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))



@TabelaRegistro.mapped_as_dataclass
class TB_AlteracaoCentro:
    """
    Modelo da tabela TB_AlteracaoCentro
    Registra alterações de centro de custo realizadas pelos usuários.
    """
    __tablename__ = "TB_AlteracaoCentro"

    # Chave primária (IDENTITY)
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Dados da solicitação
    ID_Usuario: Mapped[int | None]
    CodigoFuncionario: Mapped[int | None]
    Nome: Mapped[str | None] = mapped_column(String(100))
    Empresa: Mapped[str | None] = mapped_column(String(100))
    Motivo: Mapped[str | None] = mapped_column(default=None)
    CentroCustoAtual: Mapped[str | None] = mapped_column(default=None)
    CentroCustoNovo: Mapped[str | None] = mapped_column(default=None)
    IDProprietario: Mapped[int | None] = mapped_column(ForeignKey('DIM_Proprietario.ID'),  default=None)
    Status: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))

    # Datas
    DataInicio: Mapped[datetime | None] = mapped_column(default=None)
    DataConclusao: Mapped[datetime | None] = mapped_column(default=None)
    DataCadastro: Mapped[datetime | None] = mapped_column(
        init=False,
        server_default=text("GETDATE()")   # equivalente ao CURRENT_TIMESTAMP no SQL Server
    )

@TabelaRegistro.mapped_as_dataclass
class TB_AlteracaoSalario:
    __tablename__ = "TB_AlteracaoSalario"

    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Usuario: Mapped[int | None]
    CodigoFuncionario: Mapped[int | None]
    Nome: Mapped[str | None] = mapped_column(String(100))
    Empresa: Mapped[str | None] = mapped_column(String(100))
    Motivo: Mapped[str | None] = mapped_column(String(50))
    SalarioAtual: Mapped[float | None]
    SalarioNovo: Mapped[float | None] 
    Percentual: Mapped[float | None] 
    IDProprietario: Mapped[int | None] = mapped_column(ForeignKey('DIM_Proprietario.ID'),  default=None)
    Status: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))

    # Datas
    DataInicio: Mapped[datetime | None] = mapped_column(default=None)
    DataConclusao: Mapped[datetime | None] = mapped_column(default=None)
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text("GETDATE()"))

@TabelaRegistro.mapped_as_dataclass
class TB_AlteracaoVale:
    __tablename__ = "TB_AlteracaoVale"

    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Usuario: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    CodigoFuncionario: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Nome: Mapped[str | None] = mapped_column(String(100))
    Empresa: Mapped[str | None] = mapped_column(String(100))

    Motivo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Desconto geral (se houver)
    Desconto: Mapped[Optional[float]] = mapped_column(Numeric(5,2), nullable=True)

    # Vigência da alteração
    Vigencia: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Vale Refeição
    VRCheck: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    VRAtual: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    VRNovo: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    # Vale Alimentação
    VACheck: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    VAAtual: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    VANovo: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    # Controle
    IDProprietario: Mapped[int | None] = mapped_column(ForeignKey('DIM_Proprietario.ID'),  default=None)
    Status: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))

    # Datas
    DataInicio: Mapped[datetime | None] = mapped_column(default=None)
    DataConclusao: Mapped[datetime | None] = mapped_column(default=None)
    DataCadastro: Mapped[datetime] = mapped_column(DateTime,init=False, server_default=text("GETDATE()"),nullable=False)



@TabelaRegistro.mapped_as_dataclass
class TB_AlteracaoJornada:
    __tablename__ = "TB_AlteracaoJornada"

    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    ID_Usuario: Mapped[int | None]
    CodigoFuncionario: Mapped[int | None]
    Nome: Mapped[str | None] = mapped_column(String(100))
    Empresa: Mapped[str | None] = mapped_column(String(100))
    Motivo: Mapped[str | None] = mapped_column(String(50))
    HorarioAtual: Mapped[int | None]
    HorarioAtualDescricao: Mapped[str | None]
    HorarioNovo: Mapped[int | None] 
    JornadaAtual: Mapped[int | None]
    JornadaNovo: Mapped[int | None] 
    Status: Mapped[str | None] = mapped_column(default=None, nullable=True)
    Visivel: Mapped[bool] = mapped_column(default=True, server_default=text("TRUE"))
    IDProprietario: Mapped[int | None] = mapped_column(ForeignKey('DIM_Proprietario.ID'),  default=None, nullable=True)

    # Datas
    DataInicio: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    DataConclusao: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text("GETDATE()"))


    


@TabelaRegistro.mapped_as_dataclass
class TB_Destinatario:
    """
    Modelo da tabela TB_Destinatario
    Registra os destinatários por funcionalidade.
    """
    __tablename__ = "TB_Destinatario"

    # Primary Key IDENTITY
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Dados principais
    IDFuncionalidade: Mapped[int] = mapped_column(ForeignKey('DIM_Funcionalidade.ID'))
    IDProprietario: Mapped[int] = mapped_column(ForeignKey('DIM_Proprietario.ID'))
    Nome: Mapped[str] = mapped_column(String(200))
    Ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Datas
    DataAtualizacao: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text("GETDATE()")
    )

    DataCadastro: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text("GETDATE()")
    )





@TabelaRegistro.mapped_as_dataclass
class DIM_Funcionalidade:
    """
    Tabela de dimensão para funcionalidades do sistema

    Utilizada para análises e relatórios.
    """
    __tablename__ = 'DIM_Funcionalidade'

    # Chave Primária
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Campos obrigatórios (devem vir antes dos opcionais para dataclasses)
    Nome: Mapped[str] = mapped_column(String(100), unique=True)
    Descricao: Mapped[str] = mapped_column(String(250))
    Tabela: Mapped[str] = mapped_column(String(50))

    # Campos opcionais (com default, devem vir depois dos obrigatórios)
    Ativo: Mapped[bool] = mapped_column(default=True, server_default=text('1'))

    # Timestamps
    DataCadastro: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP')
    )



@TabelaRegistro.mapped_as_dataclass
class DIM_Proprietario:
    """
    Tabela de dimensão para proprietários de registros no sistema

    Utilizada para análises e relatórios.
    """
    __tablename__ = 'DIM_Proprietario'

    # Chave Primária
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Campos obrigatórios (devem vir antes dos opcionais para dataclasses)
    Nome: Mapped[str] = mapped_column(String(100))

    PrimeiroNome: Mapped[str] = mapped_column(String(100))
    UltimoSobrenome: Mapped[str] = mapped_column(String(100))
    Email: Mapped[str] = mapped_column(String(250))

    # Campos opcionais (com default, devem vir depois dos obrigatórios)
    Ativo: Mapped[bool] = mapped_column(default=True, server_default=text('1'))

    # Timestamps
    DataCadastro: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP')
    )

        

@TabelaRegistro.mapped_as_dataclass
class VW_Solicitacoes:
    """
    View unificada de solicitações do sistema

    Read-only
    Utilizada para listagens, dashboards e relatórios.
    """
    __tablename__ = "VW_Solicitacoes"
    __table_args__ = {"schema": "dbo"}

    # Chave técnica (obrigatória para o ORM)
 
    ViewID: Mapped[int] = mapped_column(primary_key=True)
    ID: Mapped[int]
    # Campos obrigatórios
    Tipo: Mapped[str] = mapped_column(String(50))
    Titulo: Mapped[str] = mapped_column(String(250))
    Status: Mapped[str] = mapped_column(String(30))

    DataInicio: Mapped[datetime | None] = mapped_column(DateTime)
    DataConclusao: Mapped[datetime | None] = mapped_column(DateTime)

    DataCadastro: Mapped[datetime] = mapped_column(DateTime)

    ID_Usuario: Mapped[int] = mapped_column()
    IDProprietario: Mapped[int | None] = mapped_column()

    Visivel: Mapped[bool] = mapped_column(Boolean)

    TabelaOrigem: Mapped[str] = mapped_column(String(50))

        
@TabelaRegistro.mapped_as_dataclass
class TB_Duplicata:
    """
    Modelo para a tabela TB_Duplicata (Notas Fiscais/Duplicatas)

    ⚠️ IMPORTANTE - Entendimento dos Campos de Documentos Fiscais:
    ------------------------------------------------------------------
    - **Duplicata**: Número da RPS (Recibo Provisório de Serviço)
                     Este é o identificador PRINCIPAL da RPS no sistema!

    - **NroNFe**: Número da Nota Fiscal Eletrônica (emitida APÓS aprovação da RPS)
                  Diferente do número da RPS. Preenchido apenas após emissão da NF.

    - **NumeroRPS**: Campo LEGACY do sistema antigo (deprecated)
                     Usar o campo 'Duplicata' como número da RPS.
                     Mantido apenas para compatibilidade temporária.

    Chave Primária Composta: (CodigoEmpresaFat, CodigoFilialFat, Duplicata)
    """
    __tablename__ = 'TB_Duplicata'

    # Chave Primária Composta
    CodigoEmpresaFat: Mapped[int] = mapped_column(primary_key=True)
    CodigoFilialFat: Mapped[int] = mapped_column(primary_key=True)
    Duplicata: Mapped[int] = mapped_column(primary_key=True)
    # 👆 ESTE É O NÚMERO DA RPS (Recibo Provisório de Serviço)

    # Campos de relacionamento
    CodigoCliente: Mapped[Optional[int]] = mapped_column(index=True, init=False)
    CodigoContrato: Mapped[Optional[int]] = mapped_column(init=False)

    # Datas
    DataEmissao: Mapped[Optional[datetime]] = mapped_column(init=False)
    DataVecto: Mapped[Optional[datetime]] = mapped_column(index=True, init=False)
    DataBaixa: Mapped[Optional[datetime]] = mapped_column(init=False)
    DataCompetencia: Mapped[Optional[str]] = mapped_column(index=True, init=False)

    # Valores
    ValorBruto: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), init=False)
    ValorLiquido: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), init=False)

    # Números de Documentos Fiscais
    NroNFe: Mapped[Optional[int]] = mapped_column(init=False)
    # 👆 NÚMERO DA NOTA FISCAL (emitida APÓS aprovação da RPS)

    NumeroRPS: Mapped[Optional[int]] = mapped_column(init=False)
    # 👆 DEPRECATED: Campo legacy. Usar 'Duplicata' como número da RPS

    # Status da duplicata no sistema ('A' = Ativo, 'B' = Baixado, 'C' = Cancelado)
    Status: Mapped[Optional[str]] = mapped_column(index=True, init=False)


@TabelaRegistro.mapped_as_dataclass
class TB_StatusAprovacao:
    """
    Tabela de domínio para status de aprovação de RPS

    Normaliza os valores de status para melhorar performance em consultas e filtros.
    Ao invés de usar campo texto (pendente/aprovado/reprovado), usa chave numérica.

    Valores possíveis:
    - 1: pendente
    - 2: aprovado
    - 3: reprovado
    """
    __tablename__ = 'TB_StatusAprovacao'

    # Chave Primária
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Campos obrigatórios (devem vir antes dos opcionais para dataclasses)
    # Código do status (pendente, aprovado, reprovado)
    Codigo: Mapped[str] = mapped_column(String(20), unique=True)

    # Descrição legível
    Descricao: Mapped[str] = mapped_column(String(100))

    # Ordem de exibição
    Ordem: Mapped[int]

    # Campos opcionais (com default, devem vir depois dos obrigatórios)
    # Status ativo no sistema
    Ativo: Mapped[bool] = mapped_column(default=True, server_default=text('1'))

    # Timestamps
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))


@TabelaRegistro.mapped_as_dataclass
class TB_AprovacaoRPS:
    """
    Tabela de controle de aprovações e reprovações de RPS

    Mantém histórico completo de todas as ações (relação 1:N)
    Não modifica TB_Duplicata (tabela do sistema legado)

    ⚠️ IMPORTANTE - Identificação da RPS:
    -------------------------------------
    - O campo **Duplicata** identifica o número da RPS
    - A chave composta (CodigoEmpresaFat, CodigoFilialFat, Duplicata)
      referencia a RPS na tabela TB_Duplicata

    Workflow de Aprovação:
    ----------------------
    1. RPS é criada na TB_Duplicata (status pendente por padrão)
    2. Cliente aprova/reprova via Portal
    3. Registro é criado nesta tabela (TB_AprovacaoRPS) com histórico
    4. Última ação determina o status atual (StatusAprovacao)
    5. TB_Duplicata permanece inalterada (read-only)
    """
    __tablename__ = 'TB_AprovacaoRPS'

    # Chave Primária
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Relacionamento com TB_Duplicata (chave composta)
    CodigoEmpresaFat: Mapped[int] = mapped_column(index=True)
    CodigoFilialFat: Mapped[int] = mapped_column(index=True)
    Duplicata: Mapped[int] = mapped_column(index=True)
    # 👆 ESTE É O NÚMERO DA RPS (referencia TB_Duplicata.Duplicata)

    # Status e Tipo de Ação
    IdStatusAprovacao: Mapped[int] = mapped_column(ForeignKey('TB_StatusAprovacao.ID'), index=True)
    # 👆 NOVO: Chave estrangeira para TB_StatusAprovacao (substitui campo texto)

    StatusAprovacao: Mapped[str]  # ⚠️ DEPRECATED: Usar IdStatusAprovacao (será removido após migração)
    TipoAcao: Mapped[str]  # 'aprovacao', 'reprovacao', 'cancelamento'

    # Rastreabilidade (campos obrigatórios - devem vir antes dos opcionais)
    ID_Usuario: Mapped[int] = mapped_column(ForeignKey('TB_Usuarios.ID'))
    NomeUsuario: Mapped[str]
    EmailUsuario: Mapped[str]

    # Motivo da Reprovação (campos opcionais - devem vir depois dos obrigatórios)
    MotivoReprovacao: Mapped[Optional[str]] = mapped_column(default=None)
    DescricaoReprovacao: Mapped[Optional[str]] = mapped_column(default=None)

    # Timestamps
    DataAcao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataCadastro: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'))
    DataAtualizacao: Mapped[datetime] = mapped_column(init=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))


@TabelaRegistro.mapped_as_dataclass
class TB_MotivoReprovacaoRPS:
    """
    Tabela de motivos de reprovação de RPS

    Armazena os motivos padronizados que podem ser selecionados
    ao reprovar um RPS, com deleção lógica (flag Ativo)
    """
    __tablename__ = 'TB_MotivoReprovacaoRPS'

    # Primary Key
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Campos obrigatórios
    Codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    Descricao: Mapped[str] = mapped_column(String(200))
    Ativo: Mapped[bool] = mapped_column(default=True, index=True)
    Ordem: Mapped[int] = mapped_column(default=999, index=True)

    # Campos opcionais
    DescricaoDetalhada: Mapped[Optional[str]] = mapped_column(String(500), default=None)

    # Timestamps
    DataCadastro: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP')
    )
    DataAtualizacao: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP')
    )


@TabelaRegistro.mapped_as_dataclass
class TB_Contratos:
    """
    Modelo para a tabela TB_Contratos (Gestão de Contratos)

    Armazena informações dos contratos dos clientes.
    Filtrado automaticamente por empresa do usuário logado.

    Campos principais:
    - Identificação: NumeroContrato, CNPJ, RazaoSocial
    - Detalhes: ServicosContemplados, Vigencia, Valor
    - Datas: DataAssinatura, DataVencimento
    - Arquivo: ArquivoPDF (URL Azure Blob)
    - Status: A=Ativo, I=Inativo
    """
    __tablename__ = 'TB_Contratos'

    # Primary Key
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Relacionamento com Cliente/Empresa
    CodigoCliente: Mapped[int] = mapped_column(index=True)

    # Campos Principais do Contrato
    NumeroContrato: Mapped[str] = mapped_column(String(50))
    CNPJ: Mapped[str] = mapped_column(String(18), index=True)
    RazaoSocial: Mapped[str] = mapped_column(String(200))
    ServicosContemplados: Mapped[str] = mapped_column(String)

    # Datas e Vigência
    DataAssinatura: Mapped[datetime] = mapped_column(index=True)
    Vigencia: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    DataVencimento: Mapped[Optional[datetime]] = mapped_column(default=None)

    # Informações Financeiras
    Valor: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), default=None)

    # Status e Controle
    Status: Mapped[str] = mapped_column(String(20), index=True, default='A')

    # Arquivo PDF (Azure Blob Storage)
    ArquivoPDF: Mapped[Optional[str]] = mapped_column(String(500), default=None)

    # Timestamps de Auditoria
    DataCadastro: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP')
    )
    DataAtualizacao: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP')
    )

















































#=================================================================================================
## Mapeamento Dinâmico de Modelos por Nome de Tabela

MAP_Funcionalidades = {
    "TB_AlteracaoJornada": TB_AlteracaoJornada,
    "TB_AlteracaoCentro": TB_AlteracaoCentro,
    "TB_AlteracaoSalario": TB_AlteracaoSalario,
    "TB_AlteracaoVale": TB_AlteracaoVale,
    "TB_Admissao": TB_Admissao,
    "TB_Demissao": TB_Demissao,
    "TB_Orcamento": TB_Orcamento,
    "TB_AprovacaoRPS": TB_AprovacaoRPS,
}

def model_dinamico(nome_tabela: str):
    return MAP_Funcionalidades.get(nome_tabela, None)