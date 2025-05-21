"use client";

import Form from "next/form";
import Link from "next/link";
import { useActionState, useCallback, useEffect, useState } from "react";
import login from "./login";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { setAuthToken } from "@/src/lib/cockies";

export default function FormLogin() {
  const [state, formAction, isPending] = useActionState(login, null);
  const router = useRouter();
  const [visivel, setVisivel] = useState(false);

  useEffect(() => {
    if (state?.status === "Sucesso" && state.token) {
      setAuthToken(state.token);
      router.push("/");
    }
  }, [state, router]);

  return (
    <Form action={formAction}>
      <div className="grid w-sm h-full gap-5 -top-10 ">
        <div>
          <h4 className="text-sm pl-1">E-mail</h4>
          <input
            autoFocus
            name="email"
            className="w-full h-8 border border-gray-400 rounded-md p-3"
            type="text"
            placeholder="Digite seu e-mail"
          />
        </div>
        <div className="relative">
          <h4 className="text-sm pl-1">Senha</h4>
          <input
            name="senha"
            className="w-full h-8 border border-gray-400 rounded-md p-3"
            type={!visivel ? "password" : "text"}
            placeholder="Digite sua senha"
          />
          <div
            onClick={() => {
              setVisivel(!visivel);
            }}
            className={`grid bi  absolute h-6 w-6 items-center right-1 top-6 hover:bg-purple-200 cursor-pointer rounded-full pl-1 ${
              visivel ? "bi-eye" : "bi-eye-slash"
            }`}
          ></div>
        </div>
        <h1 className="text-sm text-center cursor-pointer hover:text-purple-700">
          Esqueci a Senha ?
        </h1>
        <button className="bg-purple-500 text-2xl text-white rounded-md p-1 mt-10 cursor-pointer hover:bg-purple-600 ">
          Entrar
        </button>
        <Link href={"/Registrar"}>
          <h1 className="text-sm text-center cursor-pointer hover:text-purple-700">
            Não possuo cadastro !
          </h1>
        </Link>
      </div>
    </Form>
  );
}
