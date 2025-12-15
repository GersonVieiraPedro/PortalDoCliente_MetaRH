"""
Router para endpoints de Simulações Financeiras
Inclui consultas de ISS, encargos, benefícios, contratos ativos, cadastro de simulações
e upload de PDFs de simulações para Azure Blob Storage.
"""

from http import HTTPStatus
from fastapi import APIRouter, Depends, Body, File, Form, HTTPException, UploadFile  # type: ignore
from sqlalchemy.future import select
from collections import defaultdict
import json
import traceback  # Para capturar stack trace detalhado em logs

from backend.database import AtivarSession
from backend.models import TB_ISS, TB_Encargo, TB_Beneficio, TB_Orcamento, TB_OrcamentoEncargo, TB_OrcamentoBeneficio, DIM_Proprietario
from backend.TabelasGI import TabelaContrato
from backend.schema import SimulacaoCadastroSchema
from ..email_utils import enviar_email
from ..aruze_storage import azure_container, upload_pdf

router = APIRouter(prefix='/simulacoes', tags=['Simulações'])


@router.get('/iss', status_code=HTTPStatus.OK)
def consultar_iss(session=Depends(AtivarSession)):
    """
    Retorna a tabela completa de ISS por município.
    - Query simples da tabela TB_ISS.
    - Retorno: lista de registros com UF, Município, Label e percentual de ISS.
    """
    try:
        print("[LOG] Iniciando consulta de ISS...")
        query = select(TB_ISS)
        result = session.scalars(query).all()
        print(f"[LOG] Consulta de ISS finalizada com {len(result)} registros retornados.")
        return result
    except Exception as e:
        print("[ERRO] Falha ao consultar ISS:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao consultar ISS")


@router.get('/encargos', status_code=HTTPStatus.OK)
def consultar_encargos(session=Depends(AtivarSession)):
    """
    Retorna os encargos agrupados por serviço e grupo.
    - Agrupa encargos da tabela TB_Encargo por 'Servico' e 'Grupo'.
    - Cada item inclui ID, nome e percentual do encargo.
    - Retorno: dict estruturado {servico: {grupo: [encargos]}}
    """
    try:
        print("[LOG] Iniciando consulta de encargos...")

        # Trazendo apenas os visíveis
        query = session.scalars(select(TB_Encargo).where(TB_Encargo.Visivel == 1))
        agrupado = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        count = 0
        # Agrupa por Serviço, Grupo e ModalidadeContrato (se existir)
        for item in query:
            count += 1
            if item.ModalidadeContrato:
                agrupado[item.Servico][item.ModalidadeContrato][item.Grupo].append({
                    "id": item.ID,
                    "nome": item.Nome,
                    "percentual": float(item.Percentual)
                })
            else:
                agrupado[item.Servico]["SemModalidadeContrato"][item.Grupo].append({
                    "id": item.ID,
                    "nome": item.Nome,
                    "percentual": float(item.Percentual)
                })

        print(f"[LOG] Consulta de encargos concluída. {count} registros processados.")
        return {serv: {grp: dict(mods) for grp, mods in grupos.items()} for serv, grupos in agrupado.items()}

    except Exception as e:
        print("[ERRO] Falha ao consultar encargos:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao consultar encargos")


@router.get('/beneficios', status_code=HTTPStatus.OK)
def consultar_beneficios(session=Depends(AtivarSession)):
    """
    Retorna todos os benefícios disponíveis.
    - Query simples da tabela TB_Beneficio.
    - Retorno: lista de registros com nome, frequência, quantidade, valor unitário, desconto e categoria.
    """
    try:
        print("[LOG] Iniciando consulta de benefícios...")
        query = select(TB_Beneficio)
        result = session.scalars(query).all()
        print(f"[LOG] Consulta de benefícios concluída. {len(result)} registros retornados.")
        return result
    except Exception as e:
        print("[ERRO] Falha ao consultar benefícios:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao consultar benefícios")


@router.post('/contratos-ativos', status_code=HTTPStatus.OK)
def contratos_ativos(CodigoCliente: list[int]):
    """
    Retorna os contratos ativos para uma lista de códigos de clientes.
    - Parâmetro: CodigoCliente (lista de IDs de clientes).
    - Retorno: lista de contratos ativos filtrados pelos clientes informados.
    """
    try:
        print(f"[LOG] Consultando contratos ativos para clientes: {CodigoCliente}")
        result = TabelaContrato(CodigoCliente=CodigoCliente)
        print(f"[LOG] Consulta de contratos concluída. {len(result)} contratos retornados.")
        return result
    except Exception as e:
        print("[ERRO] Falha ao consultar contratos ativos:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro ao consultar contratos ativos")


@router.post('/Cadastro', status_code=HTTPStatus.CREATED)
def cadastrar_simulacao(data: SimulacaoCadastroSchema, session=Depends(AtivarSession)):
    """
    Cadastra uma simulação consolidada no banco.
    """
    s = data.simulacao_consolidada
    try:
        print(f"[LOG] Iniciando cadastro da simulação: usuário={s.usuarioID}, serviço={s.servicoID}")
        # Registro principal da simulação
        cadastro = TB_Orcamento(
            ID_Usuario=s.usuarioID,
            ID_Servico=s.servicoID,
            ID_Contrato=s.contratoID,
            ID_MunicipioISS=s.municipio_iss,
            ModalidadeContrato=getattr(s, "modalidade_contrato", None),
            TaxaAdministrativa=getattr(s, "taxa_administrativa", 0.0),
            Cargo=s.cargo,
            Salario=s.salario_base,
            Quantidade=s.quantidade_colaboradores,
            Periculosidade=s.periculosidade,
            Insalubridade=s.insalubridade.percentual if s.insalubridade else '0%',
            SalarioBruto=s.salario_bruto,
            GrupoAPercentual=s.Grupo_A.percentual,
            GrupoAValor=s.Grupo_A.valor,
            GrupoBPercentual=s.Grupo_B.percentual,
            GrupoBValor=s.Grupo_B.valor,
            TotalEncargosTrabalistasPercentual=s.total_encargos_trabalistas.percentual,
            TotalEncargosTrabalistasValor=s.total_encargos_trabalistas.valor,
            TotalSalarioBrutoEncargos=s.total_salario_bruto_encargos,
            TotalBeneficiosFornecido=s.total_beneficios.fornecido,
            TotalBeneficiosRepasse=s.total_beneficios.repasse,
            SubtotalNotaFiscalServico=s.subtotal_nota_fiscal,
            ExameASO=s.exames_clinicos_aso,
            TotalEncargosTributariosPercentual=s.total_encargos_tributarios.percentual,
            TotalEncargosTributariosValor=s.total_encargos_tributarios.valor,
            ProjecaoPorColaboradorAdministrado=s.projecao_colaborador_administrado,
            ProjecaoTotalNotaFiscalServico=s.projecao_total_nota_fiscal
        )

        session.add(cadastro)
        session.flush()
        print(f"[LOG] Simulação registrada com ID {cadastro.ID}")

        # Benefícios
        beneficios = [
            TB_OrcamentoBeneficio(
                ID_Orcamento=cadastro.ID,
                ID_Beneficio=b.id,
                Quantidade=b.quantidade,
                ValorUnitario=b.valorUnitario,
                Fornecido=b.fornecido,
                Repasse=b.repasse
            ) for b in data.beneficios
        ]
        session.add_all(beneficios)
        print(f"[LOG] {len(beneficios)} benefícios adicionados.")

        # Encargos trabalhistas
        encargos = [
            TB_OrcamentoEncargo(
                ID_Orcamento=cadastro.ID,
                ID_Encargo=e.id,
                TipoEncargo="Encargos Trabalistas",
                Percentual=e.percentual,
                Valor=e.valor
            ) for e in data.encargos
        ]
        session.add_all(encargos)
        print(f"[LOG] {len(encargos)} encargos trabalhistas adicionados.")

        # Encargos tributários
        tributos = [
            TB_OrcamentoEncargo(
                ID_Orcamento=cadastro.ID,
                ID_Encargo=t.id,
                TipoEncargo="Encargos Tributarios",
                Percentual=t.percentual,
                Valor=t.valor
            ) for t in data.tributos
        ]
        session.add_all(tributos)
        print(f"[LOG] {len(tributos)} encargos tributários adicionados.")

        session.commit()
        print(f"[LOG] Cadastro de simulação concluído com sucesso! ID={cadastro.ID}")
        return {'status': 'Sucesso', 'ID': cadastro.ID}

    except Exception as e:
        session.rollback()
        print("[ERRO] Falha ao cadastrar simulação:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Erro ao salvar cadastro: {str(e)}")


@router.post('/SalvarPDF', status_code=HTTPStatus.CREATED)
async def salvar_arquivo_pdf(
    id_orcamento: int,
    Servico: str,
    pdfFile: UploadFile = File(...),
    gerente: str = Form(...),
    cliente: str = Form(...)
):
    """
    Salva PDF de simulação no Azure Blob Storage e envia e-mail para gerente e cliente.
    """
    try:
        print(f"[LOG] Iniciando upload de PDF do orçamento #{id_orcamento} - Serviço: {Servico}")

        if pdfFile.content_type != 'application/pdf':
            print("[ERRO] Tipo de arquivo inválido:", pdfFile.content_type)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Arquivo deve ser um PDF")

        content = await pdfFile.read()
        filename = f"requisicoes/simulacoes/orcamento/{id_orcamento}_{Servico}_orcamento.pdf"

        async with azure_container() as container_client:
            await upload_pdf(filename, content, container_client)
        print(f"[LOG] PDF salvo com sucesso no Azure Blob Storage: {filename}")

        # Parse de dados do gerente e cliente
        try:
            gerente_dict = json.loads(gerente) if gerente and gerente != "undefined" else {}
        except Exception as e:
            print("[ERRO] Falha ao ler JSON do gerente:", gerente, str(e))
            gerente_dict = {}

        try:
            cliente_dict = json.loads(cliente) if cliente and cliente != "undefined" else {}
        except Exception as e:
            print("[ERRO] Falha ao ler JSON do cliente:", cliente, str(e))
            cliente_dict = {}

        print("[LOG] Gerente:", gerente_dict)
        print("[LOG] Cliente:", cliente_dict)

        html_corpo = f"""
        <p>Olá <strong>{gerente_dict.get('Nome', '[Não encontramos o gerente]')}</strong>,</p>
        <p>O cliente <strong>{cliente_dict.get('usuarioNome', '[Não encontramos o cliente]')}</strong> realizou uma simulação no Portal do Cliente.</p>
        """

        lista_copia = []
        lista_destinatarios = []
        if not gerente_dict.get('owner_email'):
            lista_destinatarios.append('gersonvieira@metarh.com.br')
            lista_copia.append(cliente_dict.get('usuarioEmail'))
        else:
            lista_destinatarios.append(gerente_dict['owner_email'])
            lista_copia.append('gersonvieira@metarh.com.br')

        print(f"[LOG] Enviando e-mail para {lista_destinatarios} com cópia para {lista_copia}")

        enviar_email(
            destinatarios=lista_destinatarios,
            copia=lista_copia,
            assunto=f"Orçamento #{id_orcamento} - {Servico}",
            html_corpo=html_corpo,
            arquivo_bytes=content,
            nome_arquivo=f"{id_orcamento}_{Servico}_orcamento.pdf",
            nome_remetente="Portal Cliente"
        )

        print(f"[LOG] E-mail enviado com sucesso para {lista_destinatarios}.")
        return {"message": f"Orçamento #{id_orcamento} - PDF salvo e e-mail enviado com sucesso."}

    except Exception as e:
        print("[ERRO] Falha em SalvarPDF:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}")
