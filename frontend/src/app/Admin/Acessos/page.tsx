"use server";

import { redirect } from "next/navigation";
import { TabelaUsuariosAcessos } from "@/src/components/TabelaUsuariosAcessos";
import { Alerta } from "@/src/components/Alerta";
import { cookies } from "next/headers";

interface Usuario {
  ID: number;
  Nome: string;
  Email: string;
  CNPJ: string;
  TipoAcesso: string;
  PipedriveID: string;
  CodigoCliente: string;
  Status: boolean;
  DataCadastro: string;
  DataAtualizacao: string;
}

export default async function Acessos() {
  const cookieStore = await cookies();

  const token = cookieStore.get("token");

  return (
    <>
      <div className="bg-gray-200 max-w-dvw h-screen pt-20 pl-20 p-5 ">
        <TabelaUsuariosAcessos />
      </div>
    </>
  );
}
