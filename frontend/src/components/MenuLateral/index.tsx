'use client'

import { useEffect, useState } from 'react'

import Link from 'next/link'
import { VerificarTipoAcesso } from '@/src/lib/decode'
import { useUsuario } from '@/src/app/contexts/UsuarioContext'

export function MenuLateral() {
  const [open, setOpen] = useState(false)
  const [menu, setMenu] = useState('')
  const [acesso, setAcesso] = useState('')
  const { usuario, setUsuario } = useUsuario()
  console.log('usuario - MenuLateral :', usuario)
  useEffect(() => {
    const token = usuario?.token ? usuario?.token : ''

    if (token !== '') {
      const vAcesso = VerificarTipoAcesso(token)
      setAcesso(vAcesso || '')
    }
  }, [usuario])

  return (
    <div className="fixed z-20 grid grid-cols-2">
      <div className="relative z-30 flex h-screen w-15 grid-cols-1 grid-rows-3 flex-col items-center justify-between bg-purple-500 text-gray-700">
        <div className="row-span-1">
          <button className="w-full justify-items-center p-3">
            <Link href="/">
              <img src="/LogoMetaRH.png" alt="" className="h-9 w-9 cursor-pointer" />
            </Link>
          </button>
        </div>
        <div className="row-auto items-center justify-center justify-items-center gap-2 px-2">
          <button
            onClick={() => {
              setOpen(!open)
              setMenu('Requisição')
              console.log(menu)
            }}
            id="BtRequisicao"
            className="my-1 w-full justify-items-center rounded-lg p-2 hover:bg-purple-600"
          >
            <i className="bi bi-file-earmark-text-fill cursor-pointer text-3xl text-white hover:text-4xl"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open)
              setMenu('DashBoard')
            }}
            className="my-1 w-full justify-items-center rounded-lg p-2 hover:bg-purple-600"
          >
            <i className="bi bi-bar-chart-line-fill cursor-pointer text-3xl text-white hover:text-4xl"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open)
              setMenu('Contatos')
            }}
            className="my-1 w-full justify-items-center rounded-lg p-2 hover:bg-purple-600"
          >
            <i className="bi bi-person-vcard cursor-pointer text-3xl text-white hover:text-4xl"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open)
              setMenu('Financeiro')
            }}
            className="my-1 w-full justify-items-center rounded-lg p-2 hover:bg-purple-600"
          >
            <i className="bi bi-cash-stack cursor-pointer text-3xl text-white hover:text-4xl"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open)
              setMenu('Conhecimento')
            }}
            className="my-1 w-full justify-items-center rounded-lg p-2 hover:bg-purple-600"
          >
            <i className="bi bi-book-half cursor-pointer text-3xl text-white hover:text-4xl"></i>
          </button>
          {acesso == 'Admin' && (
            <button
              onClick={() => {
                setOpen(!open)
                setMenu('Administrar')
              }}
              className="my-1 w-full justify-items-center rounded-lg p-2 hover:bg-purple-600"
            >
              <i className="bi bi-house-gear-fill cursor-pointer text-3xl text-white hover:text-4xl"></i>
            </button>
          )}
        </div>
        <div className="row-end-1 w-full">
          <button className="w-full justify-items-center p-3">
            <i className="bi bi-list cursor-pointer text-3xl text-white"></i>
          </button>
        </div>
      </div>
      <div
        id="MenuEspancao"
        className={`absolute z-10 ml-15 h-screen min-w-max items-center-safe justify-center bg-purple-600 p-4 text-center ${
          open ? 'MenuOpen opacity-100' : 'MenuClose opacity-0'
        }`}
      >
        {open && menu == 'Requisição' && (
          <div className="sidebar-content">
            <h1 className="text-lg font-bold">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <link />

              <li className="flex items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-person-fill-add text-2xl text-white"></i>
                <Link
                  onClick={() => {
                    setOpen(!open)
                  }}
                  href="/Requisicao/Admissao"
                >
                  <h2 className="cursor-pointer text-sm">Solicitar Admissão</h2>
                </Link>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-person-fill-x text-2xl text-white"></i>
                <Link
                  onClick={() => {
                    setOpen(!open)
                  }}
                  href="/Requisicao/Demissao"
                >
                  <h2 className="cursor-pointer text-sm">Solicitar Demissão</h2>
                </Link>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-file-text-fill text-2xl text-white"></i>
                <Link
                  onClick={() => {
                    setOpen(!open)
                  }}
                  href="/Requisicao/Orcamento"
                >
                  <h2 className="text-sm">Orçamento de Colaboradores</h2>
                </Link>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-file-person-fill text-2xl text-white"></i>
                <h2 className="text-sm">Orçamento de Demissão</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == 'DashBoard' && (
          <div className="sidebar-content">
            <h1 className="text-lg font-bold">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Análises Vagas</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Análises Financeiras</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Análises Colaboradores</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == 'Contatos' && (
          <div className="sidebar-content">
            <h1 className="text-lg font-bold">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Recursos Humanos</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Administração</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Faturamento</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Comercial</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Inteligência Empresarial</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == 'Financeiro' && (
          <div className="sidebar-content">
            <h1 className="text-lg font-bold">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Recursos Humanos</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Administração</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Faturamento</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Comercial</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Inteligência Empresarial</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == 'Conhecimento' && (
          <div className="sidebar-content">
            <h1 className="text-lg font-bold">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Recursos Humanos</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Administração</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Faturamento</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Comercial</h2>
              </li>
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm">Inteligência Empresarial</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == 'Administrar' && (
          <div className="sidebar-content">
            <h1 className="text-lg font-bold">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="flex cursor-pointer items-center gap-3 rounded-lg p-1 px-4 hover:bg-purple-700">
                <i className="bi bi-people-fill text-2xl text-white"></i>
                <Link
                  onClick={() => {
                    setOpen(!open)
                  }}
                  href="/Admin/Acessos"
                >
                  <h2 className="cursor-pointer text-sm">Acessos de Usuários</h2>
                </Link>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
