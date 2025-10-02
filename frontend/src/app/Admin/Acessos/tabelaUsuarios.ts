'use server'

// Removed incorrect import of 'url'

interface Usuario {
  ID: number
  Nome: string
  Email: string
  CNPJ: string
  TipoAcesso: string
  PipedriveID: string
  CodigoCliente: string
  Status: boolean
  DataCadastro: string
  DataAtualizacao: string
}

export async function ConsultarUsuarios(
  token: string,
  TipoFiltro: string | null,
  Filtro: string | null
): Promise<Usuario[]> {
  let url: string

  if (TipoFiltro != null && Filtro != null) {
    url = `http://127.0.0.1:8000/usuarios/listar?TipoFiltro=${TipoFiltro}&Filtro=${Filtro}`
  } else {
    url = 'http://127.0.0.1:8000/usuarios/listar'
  }

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })

  const data = await response.json()

  return data.usuarios
}

export async function SalvarAlteracaoUsuarios(token: string, ListaUsuarios: any[]) {
  // Verifica se o token ou a lista estão ausentes ou vazios
  if (!token || !ListaUsuarios || ListaUsuarios.length === 0) {
    return {
      status: 'Erro',
      mensagem: 'Você precisa fazer uma alteração antes de salvar os dados.',
    }
  }

  const response = await fetch('http://127.0.0.1:8000/usuarios/atualizar/lista', {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(ListaUsuarios),
  })

  if (!response.ok) {
    const erro = await response.json()
    return { status: 'Erro', mensagem: erro.message || 'Falha na requisição.' }
  }

  const data = await response.json()
  return data
}
