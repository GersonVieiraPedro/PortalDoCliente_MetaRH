"use client";

import { ReactNode, useEffect, useRef, useState } from "react";

type AlertaProps = {
  titulo: string;
  mensagem: ReactNode;
  tipo: "Simples" | "Completo";
  botoes: {
    cancelar: null | "Sim";
    continuar: null | "Sim";
  } | null;
  visivel: boolean;
  setMensagemALerta: (mensagem: Array<any>) => void;
};

export function Alerta(props: AlertaProps) {
  const [visivel, setVisivel] = useState(props.visivel);
  const alertaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const AlertaVisivel = localStorage.getItem("AlertaVisivel");
    if (AlertaVisivel == null || AlertaVisivel === "true") {
      localStorage.setItem("AlertaVisivel", "true");
      setVisivel(true);
    }
  }, []);

  useEffect(() => {
    if (visivel) {
      document.body.style.overflow = "hidden";
      if (alertaRef.current) alertaRef.current.focus();
    } else {
      document.body.style.overflow = "auto";
    }

    return () => {
      document.body.style.overflow = "auto";
    };
  }, [visivel]);

  const fechar = () => {
    setVisivel(false);
    localStorage.setItem("AlertaVisivel", "false");
    props.setMensagemALerta([]);
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black-transparente bg-opacity-50 flex justify-center items-center"
      hidden={!visivel}
    >
      <div
        ref={alertaRef}
        tabIndex={-1}
        className={`w-full max-w-2xl min-w-[300px] max-h-screen bg-white border border-gray-500 rounded-md text-gray-700 overflow-auto shadow-lg 
          ${props.tipo === "Simples" ? "grid grid-rows-4" : "grid grid-rows-8"} 
        `}
      >
        <div className="relative w-full h-12 flex justify-center items-center p-5 border-b border-gray-300 rounded-t-md">
          <h1 className="text-2xl font-bold">{props.titulo}</h1>
          {props.tipo === "Simples" && (
            <button
              onClick={fechar}
              className="absolute right-2 text-2xl text-gray-500 hover:text-rose-600 cursor-pointer bi bi-x-square-fill"
            ></button>
          )}
        </div>

        <div className="w-full row-span-6 flex justify-center items-center px-6 py-4">
          {props.mensagem}
        </div>

        {props.tipo === "Completo" && (
          <div className="w-full flex justify-center items-center p-5 border-t border-gray-300 rounded-b-md gap-6">
            {props.botoes?.continuar && (
              <button className="h-full bg-gray-300 py-2 px-6 rounded-md hover:bg-green-500 hover:text-white cursor-pointer">
                Continuar
              </button>
            )}
            {props.botoes?.cancelar && (
              <button className="h-full bg-gray-300 py-2 px-6 rounded-md hover:bg-red-500 hover:text-white cursor-pointer">
                Cancelar
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
