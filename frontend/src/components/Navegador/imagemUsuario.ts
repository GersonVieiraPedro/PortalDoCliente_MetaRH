'use client'

export async function ConsultarUsuario(token: string, email: string) {
  if (token != null && email != null) {
    const url = `http://127.0.0.1:8000/usuarios/listar?Limite=100&Inicio=0&TipoFiltro=Email&Filtro=${email}`

    console.log('url :', url)
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    return data.usuarios[0]
  }
}

export async function ExisteImagem(id: number) {
  if (id != null) {
    const url = `http://127.0.0.1:8000/imagens/usuario/existe/${id}.png`

    console.log('url :', url)
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    return data
  }
}
