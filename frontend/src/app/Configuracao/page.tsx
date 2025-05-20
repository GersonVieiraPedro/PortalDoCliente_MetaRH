"use client";
import { MenuLateral } from "@/src/components/MenuLateral";
import { Navegador } from "@/src/components/Navegador";
import { VerificarEmail, VerificarNome } from "@/src/lib/decode"; // Verifique se estas importações são realmente usadas, caso contrário, remova-as.
import { getToken } from "@/src/lib/token"; // Verifique se esta importação é realmente usada, caso contrário, remova-a.
import { useUsuario } from "@/src/app/contexts/UsuarioContext";
import { useEffect, useRef, useState } from "react";

export default function TelaConfiguracao() {
  // Estado não usado para nome e email, pois está usando defaultValue do usuario?.
  // Removi os `useState` para `nome` e `email` para evitar confusão,
  // mas se você planeja editá-los e salvar, eles devem ser reintroduzidos com `onChange` nos inputs.
  // const [nome, setNome] = useState("");
  // const [email, setEmail] = useState("");
  const [file, setFile] = useState<File | null>(null);
  //const [urlImagem, setUrlImagem] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { usuario, setUsuario } = useUsuario();
  const [uploadMessage, setUploadMessage] = useState<string>(""); // Para exibir mensagens de sucesso/erro no upload

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
    formData.append("file", file); // 'file' é o nome do campo que a API espera

    // URL corrigida: `http://127.0.0.1:8000/imagens/usuario?email=${usuario.Email}`
    // O `encodeURIComponent` é crucial para garantir que o email na URL seja tratado corretamente.
    const url = `http://127.0.0.1:8000/imagens/usuario?email=${encodeURIComponent(
      usuario.Email
    )}`;

    try {
      setUploadMessage("Enviando...");
      const response = await fetch(url, {
        method: "POST",
        body: formData,
        // NÃO defina 'Content-Type': 'multipart/form-data' aqui.
        // O navegador faz isso automaticamente com FormData e adiciona o 'boundary' correto.
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
      setUploadMessage(`Imagem salva com sucesso! ${data.mensagem || ""}`); // Assumindo que a API retorna 'mensagem'
      console.log("Resposta da API:", data);

      // Opcional: Recarregar a imagem do usuário para mostrar a nova foto
      // Você pode querer forçar um refresh na imagem aqui, talvez alterando um estado
      // ou atualizando o contexto do usuário se ele contiver a URL da imagem.
      // Por exemplo, se `usuario` tiver uma propriedade `fotoUrl` que você atualiza:]

      setUsuario({
        ...usuario,
        urlImagem: `https://storagecorpprod001.blob.core.windows.net/portal-web/fotos/usuarios/${
          usuario.ID
        }.png?t=${new Date().getTime()}`,
      });
    } catch (error: any) {
      // Use 'any' para pegar a mensagem de erro
      setUploadMessage(`Erro ao enviar imagem: ${error.message}`);
      console.error("Erro ao enviar imagem:", error);
    } finally {
      // Limpa o arquivo selecionado no estado após o upload (sucesso ou falha)
      setFile(null);
      // Limpa o input de arquivo (se necessário, para permitir novo upload do mesmo arquivo)
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // Este useEffect para o token e email não é mais necessário para a funcionalidade de upload,
  // pois o email é pego diretamente de `usuario?.Email`.
  // Mantenha apenas se for usado para outras funcionalidades de configuração de usuário.
  // useEffect(() => {
  //   const currentToken = getToken();
  //   if (currentToken) {
  //     setToken(currentToken);
  //     // console.log("Token:", currentToken);
  //     // console.log("Email:", VerificarEmail(currentToken));
  //     // console.log("Nome:", VerificarNome(currentToken));
  //   }
  // }, []);

  useEffect(() => {
    // console.log("usuario ;", usuario); // Apenas para depuração
    // Este useEffect pode ser usado para setar os valores iniciais dos inputs de nome e email,
    // se você reintroduzir os `useState` para eles.
    console.log("use :", usuario);
  }, [usuario]); // Dependência em 'usuario'

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
            {/* O botão "Alterar Imagem" agora apenas aciona o input de arquivo */}
            <button
              className="bg-gray-200 text-sm px-4 py-1 rounded hover:bg-gray-300 transition cursor-pointer"
              type="button"
              onClick={handleButtonClick} // Ação de clicar no botão
            >
              Alterar Imagem
            </button>
            {file && ( // Mostra um botão de upload real apenas se um arquivo for selecionado
              <button
                className="bg-blue-500 text-white text-sm px-4 py-1 rounded hover:bg-blue-600 transition cursor-pointer mt-2"
                type="button"
                onClick={handleUpload}
                disabled={!file} // Desabilita se não houver arquivo
              >
                Confirmar Upload
              </button>
            )}
            {uploadMessage && <p className="text-sm mt-2">{uploadMessage}</p>}{" "}
            {/* Exibe a mensagem de upload */}
          </div>

          <div className="grid-cols-1 flex flex-col justify-center gap-6 pl-10 ">
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium text-sm">Nome</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="NomeUsuario"
                defaultValue={usuario?.Nome} // Usando defaultValue
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
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="EmailUsuario"
                defaultValue={usuario?.Email} // Usando defaultValue
                id="2"
                required
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
                id="4"
                required
              />
            </div>
            <button className="bg-gray-200 h-8 text-sm px-4 py-1 rounded hover:bg-gray-300 transition cursor-pointer">
              Salvar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
