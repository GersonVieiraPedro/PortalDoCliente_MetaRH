"use client";

import { useEffect, useState } from "react";

import Link from "next/link";
import { VerificarTipoAcesso } from "@/src/lib/decode";
import { useUsuario } from "@/src/app/contexts/UsuarioContext";

export function MenuLateral() {
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState("");
  const [acesso, setAcesso] = useState("");
  const { usuario, setUsuario } = useUsuario();
  useEffect(() => {
    const token = usuario.token;

    if (token) {
      const vAcesso = VerificarTipoAcesso(token);
      setAcesso(vAcesso || "");
    }
  }, []);

  return (
    <div className="fixed grid grid-cols-2 z-20">
      <div className="h-screen w-15 flex flex-col bg-purple-500 text-gray-700 justify-between items-center grid-rows-3 grid-cols-1 relative z-30">
        <div className="row-span-1">
          <button className="w-full  justify-items-center p-3">
            <Link href="/">
              <img
                src="/LogoMetaRH.png"
                alt=""
                className="w-9 h-9 cursor-pointer"
              />
            </Link>
          </button>
        </div>
        <div className="row-auto gap-2 justify-center justify-items-center items-center px-2">
          <button
            onClick={() => {
              setOpen(!open);
              setMenu("Requisição");
              console.log(menu);
            }}
            id="BtRequisicao"
            className="w-full  justify-items-center hover:bg-purple-600 p-2 my-1 rounded-lg"
          >
            <i className="bi bi-file-earmark-text-fill text-3xl text-white hover:text-4xl cursor-pointer"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open);
              setMenu("DashBoard");
            }}
            className="w-full  justify-items-center hover:bg-purple-600 p-2 my-1 rounded-lg"
          >
            <i className="bi bi-bar-chart-line-fill text-3xl text-white hover:text-4xl cursor-pointer"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open);
              setMenu("Contatos");
            }}
            className="w-full justify-items-center hover:bg-purple-600 p-2  my-1 rounded-lg"
          >
            <i className="bi bi-person-vcard text-3xl text-white hover:text-4xl cursor-pointer"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open);
              setMenu("Financeiro");
            }}
            className="w-full  justify-items-center hover:bg-purple-600 p-2  my-1 rounded-lg"
          >
            <i className="bi bi-cash-stack text-3xl text-white hover:text-4xl cursor-pointer"></i>
          </button>
          <button
            onClick={() => {
              setOpen(!open);
              setMenu("Conhecimento");
            }}
            className="w-full  justify-items-center hover:bg-purple-600 p-2  my-1 rounded-lg"
          >
            <i className="bi bi-book-half text-3xl text-white hover:text-4xl cursor-pointer"></i>
          </button>
          {acesso == "Admin" && (
            <button
              onClick={() => {
                setOpen(!open);
                setMenu("Administrar");
              }}
              className="w-full  justify-items-center hover:bg-purple-600 p-2  my-1 rounded-lg"
            >
              <i className="bi bi-house-gear-fill text-3xl text-white hover:text-4xl cursor-pointer"></i>
            </button>
          )}
        </div>
        <div className="row-end-1  w-full">
          <button className="w-full  justify-items-center p-3">
            <i className="bi bi-list text-3xl text-white cursor-pointer"></i>
          </button>
        </div>
      </div>
      <div
        id="MenuEspancao"
        className={`bg-purple-600 h-screen p-4 justify-center items-center-safe text-center absolute ml-15 min-w-max z-10 ${
          open ? "MenuOpen opacity-100" : "MenuClose opacity-0 "
        }`}
      >
        {open && menu == "Requisição" && (
          <div className="sidebar-content">
            <h1 className="font-bold text-lg">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <link />

              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 ">
                <i className="bi bi-person-fill-add text-2xl text-white"></i>
                <Link
                  onClick={() => {
                    setOpen(!open);
                  }}
                  href="/Requisicao/Admissao"
                >
                  <h2 className="text-sm cursor-pointer">Solicitar Admissão</h2>
                </Link>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-person-fill-x text-2xl text-white"></i>
                <h2 className="text-sm ">Solicitar Demissão</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-file-text-fill text-2xl text-white"></i>
                <h2 className="text-sm ">Orçamento de Colaboradores</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-file-person-fill text-2xl text-white"></i>
                <h2 className="text-sm ">Orçamento de Demissão</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == "DashBoard" && (
          <div className="sidebar-content">
            <h1 className="font-bold text-lg">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Analise Vagas</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Análise Fincanceira</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Análises Colaboradores</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == "Contatos" && (
          <div className="sidebar-content">
            <h1 className="font-bold text-lg">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Recursos Humanos</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Administração</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Faturamento</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Comercial</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Inteligência Empresarial</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == "Financeiro" && (
          <div className="sidebar-content">
            <h1 className="font-bold text-lg">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Recursos Humanos</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Administração</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Faturamento</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Comercial</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Inteligência Empresarial</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == "Conhecimento" && (
          <div className="sidebar-content">
            <h1 className="font-bold text-lg">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Recursos Humanos</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Administração</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Faturamento</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Comercial</h2>
              </li>
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-graph-up-arrow text-2xl text-white"></i>
                <h2 className="text-sm ">Inteligência Empresarial</h2>
              </li>
            </ul>
          </div>
        )}
        {open && menu == "Administrar" && (
          <div className="sidebar-content">
            <h1 className="font-bold text-lg">{menu}</h1>
            <hr className="my-4 text-purple-300" />
            <ul className="grid gap-4">
              <li className="hover:bg-purple-700 rounded-lg p-1 px-4 flex items-center gap-3 cursor-pointer">
                <i className="bi bi-people-fill text-2xl text-white"></i>
                <Link
                  onClick={() => {
                    setOpen(!open);
                  }}
                  href="/Admin/Acessos"
                >
                  <h2 className="text-sm cursor-pointer">
                    Acessos de Usuários
                  </h2>
                </Link>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
