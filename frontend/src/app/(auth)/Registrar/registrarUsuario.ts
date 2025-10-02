'use server'

import { error } from 'console'
import { isCnpjValid } from './validarCNPJ'

export default async function resgistrarUsuario(_prevState: any, formData: FormData) {
  const entries = Array.from(formData.entries())

  const data = Object.fromEntries(entries)
  if (!isCnpjValid(data.cnpj)) {
    return {
      status: 'Erro',
      mensagem: 'CNPJ invalido',
    }
  }

  if (!data.email || !data.nome || !data.senha || !data.cnpj) {
    return {
      status: 'Erro',
      mensagem: 'Precisa preencher todos os campos !',
    }
    //Chamar um alerta
  } else {
    const res = await fetch('http://127.0.0.1:8000/usuarios/cadastrar', {
      method: 'POST',
      body: JSON.stringify({
        nome: data.nome,
        email: data.email,
        senha: data.senha,
        cnpj: data.cnpj,
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const dados = await res.json()
    if (res.ok) {
      return dados
    } else {
      return dados.detail
    }
  }
}
