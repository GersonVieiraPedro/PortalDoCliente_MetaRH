"use client";
import { MenuLateral } from "@/src/components/MenuLateral";
import { Navegador } from "@/src/components/Navegador";
import { useUsuario } from "@/src/app/contexts/UsuarioContext";
import { useEffect, useRef, useState } from "react";
import { AtualizarUsuario } from "./atualizar";

export default function TelaConfiguracao() {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const nomeInput = useRef<HTMLInputElement | null>(null);
  const senhaNovaInput = useRef<HTMLInputElement | null>(null);
  const senhaAntigaInput = useRef<HTMLInputElement | null>(null);
  const { usuario, setUsuario } = useUsuario();
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [mensagem, setMensagem] = useState<string>("");
  // Lida com a seleção do arquivo no input hidden
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadMessage(`Arquivo selecionado: ${e.target.files[0].name}`);
    } else {
      setFile(null);
      setUploadMessage("Nenhum arquivo selecionado.");
    }
  };

  // Dispara o clique no input de arquivo quando o botão "Alterar Imagem" é clicado
  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  // Lida com o envio do arquivo para a API
  const handleUpload = async () => {
    if (!file) {
      setUploadMessage("Por favor, selecione um arquivo primeiro.");
      return;
    }

    if (!usuario?.Email) {
      setUploadMessage("Erro: Email do usuário não encontrado.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const url = `http://127.0.0.1:8000/imagens/usuario?email=${encodeURIComponent(
      usuario.Email
    )}`;

    try {
      setUploadMessage("Enviando...");
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        // Se a resposta não for 2xx, tenta ler o erro da API
        const errorData = await response.json();
        throw new Error(
          errorData.detail ||
            `Erro no servidor: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();
      setUploadMessage(`Imagem salva com sucesso!`);
      console.log("Resposta da API:", data);

      setUsuario({
        ...usuario,
        urlImagem: `https://storagecorpprod001.blob.core.windows.net/portal-web/fotos/usuarios/${
          usuario.ID
        }.png?t=${new Date().getTime()}`,
      });
    } catch (error: any) {
      setUploadMessage(`Erro ao enviar imagem: ${error.message}`);
      console.error("Erro ao enviar imagem:", error);
    } finally {
      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };
  const Atualizar = async () => {
    const nome = nomeInput.current?.value ?? null;
    const senhaAntiga = senhaAntigaInput.current?.value ?? null;
    const senhaNova = senhaNovaInput.current?.value ?? null;

    // Limpa a mensagem anterior ao tentar uma nova atualização
    setMensagem("");

    try {
      // Verifica se pelo menos um campo foi preenchido para iniciar a atualização
      // É importante enviar apenas o que for realmente alterado, ou todos os campos se sua API espera isso.
      if (nome !== null || senhaAntiga !== null || senhaNova !== null) {
        // Prepara os dados para enviar à API.
        // Inclua apenas os campos que você quer enviar, ou que são requeridos pela API.
        const dadosAtualizacao: any = {};
        if (nome !== null) dadosAtualizacao.nome = nome;
        if (senhaAntiga !== null) dadosAtualizacao.SenhaAntiga = senhaAntiga;
        if (senhaNova !== null) dadosAtualizacao.SenhaNova = senhaNova;

        // Você pode querer adicionar validações aqui no frontend antes de enviar:
        if (senhaAntiga && !senhaNova) {
          // Se preencheu a antiga mas não a nova
          setMensagem(
            "Por favor, preencha a 'Senha Nova' para alterar a senha."
          );
          return;
        }
        if (!senhaAntiga && senhaNova) {
          // Se preencheu a nova mas não a antiga
          setMensagem(
            "Por favor, preencha a 'Senha Atual' para alterar a senha."
          );
          return;
        }
        if (senhaAntiga && senhaNova && senhaAntiga === senhaNova) {
          // Senhas iguais
          setMensagem("A nova senha não pode ser igual à senha atual.");
          return;
        }
        // Adicione aqui outras validações, como complexidade da senha, etc.

        const resposta = await AtualizarUsuario(
          usuario?.token ?? "",
          usuario?.ID ?? "",
          nome,
          senhaAntiga,
          senhaNova
        );

        console.log("Resposta completa da API:", resposta); // Mantenha para depuração

        if (!resposta.detail) {
          setMensagem("Atualização Feita com Sucesso");
          setUsuario({ ...usuario, Nome: nome });
        } else {
          setMensagem(`Erro ao atualizar :  ${resposta.detail.mensagem}`);
        }
      }
    } catch (error: any) {
      setUploadMessage(`Erro ao atualizar: ${error.message}`);
      console.error("Erro ao atualizar:", error);
    } finally {
      if (senhaAntigaInput.current) {
        senhaAntigaInput.current.value = "";
      }
      if (senhaNovaInput.current) {
        senhaNovaInput.current.value = "";
      }
    }
  };

  useEffect(() => {
    console.log("use :", usuario);
  }, [usuario]); // Dependência em 'usuario'

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setMensagem("");
    }, 5000);

    return () => clearTimeout(timeoutId);
  }, [mensagem]);

  return (
    <div>
      <MenuLateral />
      <Navegador />
      <div className="bg-gray-100 w-screen h-screen flex justify-center items-start py-10 text-gray-800">
        <div className="grid grid-cols-3 h-auto w-full max-w-[90vw] ml-15 bg-white border border-gray-200 rounded-md p-10 shadow-md">
          <div className="col-span-1 flex flex-col items-center gap-4">
            <img
              className="object-cover h-32 w-32 rounded-full border border-gray-300"
              src={usuario?.existe ? usuario?.urlImagem : "/UsuarioAvatar.jpg"}
              alt="Foto do usuário"
            />
            <input
              type="file"
              ref={fileInputRef}
              className="hidden" // Escondido para ser acionado pelo botão personalizado
              accept="image/*"
              onChange={handleFileChange}
            />
            <button
              className="bg-gray-200 text-sm px-4 py-1 rounded hover:bg-gray-300 transition cursor-pointer"
              type="button"
              onClick={handleButtonClick} // Ação de clicar no botão
            >
              Alterar Imagem
            </button>
            {file && ( // Mostra um botão de upload real apenas se um arquivo for selecionado
              <button
                className="bg-purple-500 text-white text-sm px-4 py-1 rounded hover:bg-purple-600 transition cursor-pointer mt-2"
                type="button"
                onClick={handleUpload}
                disabled={!file} // Desabilita se não houver arquivo
              >
                Confirmar Upload
              </button>
            )}
            {uploadMessage && <p className="text-sm mt-2">{uploadMessage}</p>}{" "}
          </div>

          <div className="grid-cols-1 flex flex-col justify-center gap-6 pl-10 px-10 border-l border-gray-200">
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium text-sm">Nome</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="NomeUsuario"
                defaultValue={usuario?.Nome}
                ref={nomeInput}
                id="1"
                required
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium text-sm">
                E-mail
              </label>
              <input
                type="text"
                className="p-1 border border-gray-200 bg-gray-100 inset-shadow-sm rounded-md cursor-not-allowed"
                name="EmailUsuario"
                defaultValue={usuario?.Email} // Usando defaultValue
                id="2"
                disabled
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium text-sm">
                Senha Atual
              </label>
              <input
                type="password" // Use type="password" para campos de senha
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="SenhaAtualUsuario"
                ref={senhaAntigaInput}
                id="3"
                required
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium text-sm">
                Senha Nova
              </label>
              <input
                type="password" // Use type="password" para campos de senha
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="SenhaNovaUsuario"
                ref={senhaNovaInput}
                id="4"
                required
              />
            </div>
            <button
              id="SalvarAlteracao"
              onClick={Atualizar}
              className="bg-gray-200 h-8 text-sm px-4 py-1 rounded hover:bg-gray-300 transition cursor-pointer"
            >
              Salvar
            </button>
          </div>
          <div
            className={`grid-cols-1 flex flex-col items-center gap-6 pl-10 px-5 border-l border-gray-200 ${
              mensagem ? "justify-between" : "justify-end"
            }`}
          >
            {mensagem && (
              <div
                className={`p-5 w-full h-[10vh] text-center text-white font-medium ${
                  mensagem == "Atualização Feita com Sucesso"
                    ? " bg-green-400 border border-green-500"
                    : " bg-red-400 border border-red-500"
                }`}
              >
                <h1>{mensagem}</h1>
              </div>
            )}
            <button
              id="SairAplicacao"
              className="bg-red-300 h-8 text-sm px-10 py-1 rounded hover:bg-red-400 transition cursor-pointer"
            >
              Sair da Aplicação
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
