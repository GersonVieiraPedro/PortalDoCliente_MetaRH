'use client'

import { ReactNode, useEffect, useRef, useState } from 'react'

type AlertaProps = {
  titulo: string
  mensagem: ReactNode
  tipo: 'Simples' | 'Completo'
  botoes: {
    cancelar: null | 'Sim'
    continuar: null | 'Sim'
  } | null
  visivel: boolean
  setMensagemALerta: (mensagem: Array<any>) => void
}

export function Alerta(props: AlertaProps) {
  const [visivel, setVisivel] = useState(props.visivel)
  const alertaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const AlertaVisivel = localStorage.getItem('AlertaVisivel')
    if (AlertaVisivel == null || AlertaVisivel === 'true') {
      localStorage.setItem('AlertaVisivel', 'true')
      setVisivel(true)
    }
  }, [])

  useEffect(() => {
    if (visivel) {
      document.body.style.overflow = 'hidden'
      if (alertaRef.current) alertaRef.current.focus()
    } else {
      document.body.style.overflow = 'auto'
    }

    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [visivel])

  const fechar = () => {
    setVisivel(false)
    localStorage.setItem('AlertaVisivel', 'false')
    props.setMensagemALerta([])
  }

  return (
    <div
      className="bg-black-transparente bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center"
      hidden={!visivel}
    >
      <div
        ref={alertaRef}
        tabIndex={-1}
        className={`max-h-screen w-full max-w-2xl min-w-[300px] overflow-auto rounded-md border border-gray-500 bg-white text-gray-700 shadow-lg ${props.tipo === 'Simples' ? 'grid grid-rows-4' : 'grid grid-rows-8'} `}
      >
        <div className="relative flex h-12 w-full items-center justify-center rounded-t-md border-b border-gray-300 p-5">
          <h1 className="text-2xl font-bold">{props.titulo}</h1>
          {props.tipo === 'Simples' && (
            <button
              onClick={fechar}
              className="bi bi-x-square-fill absolute right-2 cursor-pointer text-2xl text-gray-500 hover:text-rose-600"
            ></button>
          )}
        </div>

        <div className="row-span-6 flex w-full items-center justify-center px-6 py-4">
          {props.mensagem}
        </div>

        {props.tipo === 'Completo' && (
          <div className="flex w-full items-center justify-center gap-6 rounded-b-md border-t border-gray-300 p-5">
            {props.botoes?.continuar && (
              <button className="h-full cursor-pointer rounded-md bg-gray-300 px-6 py-2 hover:bg-green-500 hover:text-white">
                Continuar
              </button>
            )}
            {props.botoes?.cancelar && (
              <button className="h-full cursor-pointer rounded-md bg-gray-300 px-6 py-2 hover:bg-red-500 hover:text-white">
                Cancelar
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
