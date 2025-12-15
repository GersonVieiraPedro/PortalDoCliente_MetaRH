"""
Módulo para carregar e renderizar templates de email HTML.

Este módulo fornece funções auxiliares para carregar templates de email
do diretório templates/email/ e substituir placeholders por valores dinâmicos.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi.templating import Jinja2Templates #typo: ignore
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # pasta atual (ex: backend/)
TEMPLATES_DIR = BASE_DIR / "templates" / "email"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def carregar_template(nome_arquivo: str) -> str:
    """
    Carrega um template HTML do diretório templates/email/.

    Args:
        nome_arquivo: Nome do arquivo de template (ex: 'rps_aprovacao.html')

    Returns:
        Conteúdo do template HTML como string

    Raises:
        FileNotFoundError: Se o template não existir
    """
    # Diretório base do módulo backend
    base_dir = Path(__file__).parent
    template_path = base_dir / "templates" / "email" / nome_arquivo

    if not template_path.exists():
        raise FileNotFoundError(f"Template não encontrado: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def renderizar_template(template: str, dados: Dict[str, Any]) -> str:
    """
    Renderiza um template substituindo placeholders {chave} por valores.

    Args:
        template: String HTML com placeholders no formato {chave}
        dados: Dicionário com valores para substituir os placeholders

    Returns:
        HTML renderizado com valores substituídos

    Example:
        >>> template = "<p>Olá {nome}</p>"
        >>> dados = {"nome": "João"}
        >>> renderizar_template(template, dados)
        '<p>Olá João</p>'
    """
    return template.format(**dados)


def formatar_valor_monetario(valor: float) -> str:
    """
    Formata um valor numérico para formato monetário brasileiro.

    Args:
        valor: Valor numérico

    Returns:
        String formatada (ex: "R$ 1.234,56")
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data: datetime, formato: str = "%d/%m/%Y") -> str:
    """
    Formata um objeto datetime para string.

    Args:
        data: Objeto datetime
        formato: Formato de saída (padrão: DD/MM/YYYY)

    Returns:
        String formatada da data
    """
    if data is None:
        return "N/A"
    return data.strftime(formato)


def formatar_data_hora(data: datetime) -> str:
    """
    Formata um objeto datetime para string com hora.

    Args:
        data: Objeto datetime

    Returns:
        String formatada (ex: "29/10/2025 14:30:00")
    """
    return formatar_data(data, formato="%d/%m/%Y %H:%M:%S")


def preparar_dados_email_rps(
    duplicata,
    usuario_atual,
    data_acao: datetime,
    motivo_reprovacao: str = None,
    descricao_reprovacao: str = None
) -> Dict[str, Any]:
    """
    Prepara dicionário de dados para template de email de RPS.

    Args:
        duplicata: Objeto TB_Duplicata
        usuario_atual: Objeto TB_Usuarios (quem aprovou/reprovou)
        data_acao: Data/hora da aprovação/reprovação
        motivo_reprovacao: Motivo da reprovação (opcional)
        descricao_reprovacao: Descrição da reprovação (opcional)

    Returns:
        Dicionário com dados formatados para o template
    """
    dados = {
        # Informações do RPS
        "duplicata": str(duplicata.Duplicata),
        "numero_nfe": str(duplicata.NroNFe) if duplicata.NroNFe else "Não emitida",
        "codigo_empresa_fat": str(duplicata.CodigoEmpresaFat),
        "codigo_filial_fat": str(duplicata.CodigoFilialFat),
        "valor": formatar_valor_monetario(float(duplicata.ValorBruto) if duplicata.ValorBruto else 0),
        "vencimento": formatar_data(duplicata.DataVecto) if duplicata.DataVecto else "N/A",

        # Informações do usuário
        "usuario_nome": usuario_atual.Nome,
        "usuario_email": usuario_atual.Email,

        # Informações da ação
        "data_acao": formatar_data_hora(data_acao),

        # Ano atual (para footer)
        "ano_atual": str(datetime.now().year),
    }

    # Adiciona dados de reprovação se fornecidos
    if motivo_reprovacao:
        dados["motivo_reprovacao"] = motivo_reprovacao
    if descricao_reprovacao:
        dados["descricao_reprovacao"] = descricao_reprovacao

    return dados


def gerar_email_rps_aprovacao(duplicata, usuario_atual, data_acao: datetime) -> str:
    """
    Gera HTML completo do email de aprovação de RPS.

    Args:
        duplicata: Objeto TB_Duplicata
        usuario_atual: Objeto TB_Usuarios
        data_acao: Data/hora da aprovação

    Returns:
        HTML renderizado pronto para envio
    """
    template = carregar_template("rps_aprovacao.html")
    dados = preparar_dados_email_rps(duplicata, usuario_atual, data_acao)
    return renderizar_template(template, dados)


def gerar_email_rps_reprovacao(
    duplicata,
    usuario_atual,
    data_acao: datetime,
    motivo_reprovacao: str,
    descricao_reprovacao: str
) -> str:
    """
    Gera HTML completo do email de reprovação de RPS.

    Args:
        duplicata: Objeto TB_Duplicata
        usuario_atual: Objeto TB_Usuarios
        data_acao: Data/hora da reprovação
        motivo_reprovacao: Motivo da reprovação
        descricao_reprovacao: Descrição detalhada da reprovação

    Returns:
        HTML renderizado pronto para envio
    """
    template = carregar_template("rps_reprovacao.html")
    dados = preparar_dados_email_rps(
        duplicata,
        usuario_atual,
        data_acao,
        motivo_reprovacao,
        descricao_reprovacao
    )
    return renderizar_template(template, dados)



def render_alteracao_email_jinja(titulo: str, mensagem: str, detalhes: dict, link: str):
    """
    Renderiza o HTML de solicitação de alteração usando Jinja2.

    Args:
        titulo: Título principal do email
        mensagem: Mensagem HTML (aceita tags)
        detalhes: Dicionário chave-valor exibido na tabela
        link: URL do botão de ação

    Retorna:
        HTML final processado pelo Jinja2
    """
    return templates.get_template("alteracao.html").render(
        titulo=titulo,
        mensagem=mensagem,
        detalhes=detalhes,
        link=link
    )


def render_encerramento_email_jinja(titulo: str, mensagem: str, link_cancelar: str, link_finalizar: str):
    """
    Renderiza o HTML de encerramento usando Jinja2.

    Args:
        titulo: Título principal do email
        mensagem: Mensagem HTML (aceita tags)
        detalhes: Dicionário chave-valor exibido na tabela
        link: URL do botão de ação

    Retorna:
        HTML final processado pelo Jinja2
    """
    return templates.get_template("encerramento.html").render(
        titulo=titulo,
        mensagem=mensagem,
        link_cancelar=link_cancelar,
        link_finalizar=link_finalizar
    )


# Alterar essas funções para usar o Jinja2, Soup é só para quando eu não tenho acesso direto ao arquivo html

"""
DESCONTINUADO

def soup_alteracoes(html: str,titulo: str, mensagem: str, dadosDetalhes: dict) -> BeautifulSoup:
    
    Atualiza um template HTML de email de alteração com dados dinâmicos.

    Args:
        html: String HTML do template base
        mensagem: Mensagem principal a ser exibida no email
        dadosDetalhes: Dicionário com pares chave-valor dos detalhes da alteração
        link: URL para redirecionamento (botão de ação)

    Returns:
        Objeto BeautifulSoup com o HTML manipulado e atualizado
    

    # Cria o objeto BeautifulSoup
    html_content = carregar_template(html)
    soup = BeautifulSoup(html_content, 'html.parser')

    # Atualiza o título
    titulo_tag = soup.find(id="Titulo")
    if titulo_tag:
        titulo_tag.string = titulo

    # Atualiza o conteúdo da mensagem
    mensagem_tag = soup.find(id="Mensagem")
    if mensagem_tag:
        mensagem_tag.clear()
        mensagem_tag.append(BeautifulSoup(mensagem, "html.parser"))

    # Atualiza os detalhes da alteração
    detalhes_tag = soup.find(id="Detalhes")
    if detalhes_tag:
        detalhes_html = ""
        for chave, valor in dadosDetalhes.items():
            detalhes_html += (
                f'<tr>'
                f'<td width="40%" style="font-weight: bold; color: #333">{chave}</td>'
                f'<td width="60%" class="ValorDetalhe">{valor}</td>'
                f'</tr>'
            )
            
        detalhes_tag.clear()
        detalhes_tag.append(BeautifulSoup(detalhes_html, 'html.parser'))

    #retorna a sopa montada 
    return soup



def add_link_soup(soup: BeautifulSoup, link: str) -> BeautifulSoup:
    
    Adiciona ou atualiza o link em um objeto BeautifulSoup de email.
    Dessa forma não é necessário recriar toda a sopa apenas para alterar o link.

    Args:
        soup: Objeto BeautifulSoup do email
        link: URL para redirecionamento (botão de ação)

    Returns:
        Objeto BeautifulSoup atualizado com o link
    
    link_tag = soup.find(id="Link")
    if link_tag:
        link_tag['href'] = link
    return soup


"""
