"use client";

import {
  ConsultarUsuario,
  ExisteImagem,
} from "@/src/components/Navegador/imagemUsuario";
import { VerificarEmail, VerificarNome } from "@/src/lib/decode";
import { getToken } from "@/src/lib/token";
import { createContext, useContext, useState, useEffect } from "react";

export const UsuarioContext = createContext<any>(null);

import { PropsWithChildren } from "react";

export function UseProvider({ children }: PropsWithChildren<{}>) {
  const [usuario, setUsuario] = useState<any>(null);
  const [token, setToken] = useState<string>("");
  const [nomeUsuario, setNomeUsuario] = useState<string>("");
  const [emailUsuario, setEmailUsuario] = useState<string>("");
  const [existeImagem, setExisteImagem] = useState<any>(null);

  useEffect(() => {
    const token = getToken();

    setToken(token);
  }, []);

  useEffect(() => {
    if (token) {
      const Nome = VerificarNome(token);
      const Email = VerificarEmail(token);
      setNomeUsuario(Nome || "");
      setEmailUsuario(Email || "");
    }
  }, [token]);

  useEffect(() => {
    if (emailUsuario !== "" && nomeUsuario !== "") {
      const fetchUsuario = async () => {
        const user = await ConsultarUsuario(token, emailUsuario);
        setUsuario(user); // agora sim, o objeto real
      };

      fetchUsuario();
    }
  }, [nomeUsuario, emailUsuario]);

  useEffect(() => {
    console.log("Usuaurio : ", usuario);
    if (usuario?.ID) {
      const existes = async () => {
        const e = await ExisteImagem(usuario?.ID);
        setExisteImagem(e);
      };
      existes();
    }
  }, [usuario]);

  useEffect(() => {
    setUsuario({
      ...usuario,
      existe: existeImagem,
      urlImagem: `https://storagecorpprod001.blob.core.windows.net/portal-web/fotos/usuarios/${usuario?.ID}.png`,
      token: token,
    });
  }, [existeImagem]);

  return (
    <UsuarioContext.Provider value={{ usuario, setUsuario }}>
      {children}
    </UsuarioContext.Provider>
  );
}

export const useUsuario = () => useContext(UsuarioContext);
