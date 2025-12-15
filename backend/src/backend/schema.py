from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field

# ========================================
# MODELOS BÁSICOS DE RESPOSTA E USUÁRIOS
# ========================================

class Resposta(BaseModel):
    """Modelo base para respostas simples da API"""
    status: str = Field(..., description="Status da operação (ex: sucesso, erro)")
    mensagem: str = Field(..., description="Mensagem descritiva da resposta")


class RespostaLista(Resposta):
    """Extensão de resposta com identificação"""
    ID: int = Field(..., description="Identificador único do registro")


class UsuarioSchema(BaseModel):
    """Schema utilizado para cadastro de novos usuários"""
    nome: str = Field(..., description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Endereço de e-mail do usuário")
    senha: str = Field(..., description="Senha de acesso do usuário")
    cnpj: str = Field(..., description="CNPJ vinculado ao usuário")


class EmpresaPublica(BaseModel):
    """Schema de exibição pública dos dados de uma empresa"""
    ID: int = Field(..., description="Identificador único da empresa")
    CodigoCliente: str = Field(..., description="Código do cliente no sistema")
    CodigoEmpresaFat: int = Field(..., description="Código da empresa faturadora")
    CodigoFilialFat: int = Field(..., description="Código da filial faturadora")
    RazaoSocial: str = Field(..., description="Razão social da empresa")
    CNPJ: str = Field(..., description="CNPJ da empresa")
    Ativo: bool = Field(..., description="Status de atividade da empresa (ativo/inativo)")
    DataCadastro: datetime = Field(..., description="Data e hora do cadastro da empresa")
    DataAtualizacao: datetime = Field(..., description="Data e hora da última atualização")

    class Config:
        from_attributes = True


class UsuarioPublico(BaseModel):
    """Schema de exibição pública dos dados de um usuário"""
    ID: int = Field(..., description="Identificador único do usuário")
    Nome: str = Field(..., description="Nome completo do usuário")
    Email: EmailStr = Field(..., description="Endereço de e-mail corporativo")
    CNPJ: str = Field(..., description="CNPJ vinculado à conta do usuário")
    TipoAcesso: str = Field(..., description="Nível de acesso do usuário (Admin, Cliente, etc.)")
    PipedriveID: str = Field(..., description="Identificador do usuário no Pipedrive")
    CodigoCliente: int = Field(..., description="Código interno do cliente")
    IDEmpresa: Optional[int] = Field(None, description="ID da empresa à qual o usuário pertence")
    Status: bool = Field(..., description="Status de atividade do usuário (ativo/inativo)")
    DataCadastro: datetime = Field(..., description="Data e hora do cadastro do usuário")
    DataAtualizacao: datetime = Field(..., description="Data e hora da última atualização do cadastro")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Modelo de retorno para autenticação JWT"""
    access_token: str = Field(..., description="Token JWT gerado após login")
    token_type: str = Field(..., description="Tipo do token (geralmente 'bearer')")


class UsarioLogin(BaseModel):
    """Schema para autenticação do usuário"""
    email: EmailStr = Field(..., description="E-mail de login do usuário")
    senha: str = Field(..., description="Senha de acesso do usuário")


class ListaUsuarios(BaseModel):
    """Schema de listagem de usuários"""
    usuarios: list[UsuarioPublico] = Field(..., description="Lista de usuários cadastrados")


class AtualizarUsuarios(BaseModel):
    """Schema para atualização parcial dos dados de um usuário"""
    Nome: Optional[str] = Field(None, description="Novo nome do usuário")
    Email: Optional[EmailStr] = Field(None, description="Novo endereço de e-mail")
    SenhaAntiga: Optional[str] = Field(None, description="Senha atual do usuário para validação")
    SenhaNova: Optional[str] = Field(None, description="Nova senha a ser definida")
    CNPJ: Optional[str] = Field(None, description="CNPJ atualizado do usuário")
    TipoAcesso: Optional[str] = Field(None, description="Novo tipo de acesso do usuário")
    PipedriveID: Optional[str] = Field(None, description="Identificador atualizado no Pipedrive")
    CodigoCliente: Optional[str] = Field(None, description="Novo código interno do cliente")
    Status: Optional[bool] = Field(None, description="Status atualizado do usuário (ativo/inativo)")


class AtualizarUsuariosLista(AtualizarUsuarios):
    """Schema para atualização de usuários em lista"""
    ID: int = Field(..., description="Identificador único do usuário a ser atualizado")


class Organizacao(BaseModel):
    """Schema básico para identificação de organização"""
    CNPJ: Optional[str] = Field(None, description="CNPJ da organização")
    CodigoCliente: Optional[str] = Field(None, description="Código interno do cliente")


class EmpresaResponse(BaseModel):
    ID: int
    IDProprietario: Optional[int] = None
    IDSelecty: Optional[int] = None
    IDPipedrive: Optional[int] = None
    CodigoCliente: Optional[int] = None
    CodigoEmpresaFat: Optional[int] = None
    CodigoFilialFat: Optional[int] = None
    Nome: Optional[str] = None
    RazaoSocial: Optional[str] = None
    GrupoEconomico: Optional[str] = None
    CNPJ: Optional[str] = None
    Ativo: Optional[bool] = None
    DataCadastro: Optional[datetime] = None
    DataAtualizacao: Optional[datetime] = None
    EmailProprietario: Optional[str] = None
    NomeProprietario: Optional[str] = None

    class Config:
        from_attributes = True



class VWSolicitacaoSchema(BaseModel):
    ID: int
    ViewID: int
    Tipo: str
    Titulo: str
    Status: Optional[str] = None

    DataInicio: Optional[datetime] = None
    DataConclusao: Optional[datetime] = None
    DataCadastro: datetime

    ID_Usuario: int
    IDProprietario: Optional[int] = None

    Visivel: Optional[bool] = None
    TabelaOrigem: str

    class Config:
        from_attributes = True



# ========================================
# SCHEMAS DE ADMISSÃO E DEMISSÃO
# ========================================

class AdmissaoSchema(BaseModel):
    """Schema para solicitação de admissão de colaborador"""
    NomeUsuario: str = Field(..., description="Nome do usuário que está solicitando a admissão")
    GrupoEconomico: str = Field(..., description="Grupo econômico do usuário que está solicitando a admissão")
    TipoVaga: str = Field(..., description="Tipo da vaga (efetivo, temporário, etc.)")
    Cargo: str = Field(..., description="Cargo solicitado para contratação")
    CentroCusto: str = Field(..., description="Centro de custo associado à vaga")
    SetorTrabalho: str = Field(..., description="Setor ou departamento de atuação")
    ModalidadeTrabalho: str = Field(..., description="Modalidade de trabalho (presencial, híbrido, remoto)")
    MotivoContratacao: str = Field(..., description="Motivo da contratação")
    EscalaTrabalho: str = Field(..., description="Escala de trabalho (ex: 5x2, 12x36)")
    LocalTrabalho: str = Field(..., description="Endereço do local de trabalho")
    Salario: str = Field(..., description="Faixa salarial oferecida")
    DescricaoCargo: str = Field(..., description="Descrição detalhada das funções do cargo")
    PrecisaEPI: Optional[bool] = Field(None, description="Indica se é necessário uso de EPI")
    DescricaoEPI: Optional[str] = Field(None, description="Descrição dos EPIs necessários, se aplicável")
    NomeSubstituido: Optional[str] = Field(None, description="Nome do colaborador substituído, se aplicável")
    CPFSubstituido: Optional[str] = Field(None, description="CPF do colaborador substituído")
    MotivoSubstituido: Optional[str] = Field(None, description="Motivo da substituição")
    NomeResponsavelRH: str = Field(..., description="Nome do responsável do RH pela vaga")
    EmailResponsavelRH: str = Field(..., description="E-mail do responsável do RH")
    TelefoneResponsavelRH: str = Field(..., description="Telefone de contato do RH")
    NomeGestorPonto: str = Field(..., description="Nome do gestor responsável pelo ponto")
    EmailGestorPonto: str = Field(..., description="E-mail do gestor responsável pelo ponto")
    TelefoneGestorPonto: str = Field(..., description="Telefone do gestor responsável pelo ponto")
    NomePessoaPrimeiroDia: str = Field(..., description="Nome da pessoa que recepcionará o colaborador no primeiro dia")
    DepartamentoPrimeiroDia: str = Field(..., description="Departamento do primeiro dia de trabalho")
    HorarioPrimeiroDia: str = Field(..., description="Horário de chegada no primeiro dia")
    IDProprietario: Optional[str] = Field(None, description="Nome do proprietário da solicitação")
    DataInicio: Optional[datetime] = Field(None, description="Data prevista de início da contratação")
    DataConclusao: Optional[datetime] = Field(None, description="Data de encerramento da solicitação, se aplicável")


class DemissaoSchema(BaseModel):
    """Schema para solicitação de demissão de colaborador"""
    NomeUsuario: str = Field(..., description="Nome do usuário que está solicitando a admissão")
    GrupoEconomico: str = Field(..., description="Grupo econômico do usuário que está solicitando a admissão")
    CodigoFuncionario: int = Field(..., description="Código interno do funcionário")
    NomeFuncionario: str = Field(..., description="Nome completo do funcionário")
    Cargo: str = Field(..., description="Cargo atual do funcionário")
    CentroCusto: str = Field(..., description="Centro de custo vinculado")
    Empresa: str = Field(..., description="Nome da empresa contratante")
    Gestor: str = Field(..., description="Nome do gestor responsável")
    Salario: str = Field(..., description="Salário atual do funcionário")
    DataAdmissao: datetime = Field(..., description="Data de admissão do colaborador")
    DataDemissao: datetime = Field(..., description="Data de desligamento do colaborador")
    MotivoDemissao: str = Field(..., description="Motivo informado para demissão")
    FeriasVencidas: str = Field(..., description="Indica se há férias vencidas")
    AvisoPrevio: str = Field(..., description="Situação do aviso prévio (trabalhado, indenizado, etc.)")
    ConhecimentoDesligamento: str = Field(..., description="Confirmação do conhecimento do desligamento")
    ComunicadoPresencial: str = Field(..., description="Indica se o comunicado foi presencial")
    Endereco: str = Field(..., description="Local onde será realizado o desligamento")
    Horario: str = Field(..., description="Horário marcado para o desligamento")


# ========================================
# SCHEMAS DE SIMULAÇÃO E CÁLCULOS
# ========================================

class InsalubridadeSchema(BaseModel):
    """Schema de insalubridade"""
    percentual: str = Field(..., description="Percentual aplicado de insalubridade")
    grau: str = Field(..., description="Grau de insalubridade (mínimo, médio ou máximo)")


class GrupoSchema(BaseModel):
    """Schema genérico de grupo de encargos"""
    percentual: float = Field(..., description="Percentual aplicado no grupo")
    valor: float = Field(..., description="Valor total calculado para o grupo")


class TotalSchema(BaseModel):
    """Schema genérico de totalização"""
    percentual: float = Field(..., description="Percentual total aplicado")
    valor: float = Field(..., description="Valor total consolidado")


class TotalBeneficiosSchema(BaseModel):
    """Schema de benefícios fornecidos e repassados"""
    fornecido: float = Field(..., description="Valor dos benefícios fornecidos")
    repasse: float = Field(..., description="Valor dos benefícios repassados ao cliente")


class SimulacaoConsolidadaSchema(BaseModel):
    """Schema de consolidação da simulação financeira"""
    usuarioID: int = Field(..., description="Identificador do usuário que realizou a simulação")
    contratoID: str = Field(..., description="Identificador do contrato vinculado")
    servicoID: int = Field(..., description="Identificador do serviço simulado")
    taxa_administrativa: float = Field(..., description="Taxa administrativa aplicada")
    cargo: str = Field(..., description="Cargo utilizado na simulação")
    quantidade_colaboradores: int = Field(..., description="Quantidade de colaboradores envolvidos")
    periculosidade: str = Field(..., description="Descrição da periculosidade (se aplicável)")
    municipio_iss: int = Field(..., description="Código do município para cálculo de ISS")
    salario_base: float = Field(..., description="Salário base utilizado na simulação")
    salario_bruto: float = Field(..., description="Salário bruto total")
    insalubridade: Optional[InsalubridadeSchema] = Field(None, description="Informações de insalubridade")
    Grupo_A: GrupoSchema = Field(..., description="Informações do grupo A de encargos")
    Grupo_B: GrupoSchema = Field(..., description="Informações do grupo B de encargos")
    total_encargos_trabalistas: TotalSchema = Field(..., description="Total de encargos trabalhistas")
    total_encargos_tributarios: TotalSchema = Field(..., description="Total de encargos tributários")
    total_salario_bruto_encargos: float = Field(..., description="Total do salário bruto com encargos")
    total_beneficios: TotalBeneficiosSchema = Field(..., description="Total consolidado dos benefícios")
    exames_clinicos_aso: Optional[float] = Field(0, description="Valor de exames clínicos e ASO")
    subtotal_nota_fiscal: float = Field(..., description="Subtotal da nota fiscal")
    projecao_colaborador_administrado: float = Field(..., description="Projeção por colaborador administrado")
    projecao_total_nota_fiscal: float = Field(..., description="Projeção total da nota fiscal")


class BeneficioSchema(BaseModel):
    """Schema de benefícios incluídos na simulação"""
    id: int = Field(..., description="Identificador do benefício")
    quantidade: int = Field(..., description="Quantidade de benefícios aplicados")
    valorUnitario: float = Field(..., description="Valor unitário de cada benefício")
    fornecido: float = Field(..., description="Valor total fornecido")
    repasse: float = Field(..., description="Valor total repassado")


class EncargoSchema(BaseModel):
    """Schema de encargos trabalhistas"""
    id: int = Field(..., description="Identificador do encargo")
    percentual: float = Field(..., description="Percentual aplicado")
    valor: float = Field(..., description="Valor calculado do encargo")


class TributoSchema(BaseModel):
    """Schema de tributos aplicados"""
    id: int = Field(..., description="Identificador do tributo")
    percentual: float = Field(..., description="Percentual aplicado do tributo")
    valor: float = Field(..., description="Valor total do tributo")


class SimulacaoCadastroSchema(BaseModel):
    """Schema completo de cadastro de simulação"""
    simulacao_consolidada: SimulacaoConsolidadaSchema = Field(..., description="Dados consolidados da simulação")
    beneficios: List[BeneficioSchema] = Field(..., description="Lista de benefícios aplicados")
    encargos: List[EncargoSchema] = Field(..., description="Lista de encargos aplicados")
    tributos: List[TributoSchema] = Field(..., description="Lista de tributos aplicados")


class AlteracaoCentroSchema(BaseModel):
    ID_Usuario: Optional[int]
    NomeUsuario: str = Field(..., description="Nome do usuário que está solicitando a admissão")
    GrupoEconomico: str = Field(..., description="Grupo econômico do usuário que está solicitando a admissão")
    EmailUsuario: str = Field(..., description="E-mail do usuário que está solicitando a admissão")
    CodigoFuncionario: Optional[int]
    Nome: str
    Empresa: str
    Motivo: Optional[str]
    CentroCustoAtual: Optional[str]
    CentroCustoNovo: Optional[str]
    


class AlteracaoSalarioSchema(BaseModel):
    ID_Usuario: int
    NomeUsuario: str = Field(..., description="Nome do usuário que está solicitando a admissão")
    GrupoEconomico: str = Field(..., description="Grupo econômico do usuário que está solicitando a admissão")
    EmailUsuario: str = Field(..., description="E-mail do usuário que está solicitando a admissão")
    CodigoFuncionario: int
    Nome: str
    Empresa: str
    Motivo: str
    SalarioAtual: float
    SalarioNovo: float
    Percentual: float

class AlteracaoValeSchema(BaseModel):
    """Schema para criar uma nova alteração de vale"""
    ID_Usuario: int
    NomeUsuario: str = Field(..., description="Nome do usuário que está solicitando a admissão")
    GrupoEconomico: str = Field(..., description="Grupo econômico do usuário que está solicitando a admissão")
    EmailUsuario: str = Field(..., description="E-mail do usuário que está solicitando a admissão")
    CodigoFuncionario: int | str
    Nome: str
    Empresa: str
    Motivo: str 
    Desconto: Optional[float] = None
    Vigencia: Optional[datetime] = Field(None, description="Data de vigência da alteração")
    VRCheck: Optional[bool] = False
    VRAtual: Optional[float]
    VRNovo: Optional[float] 
    VACheck: Optional[bool] = False
    VAAtual: Optional[float] 
    VANovo: Optional[float] 

  

# ========================================
# SCHEMAS PARA NOTAS FISCAIS (DUPLICATAS)
# ========================================

class NotaFiscalResponse(BaseModel):
    """
    Schema de resposta para uma nota fiscal individual

    ⚠️ IMPORTANTE:
    - id (Duplicata) identifica a duplicata
    - numeroNFe é o número da Nota Fiscal emitida (pode ser None se ainda não foi emitida)
    """
    # Identificadores
    id: int = Field(..., description="ID da duplicata")
    numeroNFe: Optional[str] = Field(None, description="Número da NFe (emitida após aprovação)")

    # Datas
    dataEmissao: str = Field(..., description="Data de emissão no formato ISO")
    competencia: str = Field(..., description="Competência no formato MM/YYYY")
    vencimento: str = Field(..., description="Data de vencimento no formato ISO")

    # Valores e Status
    valorTotal: float = Field(..., description="Valor total da nota fiscal")
    status: Literal['a_vencer', 'vencida', 'paga'] = Field(..., description="Status calculado da nota")

    class Config:
        from_attributes = True


class ResumoNotasFiscaisResponse(BaseModel):
    """Schema de resposta para o resumo das notas fiscais"""
    totalNotasAVencer: int = Field(..., description="Quantidade de notas a vencer")
    valorNotasAVencer: float = Field(..., description="Valor total das notas a vencer")
    totalNotasVencidas: int = Field(..., description="Quantidade de notas vencidas")
    valorNotasVencidas: float = Field(..., description="Valor total das notas vencidas")


class ListaNotasFiscaisResponse(BaseModel):
    """Schema de resposta para listagem de notas fiscais com resumo"""
    notas: list[NotaFiscalResponse] = Field(..., description="Lista de notas fiscais")
    total: int = Field(..., description="Total de registros encontrados")
    resumo: ResumoNotasFiscaisResponse = Field(..., description="Resumo das notas fiscais")


class FiltroNotasFiscaisQuery(BaseModel):
    """Schema para filtros de query parameters"""
    codigo_cliente: Optional[int] = Field(None, description="Código do cliente")
    competencia: Optional[str] = Field(None, description="Competência no formato YYYYMM")
    status_nota: Optional[Literal['a_vencer', 'vencida', 'paga']] = Field(None, description="Filtro por status")
    data_inicio: Optional[str] = Field(None, description="Data início do período (YYYY-MM-DD)")
    data_fim: Optional[str] = Field(None, description="Data fim do período (YYYY-MM-DD)")
    limit: int = Field(100, ge=1, le=500, description="Limite de registros por página")
    offset: int = Field(0, ge=0, description="Offset para paginação")


class ArquivoNotaFiscalResponse(BaseModel):
    """Schema de resposta para informações do arquivo da nota fiscal"""
    nomeArquivo: str = Field(..., description="Nome esperado do arquivo TX2")
    duplicata: int = Field(..., description="Número da duplicata")
    numeroNFe: Optional[str] = Field(None, description="Número da Nota Fiscal emitida")
    codigoEmpresaFat: int = Field(..., description="Código da empresa faturadora")
    codigoFilialFat: int = Field(..., description="Código da filial faturadora")
    mensagem: str = Field(..., description="Mensagem sobre o status do arquivo")


# ========================================
# SCHEMAS PARA RPS
# ========================================

class RPSResponse(BaseModel):
    """
    Schema de resposta para um RPS individual

    ⚠️ IMPORTANTE:
    - duplicata é o identificador da RPS (campo Duplicata da TB_Duplicata)
    - numeroNFE é o número da Nota Fiscal (emitida após aprovação)
    - Campos da chave composta (codigoEmpresaFat, codigoFilialFat, duplicata) necessários para operações
    """
    # Identificadores - Chave composta
    duplicata: int = Field(..., description="Número da duplicata/RPS (campo Duplicata da TB_Duplicata)")
    numeroNFE: Optional[str] = Field(None, description="Número da Nota Fiscal (campo NroNFe)")

    # Chave composta (necessária para aprovação/reprovação)
    codigoEmpresaFat: int = Field(..., description="Código da empresa faturadora")
    codigoFilialFat: int = Field(..., description="Código da filial faturadora")

    # Datas
    dataEmissao: str = Field(..., description="Data de emissão no formato ISO")
    competencia: str = Field(..., description="Competência no formato MM/YYYY")
    vencimento: str = Field(..., description="Data de vencimento no formato ISO")

    # Valores e Status
    valorTotal: float = Field(..., description="Valor total do RPS")
    status: Literal['a_vencer', 'vencida', 'paga'] = Field(..., description="Status calculado do RPS")
    statusAprovacao: str = Field(default='pendente', description="Status de aprovação: pendente, aprovado ou reprovado")

    class Config:
        from_attributes = True


class ResumoRPSResponse(BaseModel):
    """Schema de resposta para o resumo dos RPS por status de aprovação"""
    totalRPSPendentes: int = Field(..., description="Quantidade de RPS pendentes de aprovação")
    valorRPSPendentes: float = Field(..., description="Valor total dos RPS pendentes")
    totalRPSAprovados: int = Field(..., description="Quantidade de RPS aprovados")
    valorRPSAprovados: float = Field(..., description="Valor total dos RPS aprovados")
    totalRPSReprovados: int = Field(..., description="Quantidade de RPS reprovados")
    valorRPSReprovados: float = Field(..., description="Valor total dos RPS reprovados")


class ListaRPSResponse(BaseModel):
    """Schema de resposta para listagem de RPS com resumo"""
    rps: list[RPSResponse] = Field(..., description="Lista de RPS")
    total: int = Field(..., description="Total de registros encontrados")
    resumo: ResumoRPSResponse = Field(..., description="Resumo dos RPS")


class ArquivoRPSResponse(BaseModel):
    """Schema de resposta para informações do arquivo do RPS"""
    nomeArquivo: str = Field(..., description="Nome esperado do arquivo TX2")
    duplicata: int = Field(..., description="Número da duplicata/RPS")
    numeroNFE: Optional[int] = Field(None, description="Número da NFE (se já foi emitida)")
    codigoEmpresaFat: int = Field(..., description="Código da empresa faturadora")
    codigoFilialFat: int = Field(..., description="Código da filial faturadora")
    mensagem: str = Field(..., description="Mensagem sobre o status do arquivo")


# ========================================
# SCHEMAS PARA APROVAÇÃO/REPROVAÇÃO DE RPS
# ========================================

class AprovarRPSRequest(BaseModel):
    """
    Schema de requisição para aprovar RPS

    ⚠️ IMPORTANTE: Usar os 3 campos da chave composta para identificar a RPS
    """
    codigo_empresa_fat: int = Field(..., description="Código da empresa faturadora")
    codigo_filial_fat: int = Field(..., description="Código da filial faturadora")
    duplicata: int = Field(..., description="Número da Duplicata (= número da RPS)")


class ReprovarRPSRequest(BaseModel):
    """
    Schema de requisição para reprovar RPS

    ⚠️ IMPORTANTE: Usar os 3 campos da chave composta para identificar a RPS
    """
    codigo_empresa_fat: int = Field(..., description="Código da empresa faturadora")
    codigo_filial_fat: int = Field(..., description="Código da filial faturadora")
    duplicata: int = Field(..., description="Número da Duplicata (= número da RPS)")
    motivo_reprovacao: str = Field(..., min_length=1, description="Motivo da reprovação (obrigatório)")
    descricao_reprovacao: str = Field(..., min_length=1, description="Descrição detalhada da reprovação (obrigatório)")


class AcaoRPSResponse(BaseModel):
    """Schema de resposta para ações de aprovação/reprovação"""
    sucesso: bool = Field(..., description="Indica se a ação foi bem-sucedida")
    mensagem: str = Field(..., description="Mensagem de sucesso ou erro")
    status_atual: str = Field(..., description="Status atual: 'aprovado' ou 'reprovado'")
    data_acao: str = Field(..., description="Data/hora da ação no formato ISO")


class HistoricoAprovacaoRPS(BaseModel):
    """Schema para histórico de aprovações de um RPS"""
    id: int = Field(..., description="ID do registro de aprovação")
    status_aprovacao: str = Field(..., description="Status: pendente, aprovado ou reprovado")
    tipo_acao: str = Field(..., description="Tipo: aprovacao, reprovacao ou cancelamento")
    motivo_reprovacao: Optional[str] = Field(None, description="Motivo da reprovação (se aplicável)")
    descricao_reprovacao: Optional[str] = Field(None, description="Descrição da reprovação (se aplicável)")
    nome_usuario: str = Field(..., description="Nome do usuário que executou a ação")
    email_usuario: str = Field(..., description="Email do usuário que executou a ação")
    data_acao: str = Field(..., description="Data/hora da ação no formato ISO")

    class Config:
        from_attributes = True


# ========================================
# SCHEMAS PARA MOTIVOS DE REPROVAÇÃO
# ========================================

class MotivoReprovacaoResponse(BaseModel):
    """Schema de resposta para motivo de reprovação"""
    id: int = Field(..., description="ID do motivo")
    codigo: str = Field(..., description="Código único do motivo")
    descricao: str = Field(..., description="Descrição curta do motivo")
    descricaoDetalhada: Optional[str] = Field(None, description="Descrição detalhada/orientações")

    class Config:
        from_attributes = True


# ========================================
# SCHEMAS PARA CONTRATOS
# ========================================

class ContratoResponse(BaseModel):
    """Schema de resposta para um contrato individual"""
    id: int = Field(..., description="ID do contrato")
    numero_contrato: str = Field(..., description="Número do contrato")
    cnpj: str = Field(..., description="CNPJ do cliente")
    razao_social: str = Field(..., description="Razão social do cliente")
    servicos_contemplados: str = Field(..., description="Descrição dos serviços contemplados")
    data_assinatura: str = Field(..., description="Data de assinatura (formato DD/MM/YYYY)")
    vigencia: Optional[str] = Field(None, description="Vigência do contrato (ex: 12 meses)")
    data_vencimento: Optional[str] = Field(None, description="Data de vencimento (formato DD/MM/YYYY)")
    valor: Optional[float] = Field(None, description="Valor do contrato")
    status: str = Field(..., description="Status: A=Ativo, I=Inativo")
    tem_arquivo_pdf: bool = Field(..., description="Indica se existe arquivo PDF disponível")

    class Config:
        from_attributes = True


class ListaContratosResponse(BaseModel):
    """Schema de resposta para listagem de contratos"""
    items: list[ContratoResponse] = Field(..., description="Lista de contratos")
    total: int = Field(..., description="Total de registros encontrados (sem paginação)")

    class Config:
        from_attributes = True


class DownloadContratoResponse(BaseModel):
    """Schema de resposta para download de contrato"""
    url: str = Field(..., description="URL do arquivo PDF no Azure Blob Storage")
    numero_contrato: str = Field(..., description="Número do contrato")
    disponivel_ate: Optional[str] = Field(None, description="Data/hora de expiração da URL (se aplicável)")

    class Config:
        from_attributes = True


class ListaMotivosReprovacaoResponse(BaseModel):
    """Schema de resposta para listagem de motivos"""
    motivos: list[MotivoReprovacaoResponse] = Field(..., description="Lista de motivos ativos")
    total: int = Field(..., description="Total de motivos encontrados")
