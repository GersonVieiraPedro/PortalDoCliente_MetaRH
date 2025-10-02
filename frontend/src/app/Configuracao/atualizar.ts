'use client'

export async function AtualizarUsuario(
  token: string,
  id: string,
  nome: string | null,
  senhaAntiga: string | null,
  senhaNova: string | null
) {
  if (token != null && id != null) {
    const url = `http://127.0.0.1:8000/usuarios/atualizar/${id}`

    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        Nome: nome || null,
        SenhaAntiga: senhaAntiga || null,
        SenhaNova: senhaNova || null,
      }),
    })

    const data = await response.json()
    return data
  }
}
