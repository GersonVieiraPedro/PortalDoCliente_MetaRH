"use client";

import { useEffect, useState } from "react";
import image from "next/image";
import Link from "next/link";
import { VerificarTipoAcesso } from "@/src/lib/decode";

type ModalProps = {
  titulo: string;
  mensagem: string;
  botoes: {
    cancelar: null | "Sim";
    continuar: null | "Sim";
  } | null;
  tipo: "Sucesso" | "Erro" | "Informacao" | null;
};

export function Modal(props: ModalProps) {
  return (
    <div className="absolute w-screen h-screen bg-black-transparente z-50 flex justify-center items-center">
      <div className="grid h-auto min-h-1/2 w-auto min-w-3xl bg-white border-1 border-gray-500 rounded-md text-gray-700 grid-cols-1 grid-rows-8">
        <div className="w-full h-12 flex justify-center items-center p-5 border border-b-1 border-gray-300 rounded-t-md">
          <h1 className="text-2xl font-bold ">{props.titulo}</h1>
        </div>
        <div className="w-full h-full row-span-6 flex justify-center items-center p-5"></div>
        <div className="w-full h-15 flex justify-center items-center p-5 border border-t-1 border-gray-300 rounded-b-md gap-25">
          <button className="flex h-full w-max bg-gray-300 p-5 px-20 justify-center items-center rounded-md hover:bg-green-500  hover:text-white cursor-pointer">
            Continuar
          </button>
          <button className="flex h-full w-max bg-gray-300 p-5 px-20 justify-center items-center rounded-md hover:bg-red-500  hover:text-white cursor-pointer">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
