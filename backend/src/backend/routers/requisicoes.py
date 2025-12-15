import os, json, logging
from datetime import datetime, date
from http import HTTPStatus
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, Body, File, Form, UploadFile #type: ignore
from ..database import AtivarSession
from ..aruze_storage import upload_xlsx, azure_container
from ..email_templates import  render_alteracao_email_jinja
from ..email_utils import  formatar_admissao, formatar_demissao, formatar_alteracao, formatar_jornada, listar_destinatarios, enviar_email
from ..models import TB_AlteracaoCentro, TB_AlteracaoSalario, TB_AlteracaoVale, TB_Demissao, TB_Admissao, TB_AlteracaoJornada
from ..schema import AdmissaoSchema, AlteracaoCentroSchema, DemissaoSchema, Resposta, AlteracaoSalarioSchema, AlteracaoValeSchema

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL") or os.environ.get("API_BASE_URL")

# ============================================================
# CONFIGURAÇÃO DE LOG
# ============================================================
# Cria logger principal para registrar eventos no console e no Azure
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/requisicoes", tags=["Requisições"])


# ============================================================
# ROTA: Cadastro de Admissão
# ============================================================
@router.post("/Admissao/Cadastro", status_code=HTTPStatus.CREATED, response_model=Resposta)
def Cadastrar_Admissao(
    ID_Usuario: int,
    Admissao: AdmissaoSchema,
    Session=Depends(AtivarSession)
):
    """
    Cadastra uma nova solicitação de admissão.
    Inclui tratamento de exceções e logs detalhados.
    """
    print("dados: ", Admissao)
    logger.info("[LOG] Iniciando cadastro de admissão para ID_Usuario: %d", ID_Usuario)
    PrecisaEPI = None
    if Admissao.PrecisaEPI == False:
        PrecisaEPI = 0
    else :
        PrecisaEPI = 1

    try:
        # Cria o registro de admissão com base no schema recebido
        cadastro = TB_Admissao(
            TipoVaga=Admissao.TipoVaga,
            Cargo=Admissao.Cargo,
            CentroCusto=Admissao.CentroCusto,
            SetorTrabalho=Admissao.SetorTrabalho,
            ModalidadeTrabalho=Admissao.ModalidadeTrabalho,
            MotivoContratacao=Admissao.MotivoContratacao,
            EscalaTrabalho=Admissao.EscalaTrabalho,
            LocalTrabalho=Admissao.LocalTrabalho,
            Salario=Admissao.Salario,
            DescricaoCargo=Admissao.DescricaoCargo,
            PrecisaEPI=PrecisaEPI,
            DescricaoEPI=Admissao.DescricaoEPI or None,
            NomeSubstituido=Admissao.NomeSubstituido or None,
            CPFSubstituido=Admissao.CPFSubstituido or None,
            MotivoSubstituido=Admissao.MotivoSubstituido or None,
            NomeResponsavelRH=Admissao.NomeResponsavelRH,
            EmailResponsavelRH=Admissao.EmailResponsavelRH,
            TelefoneResponsavelRH=Admissao.TelefoneResponsavelRH,
            NomeGestorPonto=Admissao.NomeGestorPonto,
            EmailGestorPonto=Admissao.EmailGestorPonto,
            TelefoneGestorPonto=Admissao.TelefoneGestorPonto,
            NomePessoaPrimeiroDia=Admissao.NomePessoaPrimeiroDia,
            DepartamentoPrimeiroDia=Admissao.DepartamentoPrimeiroDia,
            HorarioPrimeiroDia=Admissao.HorarioPrimeiroDia,
        )
        cadastro.ID_Usuario = ID_Usuario

        Session.add(cadastro)
        Session.commit()

        logger.info("[LOG] Solicitação de admissão salva com sucesso para ID_Usuario: %d", ID_Usuario)


        # ------------------------------------------
        # Remover dados que não devem aparecer no email
        # ------------------------------------------
        ad = Admissao.model_dump()

        dados = {}

        for key, value in ad.items():

            # remover sempre
            if key in ["ID_Usuario", "NomeUsuario", "GrupoEconomico", "Email", "IDProprietario", "DataInicio", "DataConclusao", "Status"]:
                continue

            # remover DescricaoEPI se PrecisaEPI == False
            if ad.get("PrecisaEPI") is False and key == "DescricaoEPI":
                continue

            # remover dados de substituição se motivo for SUBSTITUIÇÃO
            if ad.get("MotivoContratacao") != "SUBSTITUIÇÃO" and key in ["NomeSubstituido", "CPFSubstituido", "MotivoSubstituido"]:
                continue

            dados[key] = value


        # Formatação opcional para deixar amigável
        dados_detalhes = formatar_admissao(dados)

        # ------------------------------------------
        # Buscar destinatários (ID funcionalidade = 5)
        # ------------------------------------------
        destinatarios = listar_destinatarios(Session, id_funcionalidade=1, completo=True)

        nome_destino = destinatarios.get("Nome") or "Colaborador"

        mensagem_email = (
            f"Olá {nome_destino},<br>"
            f"{Admissao.NomeUsuario} do grupo {Admissao.GrupoEconomico} solicitou uma admissão de um colaborador.<br>"
            f"Por favor, revise os detalhes abaixo e tome as ações necessárias."
        )

        # ------------------------------------------
        # Enviar email para cada destinatário
        # ------------------------------------------

        for dest in destinatarios.get("Email", []):
            link = f"{API_BASE_URL}/mensageria/processo?id={cadastro.ID}&p={dest.get('id')}&f=5&a=1"

            # Renderiza com Jinja2
            html_final = render_alteracao_email_jinja(
                titulo=f"#{cadastro.ID:04d} - Solicitação de Admissão",
                mensagem=mensagem_email,
                detalhes=dados_detalhes,
                link=link
            )

            enviar_email(
                assunto=f"#{cadastro.ID:04d} - Solicitação de Admissão",
                destinatarios=[dest.get("email")],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )

        return Resposta(
            status="Sucesso",
            mensagem="Recebemos sua solicitação de admissão."
        )

    except SQLAlchemyError as e:
        # Erro relacionado ao banco de dados
        Session.rollback()
        logger.error("[ERRO] Falha ao salvar admissão no banco: %s", e, exc_info=True)
        return Resposta(
            status="Erro",
            mensagem="Ocorreu um erro ao salvar sua solicitação de admissão. Tente novamente."
        )

    except Exception as e:
        # Qualquer outro erro inesperado
        logger.exception("[ERRO] Erro inesperado no cadastro de admissão: %s", e)
        return Resposta(
            status="Erro",
            mensagem="Erro interno no servidor durante o cadastro de admissão."
        )


# ============================================================
# ROTA: Cadastro de Demissão
# ============================================================
@router.post("/Demissao/Cadastro", status_code=HTTPStatus.CREATED, response_model=Resposta)
def Cadastrar_Demissao(
    ID_Usuario: int,
    Demissao: DemissaoSchema,
    Session=Depends(AtivarSession)
):
    """
    Cadastra uma nova solicitação de demissão.

    - Valida dados recebidos
    - Salva no banco
    - Gera logs completos
    - Envia e-mail aos responsáveis
    - Retorna sempre o modelo `Resposta` para evitar erros de validação
    """

    logger.info(
        "[LOG] Iniciando cadastro de demissão | ID_Usuario=%d | Dados=%s",
        ID_Usuario, Demissao.model_dump()
    )

    try:
        # ============================================================
        # 1) Construção do objeto para salvar
        # ============================================================
        cadastro = TB_Demissao(
            ID_Usuario=ID_Usuario,
            CodigoFuncionario=Demissao.CodigoFuncionario,
            NomeFuncionario=Demissao.NomeFuncionario,
            Empresa=Demissao.Empresa,
            Gestor=Demissao.Gestor,
            Salario=Demissao.Salario,
            Cargo=Demissao.Cargo,
            CentroCusto=Demissao.CentroCusto,
            DataAdmissao=Demissao.DataAdmissao,
            DataDemissao=Demissao.DataDemissao,
            MotivoDemissao=Demissao.MotivoDemissao,
            FeriasVencidas=Demissao.FeriasVencidas,
            AvisoPrevio=Demissao.AvisoPrevio,
            ConhecimentoDesligamento=Demissao.ConhecimentoDesligamento,
            ComunicadoPresencial=Demissao.ComunicadoPresencial,
            Endereco=Demissao.Endereco,
            Horario=Demissao.Horario,
        )

        Session.add(cadastro)
        Session.commit()
        Session.refresh(cadastro)

        logger.info(
            "[LOG] Demissão cadastrada com sucesso | ID=%d | Usuario=%d",
            cadastro.ID, ID_Usuario
        )

        # ============================================================
        # 2) Preparação dos dados limpos para email
        # ============================================================
        dados_detalhes = {
            key: value
            for key, value in Demissao.model_dump().items()
            if key not in {
                "ID_Usuario", "NomeUsuario", "GrupoEconomico", "IDProprietario", "DataInicio", "DataConclusao", "Status"
            }
        }

        dados_detalhes = formatar_demissao(dados_detalhes)

        # ============================================================
        # 3) Buscar destinatários (funcionalidade=6)
        # ============================================================
        destinatarios = listar_destinatarios(Session, id_funcionalidade=1, completo=True)

        nome_destino = destinatarios.get("Nome") or "Colaborador"

        mensagem_email = (
            f"Olá {nome_destino},<br>"
            f"{Demissao.NomeUsuario} do grupo {Demissao.GrupoEconomico} solicitou uma demissão de um colaborador.<br>"
            f"Por favor, revise os detalhes abaixo e tome as ações necessárias."
        )

        # ============================================================
        # 4) Disparar e-mails
        # ============================================================
        for dest in destinatarios.get("Email", []):
            link = (
                f"{API_BASE_URL}/mensageria/processo?"
                f"id={cadastro.ID}&p={dest.get('id')}&f=6&a=1"
            )

            html_final = render_alteracao_email_jinja(
                titulo=f"#{cadastro.ID:04d} - Solicitação de Demissão",
                mensagem=mensagem_email,
                detalhes=dados_detalhes,
                link=link
            )

            enviar_email(
                assunto=f"#{cadastro.ID:04d} - Solicitação de Demissão",
                destinatarios=[dest.get("email")],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )

        # ============================================================
        # 5) Resposta final (sempre envia modelo válido)
        # ============================================================
        return Resposta(
            status="Sucesso",
            mensagem="Sua solicitação de demissão foi registrada com sucesso."
        )

    # ============================================================
    # ERROS
    # ============================================================

    except SQLAlchemyError as e:
        Session.rollback()
        logger.error(
            "[ERRO] Falha ao salvar demissão no banco | Usuario=%d | Erro=%s",
            ID_Usuario, str(e),
            exc_info=True
        )
        return Resposta(
            status="Erro",
            mensagem="Erro ao salvar no banco. Tente novamente."
        )

    except Exception as e:
        logger.exception(
            "[ERRO] Erro inesperado no cadastro de demissão | Usuario=%d | Erro=%s",
            ID_Usuario, str(e)
        )
        return Resposta(
            status="Erro",
            mensagem="Erro interno no servidor."
        )




# ============================================================
# ROTA: Alteração de Centro de Custo
# ============================================================
@router.post("/Alteracao/CentroCusto", status_code=HTTPStatus.CREATED, response_model=Resposta)
def Alteracao_CentroCusto(
    data: AlteracaoCentroSchema = Body(...),
    Session=Depends(AtivarSession)
):
    """
    Registra uma nova solicitação de alteração de centro de custo.
    Inclui logs, validação e tratamento de exceções.
    """

    logger.info("[LOG] Iniciando alteração de centro de custo. Usuário: %s | Funcionário: %s",
                data.ID_Usuario, data.CodigoFuncionario)

    try:
        # Criação do registro
        registro = TB_AlteracaoCentro(
            ID_Usuario=data.ID_Usuario,
            CodigoFuncionario=data.CodigoFuncionario,
            Nome=data.Nome,
            Empresa=data.Empresa,
            Motivo=data.Motivo,
            CentroCustoAtual=data.CentroCustoAtual,
            CentroCustoNovo=data.CentroCustoNovo
        )

        #PRECISA CRIAR LOGICA DE ENVIAR EMAIL

        Session.add(registro)
        Session.commit()
        Session.refresh(registro)

        logger.info("[LOG] Alteração de centro de custo salva com sucesso. ID Registro: %s", registro.ID)


        # ============================================================
        # 2) Preparação dos dados limpos para email
        # ============================================================
        dados_detalhes = {
            key: value
            for key, value in data.model_dump().items()
            if key not in {
                "ID_Usuario", "NomeUsuario", "GrupoEconomico"
            }
        }

        dados_detalhes = formatar_alteracao(dados_detalhes)

        # ============================================================
        # 3) Buscar destinatários (funcionalidade=2)
        # ============================================================
        destinatarios = listar_destinatarios(Session, id_funcionalidade=1, completo=True)

        nome_destino = destinatarios.get("Nome") or "Colaborador"

        mensagem_email = (
            f"Olá {nome_destino},<br>"
            f"{data.NomeUsuario} do grupo {data.GrupoEconomico} solicitou uma alteração de centro de custo.<br>"
            f"Por favor, revise os detalhes abaixo e tome as ações necessárias."
        )

        # ============================================================
        # 4) Disparar e-mails
        # ============================================================
        for dest in destinatarios.get("Email", []):
            link = (
                f"{API_BASE_URL}/mensageria/processo?"
                f"id={registro.ID}&p={dest.get('id')}&f=2&a=1"
            )

            html_final = render_alteracao_email_jinja(
                titulo=f"#{registro.ID:04d} - Solicitação de Alteração de Centro de Custo",
                mensagem=mensagem_email,
                detalhes=dados_detalhes,
                link=link
            )

            enviar_email(
                assunto=f"#{registro.ID:04d} - Solicitação de Alteração de Centro de Custo",
                destinatarios=[dest.get("email")],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )


        return Resposta(
            status="Sucesso",
            mensagem="Alteração realizada com sucesso."
        )

    except SQLAlchemyError as e:
        Session.rollback()
        logger.error("[ERRO] Falha ao salvar alteração de centro de custo: %s", e, exc_info=True)
        return Resposta(
            status="Erro",
            mensagem="Ocorreu um erro ao salvar a solicitação de alteração. Tente novamente."
        )

    except Exception as e:
        logger.exception("[ERRO] Erro inesperado na alteração de centro de custo: %s", e)
        return Resposta(
            status="Erro",
            mensagem="Erro interno no servidor durante a alteração de centro de custo."
        )
    

# ============================================================
# ROTA: Alteração de Salário
# ============================================================
@router.post("/Alteracao/Salario", status_code=HTTPStatus.CREATED, response_model=Resposta)
def Alteracao_Salario(
    data: AlteracaoSalarioSchema = Body(...),
    Session=Depends(AtivarSession)
):
    """
    Registra uma nova solicitação de alteração de salário.
    Inclui logs, validação e tratamento de exceções.
    """

    logger.info(
        "[LOG] Iniciando alteração salarial. Usuário: %s | Funcionário: %s",
        data.ID_Usuario, data.CodigoFuncionario
    )

    try:
        # Criação do registro
        registro = TB_AlteracaoSalario(
            ID_Usuario=data.ID_Usuario,
            CodigoFuncionario=data.CodigoFuncionario,
            Nome=data.Nome,
            Empresa=data.Empresa,
            Motivo=data.Motivo,
            SalarioAtual=data.SalarioAtual,
            SalarioNovo=data.SalarioNovo,
            Percentual=data.Percentual
        )

        # FUTURAMENTE: Envio de e-mail
        # ex.: enviar_email_alteracao_salario(data)

        Session.add(registro)
        Session.commit()
        Session.refresh(registro)

        logger.info(
            "[LOG] Alteração salarial salva com sucesso. ID Registro: %s",
            registro.ID
        )

        # ============================================================
        # 2) Preparação dos dados limpos para email
        # ============================================================

        dados_detalhes = {
            key: value
            for key, value in data.model_dump().items()
            if key not in {
                "ID_Usuario", "NomeUsuario", "GrupoEconomico"
            }
        }

        dados_detalhes = formatar_alteracao(dados_detalhes)



        # ============================================================
        # 3) Buscar destinatários (funcionalidade=4)
        # ============================================================
        destinatarios = listar_destinatarios(Session, id_funcionalidade=1, completo=True)

        nome_destino = destinatarios.get("Nome") or "Colaborador"

        mensagem_email = (
            f"Olá {nome_destino},<br>"
            f"{data.NomeUsuario} do grupo {data.GrupoEconomico} solicitou uma alteração de salário.<br>"
            f"Por favor, revise os detalhes abaixo e tome as ações necessárias."
        )

        # ============================================================
        # 4) Disparar e-mails
        # ============================================================
        for dest in destinatarios.get("Email", []):
            link = (
                f"{API_BASE_URL}/mensageria/processo?"
                f"id={registro.ID}&p={dest.get('id')}&f=2&a=1"
            )

            html_final = render_alteracao_email_jinja(
                titulo=f"#{registro.ID:04d} - Solicitação de Alteração de Salário",
                mensagem=mensagem_email,
                detalhes=dados_detalhes,
                link=link
            )

            enviar_email(
                assunto=f"#{registro.ID:04d} - Solicitação de Alteração de Salário",
                destinatarios=[dest.get("email")],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )


        return Resposta(
            status="Sucesso",
            mensagem="Alteração salarial registrada com sucesso."
        )

    except SQLAlchemyError as e:
        Session.rollback()
        logger.error(
            "[ERRO] Falha ao salvar alteração salarial: %s",
            e, exc_info=True
        )
        return Resposta(
            status="Erro",
            mensagem="Ocorreu um erro ao salvar a alteração salarial. Tente novamente."
        )

    except Exception as e:
        logger.exception(
            "[ERRO] Erro inesperado na alteração de salário: %s",
            e
        )
        return Resposta(
            status="Erro",
            mensagem="Erro interno no servidor durante a alteração salarial."
        )


# ============================================================
# ROTA: Alteração de Vale Alimentação e Vale Refeição
# ============================================================
@router.post("/Alteracao/Vale", status_code=HTTPStatus.CREATED, response_model=Resposta)
def Alteracao_Vale_Alimentacao_Refeicao(
    data: AlteracaoValeSchema = Body(...),
    Session=Depends(AtivarSession)
):
    """
    Registra uma nova solicitação de alteração de vale refeição e alimentação.
    Inclui logs, validação e tratamento de exceções.
    """

    logger.info(
        "[LOG] Iniciando alteração vale. Usuário: %s | Funcionário: %s",
        data.ID_Usuario, data.CodigoFuncionario
    )

    try:
        # Criação do registro
        registro = TB_AlteracaoVale(
            ID_Usuario=data.ID_Usuario,
            CodigoFuncionario=data.CodigoFuncionario,
            Nome= data.Nome,
            Empresa=data.Empresa,
            Motivo=data.Motivo,
            Desconto=data.Desconto or None,
            Vigencia=data.Vigencia or None,
            VRCheck= data.VRCheck,
            VRAtual=data.VRAtual,
            VRNovo=data.VRNovo,
            VACheck= data.VACheck,
            VAAtual=data.VAAtual,
            VANovo=data.VANovo
        )

        Session.add(registro)
        Session.commit()
        Session.refresh(registro)

        logger.info(
            "[LOG] Alteração vale salva com sucesso. ID Registro: %s",
            registro.ID
        )

        # ------------------------------------------
        # Remover dados que não devem aparecer no email
        # ------------------------------------------
        ad = data.model_dump()

        dados = {}

        for key, value in ad.items():


            # remover VA se VACheck == False
            if ad.get("VACheck") is False and key in ["VAAtual", "VANovo"]:
                continue

            # remover VR se VRCheck == False
            if ad.get("VRCheck") is False and key in ["VRAtual", "VRNovo"]:
                continue

            # remover sempre
            if key in ["ID_Usuario", "NomeUsuario", "GrupoEconomico", "Email", "VRCheck", "VACheck"]:
                continue
    
            dados[key] = value
        
        dados_detalhes = formatar_alteracao(dados)

        # ============================================================
        # 3) Buscar destinatários (funcionalidade=3)
        # ============================================================

        destinatarios = listar_destinatarios(Session, id_funcionalidade=1, completo=True)

        nome_destino = destinatarios.get("Nome") or "Colaborador"

        mensagem_email = (
            f"Olá {nome_destino},<br>"
            f"{data.NomeUsuario} do grupo {data.GrupoEconomico} solicitou uma alteração de vale refeição e/ou alimentação.<br>"
            f"Por favor, revise os detalhes abaixo e tome as ações necessárias."
        )

        # ============================================================
        # 4) Disparar e-mails
        # ============================================================
        for dest in destinatarios.get("Email", []):
            link = (
                f"{API_BASE_URL}/mensageria/processo?"
                f"id={registro.ID}&p={dest.get('id')}&f=3&a=1"
            )

            html_final = render_alteracao_email_jinja(
                titulo=f"#{registro.ID:04d} - Alteração de Vale Refeição e Alimentação",
                mensagem=mensagem_email,
                detalhes=dados_detalhes,
                link=link
            )

            enviar_email(
                assunto=f"#{registro.ID:04d} - Alteração de Vale Refeição e Alimentação",
                destinatarios=[dest.get("email")],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )


        return Resposta(
            status="Sucesso",
            mensagem="Alteração vale registrada com sucesso."
        )

    except SQLAlchemyError as e:
        Session.rollback()
        logger.error(
            "[ERRO] Falha ao salvar alteração vale: %s",
            e, exc_info=True
        )
        return Resposta(
            status="Erro",
            mensagem="Ocorreu um erro ao salvar a alteração vale. Tente novamente."
        )

    except Exception as e:
        logger.exception(
            "[ERRO] Erro inesperado na alteração de vale: %s",
            e
        )
        return Resposta(
            status="Erro",
            mensagem="Erro interno no servidor durante a alteração vale."
        )



# ============================================================
# ROTA: Alteração de Jornada (com Upload de Arquivo XLSX)
# ============================================================



@router.post("/Alteracao/Jornada", status_code=HTTPStatus.CREATED, response_model=Resposta)
async def Alteracao_Jornada(
    dados: str = Form(...),
    arquivo: UploadFile = File(None),
    Session=Depends(AtivarSession)
):
    """
    Registra uma nova solicitação de alteração de jornada.

    Fluxo:
    1. Recebe JSON + arquivo XLSX opcional
    2. Converte dados
    3. Salva registro no banco
    4. Faz upload do XLSX (caso enviado)
    5. Formata detalhes para o email
    6. Renderiza email usando Jinja2 (SEM BeautifulSoup)
    7. Envia para cada destinatário
    """

    logger.info("[LOG] Iniciando alteração de jornada...")

    try:
        # ------------------------------------------
        # 1. Parse JSON recebido do front-end
        # ------------------------------------------
        data = json.loads(dados)

        logger.info(
            "[LOG] Dados recebidos | Usuario: %s | Funcionario: %s",
            data.get("ID_Usuario"),
            data.get("CodigoFuncionario")
        )

        # ------------------------------------------
        # 2. Criar registro no banco
        # ------------------------------------------
        registro = TB_AlteracaoJornada(
            ID_Usuario=data.get("ID_Usuario"),
            CodigoFuncionario=data.get("CodigoFuncionario"),
            Nome=data.get("Nome"),
            Empresa=data.get("Empresa"),
            Motivo=data.get("Motivo"),
            HorarioAtual=data.get('HorarioAtual'),
            HorarioAtualDescricao=data.get('HorarioAtualDescricao'),
            HorarioNovo=data.get('HorarioNovo'),
            JornadaAtual=data.get("JornadaAtual"),
            JornadaNovo=data.get("JornadaNovo")
        )

        Session.add(registro)
        Session.commit()
        Session.refresh(registro)

        # ------------------------------------------
        # 3. Upload do XLSX (caso enviado)
        # ------------------------------------------
        if arquivo is not None:
            conteudo_arquivo = await arquivo.read()
            nome_arquivo = f"requisicoes/alteracoes/jornada/ID{registro.ID}.xlsx"

            async with azure_container() as container_client:
                url_arquivo = await upload_xlsx(
                    filename=nome_arquivo,
                    data=conteudo_arquivo,
                    container_client=container_client
                )

        # ------------------------------------------
        # 4. Remover dados que não devem aparecer no email
        # ------------------------------------------
        dados_detalhes = {
            key: value for key, value in data.items()
            if key not in ["ID_Usuario", "NomeUsuario", "GrupoEconomico", "Email"]
        }

        # Formatação opcional para deixar amigável
        dados_detalhes = formatar_jornada(dados_detalhes)

        # ------------------------------------------
        # 5. Buscar destinatários
        # ------------------------------------------
        destinatarios = listar_destinatarios(Session, id_funcionalidade=1, completo=True)

        nome_destino = destinatarios.get("Nome") or "Colaborador"

        mensagem_email = (
            f"Olá {nome_destino},<br>"
            f"{data.get('NomeUsuario')} do grupo {data.get('GrupoEconomico')} solicitou uma alteração de um colaborador.<br>"
            f"Por favor, revise os detalhes abaixo e tome as ações necessárias."
        )

        # ------------------------------------------
        # 6. Enviar email para cada destinatário
        # ------------------------------------------
        for dest in destinatarios.get("Email", []):
            link = f"{API_BASE_URL}/mensageria/processo?id={registro.ID}&p={dest.get('id')}&f=1&a=1"

            # Renderiza com Jinja2
            html_final = render_alteracao_email_jinja(
                titulo=f"#{registro.ID:04d} - Alteração de Jornada",
                mensagem=mensagem_email,
                detalhes=dados_detalhes,
                link=link
            )

            enviar_email(
                assunto=f"#{registro.ID:04d} - Solicitação de Alteração de Jornada",
                destinatarios=[dest.get("email")],
                copia=["gersonvieira@metarh.com.br"],
                html_corpo=html_final
            )

            logger.info("Email enviado para: %s", dest.get("email"))

        return Resposta(
            status="Sucesso",
            mensagem="Alteração de jornada registrada com sucesso."
        )

    except SQLAlchemyError as e:
        Session.rollback()
        logger.error("[ERRO] SQLAlchemy: %s", e)
        return Resposta(status="Erro", mensagem="Erro ao salvar no banco.")

    except Exception as e:
        logger.exception("[ERRO] Erro inesperado: %s", e)
        return Resposta(status="Erro", mensagem="Erro interno no servidor.")
