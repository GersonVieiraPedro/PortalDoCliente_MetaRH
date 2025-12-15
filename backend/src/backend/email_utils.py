import os, smtplib, logging, json, re, locale
from email.message import EmailMessage
from email.utils import formataddr
from typing import Optional, List
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import TB_Destinatario, DIM_Funcionalidade, DIM_Proprietario
from datetime import datetime, date

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# -------------------------------------------------------------------
# Configuração inicial do logger
# -------------------------------------------------------------------
logger = logging.getLogger("email_utils")
logger.setLevel(logging.INFO)

# Carrega variáveis de ambiente do arquivo .env (modo local)
load_dotenv()

# -------------------------------------------------------------------
# Função principal: enviar_email()
# -------------------------------------------------------------------
def enviar_email(
    destinatarios: List[str],               # Lista de destinatários principais (To)
    assunto: str,                           # Assunto do e-mail
    html_corpo: str,                        # Corpo do e-mail em HTML
    arquivo_bytes: Optional[bytes] = None,  # Bytes do arquivo para anexar (opcional)
    nome_arquivo: Optional[str] = None,     # Nome do arquivo anexado (ex: "orcamento.pdf")
    copia: Optional[List[str]] = None,      # Lista de cópia (Cc)
    copia_oculta: Optional[List[str]] = None,  # Lista de cópia oculta (Bcc)
    remetente: Optional[str] = None,        # E-mail do remetente (pode vir do .env)
    senha: Optional[str] = None,            # Senha ou App Password do remetente
    nome_remetente: Optional[str] = None,   # Nome exibido no remetente (ex: "Equipe Portal Conecta")
    smtp_host: str = "smtp.gmail.com",      # Host SMTP padrão (pode ser Office365, etc)
    smtp_port: int = 587                    # Porta padrão com TLS
):
    """
    Envia e-mails em formato HTML com suporte a anexos (PDF),
    múltiplos destinatários, cópias (Cc) e cópias ocultas (Bcc).

    Essa função lê automaticamente as variáveis de ambiente:
      - EMAIL_REMETENTE
      - EMAIL_SENHA

    Se estiver rodando no Azure, essas variáveis devem estar
    configuradas nas Configurações do Aplicativo (App Settings).
    """

    logger.info("[LOG] Iniciando processo de envio de e-mail...")
    logger.info(f"[LOG] Assunto: {assunto}")
    logger.info(f"[LOG] Destinatários: {destinatarios}")
    logger.info(f"[LOG] Cópia: {copia if copia else 'Nenhuma'}")
    logger.info(f"[LOG] Cópia Oculta: {copia_oculta if copia_oculta else 'Nenhuma'}")

    # -------------------------------------------------------------------
    # Carrega remetente e senha do .env se não foram passados por parâmetro
    # -------------------------------------------------------------------
    remetente = remetente or os.getenv("EMAIL_REMETENTE")
    senha = senha or os.getenv("EMAIL_SENHA")

    # Loga se as variáveis de ambiente foram carregadas
    logger.info(f"[DEBUG] Remetente definido? {'Sim' if remetente else 'Não'}")
    logger.info(f"[DEBUG] Senha definida? {'Sim' if senha else 'Não'}")

    # -------------------------------------------------------------------
    # Validação: Remetente e senha obrigatórios
    # -------------------------------------------------------------------
    if not remetente or not senha:
        logger.error("[ERRO] Remetente ou senha não configurados. "
                     "Verifique as variáveis de ambiente EMAIL_REMETENTE e EMAIL_SENHA.")
        raise ValueError("Remetente ou senha não configurados.")

    # -------------------------------------------------------------------
    # Montagem da mensagem de e-mail
    # -------------------------------------------------------------------
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = formataddr((nome_remetente or remetente, remetente))
    msg["To"] = ", ".join(destinatarios)

    if copia:
        msg["Cc"] = ", ".join(copia)

    # Adiciona o corpo em HTML
    msg.add_alternative(html_corpo, subtype="html")

    # -------------------------------------------------------------------
    # Se houver arquivo anexo, adiciona ao e-mail
    # -------------------------------------------------------------------
    if arquivo_bytes and nome_arquivo:
        msg.add_attachment(
            arquivo_bytes,
            maintype="application",
            subtype="pdf",
            filename=nome_arquivo
        )
        logger.info(f"[LOG] Anexo adicionado: {nome_arquivo} ({len(arquivo_bytes)} bytes)")

    # -------------------------------------------------------------------
    # Monta a lista final de destinatários (To + Cc + Bcc)
    # -------------------------------------------------------------------
    destinatarios_envio = destinatarios + (copia or []) + (copia_oculta or [])
    logger.info(f"[LOG] Total de destinatários reais: {len(destinatarios_envio)}")

    # -------------------------------------------------------------------
    # Envio via servidor SMTP
    # -------------------------------------------------------------------
    try:
        logger.info(f"[LOG] Conectando ao servidor SMTP: {smtp_host}:{smtp_port}")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Ativa criptografia TLS
            server.login(remetente, senha)  # Faz login no servidor SMTP
            server.send_message(msg, to_addrs=destinatarios_envio)
        logger.info(f"[LOG] E-mail enviado com sucesso para {destinatarios_envio}")

    except Exception as e:
        logger.error(f"[ERRO] Falha ao enviar e-mail: {str(e)}")
        raise

    logger.info("[LOG] Finalizado envio de e-mail com sucesso")



def listar_destinatarios(session: Session, id_funcionalidade: int, completo: bool):
    """
    Consulta TB_Destinatario + DIM_Proprietario e retorna:
    
    completo=False:
        {
            "Nome": "Time Admins",
            "Email": ["email1", "email2", ...]
        }

    completo=True:
        {
            "Nome": "Time Admins",
            "Email": [{"id":1, "email":"..."}, ...]
        }
    """

    # Consulta base
    stmt = (
        select(
            TB_Destinatario.Nome,
            DIM_Proprietario.ID,
            DIM_Proprietario.Email
        )
        .join(TB_Destinatario, DIM_Proprietario.ID == TB_Destinatario.IDProprietario)
        .where(TB_Destinatario.Ativo == True)
        .where(TB_Destinatario.IDFuncionalidade == id_funcionalidade)
    )

    rows = session.execute(stmt).all()

    if not rows:
        return {"Nome": "", "Email": []}

    # Nome (sempre igual entre as linhas)
    nome_time = rows[0][0]

    # Monta resposta conforme necessidade
    if completo:
        emails = [
            {"id": row[1], "email": row[2]}
            for row in rows
            if row[2]
        ]
    else:
        emails = [
            row[2]
            for row in rows
            if row[2]
        ]

    return {
        "Nome": nome_time,
        "Email": emails
    }

def moeda(v):
    if v is None:
        return ""
    try:
        valor = float(v)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return v
    
def data_format(v):
    if not v:
        return ""

    if isinstance(v, (datetime, date)):
        return v.strftime("%d/%m/%Y")

    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(v, fmt).strftime("%d/%m/%Y")
        except:
            pass

    return v


def telefone_format(v):
    if not v:
        return ""
    numeros = re.sub(r"\D", "", v)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return v


def percentual_format(v):
    if v is None:
        return ""
    try:
        valor = float(v)
        return f"{valor:.2f}%"
    except:
        return v


def formatar_alteracao(d):

    # Labels amigáveis para todos os campos de alteração
    labels = {
        "CodigoFuncionario": "Matrícula",
        "Nome": "Nome",
        "Empresa": "Empresa",
        "Motivo": "Motivo da Alteração",
        "CentroCustoAtual": "Centro de Custo Atual",
        "CentroCustoNovo": "Novo Centro de Custo",
        "SalarioAtual": "Salário Atual",
        "SalarioNovo": "Novo Salário",
        "Percentual": "(%) Salário",
        "JornadaAtual": "Jornada Atual",
        "JornadaNovo": "Nova Jornada",
        "HorarioAtual": "Horário Atual",
        "HorarioAtualDescricao": "Descrição do Horário Atual",
        "HorarioNovo": "Novo Horário",
        "HorarioNovoDescricao": "Descrição do Novo Horário",
        "SalarioAtualizado": "Salário Atualizado",
        "Vigencia": "Vigência",
        "EmailUsuario": "E-mail do Usuário",
        "VRAtual": "Vale Refeição Atual",
        "VRNovo": "Novo Vale Refeição",
        "VAAtual": "Vale Alimentação Atual",
        "VANovo": "Novo Vale Alimentação",
    }

    detalhes_formatados = {}

    for key, value in d.items():
                
        if key == "Vigencia":
            value = data_format(value)
        
        if key in ["SalarioAtual", "SalarioNovo", "SalarioAtualizado", "VRAtual", "VRNovo", "VAAtual", "VANovo"]:
            value = moeda(value)

        if key in ["Percentual", "Desconto"]:
            value = percentual_format(value)

        # Aplica label se existir
        detalhes_formatados[labels.get(key, key)] = value

    return detalhes_formatados



def formatar_jornada(d):

    
    labels = {
        "CodigoFuncionario": "Matrícula",
        "Nome": "Nome",
        "Empresa": "Empresa",
        "Motivo": "Motivo da Alteração",
        "JornadaAtual": "Jornada Atual",
        "JornadaNovo": "Nova Jornada",
        "HorarioAtual": "Horário Atual",
        "HorarioAtualDescricao": "Descrição do Horário Atual",
        "HorarioNovo": "Novo Horário",
        "HorarioNovoDescricao": "Descrição do Novo Horário",
        "SalarioAtualizado": "Salário Atualizado",
        "Vigencia": "Vigência",
        "EmailUsuario": "E-mail do Usuário"
    }

    detalhes_formatados = {}

    for key, value in d.items():

        if key == "Vigencia":
            value = data_format(value)

        if key == "SalarioAtualizado":
            value = moeda(value)

        # atribui o nome formatado
        detalhes_formatados[labels.get(key, key)] = value

    return detalhes_formatados


def formatar_admissao(d):

    # Labels amigáveis para todos os campos de admissão
    labels = {
        "Cargo": "Cargo",
        "TipoVaga": "Tipo de Vaga",
        "CentroCusto": "Centro de Custo",
        "SetorTrabalho": "Setor de Trabalho",
        "ModalidadeTrabalho": "Modalidade de Trabalho",
        "MotivoContratacao": "Motivo da Contratação",
        "EscalaTrabalho": "Escala de Trabalho",
        "LocalTrabalho": "Local de Trabalho",
        "Salario": "Salário",
        "DescricaoCargo": "Descrição do Cargo",
        "PrecisaEPI": "Precisa de EPI?",
        "DescricaoEPI": "Descrição do EPI",
        "NomeSubstituido": "Nome do Substituído",
        "CPFSubstituido": "CPF do Substituído",
        "MotivoSubstituido": "Motivo da Substituição",
        "NomeResponsavelRH": "Responsável RH",
        "EmailResponsavelRH": "E-mail RH",
        "TelefoneResponsavelRH": "Telefone RH",
        "NomeGestorPonto": "Gestor do Ponto",
        "EmailGestorPonto": "E-mail do Gestor",
        "TelefoneGestorPonto": "Telefone do Gestor",
        "NomePessoaPrimeiroDia": "(1º Dia) Pessoa Responsável",
        "DepartamentoPrimeiroDia": "(1º Dia) Departamento",
        "HorarioPrimeiroDia": "(1º Dia) Horário",
    }

    detalhes_formatados = {}

    for key, value in d.items():

        # Regras específicas
        if key == "Salario":
            value = moeda(value)

        if "Telefone" in key:
            value = telefone_format(value)

        if "Data" in key or "Vigencia" in key:
            value = data_format(value)

        # Aplica label se existir
        detalhes_formatados[labels.get(key, key)] = value

    return detalhes_formatados


def formatar_demissao(d):

    # Labels amigáveis para todos os campos de demissão
    labels = {
        "CodigoFuncionario": "Matrícula",
        "NomeFuncionario": "Nome",
        "Empresa": "Empresa",
        "Salario": "Salário",
        "Cargo": "Cargo",
        "Gestor": "Gestor Imediato",
        "CentroCusto": "Centro de Custo",
        "DataAdmissao": "Data de Admissão",
        "DataDemissao": "Data da Demissão",
        "MotivoDemissao": "Motivo da Demissão",
        "FeriasVencidas": "Férias Vencidas?",
        "AvisoPrevio": "Aviso Prévio",
        "ConhecimentoDesligamento": "Tem Conhecimento do desligamento?",
        "ComunicadoPresencial": "Comunicado Presencialmente?",
        "Endereco": "Endereço",
        "Horario": "Horário de Término",
    }

    detalhes_formatados = {}

    for key, value in d.items():

        # Regras específicas
        if key == "Salario":
            value = moeda(value)

        if "Telefone" in key:
            value = telefone_format(value)

        if "Data" in key:
            value = data_format(value)

        # Aplica label se existir
        detalhes_formatados[labels.get(key, key)] = value

    return detalhes_formatados
