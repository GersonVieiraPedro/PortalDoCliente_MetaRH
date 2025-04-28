"use client";

import { usePathname } from "next/navigation";
import { useRef, useState } from "react";

export function Navegador() {
  const [openNotif, setOpenNofif] = useState(false);

  const nomeDiretorio = usePathname();

  const TipoFiltroRef = useRef<HTMLSelectElement>(null);
  const ValorFiltradoRef = useRef<HTMLInputElement>(null);

  const titulo = () => {
    switch (nomeDiretorio) {
      case "/":
        return "Bem Vindo !";
      case "/Requisicao/Admissao":
        return "Requisição";
      case "/Admin/Acessos":
        return "Administração de Acessos";
      default:
        return "";
    }
  };

  return (
    <nav className="bg-gray-100 w-screen h-15 fixed flex text-gray-600 z-1">
      <div className=" w-lvw h-full ml-15 grid grid-cols-3 justify-between content-center shadow-md ">
        <div className="h-full w-full flex items-center text-3xl font-bold pl-2 gap-2">
          <i className="bi bi-caret-right text-2xl"></i>
          <h2>{titulo()}</h2>
        </div>
        <div className="h-full w-full ">
          <div className="flex rounded-md border border-gray-100 w-full items-center">
            <input
              className=" h-10 border border-gray-200 bg-white w-full p-2 outline-gray-300"
              type="text"
              name=""
              id="ValorFiltro"
              placeholder="Pesquisar"
              ref={ValorFiltradoRef}
            />

            <button
              onClick={() => {
                const Tipo = TipoFiltroRef.current?.value || "";
                const Valor = ValorFiltradoRef.current?.value || "";
              }}
              className="bi bi-search h-10 w-15 bg-gray-200 cursor-pointer hover:bg-gray-300"
            ></button>
          </div>
        </div>
        <div className="h-full w-full justify-end pr-10 flex items-center gap-4 relative">
          {openNotif && (
            <div
              className={`absolute px-5 py-2 rounded-md left-30 top-13 bg-gray-50 w-80 h-50 overflow-y-auto shadow-md ${
                openNotif
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 translate-y-10"
              } `}
            >
              <div className="sticky top-0 h-auto w-full text-2xl font-medium border-b border-gray-300 p-2 mb-2 flex justify-between bg-gray-50">
                <h2>Notificações</h2>
                <button className="rounded-full hover:bg-gray-300 cursor-pointer px-1 relative group inline-block">
                  <i className="bi bi-check2-circle  "></i>
                  <div className="absolute right-full mr-2 top-1/2 -translate-y-1/2 hidden group-hover:block bg-gray-500 text-white text-xs rounded py-1 px-2 z-50 whitespace-nowrap">
                    Marcar todos como lido !
                  </div>
                </button>
              </div>

              <ul className="gap-2 grid pl-2">
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
              setOpenNofif(!openNotif);
            }}
            className="h-full w-10 rounded-md border-0 hover:bg-gray-300 cursor-pointer relative"
          >
            <samp className="absolute -top-0 -right-0 bg-red-600 text-white font-bold px-1.5 py-0.5 rounded-full Font-micro">
              2
            </samp>
            <i className="bi bi-bell-fill"></i>
          </button>

          <div className="border-l pl-5 flex items-center gap-4 ">
            <h5 className="">Gerson V.</h5>
            <img
              className="object-contain h-10 w-10 rounded-full"
              src="/Foto.png"
              alt=""
            />
          </div>
        </div>
      </div>
    </nav>
  );
}
