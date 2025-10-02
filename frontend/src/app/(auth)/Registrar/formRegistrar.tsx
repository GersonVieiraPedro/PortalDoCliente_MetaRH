'use client'

import Form from 'next/form'
import Link from 'next/link'
import resgistrarUsuario from './registrarUsuario'
import { useActionState, useCallback, useEffect, useRef, useState } from 'react'
import IMask from 'imask'

export default function FormRegistrar() {
  const [state, formAction, isPending] = useActionState(resgistrarUsuario, null)
  const [visivel, setVisivel] = useState(false)
  const [alerta, setAlerta] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (inputRef.current) {
      IMask(inputRef.current, {
        mask: '00.000.000/0000-00',
      })
    }
  }, [])

  useEffect(() => {
    const timeout = setTimeout(() => {
      setAlerta(false)
    }, 5000)

    return () => clearTimeout(timeout)
  }, [alerta])

  useEffect(() => {
    setAlerta(true)
  }, [state])

  return (
    <Form action={formAction}>
      <div className="-top-10 grid h-full w-sm gap-5 pt-15">
        {alerta == true && state && (
          <div
            className={`absolute top-10 h-max w-sm border p-3 ${
              state.status === 'Erro'
                ? 'border-red-700 bg-red-300 text-red-800'
                : 'border-green-700 bg-green-300 text-green-800'
            }`}
          >
            <h1 className="mb-1 font-bold">{state.status}</h1>
            <p className="mb-1 text-sm font-medium">{state.mensagem}</p>
          </div>
        )}
        <div>
          <h4 className="pl-1 text-sm">Nome</h4>
          <input
            autoFocus
            name="nome"
            className="h-8 w-full rounded-md border border-gray-400 p-3"
            type="text"
            placeholder="Digite seu nome"
          />
        </div>
        <div>
          <h4 className="pl-1 text-sm">E-mail</h4>
          <input
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
        <div>
          <h4 className="pl-1 text-sm">CNPJ</h4>
          <input
            name="cnpj"
            className="h-8 w-full rounded-md border border-gray-400 p-3"
            type="text"
            ref={inputRef}
            placeholder="00.000.000/0000-00"
          />
        </div>
        <button className="mt-10 cursor-pointer rounded-md bg-purple-500 p-1 text-2xl text-white hover:bg-purple-600">
          Entrar
        </button>
        <Link href={'/Login'}>
          <h1 className="cursor-pointer text-center text-sm hover:text-purple-700">
            Já tenho cadastro !
          </h1>
        </Link>
      </div>
    </Form>
  )
}
