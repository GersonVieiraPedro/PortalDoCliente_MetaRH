"""
Router para endpoints de Financeiro - Notas Fiscais e RPS (Duplicatas)
"""

from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, case, String
from sqlalchemy.orm import Session

from ..models import TB_Duplicata, TB_AprovacaoRPS, TB_MotivoReprovacaoRPS, TB_StatusAprovacao, TB_Contratos
from ..schema import (
    ListaNotasFiscaisResponse,
    NotaFiscalResponse,
    ResumoNotasFiscaisResponse,
    ArquivoNotaFiscalResponse,
    ListaRPSResponse,
    RPSResponse,
    ResumoRPSResponse,
    ArquivoRPSResponse,
    AprovarRPSRequest,
    ReprovarRPSRequest,
    AcaoRPSResponse,
    HistoricoAprovacaoRPS,
    MotivoReprovacaoResponse,
    ListaMotivosReprovacaoResponse,
    ContratoResponse,
    ListaContratosResponse,
    DownloadContratoResponse
)
from ..database import AtivarSession
from ..security import UsuarioAtual
from ..email_utils import enviar_email
from ..settings import Settings
from ..email_templates import gerar_email_rps_aprovacao, gerar_email_rps_reprovacao

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

# Configurar logger
logger = logging.getLogger(__name__)


def formatar_competencia(comp: Optional[str]) -> Optional[str]:
    """
    Formata a competência de YYYYMM para MM/YYYY
    Exemplo: "202501" -> "01/2025"
    """
    if comp and len(comp) == 6:
        return f"{comp[4:6]}/{comp[0:4]}"
    return comp


def calcular_status(data_vecto: Optional[datetime], data_baixa: Optional[datetime]) -> str:
    """
    Calcula o status da nota fiscal baseado nas datas
    - Se tem data de baixa: 'paga'
    - Se vencimento passou: 'vencida'
    - Caso contrário: 'a_vencer'
    """
    if data_baixa:
        return 'paga'
    elif data_vecto and data_vecto < datetime.now():
        return 'vencida'
    else:
        return 'a_vencer'


@router.get(
    "/notas-fiscais",
    response_model=ListaNotasFiscaisResponse,
    status_code=HTTPStatus.OK,
    summary="Listar Notas Fiscais",
    description="Retorna lista de notas fiscais (duplicatas) com filtros e resumo"
)
def listar_notas_fiscais(
    codigo_cliente: Optional[int] = Query(None, description="Código do cliente"),
    competencia: Optional[str] = Query(None, description="Competência no formato YYYYMM (ex: 202501)"),
    status_nota: Optional[str] = Query(None, description="Status: a_vencer, vencida ou paga"),
    data_inicio: Optional[str] = Query(None, description="Data vencimento início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data vencimento fim (YYYY-MM-DD)"),
    data_emissao_inicio: Optional[str] = Query(None, description="Data emissão início (YYYY-MM-DD)"),
    data_emissao_fim: Optional[str] = Query(None, description="Data emissão fim (YYYY-MM-DD)"),
    numero_nfe: Optional[str] = Query(None, description="Número da NFe (busca parcial)"),
    valor_minimo: Optional[float] = Query(None, description="Valor mínimo da nota"),
    valor_maximo: Optional[float] = Query(None, description="Valor máximo da nota"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Lista notas fiscais com filtros opcionais

    - Apenas duplicatas com Status = 'A' (Ativo) são retornadas
    - O status da nota (a_vencer, vencida, paga) é calculado dinamicamente
    - Requer autenticação via JWT token
    - FILTRA AUTOMATICAMENTE pela empresa do usuário logado
    """

    # ====================================================================
    # VALIDAÇÃO DE EMPRESA - SEGURANÇA
    # ====================================================================
    # Verifica se usuário tem empresa vinculada (FK TB_Usuarios.IDEmpresa → TB_Empresas.ID)
    if not usuario_atual.IDEmpresa:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Usuário sem empresa vinculada. Contate o administrador."
        )

    # Carregar empresa via relationship (JOIN: TB_Usuarios → TB_Empresas)
    # Relationship configurado com lazy="joined" carrega automaticamente
    empresa_usuario = usuario_atual.empresa

    if not empresa_usuario:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Empresa não encontrada no sistema"
        )

    if not empresa_usuario.Ativo:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Empresa inativa. Contate o administrador."
        )

    # ====================================================================
    # FILTRO POR TB_EMPRESAS.CodigoCliente
    # ====================================================================
    # IMPORTANTE: Usa TB_Empresas.CodigoCliente (obtido via JOIN/relationship)
    #             NÃO usa TB_Usuarios.CodigoCliente (campo ignorado/legado)
    # Converte para INT (TB_Empresas usa NVARCHAR, TB_Duplicata usa INT)
    try:
        codigo_cliente_int = int(empresa_usuario.CodigoCliente)  # ← Origem: TB_Empresas
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Configuração de empresa inválida. Contate o administrador."
        )

    # ====================================================================
    # QUERY BASE + FILTRO AUTOMÁTICO DE SEGURANÇA
    # ====================================================================
    # Filtro WHERE: TB_Duplicata.CodigoCliente = TB_Empresas.CodigoCliente
    query = (
        select(TB_Duplicata)
        .where(TB_Duplicata.Status == 'A')
        .where(TB_Duplicata.CodigoCliente == codigo_cliente_int)  # FILTRO OBRIGATÓRIO via TB_Empresas
        .where(TB_Duplicata.NroNFe != 0)  # Apenas duplicatas com número de NFe
    )

    # Filtro por competência
    if competencia:
        query = query.where(TB_Duplicata.DataCompetencia == competencia)

    # Filtro por número de NFe (busca parcial usando LIKE)
    if numero_nfe:
        query = query.where(TB_Duplicata.NroNFe.like(f"%{numero_nfe}%"))

    # Filtro por valor mínimo
    if valor_minimo is not None:
        query = query.where(TB_Duplicata.ValorBruto >= valor_minimo)

    # Filtro por valor máximo
    if valor_maximo is not None:
        query = query.where(TB_Duplicata.ValorBruto <= valor_maximo)

    # Filtro por período de emissão
    if data_emissao_inicio:
        try:
            dt_emissao_inicio = datetime.strptime(data_emissao_inicio, "%Y-%m-%d")
            # Range: >= início (inclui 00:00:00 do dia)
            query = query.where(TB_Duplicata.DataEmissao >= dt_emissao_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_emissao_inicio inválido. Use YYYY-MM-DD"
            )

    if data_emissao_fim:
        try:
            dt_emissao_fim = datetime.strptime(data_emissao_fim, "%Y-%m-%d")
            # Range: < dia seguinte (inclui todo o dia até 23:59:59.999)
            dt_emissao_fim_exclusivo = dt_emissao_fim + timedelta(days=1)
            query = query.where(TB_Duplicata.DataEmissao < dt_emissao_fim_exclusivo)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_emissao_fim inválido. Use YYYY-MM-DD"
            )

    # Filtro por período de vencimento
    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            # Range: >= início (inclui 00:00:00 do dia)
            query = query.where(TB_Duplicata.DataVecto >= dt_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use YYYY-MM-DD"
            )

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            # Range: < dia seguinte (inclui todo o dia até 23:59:59.999)
            dt_fim_exclusivo = dt_fim + timedelta(days=1)
            query = query.where(TB_Duplicata.DataVecto < dt_fim_exclusivo)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_fim inválido. Use YYYY-MM-DD"
            )

    # Filtro de status (aplicado via expressão SQL para melhor performance)
    if status_nota:
        hoje = datetime.now()
        if status_nota == 'paga':
            query = query.where(TB_Duplicata.DataBaixa.is_not(None))
        elif status_nota == 'vencida':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                )
            )
        elif status_nota == 'a_vencer':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                )
            )

    # Total de registros (antes da paginação e ordenação)
    # IMPORTANTE: Usar with_only_columns() para preservar os filtros WHERE
    count_query = query.with_only_columns(func.count(), maintain_column_froms=True).order_by(None)
    total = session.scalar(count_query) or 0

    # Ordena por data de vencimento (mais recente primeiro) - APÓS contar
    query = query.order_by(TB_Duplicata.DataVecto.desc())

    # Calcula resumo usando agregação SQL (MUITO mais rápido!)
    # IMPORTANTE: Passa TODOS os filtros para garantir consistência entre grid e resumo
    resumo = calcular_resumo_sql(
        session=session,
        codigo_cliente=codigo_cliente_int,
        competencia=competencia,
        data_inicio=data_inicio,
        data_fim=data_fim,
        data_emissao_inicio=data_emissao_inicio,
        data_emissao_fim=data_emissao_fim,
        numero_nfe=numero_nfe,
        valor_minimo=valor_minimo,
        valor_maximo=valor_maximo,
        status_nota=status_nota
    )

    # Aplica paginação
    query_paginada = query.offset(offset).limit(limit)

    # Executa query paginada
    duplicatas = session.execute(query_paginada).scalars().all()

    # Processa resultados da página
    notas_processadas = []
    for dup in duplicatas:
        # Calcula o status dinamicamente
        status_calculado = calcular_status(dup.DataVecto, dup.DataBaixa)

        # Monta objeto de resposta
        nota = NotaFiscalResponse(
            id=dup.Duplicata,
            numeroNFe=str(dup.NroNFe) if dup.NroNFe else None,
            dataEmissao=dup.DataEmissao.isoformat() if dup.DataEmissao else "",
            competencia=formatar_competencia(dup.DataCompetencia),
            vencimento=dup.DataVecto.isoformat() if dup.DataVecto else "",
            valorTotal=float(dup.ValorBruto) if dup.ValorBruto else 0.0,
            status=status_calculado
        )
        notas_processadas.append(nota)

    return ListaNotasFiscaisResponse(
        notas=notas_processadas,
        total=total,  # Total de registros ANTES da paginação
        resumo=resumo
    )


@router.get(
    "/notas-fiscais/resumo",
    response_model=ResumoNotasFiscaisResponse,
    status_code=HTTPStatus.OK,
    summary="Resumo de Notas Fiscais (Otimizado)",
    description="Retorna resumo das notas fiscais usando agregação SQL para máxima performance"
)
def obter_resumo_notas_fiscais(
    codigo_cliente: Optional[int] = Query(None, description="Código do cliente"),
    competencia: Optional[str] = Query(None, description="Competência no formato YYYYMM"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Retorna resumo das notas fiscais usando agregação SQL (muito mais rápido!)

    - Total e valor das notas a vencer
    - Total e valor das notas vencidas
    - Usa SUM() e COUNT() direto no banco de dados
    - Requer autenticação via JWT token
    - FILTRA AUTOMATICAMENTE pela empresa do usuário logado
    """

    # ====================================================================
    # VALIDAÇÃO DE EMPRESA - SEGURANÇA
    # ====================================================================
    if not usuario_atual.IDEmpresa:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Usuário sem empresa vinculada. Contate o administrador."
        )

    empresa_usuario = usuario_atual.empresa

    if not empresa_usuario:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Empresa não encontrada no sistema"
        )

    if not empresa_usuario.Ativo:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Empresa inativa. Contate o administrador."
        )

    # Extrai CodigoCliente da empresa (NÃO usa parâmetro opcional)
    try:
        codigo_cliente_int = int(empresa_usuario.CodigoCliente)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Configuração de empresa inválida. Contate o administrador."
        )

    hoje = datetime.now()

    # Expressões CASE para contar e somar por status
    # NOTAS VENCIDAS: DataBaixa é NULL E DataVecto < hoje
    count_vencidas = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                ),
                1
            ),
            else_=0
        )
    ).label('total_vencidas')

    valor_vencidas = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                ),
                TB_Duplicata.ValorBruto
            ),
            else_=0
        )
    ).label('valor_vencidas')

    # NOTAS A VENCER: DataBaixa é NULL E DataVecto >= hoje
    count_a_vencer = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                ),
                1
            ),
            else_=0
        )
    ).label('total_a_vencer')

    valor_a_vencer = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                ),
                TB_Duplicata.ValorBruto
            ),
            else_=0
        )
    ).label('valor_a_vencer')

    # Query base com agregações
    query = select(
        count_vencidas,
        valor_vencidas,
        count_a_vencer,
        valor_a_vencer
    ).select_from(TB_Duplicata).where(TB_Duplicata.Status == 'A')

    # FILTRO OBRIGATÓRIO: Empresa do usuário (SEGURANÇA)
    query = query.where(TB_Duplicata.CodigoCliente == codigo_cliente_int)

    # FILTRO OBRIGATÓRIO: Apenas duplicatas com número de NFe
    query = query.where(TB_Duplicata.NroNFe != 0)

    # Aplicar filtros opcionais
    if competencia:
        query = query.where(TB_Duplicata.DataCompetencia == competencia)

    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.where(TB_Duplicata.DataVecto >= dt_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use YYYY-MM-DD"
            )

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.where(TB_Duplicata.DataVecto <= dt_fim)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_fim inválido. Use YYYY-MM-DD"
            )

    # Executa query agregada (UMA ÚNICA QUERY!)
    resultado = session.execute(query).one()

    return ResumoNotasFiscaisResponse(
        totalNotasVencidas=int(resultado.total_vencidas or 0),
        valorNotasVencidas=float(resultado.valor_vencidas or 0.0),
        totalNotasAVencer=int(resultado.total_a_vencer or 0),
        valorNotasAVencer=float(resultado.valor_a_vencer or 0.0)
    )


def calcular_resumo_sql(
    session: Session,
    codigo_cliente: Optional[int] = None,
    competencia: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    data_emissao_inicio: Optional[str] = None,
    data_emissao_fim: Optional[str] = None,
    numero_nfe: Optional[str] = None,
    valor_minimo: Optional[float] = None,
    valor_maximo: Optional[float] = None,
    status_nota: Optional[str] = None
) -> ResumoNotasFiscaisResponse:
    """
    Calcula resumo usando agregação SQL (máxima performance)
    Executa UMA ÚNICA query com SUM() e CASE
    ATUALIZADO: Agora aceita TODOS os filtros da query principal
    """
    hoje = datetime.now()

    # Expressões CASE para contar e somar por status
    count_vencidas = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                ),
                1
            ),
            else_=0
        )
    ).label('total_vencidas')

    valor_vencidas = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                ),
                TB_Duplicata.ValorBruto
            ),
            else_=0
        )
    ).label('valor_vencidas')

    count_a_vencer = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                ),
                1
            ),
            else_=0
        )
    ).label('total_a_vencer')

    valor_a_vencer = func.sum(
        case(
            (
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                ),
                TB_Duplicata.ValorBruto
            ),
            else_=0
        )
    ).label('valor_a_vencer')

    # Query base com agregações
    query = select(
        count_vencidas,
        valor_vencidas,
        count_a_vencer,
        valor_a_vencer
    ).select_from(TB_Duplicata).where(TB_Duplicata.Status == 'A')

    # FILTRO OBRIGATÓRIO: Apenas duplicatas com número de NFe
    query = query.where(TB_Duplicata.NroNFe != 0)

    # Aplicar filtros
    if codigo_cliente:
        query = query.where(TB_Duplicata.CodigoCliente == codigo_cliente)

    if competencia:
        query = query.where(TB_Duplicata.DataCompetencia == competencia)

    if data_inicio:
        dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        # Range: >= início (usa índice)
        query = query.where(TB_Duplicata.DataVecto >= dt_inicio)

    if data_fim:
        dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        # Range: < dia seguinte (mais preciso que <= 23:59:59)
        dt_fim_exclusivo = dt_fim + timedelta(days=1)
        query = query.where(TB_Duplicata.DataVecto < dt_fim_exclusivo)

    # Filtros de data de emissão
    if data_emissao_inicio:
        dt_emissao_inicio = datetime.strptime(data_emissao_inicio, "%Y-%m-%d")
        # Range: >= início (usa índice)
        query = query.where(TB_Duplicata.DataEmissao >= dt_emissao_inicio)

    if data_emissao_fim:
        dt_emissao_fim = datetime.strptime(data_emissao_fim, "%Y-%m-%d")
        # Range: < dia seguinte (mais preciso que <= 23:59:59)
        dt_emissao_fim_exclusivo = dt_emissao_fim + timedelta(days=1)
        query = query.where(TB_Duplicata.DataEmissao < dt_emissao_fim_exclusivo)

    # Filtro por número de NFe
    if numero_nfe:
        query = query.where(TB_Duplicata.NroNFe.like(f"%{numero_nfe}%"))

    # Filtros de valor
    if valor_minimo is not None:
        query = query.where(TB_Duplicata.ValorBruto >= valor_minimo)

    if valor_maximo is not None:
        query = query.where(TB_Duplicata.ValorBruto <= valor_maximo)

    # Filtro de status
    if status_nota:
        if status_nota == 'paga':
            query = query.where(TB_Duplicata.DataBaixa.is_not(None))
        elif status_nota == 'vencida':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                )
            )
        elif status_nota == 'a_vencer':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                )
            )

    # Executa query agregada
    resultado = session.execute(query).one()

    return ResumoNotasFiscaisResponse(
        totalNotasVencidas=int(resultado.total_vencidas or 0),
        valorNotasVencidas=float(resultado.valor_vencidas or 0.0),
        totalNotasAVencer=int(resultado.total_a_vencer or 0),
        valorNotasAVencer=float(resultado.valor_a_vencer or 0.0)
    )


def calcular_resumo_direto(duplicatas: list[TB_Duplicata]) -> ResumoNotasFiscaisResponse:
    """
    Calcula o resumo a partir de uma lista de duplicatas do banco
    """
    total_a_vencer = 0
    valor_a_vencer = 0.0
    total_vencidas = 0
    valor_vencidas = 0.0

    hoje = datetime.now()

    for dup in duplicatas:
        valor = float(dup.ValorBruto) if dup.ValorBruto else 0.0

        # Se tem data de baixa, já foi paga - não conta no resumo
        if dup.DataBaixa:
            continue

        # Verifica se está vencida ou a vencer
        if dup.DataVecto and dup.DataVecto < hoje:
            total_vencidas += 1
            valor_vencidas += valor
        else:
            total_a_vencer += 1
            valor_a_vencer += valor

    return ResumoNotasFiscaisResponse(
        totalNotasAVencer=total_a_vencer,
        valorNotasAVencer=valor_a_vencer,
        totalNotasVencidas=total_vencidas,
        valorNotasVencidas=valor_vencidas
    )


def calcular_resumo(notas: list[NotaFiscalResponse]) -> ResumoNotasFiscaisResponse:
    """
    Calcula o resumo a partir de uma lista de notas fiscais (NotaFiscalResponse)
    DEPRECATED: Use calcular_resumo_direto() para melhor performance
    """
    total_a_vencer = 0
    valor_a_vencer = 0.0
    total_vencidas = 0
    valor_vencidas = 0.0

    for nota in notas:
        if nota.status == 'a_vencer':
            total_a_vencer += 1
            valor_a_vencer += nota.valorTotal
        elif nota.status == 'vencida':
            total_vencidas += 1
            valor_vencidas += nota.valorTotal

    return ResumoNotasFiscaisResponse(
        totalNotasAVencer=total_a_vencer,
        valorNotasAVencer=valor_a_vencer,
        totalNotasVencidas=total_vencidas,
        valorNotasVencidas=valor_vencidas
    )


@router.get(
    "/notas-fiscais/{nota_id}/arquivo",
    response_model=ArquivoNotaFiscalResponse,
    status_code=HTTPStatus.OK,
    summary="Obter informações do arquivo da nota fiscal",
    description="Retorna informações sobre o arquivo TX2 da nota fiscal (download aguardando definição de repositório)"
)
def obter_arquivo_nota_fiscal(
    nota_id: int,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Retorna informações sobre o arquivo TX2 da nota fiscal

    **⚠️ STUB/PLACEHOLDER**: A lógica de download real está aguardando decisão da equipe
    sobre qual será o repositório oficial dos arquivos (Azure Blob Storage, filesystem local, etc.)

    **Padrão de arquivo identificado:**
    - Formato: `{CodigoEmpresaFat}_{CodigoFilialFat}_{Duplicata}_{NumeroLote}.TX2`
    - Exemplo: `002_001_093614_007790.TX2`
    - Campo usado no nome do arquivo: `TB_Duplicata.Duplicata`

    **TODO - Implementar após definição do repositório:**
    1. Conectar ao repositório de arquivos (Azure Blob / Filesystem / S3 / etc.)
    2. Buscar arquivo pelo padrão: `*_{Duplicata}_*.TX2`
    3. Validar existência do arquivo
    4. Retornar arquivo para download ou URL assinada

    **Requer autenticação via JWT token**
    """

    # Busca a duplicata no banco de dados
    # Nota: TB_Duplicata usa chave primária composta (CodigoEmpresaFat, CodigoFilialFat, Duplicata)
    # Por simplificação, assumindo que nota_id corresponde ao campo Duplicata
    # Em produção, pode ser necessário receber os 3 campos ou usar um ID único

    duplicata = session.execute(
        select(TB_Duplicata).where(TB_Duplicata.Duplicata == nota_id)
    ).scalars().first()

    if not duplicata:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Nota fiscal com ID {nota_id} não encontrada"
        )

    # Monta o nome esperado do arquivo baseado no padrão identificado
    # Formato: {CodigoEmpresaFat}_{CodigoFilialFat}_{Duplicata}_{NumeroLote}.TX2
    # Como NumeroLote não está no banco, usamos wildcard no padrão
    nome_arquivo_padrao = f"{duplicata.CodigoEmpresaFat:03d}_{duplicata.CodigoFilialFat:03d}_{duplicata.Duplicata}_*.TX2"

    # TODO: Implementar lógica de busca e download do arquivo
    # Por enquanto, retorna apenas as informações sobre qual arquivo deveria ser baixado
    return ArquivoNotaFiscalResponse(
        nomeArquivo=nome_arquivo_padrao,
        duplicata=duplicata.Duplicata,
        numeroNFe=str(duplicata.NroNFe) if duplicata.NroNFe else None,
        codigoEmpresaFat=duplicata.CodigoEmpresaFat,
        codigoFilialFat=duplicata.CodigoFilialFat,
        mensagem="Endpoint criado. Aguardando definição do repositório de arquivos para implementar download."
    )
# ==================== ENDPOINTS DE RPS ====================

def obter_status_aprovacao_rps(session: Session, empresa: int, filial: int, duplicata: int) -> str:
    """
    Retorna o status de aprovação mais recente de um RPS
    Se não houver registro, retorna 'pendente'
    """
    from ..models import TB_StatusAprovacao

    ultima_aprovacao = session.execute(
        select(TB_StatusAprovacao.Codigo)
        .join(TB_AprovacaoRPS, TB_AprovacaoRPS.IdStatusAprovacao == TB_StatusAprovacao.ID)
        .where(
            and_(
                TB_AprovacaoRPS.CodigoEmpresaFat == empresa,
                TB_AprovacaoRPS.CodigoFilialFat == filial,
                TB_AprovacaoRPS.Duplicata == duplicata
            )
        )
        .order_by(TB_AprovacaoRPS.DataAcao.desc())
        .limit(1)
    ).scalars().first()

    return ultima_aprovacao if ultima_aprovacao else 'pendente'


def obter_id_status_aprovacao(session: Session, codigo: str) -> int:
    """
    Retorna o ID do status de aprovação baseado no código
    Códigos válidos: 'pendente', 'aprovado', 'reprovado'
    """
    from ..models import TB_StatusAprovacao

    status = session.execute(
        select(TB_StatusAprovacao.ID)
        .where(TB_StatusAprovacao.Codigo == codigo)
    ).scalars().first()

    if not status:
        raise HTTPException(
            status_code=500,
            detail=f"Status '{codigo}' não encontrado na tabela de domínio TB_StatusAprovacao"
        )

    return status


@router.get(
    "/rps",
    response_model=ListaRPSResponse,
    status_code=HTTPStatus.OK,
    summary="Listar RPS",
    description="Retorna lista de RPS (Recibos Provisórios de Serviço) com filtros e resumo - OTIMIZADO"
)
def listar_rps(
    codigo_cliente: Optional[int] = Query(None, description="Código do cliente"),
    competencia: Optional[str] = Query(None, description="Competência no formato YYYYMM (ex: 202501)"),
    status_rps: Optional[str] = Query(None, description="Status: a_vencer, vencida ou paga"),
    status_aprovacao: Optional[str] = Query(None, description="Status de aprovação: pendente, aprovado ou reprovado"),
    excluir_aprovados: bool = Query(False, description="Se True, exclui RPS com status 'aprovado' da listagem"),
    data_inicio: Optional[str] = Query(None, description="Data vencimento início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data vencimento fim (YYYY-MM-DD)"),
    data_emissao_inicio: Optional[str] = Query(None, description="Data emissão início (YYYY-MM-DD)"),
    data_emissao_fim: Optional[str] = Query(None, description="Data emissão fim (YYYY-MM-DD)"),
    valor_minimo: Optional[float] = Query(None, description="Valor mínimo do RPS"),
    valor_maximo: Optional[float] = Query(None, description="Valor máximo do RPS"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Lista RPS com filtros opcionais - VERSÃO OTIMIZADA COM LEFT JOIN

    Performance:
    - UMA ÚNICA QUERY com LEFT JOIN para status de aprovação
    - Paginação no banco de dados (não em memória)
    - Filtros aplicados diretamente na query SQL

    Requer autenticação via JWT token
    """

    # Início da medição de performance
    tempo_inicio = time.perf_counter()

    logger.info(
        f"[LISTAR RPS] Iniciando busca | "
        f"Usuario={usuario_atual.Nome} | "
        f"Limit={limit} | Offset={offset} | "
        f"ExcluirAprovados={excluir_aprovados}"
    )

    # ====================================================================
    # VALIDAÇÃO DE EMPRESA - SEGURANÇA
    # ====================================================================
    # Verifica se usuário tem empresa vinculada (FK TB_Usuarios.IDEmpresa → TB_Empresas.ID)
    if not usuario_atual.IDEmpresa:
        logger.error(f"[LISTAR RPS] Usuário {usuario_atual.Email} sem empresa vinculada (IDEmpresa=NULL)")
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Usuário sem empresa vinculada. Contate o administrador."
        )

    # Carregar empresa via relationship (JOIN: TB_Usuarios → TB_Empresas)
    # Relationship configurado com lazy="joined" carrega automaticamente
    # Retorna objeto TB_Empresas completo com todos os campos
    empresa_usuario = usuario_atual.empresa

    if not empresa_usuario:
        logger.error(f"[LISTAR RPS] Empresa ID={usuario_atual.IDEmpresa} não encontrada no banco")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Empresa não encontrada no sistema"
        )

    if not empresa_usuario.Ativo:
        logger.error(f"[LISTAR RPS] Empresa ID={empresa_usuario.ID} ({empresa_usuario.RazaoSocial}) está inativa")
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Empresa inativa. Contate o administrador."
        )

    tempo_apos_validacao = time.perf_counter()
    logger.info(
        f"[LISTAR RPS] Empresa validada | "
        f"Empresa={empresa_usuario.RazaoSocial} | "
        f"CodigoCliente={empresa_usuario.CodigoCliente} (origem: TB_Empresas via JOIN) | "
        f"Tempo validação: {(tempo_apos_validacao - tempo_inicio)*1000:.2f}ms"
    )

    # ====================================================================
    # SUBQUERY: Busca o status de aprovação mais recente de cada RPS
    # ====================================================================
    from sqlalchemy import literal_column

    subquery_status = (
        select(
            TB_AprovacaoRPS.Duplicata.label('aprov_duplicata'),
            TB_AprovacaoRPS.CodigoEmpresaFat.label('aprov_empresa'),
            TB_AprovacaoRPS.CodigoFilialFat.label('aprov_filial'),
            TB_StatusAprovacao.Codigo.label('status_aprov'),
            func.row_number().over(
                partition_by=[
                    TB_AprovacaoRPS.Duplicata,
                    TB_AprovacaoRPS.CodigoEmpresaFat,
                    TB_AprovacaoRPS.CodigoFilialFat
                ],
                order_by=TB_AprovacaoRPS.DataAcao.desc()
            ).label('rn')
        )
        .join(TB_StatusAprovacao, TB_AprovacaoRPS.IdStatusAprovacao == TB_StatusAprovacao.ID)
        .subquery()
    )

    # ====================================================================
    # QUERY PRINCIPAL: TB_Duplicata LEFT JOIN com status de aprovação
    # ====================================================================
    query = (
        select(
            TB_Duplicata,
            func.coalesce(subquery_status.c.status_aprov, literal_column("'pendente'")).label('status_aprovacao')
        )
        .outerjoin(
            subquery_status,
            and_(
                TB_Duplicata.Duplicata == subquery_status.c.aprov_duplicata,
                TB_Duplicata.CodigoEmpresaFat == subquery_status.c.aprov_empresa,
                TB_Duplicata.CodigoFilialFat == subquery_status.c.aprov_filial,
                subquery_status.c.rn == 1
            )
        )
        .where(TB_Duplicata.Status == 'A')
    )

    # ====================================================================
    # FILTRO AUTOMÁTICO DE SEGURANÇA - EMPRESA DO USUÁRIO
    # ====================================================================
    # IMPORTANTE: Usa TB_Empresas.CodigoCliente (obtido via JOIN/relationship)
    #             NÃO usa TB_Usuarios.CodigoCliente (campo ignorado/legado)
    #
    # Fluxo: TB_Usuarios.IDEmpresa → TB_Empresas.ID (JOIN)
    #        TB_Empresas.CodigoCliente → Usado no filtro
    #
    # Converte CodigoCliente para INT (TB_Empresas usa NVARCHAR, TB_Duplicata usa INT)
    try:
        codigo_cliente_int = int(empresa_usuario.CodigoCliente)  # ← Origem: TB_Empresas via relationship
    except (ValueError, TypeError):
        logger.error(
            f"[LISTAR RPS] CodigoCliente inválido da TB_Empresas: {empresa_usuario.CodigoCliente} "
            f"(Empresa ID={empresa_usuario.ID}, Razão Social={empresa_usuario.RazaoSocial})"
        )
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Configuração de empresa inválida. Contate o administrador."
        )

    # Aplica filtro WHERE: TB_Duplicata.CodigoCliente = TB_Empresas.CodigoCliente
    query = query.where(TB_Duplicata.CodigoCliente == codigo_cliente_int)

    tempo_apos_query_base = time.perf_counter()
    logger.info(
        f"[LISTAR RPS] Filtro automático aplicado | "
        f"CodigoCliente={codigo_cliente_int} (origem: TB_Empresas.CodigoCliente via JOIN com IDEmpresa={usuario_atual.IDEmpresa}) | "
        f"Tempo construção query base: {(tempo_apos_query_base - tempo_apos_validacao)*1000:.2f}ms"
    )

    # ====================================================================
    # FILTROS OPCIONAIS SQL (aplicados no banco de dados)
    # ====================================================================

    if competencia:
        query = query.where(TB_Duplicata.DataCompetencia == competencia)

    if valor_minimo is not None:
        query = query.where(TB_Duplicata.ValorBruto >= valor_minimo)

    if valor_maximo is not None:
        query = query.where(TB_Duplicata.ValorBruto <= valor_maximo)

    # Filtros de data
    if data_emissao_inicio:
        try:
            dt_emissao_inicio = datetime.strptime(data_emissao_inicio, "%Y-%m-%d")
            # Range: >= início (usa índice)
            query = query.where(TB_Duplicata.DataEmissao >= dt_emissao_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_emissao_inicio inválido. Use YYYY-MM-DD"
            )

    if data_emissao_fim:
        try:
            dt_emissao_fim = datetime.strptime(data_emissao_fim, "%Y-%m-%d")
            # Range: < dia seguinte (mais preciso que <= 23:59:59)
            dt_emissao_fim_exclusivo = dt_emissao_fim + timedelta(days=1)
            query = query.where(TB_Duplicata.DataEmissao < dt_emissao_fim_exclusivo)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_emissao_fim inválido. Use YYYY-MM-DD"
            )

    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            # Range: >= início (usa índice)
            query = query.where(TB_Duplicata.DataVecto >= dt_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use YYYY-MM-DD"
            )

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            # Range: < dia seguinte (mais preciso que <= 23:59:59)
            dt_fim_exclusivo = dt_fim + timedelta(days=1)
            query = query.where(TB_Duplicata.DataVecto < dt_fim_exclusivo)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_fim inválido. Use YYYY-MM-DD"
            )

    # Filtro de status (vencida/paga/a_vencer)
    if status_rps:
        hoje = datetime.now()
        if status_rps == 'paga':
            query = query.where(TB_Duplicata.DataBaixa.is_not(None))
        elif status_rps == 'vencida':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                )
            )
        elif status_rps == 'a_vencer':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                )
            )

    # ====================================================================
    # FILTRO DE STATUS DE APROVAÇÃO (aplicado na query SQL)
    # ====================================================================
    from sqlalchemy import or_

    if status_aprovacao:
        if status_aprovacao == 'pendente':
            query = query.where(
                or_(
                    subquery_status.c.status_aprov.is_(None),
                    subquery_status.c.status_aprov == 'pendente'
                )
            )
        else:
            query = query.where(subquery_status.c.status_aprov == status_aprovacao)

    if excluir_aprovados:
        query = query.where(
            or_(
                subquery_status.c.status_aprov.is_(None),
                subquery_status.c.status_aprov != 'aprovado'
            )
        )

    # ====================================================================
    # TOTAL DE REGISTROS (antes da paginação)
    # ====================================================================
    tempo_antes_count = time.perf_counter()
    logger.info(f"[LISTAR RPS] Filtros aplicados | Tempo aplicação filtros: {(tempo_antes_count - tempo_apos_query_base)*1000:.2f}ms")

    # IMPORTANTE: Usar with_only_columns() para preservar os filtros WHERE e JOINs
    count_query = query.with_only_columns(func.count(), maintain_column_froms=True).order_by(None)
    total = session.scalar(count_query) or 0

    tempo_apos_count = time.perf_counter()
    logger.info(f"[LISTAR RPS] Total calculado: {total} | Tempo COUNT query: {(tempo_apos_count - tempo_antes_count)*1000:.2f}ms")

    # ====================================================================
    # ORDENAÇÃO E PAGINAÇÃO (no banco de dados)
    # ====================================================================
    query = query.order_by(TB_Duplicata.DataVecto.desc())
    query = query.offset(offset).limit(limit)

    # ====================================================================
    # EXECUTA QUERY (UMA ÚNICA VEZ!)
    # ====================================================================
    tempo_antes_query = time.perf_counter()
    resultados = session.execute(query).all()
    tempo_apos_query = time.perf_counter()
    logger.info(f"[LISTAR RPS] Query principal executada | Registros: {len(resultados)} | Tempo query: {(tempo_apos_query - tempo_antes_query)*1000:.2f}ms")

    # ====================================================================
    # PROCESSA RESULTADOS
    # ====================================================================
    rps_processados = []
    for row in resultados:
        dup = row[0]  # TB_Duplicata
        status_aprovacao_atual = row[1]  # status_aprovacao do LEFT JOIN

        # Calcula status (vencida/paga/a_vencer)
        status_calculado = calcular_status(dup.DataVecto, dup.DataBaixa)

        rps = RPSResponse(
            duplicata=dup.Duplicata,
            numeroNFE=str(dup.NroNFe) if dup.NroNFe else None,
            codigoEmpresaFat=dup.CodigoEmpresaFat,
            codigoFilialFat=dup.CodigoFilialFat,
            dataEmissao=dup.DataEmissao.isoformat() if dup.DataEmissao else "",
            competencia=formatar_competencia(dup.DataCompetencia),
            vencimento=dup.DataVecto.isoformat() if dup.DataVecto else "",
            valorTotal=float(dup.ValorBruto) if dup.ValorBruto else 0.0,
            status=status_calculado,
            statusAprovacao=status_aprovacao_atual
        )
        rps_processados.append(rps)

    tempo_apos_processamento = time.perf_counter()
    logger.info(f"[LISTAR RPS] Resultados processados | Tempo processamento: {(tempo_apos_processamento - tempo_apos_query)*1000:.2f}ms")

    # ====================================================================
    # CALCULA RESUMO
    # ====================================================================
    # IMPORTANTE: Passa TODOS os filtros para garantir consistência entre grid e resumo
    resumo = calcular_resumo_rps_sql(
        session=session,
        codigo_cliente=codigo_cliente_int,  # Usa o código da empresa do usuário logado
        competencia=competencia,
        data_inicio=data_inicio,
        data_fim=data_fim,
        data_emissao_inicio=data_emissao_inicio,
        data_emissao_fim=data_emissao_fim,
        valor_minimo=valor_minimo,
        valor_maximo=valor_maximo,
        status_rps=status_rps,
        status_aprovacao=status_aprovacao,
        excluir_aprovados=excluir_aprovados
    )

    tempo_apos_resumo = time.perf_counter()
    tempo_total = (tempo_apos_resumo - tempo_inicio) * 1000
    tempo_resumo = (tempo_apos_resumo - tempo_apos_processamento) * 1000

    logger.info(
        f"[LISTAR RPS] Resumo calculado | Tempo resumo: {tempo_resumo:.2f}ms"
    )

    logger.info(
        f"[LISTAR RPS] ✅ Busca concluída | "
        f"Total={total} | "
        f"Página={offset//limit + 1} | "
        f"Retornados={len(rps_processados)} registros | "
        f"⏱️  TEMPO TOTAL: {tempo_total:.2f}ms"
    )

    # Breakdown detalhado de performance
    logger.info(
        f"[LISTAR RPS] 📊 Performance breakdown: "
        f"Validação={((tempo_apos_validacao - tempo_inicio)*1000):.1f}ms | "
        f"Query_Base={((tempo_apos_query_base - tempo_apos_validacao)*1000):.1f}ms | "
        f"Filtros={((tempo_antes_count - tempo_apos_query_base)*1000):.1f}ms | "
        f"Count={((tempo_apos_count - tempo_antes_count)*1000):.1f}ms | "
        f"Query_Principal={((tempo_apos_query - tempo_antes_query)*1000):.1f}ms | "
        f"Processamento={((tempo_apos_processamento - tempo_apos_query)*1000):.1f}ms | "
        f"Resumo={tempo_resumo:.1f}ms"
    )

    return ListaRPSResponse(
        rps=rps_processados,
        total=total,
        resumo=resumo
    )


@router.get(
    "/rps/resumo",
    response_model=ResumoRPSResponse,
    status_code=HTTPStatus.OK,
    summary="Resumo de RPS (Otimizado)",
    description="Retorna resumo dos RPS usando agregação SQL para máxima performance"
)
def obter_resumo_rps(
    competencia: Optional[str] = Query(None, description="Competência no formato YYYYMM"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Retorna resumo dos RPS usando agregação SQL

    - Total e valor dos RPS a vencer
    - Total e valor dos RPS vencidos
    - Usa SUM() e COUNT() direto no banco de dados
    - Requer autenticação via JWT token
    - FILTRA AUTOMATICAMENTE pela empresa do usuário logado
    """

    # ====================================================================
    # VALIDAÇÃO DE EMPRESA - SEGURANÇA
    # ====================================================================
    # Verifica se usuário tem empresa vinculada (FK TB_Usuarios.IDEmpresa → TB_Empresas.ID)
    if not usuario_atual.IDEmpresa:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Usuário sem empresa vinculada. Contate o administrador."
        )

    # Carregar empresa via relationship (JOIN: TB_Usuarios → TB_Empresas)
    empresa_usuario = usuario_atual.empresa

    if not empresa_usuario or not empresa_usuario.Ativo:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Empresa inativa ou inválida. Contate o administrador."
        )

    # ====================================================================
    # FILTRO POR TB_EMPRESAS.CodigoCliente
    # ====================================================================
    # IMPORTANTE: Usa TB_Empresas.CodigoCliente (via JOIN), NÃO TB_Usuarios.CodigoCliente
    # Converte para INT (TB_Empresas usa NVARCHAR, TB_Duplicata usa INT)
    try:
        codigo_cliente_int = int(empresa_usuario.CodigoCliente)  # ← Origem: TB_Empresas
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Configuração de empresa inválida. Contate o administrador."
        )

    return calcular_resumo_rps_sql(
        session=session,
        codigo_cliente=codigo_cliente_int,
        competencia=competencia,
        data_inicio=data_inicio,
        data_fim=data_fim,
        data_emissao_inicio=None,
        data_emissao_fim=None,
        valor_minimo=None,
        valor_maximo=None,
        status_rps=None,
        status_aprovacao=None,
        excluir_aprovados=False
    )


def calcular_resumo_rps_sql(
    session: Session,
    codigo_cliente: int,  # OBRIGATÓRIO - código da empresa do usuário
    competencia: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    data_emissao_inicio: Optional[str] = None,
    data_emissao_fim: Optional[str] = None,
    valor_minimo: Optional[float] = None,
    valor_maximo: Optional[float] = None,
    status_rps: Optional[str] = None,
    status_aprovacao: Optional[str] = None,
    excluir_aprovados: bool = False
) -> ResumoRPSResponse:
    """
    Calcula resumo de RPS baseado no status de aprovação - OTIMIZADO

    ✅ Estratégia OTIMIZADA (UMA ÚNICA QUERY com agregação SQL):
    1. Subquery com ROW_NUMBER() para obter status de aprovação mais recente
    2. LEFT JOIN da TB_Duplicata com subquery
    3. Agregação SQL com SUM() e COUNT() agrupado por status
    4. Retorna totais em UMA ÚNICA execução

    ⚡ Performance: ~100x mais rápido que a versão anterior (N+1 queries eliminado)

    IMPORTANTE: codigo_cliente é OBRIGATÓRIO para filtrar por empresa (segurança)
    ATUALIZADO: Agora aceita TODOS os filtros da query principal
    """
    tempo_inicio_resumo = time.perf_counter()

    from sqlalchemy import literal_column, or_

    # ====================================================================
    # SUBQUERY: Status de aprovação mais recente (MESMA estratégia de listar_rps)
    # ====================================================================
    subquery_status = (
        select(
            TB_AprovacaoRPS.Duplicata.label('aprov_duplicata'),
            TB_AprovacaoRPS.CodigoEmpresaFat.label('aprov_empresa'),
            TB_AprovacaoRPS.CodigoFilialFat.label('aprov_filial'),
            TB_StatusAprovacao.Codigo.label('status_aprov'),
            func.row_number().over(
                partition_by=[
                    TB_AprovacaoRPS.Duplicata,
                    TB_AprovacaoRPS.CodigoEmpresaFat,
                    TB_AprovacaoRPS.CodigoFilialFat
                ],
                order_by=TB_AprovacaoRPS.DataAcao.desc()
            ).label('rn')
        )
        .join(TB_StatusAprovacao, TB_AprovacaoRPS.IdStatusAprovacao == TB_StatusAprovacao.ID)
        .subquery()
    )

    # ====================================================================
    # QUERY PRINCIPAL: Agregação com LEFT JOIN
    # ====================================================================
    query = (
        select(
            func.coalesce(subquery_status.c.status_aprov, literal_column("'pendente'")).label('status_aprovacao'),
            func.count().label('total'),
            func.sum(TB_Duplicata.ValorBruto).label('valor_total')
        )
        .outerjoin(
            subquery_status,
            and_(
                TB_Duplicata.Duplicata == subquery_status.c.aprov_duplicata,
                TB_Duplicata.CodigoEmpresaFat == subquery_status.c.aprov_empresa,
                TB_Duplicata.CodigoFilialFat == subquery_status.c.aprov_filial,
                subquery_status.c.rn == 1
            )
        )
        .where(TB_Duplicata.Status == 'A')
        .where(TB_Duplicata.CodigoCliente == codigo_cliente)  # FILTRO OBRIGATÓRIO
        .group_by(func.coalesce(subquery_status.c.status_aprov, literal_column("'pendente'")))
    )

    # ====================================================================
    # APLICAR FILTROS (mesmos da query principal)
    # ====================================================================
    if competencia:
        query = query.where(TB_Duplicata.DataCompetencia == competencia)

    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.where(TB_Duplicata.DataVecto >= dt_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use YYYY-MM-DD"
            )

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            dt_fim_exclusivo = dt_fim + timedelta(days=1)
            query = query.where(TB_Duplicata.DataVecto < dt_fim_exclusivo)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_fim inválido. Use YYYY-MM-DD"
            )

    if data_emissao_inicio:
        try:
            dt_emissao_inicio = datetime.strptime(data_emissao_inicio, "%Y-%m-%d")
            query = query.where(TB_Duplicata.DataEmissao >= dt_emissao_inicio)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_emissao_inicio inválido. Use YYYY-MM-DD"
            )

    if data_emissao_fim:
        try:
            dt_emissao_fim = datetime.strptime(data_emissao_fim, "%Y-%m-%d")
            dt_emissao_fim_exclusivo = dt_emissao_fim + timedelta(days=1)
            query = query.where(TB_Duplicata.DataEmissao < dt_emissao_fim_exclusivo)
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Formato de data_emissao_fim inválido. Use YYYY-MM-DD"
            )

    if valor_minimo is not None:
        query = query.where(TB_Duplicata.ValorBruto >= valor_minimo)

    if valor_maximo is not None:
        query = query.where(TB_Duplicata.ValorBruto <= valor_maximo)

    if status_rps:
        hoje = datetime.now()
        if status_rps == 'paga':
            query = query.where(TB_Duplicata.DataBaixa.is_not(None))
        elif status_rps == 'vencida':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto < hoje
                )
            )
        elif status_rps == 'a_vencer':
            query = query.where(
                and_(
                    TB_Duplicata.DataBaixa.is_(None),
                    TB_Duplicata.DataVecto >= hoje
                )
            )

    # ====================================================================
    # FILTROS DE STATUS DE APROVAÇÃO (aplicados na query SQL)
    # ====================================================================
    if status_aprovacao:
        if status_aprovacao == 'pendente':
            query = query.where(
                or_(
                    subquery_status.c.status_aprov.is_(None),
                    subquery_status.c.status_aprov == 'pendente'
                )
            )
        else:
            query = query.where(subquery_status.c.status_aprov == status_aprovacao)

    if excluir_aprovados:
        query = query.where(
            or_(
                subquery_status.c.status_aprov.is_(None),
                subquery_status.c.status_aprov != 'aprovado'
            )
        )

    # ====================================================================
    # EXECUTAR QUERY AGREGADA (UMA ÚNICA VEZ!)
    # ====================================================================
    tempo_antes_query = time.perf_counter()
    resultados = session.execute(query).all()
    tempo_apos_query = time.perf_counter()

    # ====================================================================
    # PROCESSAR RESULTADOS AGREGADOS
    # ====================================================================
    pendentes_count = 0
    pendentes_valor = 0.0
    aprovados_count = 0
    aprovados_valor = 0.0
    reprovados_count = 0
    reprovados_valor = 0.0

    for row in resultados:
        status = row[0]  # status_aprovacao
        total = row[1]   # count
        valor = float(row[2]) if row[2] else 0.0  # sum

        if status == 'pendente':
            pendentes_count = total
            pendentes_valor = valor
        elif status == 'aprovado':
            aprovados_count = total
            aprovados_valor = valor
        elif status == 'reprovado':
            reprovados_count = total
            reprovados_valor = valor

    tempo_total = (tempo_apos_query - tempo_inicio_resumo) * 1000

    logger.info(
        f"[RESUMO RPS] ✅ Agregação SQL concluída | "
        f"Query única executada em {(tempo_apos_query - tempo_antes_query)*1000:.2f}ms | "
        f"Tempo total: {tempo_total:.2f}ms | "
        f"Pendentes={pendentes_count}, Aprovados={aprovados_count}, Reprovados={reprovados_count}"
    )

    return ResumoRPSResponse(
        totalRPSPendentes=pendentes_count,
        valorRPSPendentes=pendentes_valor,
        totalRPSAprovados=aprovados_count,
        valorRPSAprovados=aprovados_valor,
        totalRPSReprovados=reprovados_count,
        valorRPSReprovados=reprovados_valor
    )


@router.get(
    "/rps/{duplicata}/arquivo",
    response_model=ArquivoRPSResponse,
    status_code=HTTPStatus.OK,
    summary="Obter informações do arquivo RPS",
    description="Retorna informações sobre o arquivo do RPS (download aguardando definição de repositório)"
)
def obter_arquivo_rps(
    duplicata: int,
    codigo_empresa: int = Query(..., description="Código da empresa faturadora"),
    codigo_filial: int = Query(..., description="Código da filial faturadora"),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Retorna informações sobre o arquivo do RPS

    **⚠️ STUB/PLACEHOLDER**: A lógica de download real está aguardando decisão da equipe
    sobre qual será o repositório oficial dos arquivos

    **Requer autenticação via JWT token**
    """

    # Busca o RPS usando chave composta
    dup = session.execute(
        select(TB_Duplicata).where(
            and_(
                TB_Duplicata.CodigoEmpresaFat == codigo_empresa,
                TB_Duplicata.CodigoFilialFat == codigo_filial,
                TB_Duplicata.Duplicata == duplicata,
                TB_Duplicata.Status == 'A'
            )
        )
    ).scalars().first()

    if not dup:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"RPS {duplicata} não encontrado para Empresa {codigo_empresa}, Filial {codigo_filial}"
        )

    # Monta o nome esperado do arquivo usando Duplicata
    nome_arquivo_padrao = f"{dup.CodigoEmpresaFat:03d}_{dup.CodigoFilialFat:03d}_{dup.Duplicata}_*.TX2"

    return ArquivoRPSResponse(
        nomeArquivo=nome_arquivo_padrao,
        duplicata=dup.Duplicata,
        numeroNFE=dup.NroNFe,
        codigoEmpresaFat=dup.CodigoEmpresaFat,
        codigoFilialFat=dup.CodigoFilialFat,
        mensagem="Endpoint criado. Aguardando definição do repositório de arquivos para implementar download."
    )


# ==================== ENDPOINTS DE APROVAÇÃO/REPROVAÇÃO ====================

@router.post(
    "/rps/aprovar",
    response_model=AcaoRPSResponse,
    status_code=HTTPStatus.OK,
    summary="Aprovar RPS",
    description="Aprova um RPS e registra a ação no histórico"
)
def aprovar_rps(
    request: AprovarRPSRequest,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Aprova um RPS, registrando a ação no histórico

    Fluxo:
    1. Valida se RPS existe (usando chave composta)
    2. Verifica se já não foi aprovado
    3. Cria registro de aprovação
    4. Retorna confirmação

    Requer autenticação via JWT token
    """

    logger.info(
        f"[APROVACAO RPS] Iniciando aprovação | "
        f"Duplicata={request.duplicata} | "
        f"CodigoEmpresaFat={request.codigo_empresa_fat} | "
        f"CodigoFilialFat={request.codigo_filial_fat} | "
        f"Usuario={usuario_atual.Nome} (ID={usuario_atual.ID})"
    )

    try:
        # 1. Buscar RPS usando chave composta
        logger.info(f"[APROVACAO RPS] Buscando RPS na base de dados | Duplicata={request.duplicata}")

        duplicata = session.execute(
            select(TB_Duplicata).where(
                and_(
                    TB_Duplicata.CodigoEmpresaFat == request.codigo_empresa_fat,
                    TB_Duplicata.CodigoFilialFat == request.codigo_filial_fat,
                    TB_Duplicata.Duplicata == request.duplicata,
                    TB_Duplicata.Status == 'A'
                )
            )
        ).scalars().first()

        if not duplicata:
            logger.warning(
                f"[APROVACAO RPS] RPS não encontrado | "
                f"Duplicata={request.duplicata} | "
                f"CodigoEmpresaFat={request.codigo_empresa_fat} | "
                f"CodigoFilialFat={request.codigo_filial_fat}"
            )
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"RPS {request.duplicata} não encontrado para Empresa {request.codigo_empresa_fat}, Filial {request.codigo_filial_fat}"
            )

        logger.info(f"[APROVACAO RPS] RPS encontrado | ValorBruto={duplicata.ValorBruto} | NroNFe={duplicata.NroNFe}")

        # 2. Verificar status atual
        logger.info(f"[APROVACAO RPS] Verificando status atual de aprovação")

        status_atual = obter_status_aprovacao_rps(
            session,
            duplicata.CodigoEmpresaFat,
            duplicata.CodigoFilialFat,
            duplicata.Duplicata
        )

        logger.info(f"[APROVACAO RPS] Status atual: {status_atual}")

        if status_atual == 'aprovado':
            logger.warning(f"[APROVACAO RPS] RPS já aprovado | Duplicata={duplicata.Duplicata}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"RPS {duplicata.Duplicata} já está aprovado"
            )

        # 3. Criar registro de aprovação
        logger.info(f"[APROVACAO RPS] Criando objeto de aprovação")

        # Obter ID do status 'aprovado'
        id_status_aprovado = obter_id_status_aprovacao(session, 'aprovado')

        nova_aprovacao = TB_AprovacaoRPS(
            CodigoEmpresaFat=duplicata.CodigoEmpresaFat,
            CodigoFilialFat=duplicata.CodigoFilialFat,
            Duplicata=duplicata.Duplicata,
            IdStatusAprovacao=id_status_aprovado,
            StatusAprovacao='aprovado',  # ⚠️ DEPRECATED: Será removido após migração
            TipoAcao='aprovacao',
            ID_Usuario=usuario_atual.ID,
            NomeUsuario=usuario_atual.Nome,
            EmailUsuario=usuario_atual.Email
        )

        logger.info(
            f"[APROVACAO RPS] Salvando registro de aprovação no banco | "
            f"RPS (Duplicata)={duplicata.Duplicata} | "
            f"NFE={duplicata.NroNFe or 'Não emitida'} | "
            f"CodigoEmpresaFat={duplicata.CodigoEmpresaFat} | "
            f"CodigoFilialFat={duplicata.CodigoFilialFat} | "
            f"Usuario={usuario_atual.Nome} (ID={usuario_atual.ID}) | "
            f"Email={usuario_atual.Email} | "
            f"StatusAprovacao=aprovado | "
            f"TipoAcao=aprovacao"
        )

        session.add(nova_aprovacao)
        session.commit()
        session.refresh(nova_aprovacao)

        logger.info(
            f"[APROVACAO RPS] Registro salvo com sucesso | "
            f"ID_Registro={nova_aprovacao.ID} | "
            f"DataAcao={nova_aprovacao.DataAcao}"
        )

        # ====================================================================
        # ENVIAR EMAIL DE NOTIFICAÇÃO
        # ====================================================================
        try:
            settings = Settings()

            # Verifica se o envio de email está ativo (feature toggle)
            if not settings.EMAIL_RPS_ATIVO:
                logger.info("[APROVACAO RPS] Email desativado via configuração (EMAIL_RPS_ATIVO=false)")
            else:
                destinatarios_email = settings.EMAIL_DESTINATARIOS_RPS

                if not destinatarios_email or not destinatarios_email.strip():
                    logger.warning("[APROVACAO RPS] EMAIL_DESTINATARIOS_RPS não configurado - Email não enviado")
                else:
                    # Converte string de emails separados por vírgula em lista
                    lista_destinatarios = [email.strip() for email in destinatarios_email.split(',') if email.strip()]

                    # Gera HTML do email usando template
                    html_corpo = gerar_email_rps_aprovacao(
                        duplicata=duplicata,
                        usuario_atual=usuario_atual,
                        data_acao=nova_aprovacao.DataAcao
                    )

                    # Envia email
                    enviar_email(
                        destinatarios=lista_destinatarios,
                        assunto=f"✅ RPS #{duplicata.Duplicata} Aprovado - Portal MetaRH",
                        html_corpo=html_corpo,
                        remetente=settings.EMAIL_RPS_REMETENTE if settings.EMAIL_RPS_REMETENTE else None,
                        senha=settings.EMAIL_RPS_SENHA if settings.EMAIL_RPS_SENHA else None,
                        nome_remetente="Portal Cliente MetaRH"
                    )

                    logger.info(
                        f"[APROVACAO RPS] Email enviado com sucesso | "
                        f"Destinatarios={lista_destinatarios} | "
                        f"RPS={duplicata.Duplicata}"
                    )

        except Exception as e_email:
            # Não falha a aprovação se o email der erro
            logger.error(
                f"[APROVACAO RPS] ERRO ao enviar email | "
                f"RPS={duplicata.Duplicata} | "
                f"Erro={str(e_email)}",
                exc_info=True
            )

        return AcaoRPSResponse(
            sucesso=True,
            mensagem=f"RPS {duplicata.Duplicata} aprovado com sucesso",
            status_atual='aprovado',
            data_acao=nova_aprovacao.DataAcao.isoformat()
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(
            f"[APROVACAO RPS] ERRO NÃO TRATADO | "
            f"Duplicata={request.duplicata} | "
            f"Tipo do erro={type(e).__name__} | "
            f"Mensagem={str(e)} | "
            f"Usuario={usuario_atual.Nome}",
            exc_info=True
        )
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Erro ao aprovar RPS: {str(e)}"
        )


@router.post(
    "/rps/reprovar",
    response_model=AcaoRPSResponse,
    status_code=HTTPStatus.OK,
    summary="Reprovar RPS",
    description="Reprova um RPS com motivo e descrição obrigatórios"
)
def reprovar_rps(
    request: ReprovarRPSRequest,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Reprova um RPS com motivo e descrição obrigatórios

    Fluxo:
    1. Valida motivo e descrição
    2. Buscar RPS (usando chave composta)
    3. Cria registro de reprovação
    4. Retorna confirmação

    Requer autenticação via JWT token
    """

    # 1. Validações
    if not request.motivo_reprovacao or not request.motivo_reprovacao.strip():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Motivo da reprovação é obrigatório"
        )

    if not request.descricao_reprovacao or not request.descricao_reprovacao.strip():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Descrição da reprovação é obrigatória"
        )

    # 2. Buscar RPS usando chave composta
    duplicata = session.execute(
        select(TB_Duplicata).where(
            and_(
                TB_Duplicata.CodigoEmpresaFat == request.codigo_empresa_fat,
                TB_Duplicata.CodigoFilialFat == request.codigo_filial_fat,
                TB_Duplicata.Duplicata == request.duplicata,
                TB_Duplicata.Status == 'A'
            )
        )
    ).scalars().first()

    if not duplicata:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"RPS {request.duplicata} não encontrado para Empresa {request.codigo_empresa_fat}, Filial {request.codigo_filial_fat}"
        )

    # 3. Criar registro de reprovação
    # Obter ID do status 'reprovado'
    id_status_reprovado = obter_id_status_aprovacao(session, 'reprovado')

    nova_reprovacao = TB_AprovacaoRPS(
        CodigoEmpresaFat=duplicata.CodigoEmpresaFat,
        CodigoFilialFat=duplicata.CodigoFilialFat,
        Duplicata=duplicata.Duplicata,
        IdStatusAprovacao=id_status_reprovado,
        StatusAprovacao='reprovado',  # ⚠️ DEPRECATED: Será removido após migração
        TipoAcao='reprovacao',
        MotivoReprovacao=request.motivo_reprovacao.strip(),
        DescricaoReprovacao=request.descricao_reprovacao.strip(),
        ID_Usuario=usuario_atual.ID,
        NomeUsuario=usuario_atual.Nome,
        EmailUsuario=usuario_atual.Email
    )

    # Log atualizado
    logger.info(
        f"[REPROVACAO RPS] Salvando registro de reprovação no banco | "
        f"RPS (Duplicata)={duplicata.Duplicata} | "
        f"NFE={duplicata.NroNFe or 'Não emitida'} | "
        f"CodigoEmpresaFat={duplicata.CodigoEmpresaFat} | "
        f"CodigoFilialFat={duplicata.CodigoFilialFat} | "
        f"Usuario={usuario_atual.Nome} (ID={usuario_atual.ID}) | "
        f"Email={usuario_atual.Email} | "
        f"StatusAprovacao=reprovado | "
        f"TipoAcao=reprovacao | "
        f"Motivo={request.motivo_reprovacao.strip()} | "
        f"Descricao={request.descricao_reprovacao.strip()}"
    )

    session.add(nova_reprovacao)
    session.commit()
    session.refresh(nova_reprovacao)

    logger.info(
        f"[REPROVACAO RPS] Registro salvo com sucesso | "
        f"ID_Registro={nova_reprovacao.ID} | "
        f"DataAcao={nova_reprovacao.DataAcao}"
    )

    # ====================================================================
    # ENVIAR EMAIL DE NOTIFICAÇÃO
    # ====================================================================
    try:
        settings = Settings()

        # Verifica se o envio de email está ativo (feature toggle)
        if not settings.EMAIL_RPS_ATIVO:
            logger.info("[REPROVACAO RPS] Email desativado via configuração (EMAIL_RPS_ATIVO=false)")
        else:
            destinatarios_email = settings.EMAIL_DESTINATARIOS_RPS

            if not destinatarios_email or not destinatarios_email.strip():
                logger.warning("[REPROVACAO RPS] EMAIL_DESTINATARIOS_RPS não configurado - Email não enviado")
            else:
                # Converte string de emails separados por vírgula em lista
                lista_destinatarios = [email.strip() for email in destinatarios_email.split(',') if email.strip()]

                # Gera HTML do email usando template
                html_corpo = gerar_email_rps_reprovacao(
                    duplicata=duplicata,
                    usuario_atual=usuario_atual,
                    data_acao=nova_reprovacao.DataAcao,
                    motivo_reprovacao=request.motivo_reprovacao,
                    descricao_reprovacao=request.descricao_reprovacao
                )

                # Envia email
                enviar_email(
                    destinatarios=lista_destinatarios,
                    assunto=f"❌ RPS #{duplicata.Duplicata} Reprovado - Portal MetaRH",
                    html_corpo=html_corpo,
                    remetente=settings.EMAIL_RPS_REMETENTE if settings.EMAIL_RPS_REMETENTE else None,
                    senha=settings.EMAIL_RPS_SENHA if settings.EMAIL_RPS_SENHA else None,
                    nome_remetente="Portal Cliente MetaRH"
                )

                logger.info(
                    f"[REPROVACAO RPS] Email enviado com sucesso | "
                    f"Destinatarios={lista_destinatarios} | "
                    f"RPS={duplicata.Duplicata}"
                )

    except Exception as e_email:
        # Não falha a reprovação se o email der erro
        logger.error(
            f"[REPROVACAO RPS] ERRO ao enviar email | "
            f"RPS={duplicata.Duplicata} | "
            f"Erro={str(e_email)}",
            exc_info=True
        )

    return AcaoRPSResponse(
        sucesso=True,
        mensagem=f"RPS {duplicata.Duplicata} reprovado",
        status_atual='reprovado',
        data_acao=nova_reprovacao.DataAcao.isoformat()
    )


@router.get(
    "/rps/{rps_id}/historico-aprovacoes",
    response_model=list[HistoricoAprovacaoRPS],
    status_code=HTTPStatus.OK,
    summary="Histórico de Aprovações do RPS",
    description="Retorna histórico completo de aprovações/reprovações ordenado por data"
)
def obter_historico_aprovacoes_rps(
    rps_id: int,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Retorna histórico completo de aprovações/reprovações
    Ordenado da mais recente para a mais antiga

    Requer autenticação via JWT token
    """

    # Buscar RPS para validar existência
    duplicata = session.execute(
        select(TB_Duplicata).where(TB_Duplicata.Duplicata == rps_id)
    ).scalars().first()

    if not duplicata:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"RPS com ID {rps_id} não encontrado"
        )

    # Buscar histórico com JOIN para obter código do status
    from ..models import TB_StatusAprovacao

    historico = session.execute(
        select(TB_AprovacaoRPS, TB_StatusAprovacao.Codigo)
        .join(TB_StatusAprovacao, TB_AprovacaoRPS.IdStatusAprovacao == TB_StatusAprovacao.ID)
        .where(
            and_(
                TB_AprovacaoRPS.CodigoEmpresaFat == duplicata.CodigoEmpresaFat,
                TB_AprovacaoRPS.CodigoFilialFat == duplicata.CodigoFilialFat,
                TB_AprovacaoRPS.Duplicata == duplicata.Duplicata
            )
        )
        .order_by(TB_AprovacaoRPS.DataAcao.desc())
    ).all()

    return [
        HistoricoAprovacaoRPS(
            id=item[0].ID,
            status_aprovacao=item[1],  # Código do status da tabela de domínio
            tipo_acao=item[0].TipoAcao,
            motivo_reprovacao=item[0].MotivoReprovacao,
            descricao_reprovacao=item[0].DescricaoReprovacao,
            nome_usuario=item[0].NomeUsuario,
            email_usuario=item[0].EmailUsuario,
            data_acao=item[0].DataAcao.isoformat()
        )
        for item in historico
    ]


@router.get(
    "/rps/motivos-reprovacao",
    response_model=ListaMotivosReprovacaoResponse,
    summary="Listar motivos de reprovação ativos",
    description="""
    Lista todos os motivos de reprovação ativos para exibição em dropdown.

    Retorna apenas motivos com Ativo=True, ordenados pelo campo Ordem.
    """
)
def listar_motivos_reprovacao(
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Lista motivos de reprovação ativos para dropdown

    Retorna:
    - Lista de motivos ordenados por Ordem ASC
    - Apenas motivos com flag Ativo=True
    """
    logger.info(f"[MOTIVOS REPROVACAO] Listando motivos ativos | Usuario={usuario_atual.Nome}")

    try:
        # Query para buscar motivos ativos ordenados
        query = (
            select(TB_MotivoReprovacaoRPS)
            .where(TB_MotivoReprovacaoRPS.Ativo == True)
            .order_by(TB_MotivoReprovacaoRPS.Ordem.asc())
        )

        result = session.execute(query)
        motivos = result.scalars().all()

        # Mapear para schema de resposta
        motivos_response = [
            MotivoReprovacaoResponse(
                id=m.ID,
                codigo=m.Codigo,
                descricao=m.Descricao,
                descricaoDetalhada=m.DescricaoDetalhada
            )
            for m in motivos
        ]

        logger.info(f"[MOTIVOS REPROVACAO] Encontrados {len(motivos_response)} motivos ativos")

        return ListaMotivosReprovacaoResponse(
            motivos=motivos_response,
            total=len(motivos_response)
        )

    except Exception as e:
        logger.error(f"[MOTIVOS REPROVACAO] Erro ao listar motivos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar motivos de reprovação: {str(e)}"
        )


# ====================================================================
# ENDPOINTS DE CONTRATOS
# ====================================================================

@router.get(
    "/contratos",
    response_model=ListaContratosResponse,
    status_code=HTTPStatus.OK,
    summary="Listar Contratos",
    description="Retorna lista de contratos com filtros opcionais e paginação"
)
def listar_contratos(
    cnpj: Optional[str] = Query(None, description="Filtro por CNPJ do cliente"),
    numero_contrato: Optional[str] = Query(None, description="Filtro por número do contrato"),
    status: Optional[str] = Query(None, description="Filtro por status (A=Ativo, I=Inativo)"),
    data_assinatura_inicio: Optional[str] = Query(None, description="Data início assinatura (YYYY-MM-DD)"),
    data_assinatura_fim: Optional[str] = Query(None, description="Data fim assinatura (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros por página"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Lista contratos do cliente com filtros opcionais

    - Requer autenticação via JWT token
    - FILTRA AUTOMATICAMENTE pela empresa do usuário logado
    - Suporta paginação via limit/offset
    - Retorna lista de contratos + total de registros
    """

    logger.info(
        f"[CONTRATOS] Listando contratos | "
        f"Usuario={usuario_atual.Nome} (ID={usuario_atual.ID}) | "
        f"Filtros: CNPJ={cnpj}, NumeroContrato={numero_contrato}, Status={status}"
    )

    # ================================================================
    # VALIDAÇÃO DE EMPRESA - SEGURANÇA
    # ================================================================
    if not usuario_atual.IDEmpresa:
        logger.warning(f"[CONTRATOS] Usuário {usuario_atual.ID} sem empresa vinculada")
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Usuário sem empresa vinculada"
        )

    empresa_usuario = usuario_atual.empresa

    if not empresa_usuario or not empresa_usuario.Ativo:
        logger.warning(f"[CONTRATOS] Empresa inativa para usuário {usuario_atual.ID}")
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Empresa inativa ou não encontrada"
        )

    try:
        codigo_cliente_int = int(empresa_usuario.CodigoCliente)
    except (ValueError, TypeError):
        logger.error(f"[CONTRATOS] CodigoCliente inválido: {empresa_usuario.CodigoCliente}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Configuração de empresa inválida"
        )

    logger.info(f"[CONTRATOS] Filtrando por CodigoCliente={codigo_cliente_int}")

    try:
        # ============================================================
        # QUERY BASE + FILTRO AUTOMÁTICO DE SEGURANÇA
        # ============================================================
        query = (
            select(TB_Contratos)
            .where(TB_Contratos.CodigoCliente == codigo_cliente_int)  # FILTRO OBRIGATÓRIO
        )

        # ============================================================
        # APLICAR FILTROS OPCIONAIS
        # ============================================================
        if cnpj:
            # Remove formatação do CNPJ para busca
            cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")
            query = query.where(TB_Contratos.CNPJ.like(f"%{cnpj_limpo}%"))

        if numero_contrato:
            query = query.where(TB_Contratos.NumeroContrato.like(f"%{numero_contrato}%"))

        if status and status in ['A', 'I']:
            query = query.where(TB_Contratos.Status == status)

        # Filtro por data de assinatura (intervalo)
        if data_assinatura_inicio:
            try:
                dt_inicio = datetime.strptime(data_assinatura_inicio, "%Y-%m-%d")
                # Range: >= início (usa índice)
                query = query.where(TB_Contratos.DataAssinatura >= dt_inicio)
            except ValueError:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Formato de data_assinatura_inicio inválido. Use YYYY-MM-DD"
                )

        if data_assinatura_fim:
            try:
                dt_fim = datetime.strptime(data_assinatura_fim, "%Y-%m-%d")
                # Range: < dia seguinte (mais preciso que <= 23:59:59)
                dt_fim_exclusivo = dt_fim + timedelta(days=1)
                query = query.where(TB_Contratos.DataAssinatura < dt_fim_exclusivo)
            except ValueError:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Formato de data_assinatura_fim inválido. Use YYYY-MM-DD"
                )

        # ============================================================
        # TOTAL DE REGISTROS (antes da paginação e ordenação)
        # ============================================================
        # IMPORTANTE: Usar with_only_columns() para preservar os filtros WHERE
        count_query = query.with_only_columns(func.count(), maintain_column_froms=True).order_by(None)
        total = session.scalar(count_query) or 0

        logger.info(f"[CONTRATOS] Total encontrado: {total}")

        # ============================================================
        # ORDENAÇÃO
        # ============================================================
        query = query.order_by(TB_Contratos.DataAssinatura.desc())

        # ============================================================
        # APLICAR PAGINAÇÃO
        # ============================================================
        query_paginada = query.offset(offset).limit(limit)

        # ============================================================
        # EXECUTAR QUERY
        # ============================================================
        contratos = session.execute(query_paginada).scalars().all()

        logger.info(f"[CONTRATOS] Retornando {len(contratos)} contratos (página offset={offset}, limit={limit})")

        # ============================================================
        # PROCESSAR RESULTADOS
        # ============================================================
        contratos_processados = []
        for contrato in contratos:
            # Formatar datas para DD/MM/YYYY
            data_assinatura_fmt = contrato.DataAssinatura.strftime("%d/%m/%Y") if contrato.DataAssinatura else ""
            data_vencimento_fmt = contrato.DataVencimento.strftime("%d/%m/%Y") if contrato.DataVencimento else None

            contrato_response = ContratoResponse(
                id=contrato.ID,
                numero_contrato=contrato.NumeroContrato,
                cnpj=contrato.CNPJ,
                razao_social=contrato.RazaoSocial,
                servicos_contemplados=contrato.ServicosContemplados,
                data_assinatura=data_assinatura_fmt,
                vigencia=contrato.Vigencia,
                data_vencimento=data_vencimento_fmt,
                valor=float(contrato.Valor) if contrato.Valor else None,
                status=contrato.Status,
                tem_arquivo_pdf=bool(contrato.ArquivoPDF)
            )
            contratos_processados.append(contrato_response)

        return ListaContratosResponse(
            items=contratos_processados,
            total=total
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CONTRATOS] Erro ao listar contratos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar contratos: {str(e)}"
        )


@router.get(
    "/contratos/{contrato_id}/download",
    response_model=DownloadContratoResponse,
    status_code=HTTPStatus.OK,
    summary="Download Contrato PDF",
    description="Retorna URL do arquivo PDF do contrato"
)
def download_contrato(
    contrato_id: int,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """
    Retorna URL para download do contrato em PDF

    - Requer autenticação via JWT token
    - Valida que o contrato pertence à empresa do usuário
    - Retorna erro se não houver arquivo PDF cadastrado
    """

    logger.info(
        f"[CONTRATOS DOWNLOAD] Solicitação | "
        f"ContratoID={contrato_id} | "
        f"Usuario={usuario_atual.Nome} (ID={usuario_atual.ID})"
    )

    # ================================================================
    # VALIDAÇÃO DE EMPRESA - SEGURANÇA
    # ================================================================
    if not usuario_atual.IDEmpresa:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Usuário sem empresa vinculada"
        )

    empresa_usuario = usuario_atual.empresa

    if not empresa_usuario or not empresa_usuario.Ativo:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Empresa inativa ou não encontrada"
        )

    try:
        codigo_cliente_int = int(empresa_usuario.CodigoCliente)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Configuração de empresa inválida"
        )

    try:
        # ============================================================
        # BUSCAR CONTRATO
        # ============================================================
        query = (
            select(TB_Contratos)
            .where(TB_Contratos.ID == contrato_id)
            .where(TB_Contratos.CodigoCliente == codigo_cliente_int)  # SEGURANÇA: mesma empresa
        )

        contrato = session.execute(query).scalars().first()

        if not contrato:
            logger.warning(f"[CONTRATOS DOWNLOAD] Contrato {contrato_id} não encontrado ou sem acesso")
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Contrato {contrato_id} não encontrado"
            )

        # ============================================================
        # VALIDAR EXISTÊNCIA DE ARQUIVO PDF
        # ============================================================
        if not contrato.ArquivoPDF:
            logger.warning(f"[CONTRATOS DOWNLOAD] Contrato {contrato_id} sem arquivo PDF")
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Contrato {contrato.NumeroContrato} não possui arquivo PDF disponível"
            )

        logger.info(f"[CONTRATOS DOWNLOAD] Sucesso | Contrato={contrato.NumeroContrato} | URL={contrato.ArquivoPDF}")

        return DownloadContratoResponse(
            url=contrato.ArquivoPDF,
            numero_contrato=contrato.NumeroContrato,
            disponivel_ate=None  # Pode ser implementado futuramente com SAS tokens do Azure
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CONTRATOS DOWNLOAD] Erro: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter arquivo do contrato: {str(e)}"
        )
