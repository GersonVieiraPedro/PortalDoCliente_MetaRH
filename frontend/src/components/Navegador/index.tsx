'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import router from 'next/router'
import { useEffect, useRef, useState } from 'react'
import { useUsuario } from '@/src/app/contexts/UsuarioContext'
import { es } from 'date-fns/locale'

export function Navegador() {
  const [openNotif, setOpenNofif] = useState(false)
  const { usuario } = useUsuario()

  const [nomeUsuario, setNomeUsuario] = useState<string>('')

  const [existeImagem, setExisteImagem] = useState<any>(null)

  const nomeDiretorio = usePathname()

  useEffect(() => {
    if (usuario?.existeImagem !== null && usuario?.existeImagem !== undefined) {
      setExisteImagem(usuario.existeImagem)
    }
  }, [usuario])

  useEffect(() => {
    //console.log("existeImagem:", existeImagem);
  }, [existeImagem])

  const TipoFiltroRef = useRef<HTMLSelectElement>(null)
  const ValorFiltradoRef = useRef<HTMLInputElement>(null)

  const titulo = () => {
    switch (nomeDiretorio) {
      case '/':
        return ' '
      case '/Requisicao/Admissao':
        return 'Requisição'
      case '/Admin/Acessos':
        return 'Administração de Acessos'
      default:
        return ''
    }
  }

  return (
    <nav className="fixed z-1 flex h-15 w-screen bg-gray-100 text-gray-600">
      <div className="ml-15 grid h-full w-lvw grid-cols-3 content-center justify-between shadow-md">
        <div className="flex h-full w-full items-center gap-2 pl-2 text-3xl font-bold">
          <i className="bi bi-caret-right text-2xl"></i>
          <h2>{titulo()}</h2>
        </div>
        <div className="h-full w-full"></div>
        <div className="relative flex h-full w-full items-center justify-end gap-4 pr-10">
          {openNotif && (
            <div
              className={`absolute top-13 left-30 h-50 w-80 overflow-y-auto rounded-md bg-gray-50 px-5 py-2 shadow-md ${
                openNotif ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
              } `}
            >
              <div className="sticky top-0 mb-2 flex h-auto w-full justify-between border-b border-gray-300 bg-gray-50 p-2 text-2xl font-medium">
                <h2>Notificações</h2>
                <button className="group relative inline-block cursor-pointer rounded-full px-1 hover:bg-gray-300">
                  <i className="bi bi-check2-circle"></i>
                  <div className="absolute top-1/2 right-full z-50 mr-2 hidden -translate-y-1/2 rounded bg-gray-500 px-2 py-1 text-xs whitespace-nowrap text-white group-hover:block">
                    Marcar todos como lido !
                  </div>
                </button>
              </div>

              <ul className="grid gap-2 pl-2">
                <li>AAAAAAAAA</li>
                <li>Notificação 2</li>
                <li>Notificação 3</li>
                <li>Notificação 3</li>
                <li>Notificação 3</li>
                <li>Notificação 3</li>
              </ul>
            </div>
          )}

          <button
            onClick={() => {
              setOpenNofif(!openNotif)
            }}
            className="relative h-full w-10 cursor-pointer rounded-md border-0 hover:bg-gray-300"
          >
            <samp className="Font-micro absolute -top-0 -right-0 rounded-full bg-red-600 px-1.5 py-0.5 font-bold text-white">
              2
            </samp>
            <i className="bi bi-bell-fill"></i>
          </button>

          <div className="flex cursor-pointer items-center gap-4 border-l pl-5">
            <h5 className="">{usuario?.Nome}</h5>
            <Link href="/Configuracao">
              {existeImagem && (
                <img
                  className="h-10 w-10 rounded-full object-contain"
                  src={existeImagem ? usuario?.urlImagem : '/UsuarioAvatar.jpg'}
                  alt=""
                />
              )}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
