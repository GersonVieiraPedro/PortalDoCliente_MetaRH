'use client'

import Form from 'next/form'
import Link from 'next/link'
import { useActionState, useCallback, useEffect, useState } from 'react'
import login from './login'
import { useRouter } from 'next/navigation'
import Cookies from 'js-cookie'
import { setAuthToken } from '@/src/lib/cockies'
import { useUsuario } from '../../contexts/UsuarioContext'

export default function FormLogin() {
  const [state, formAction, isPending] = useActionState(login, null)
  const router = useRouter()
  const [visivel, setVisivel] = useState(false)
  const { usuario, setUsuario, carregarUsuario } = useUsuario()

  useEffect(() => {
    if (state?.status === 'Sucesso' && state.token) {
      setAuthToken(state.token) // Salva o token no cookie
      carregarUsuario() // Força o contexto a recarregar o usuário
      router.push('/') // Redireciona após atualizar os dados
    }
  }, [state, router])

  return (
    <Form action={formAction}>
      <div className="-top-10 grid h-full w-sm gap-5">
        <div>
          <h4 className="pl-1 text-sm">E-mail</h4>
          <input
            autoFocus
            name="email"
            className="h-8 w-full rounded-md border border-gray-400 p-3"
            type="text"
            placeholder="Digite seu e-mail"
          />
        </div>
        <div className="relative">
          <h4 className="pl-1 text-sm">Senha</h4>
          <input
            name="senha"
            className="h-8 w-full rounded-md border border-gray-400 p-3"
            type={!visivel ? 'password' : 'text'}
            placeholder="Digite sua senha"
          />
          <div
            onClick={() => {
              setVisivel(!visivel)
            }}
            className={`bi absolute top-6 right-1 grid h-6 w-6 cursor-pointer items-center rounded-full pl-1 hover:bg-purple-200 ${
              visivel ? 'bi-eye' : 'bi-eye-slash'
            }`}
          ></div>
        </div>
        <h1 className="cursor-pointer text-center text-sm hover:text-purple-700">
          Esqueci a Senha ?
        </h1>
        <button className="mt-10 cursor-pointer rounded-md bg-purple-500 p-1 text-2xl text-white hover:bg-purple-600">
          Entrar
        </button>
        <Link href={'/Registrar'}>
          <h1 className="cursor-pointer text-center text-sm hover:text-purple-700">
            Não possuo cadastro !
          </h1>
        </Link>
      </div>
    </Form>
  )
}
