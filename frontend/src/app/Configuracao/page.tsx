"use client";
import { MenuLateral } from "@/src/components/MenuLateral";
import { Navegador } from "@/src/components/Navegador";

import { useRef, useState } from "react";

export default function TelaConfiguracao() {
  const [nome, setNome] = useState("Thais Teste Cliente");
  const [email, setEmail] = useState("gerson123vieira@gmail.com");
  const [editandoNome, setEditandoNome] = useState(false);
  const [editandoEmail, setEditandoEmail] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImagemClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div>
      <MenuLateral />
      <Navegador />
      <div className="bg-gray-100 w-screen h-screen flex justify-center items-start py-10 text-gray-800">
        <div className="grid grid-cols-3 h-auto w-full max-w-5xl bg-white border border-gray-200 rounded-md p-10 shadow-md">
          <div className="col-span-1 flex flex-col items-center gap-4">
            <img
              className="object-cover h-32 w-32 rounded-full border"
              src="/UsuarioAvatar.jpg"
              alt="Foto do usuário"
            />
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              accept="image/*"
              onChange={(e) => {
                // Aqui você pode tratar o upload
                console.log(e.target.files);
              }}
            />
            <button
              className="bg-gray-200 text-sm px-4 py-1 rounded hover:bg-gray-300 transition"
              type="button"
              onClick={handleImagemClick}
            >
              Alterar Imagem
            </button>
          </div>

          <div className="col-span-2 flex flex-col justify-center gap-6 pl-10">
            <div className="flex items-center gap-4">
              {editandoNome ? (
                <>
                  <input
                    type="text"
                    value={nome}
                    onChange={(e) => setNome(e.target.value)}
                    className="border rounded px-3 py-1 w-full max-w-md"
                  />
                  <button
                    className="text-sm text-blue-600 hover:underline"
                    onClick={() => setEditandoNome(false)}
                  >
                    Salvar
                  </button>
                </>
              ) : (
                <>
                  <h1 className="text-lg font-semibold">{nome}</h1>
                  <button
                    className="bi bi-pencil-fill w-8 h-8 bg-gray-100 flex justify-center items-center rounded hover:bg-gray-200"
                    onClick={() => setEditandoNome(true)}
                  />
                </>
              )}
            </div>

            <div className="flex items-center gap-4">
              {editandoEmail ? (
                <>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="border rounded px-3 py-1 w-full max-w-md"
                  />
                  <button
                    className="text-sm text-blue-600 hover:underline"
                    onClick={() => setEditandoEmail(false)}
                  >
                    Salvar
                  </button>
                </>
              ) : (
                <>
                  <h1 className="text-md">{email}</h1>
                  <button
                    className="bi bi-pencil-fill w-8 h-8 bg-gray-100 flex justify-center items-center rounded hover:bg-gray-200"
                    onClick={() => setEditandoEmail(true)}
                  />
                </>
              )}
            </div>

            {/* Aqui você pode adicionar permissões depois */}
          </div>
        </div>
      </div>
    </div>
  );
}
