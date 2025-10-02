'use client'

import { useEffect, useState } from 'react'
import image from 'next/image'
import Link from 'next/link'
import { VerificarTipoAcesso } from '@/src/lib/decode'

type ModalProps = {
  titulo: string
  mensagem: string
  botoes: {
    cancelar: null | 'Sim'
    continuar: null | 'Sim'
  } | null
  tipo: 'Sucesso' | 'Erro' | 'Informacao' | null
}

export function Modal(props: ModalProps) {
  return (
    <div className="bg-black-transparente absolute z-50 flex h-screen w-screen items-center justify-center">
      <div className="grid h-auto min-h-1/2 w-auto min-w-3xl grid-cols-1 grid-rows-8 rounded-md border-1 border-gray-500 bg-white text-gray-700">
        <div className="flex h-12 w-full items-center justify-center rounded-t-md border border-b-1 border-gray-300 p-5">
          <h1 className="text-2xl font-bold">{props.titulo}</h1>
        </div>
        <div className="row-span-6 flex h-full w-full items-center justify-center p-5"></div>
        <div className="flex h-15 w-full items-center justify-center gap-25 rounded-b-md border border-t-1 border-gray-300 p-5">
          <button className="flex h-full w-max cursor-pointer items-center justify-center rounded-md bg-gray-300 p-5 px-20 hover:bg-green-500 hover:text-white">
            Continuar
          </button>
          <button className="flex h-full w-max cursor-pointer items-center justify-center rounded-md bg-gray-300 p-5 px-20 hover:bg-red-500 hover:text-white">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  )
}
