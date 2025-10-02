'use client'
import { useRouter } from 'next/navigation'
import { MenuLateral } from '../components/MenuLateral'
import { Navegador } from '../components/Navegador'
import { use, useEffect, useState } from 'react'
import { VerificarNome } from '../lib/decode'
import { getAuthToken } from '../lib/cockies'

export default function Home() {
  const router = useRouter()

  const [token, setToken] = useState<string>('')
  const [NomeUsuario, setNomeUsuario] = useState<string>('')

  useEffect(() => {
    const fetchToken = async () => {
      const token = await getAuthToken()
      setToken(token || '')
      if (!token) {
        router.push('/Login')
      }
    }
    fetchToken()
  }, [])

  useEffect(() => {
    if (token) {
      const Nome = VerificarNome(token)
      setNomeUsuario(Nome || '')
      //window.location.reload();
    }
  }, [token])

  return (
    <div>
      <MenuLateral />
      <Navegador />
      <div className="grid h-screen w-full grid-cols-5 gap-5 pt-20 pr-5 pb-5 pl-20 text-gray-600">
        <div className="z-0 col-span-3 grid content-start overflow-y-auto rounded-lg border border-gray-300 bg-white">
          <div className="sticky top-0 flex h-15 w-full items-center border-b border-b-gray-200 bg-white p-2 pl-5 text-2xl font-medium">
            <h2>Solicitações</h2>
          </div>
          <ul className="List-border mt-2 grid w-full gap-2 pr-1 pl-6">
            <li className="flex justify-between">
              <div className="">
                <h2 className="pb-2 text-lg font-medium">Solicitação de Admissão</h2>
                <h5 className="pb-1 text-xs">11/09 12:55</h5>
              </div>
              <div className="flex items-center gap-5">
                <div className="rounded-full bg-green-500 px-2 py-1">
                  <i className="bi bi-check text-2xl text-white"></i>
                </div>
                <button className="h-full cursor-pointer rounded-md p-2 px-4 hover:bg-gray-200">
                  <i className="bi bi-trash-fill text-red-600"></i>
                </button>
              </div>
            </li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 1</li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 1</li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
          </ul>
        </div>
        <div className="col-span-2 grid max-h-screen grid-rows-3 gap-4">
          <div className="relative h-50 w-full overflow-hidden rounded-lg border border-gray-300 bg-white">
            <img
              className="absolute z-0 rounded-lg object-cover"
              src="/RH-Estrategico-Gestao-negocio-Horizontal.jpg"
              alt=""
            />
            <button className="bi bi-images bg-cinza-transparente absolute right-0 cursor-pointer px-5 py-2 font-bold text-white"></button>
          </div>
          <div className="h-full w-full rounded-lg border border-gray-300 bg-white"></div>
          <div className="h-full w-full rounded-lg border border-gray-300 bg-white"></div>
        </div>
      </div>
    </div>
  )
}
