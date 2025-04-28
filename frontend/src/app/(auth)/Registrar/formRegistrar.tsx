"use client";

import Form from "next/form";
import Link from "next/link";
import resgistrarUsuario from "./registrarUsuario";
import {
  useActionState,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import IMask from "imask";

export default function FormRegistrar() {
  const [state, formAction, isPending] = useActionState(
    resgistrarUsuario,
    null
  );
  const [visivel, setVisivel] = useState(false);
  const [alerta, setAlerta] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (inputRef.current) {
      IMask(inputRef.current, {
        mask: "00.000.000/0000-00",
      });
    }
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setAlerta(false);
    }, 5000);

    return () => clearTimeout(timeout);
  }, [alerta]);

  useEffect(() => {
    setAlerta(true);
  }, [state]);

  return (
    <Form action={formAction}>
      <div className="grid w-sm h-full gap-5 -top-10 pt-15">
        {alerta == true && state && (
          <div
            className={`absolute top-10 h-max w-sm border p-3 ${
              state.status === "Erro"
                ? "bg-red-300 border-red-700 text-red-800"
                : "bg-green-300 border-green-700 text-green-800"
            }`}
          >
            <h1 className="font-bold mb-1">{state.status}</h1>
            <p className="text-sm font-medium mb-1">{state.mensagem}</p>
          </div>
        )}
        <div>
          <h4 className="text-sm pl-1">Nome</h4>
          <input
            autoFocus
            name="nome"
            className="w-full h-8 border border-gray-400 rounded-md p-3"
            type="text"
            placeholder="Digite seu nome"
          />
        </div>
        <div>
          <h4 className="text-sm pl-1">E-mail</h4>
          <input
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
        <div>
          <h4 className="text-sm pl-1">CNPJ</h4>
          <input
            name="cnpj"
            className="w-full h-8 border border-gray-400 rounded-md p-3"
            type="text"
            ref={inputRef}
            placeholder="00.000.000/0000-00"
          />
        </div>
        <button className="bg-purple-500 text-2xl text-white rounded-md p-1 mt-10 cursor-pointer hover:bg-purple-600 ">
          Entrar
        </button>
        <Link href={"/Login"}>
          <h1 className="text-sm text-center cursor-pointer hover:text-purple-700">
            Já tenho cadastro !
          </h1>
        </Link>
      </div>
    </Form>
  );
}
