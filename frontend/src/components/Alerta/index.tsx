"use client";

import { ReactNode, useEffect, useState } from "react";

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

  useEffect(() => {
    const AlertaVisivel = localStorage.getItem("AlertaVisivel");
    if (AlertaVisivel == null) {
      localStorage.setItem("AlertaVisivel", "true");
      setVisivel(true);
    } else if (AlertaVisivel === "true") {
      localStorage.setItem("AlertaVisivel", "true");
      setVisivel(true);
    }
  }, [visivel]);

  const fechar = () => {
    setVisivel(false);
    localStorage.setItem("AlertaVisivel", "false");
    return props.setMensagemALerta([]); // Limpa a mensagem do alerta
  };

  return (
    <div
      className="absolute w-screen h-screen bg-black-transparente z-50 flex justify-center items-center top-0 left-0"
      hidden={!visivel} // Mantém o alerta visível ou invisível baseado no estado
    >
      <div
        className={`grid h-auto max-w-4xl min-w-3xl bg-white border-1 border-gray-500 rounded-md text-gray-700 grid-cols-1${
          props.tipo === "Simples" ? " grid-rows-4" : " grid-rows-8"
        }`}
      >
        <div className="relative w-full h-12 flex justify-center items-center p-5 border border-b-1 border-gray-300 rounded-t-md">
          <h1 className="text-2xl font-bold">{props.titulo}</h1>
          {props.tipo === "Simples" && (
            <button
              onClick={fechar} // Chama a função fechar quando o botão for clicado
              className="row-start-1 absolute bi bi-x-square-fill right-2 text-2xl text-gray-500 hover:text-rose-600 cursor-pointer"
            ></button>
          )}
        </div>
        <div
          className={`w-full row-span-6 flex justify-center items-center px-20 py-5`}
        >
          {props.mensagem}
        </div>
        {props.tipo === "Completo" && (
          <div className="row-start-1-1 w-full h-15 flex justify-center items-center p-5 border border-t-1 border-gray-300 rounded-b-md gap-25">
            {props.botoes?.continuar && (
              <button className="flex h-full w-max bg-gray-300 p-5 px-20 justify-center items-center rounded-md hover:bg-green-500 hover:text-white cursor-pointer">
                Continuar
              </button>
            )}

            {props.botoes?.cancelar && (
              <button className="flex h-full w-max bg-gray-300 p-5 px-20 justify-center items-center rounded-md hover:bg-red-500 hover:text-white cursor-pointer">
                Cancelar
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
