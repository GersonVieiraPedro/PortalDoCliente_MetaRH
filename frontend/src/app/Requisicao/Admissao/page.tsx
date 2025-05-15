"use client";

import { useActionState, useEffect, useRef, useState } from "react";
import { MinhasEmpresas, MeusFuncionarios } from "./MeusDados";
import { VerificarEmail } from "@/src/lib/decode";
import { getToken } from "@/src/lib/token";
import Select from "react-select";
import { NumericFormat } from "react-number-format";
import IMask from "imask";
import { motion, AnimatePresence } from "framer-motion";
import Form from "next/form";
import RegistrarAdmissao from "./registrarAdmissao";

export default function Admissao() {
  const [dados, setDados] = useState<any>(null);
  const [funcionarios, setFuncionarios] = useState<any>(null);
  const [email, setEmail] = useState<string | null>("");
  const [token, setToken] = useState<string>("");
  const [funcaos, setFuncaos] = useState<any>(null);
  const [funcaoSelecionada, setFuncaoSelecionada] = useState<string>("");
  const [centrosCustos, setCentrosCustos] = useState<any>("");
  const [centroSelecionado, setCentroSelecionado] = useState<string>("");
  const [motivoSelecionado, setMotivoSelecionado] = useState<string>("");
  const [prescisaEPI, setPrecisaEPI] = useState(false);

  const inputCPF = useRef<HTMLInputElement>(null);
  const inputTelefoneRHResponsavel = useRef<HTMLInputElement>(null);
  const inputGestorPonto = useRef<HTMLInputElement>(null);
  const inputHorario = useRef<HTMLInputElement>(null);

  const [state, formAction, isPending] = useActionState(
    RegistrarAdmissao,
    null
  );

  useEffect(() => {
    const CarregarDados = async () => {
      const varToken = await getToken();
      setToken(varToken);

      const varEmail = await VerificarEmail(varToken);
      setEmail(varEmail);

      const varDados = await MinhasEmpresas(varEmail);
      setDados(varDados);

      /*  Consoles de Validação 
      console.log('token: ', varToken)
      console.log('email: ', varEmail)
      console.log('Dados: ', varDados)
      */
    };

    //Mascara de Entrada Telefone
    if (inputGestorPonto.current) {
      IMask(inputGestorPonto.current, {
        mask: "(00) 00000-0000",
      });
    }

    //Mascara de Entrada Telefone
    if (inputTelefoneRHResponsavel.current) {
      IMask(inputTelefoneRHResponsavel.current, {
        mask: "(00) 00000-0000",
      });
    }

    //Mascara de Entrada Horario
    if (inputHorario.current) {
      IMask(inputHorario.current, {
        mask: "00:00:00",
      });
    }

    CarregarDados();
  }, []);

  useEffect(() => {
    //Transofrmando os objetos em lista distantas de CNPJ e CodigoCliente
    const CNPJS = [...new Set(dados?.map((d: { CNPJ: any }) => d.CNPJ))];
    const CodigoCliente = [
      ...new Set(
        dados?.map((d: { ["COD Contrato G.I"]: any }) => d["COD Contrato G.I"])
      ),
    ];

    /* Consoles Testes
    console.log('CNPJS :', CNPJS)
    console.log('Cod :', CodigoCliente)
    */
    //Função assincrona que chama a consulta do backend
    const Funcionarios = async () => {
      if (CNPJS.length + CodigoCliente.length > 0) {
        const varFuncionarios = await MeusFuncionarios(CNPJS, CodigoCliente);
        setFuncionarios(varFuncionarios);
        //console.log(varFuncionarios)
      }
    };

    if (dados?.length > 0) {
      Funcionarios();
    }
  }, [dados]);

  useEffect(() => {
    if (funcionarios?.length > 0) {
      const Funcao = [
        ...new Set(funcionarios?.map((f: { Funcao: any }) => f.Funcao)),
      ];
      const CCusto = [
        ...new Set(
          funcionarios?.map((f: { NomeCentroCusto: any }) => f.NomeCentroCusto)
        ),
      ];

      setFuncaos(Funcao.sort());
      setCentrosCustos(CCusto.sort());
    }
  }, [funcionarios]);

  useEffect(() => {
    if (motivoSelecionado === "SUBSTITUIÇÃO" && inputCPF.current) {
      // reaplica máscara ao CPF
      IMask(inputCPF.current, {
        mask: "000.000.000-00",
      });
    }
  }, [motivoSelecionado]);

  useEffect(() => {
    console.log(state);
  }, [state]);

  useEffect(() => {
    console.log("Apos Atualização de state :", prescisaEPI);
  }, [prescisaEPI]);

  return (
    <div className="bg-gray-200 ml-15 mt-15 max-w-dvw h-auto p-5">
      <div className="bg-white h-full max-w-dvw rounded-md border border-gray-300 ">
        <h1 className="text-2xl text-gray-800 text-center justify-center p-2 font-bold">
          Requisição de Admissão
        </h1>
        <hr />
        <h2 className="p-5 text-gray-800 font-bold text-">
          Datalhes da posição
        </h2>
        <Form action={formAction}>
          <div className="grid grid-cols-3 gap-5 p-5 text-gray-500">
            {/* campo oculto que recebe o e-mail do solicitante */}
            <input type="hidden" name="Email" value={email || ""} />

            <div className=" justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Tipo de Vaga</label>

              <select
                className="p-1 border border-gray-200 rounded-md cursor-pointer inset-shadow-sm"
                name="TipoVaga"
                id="1"
                required
              >
                <option value=" "></option>
                <option value="Temporario">Temporário</option>
                <option value="Terceiro">Terceiro</option>
                <option value="Estagiario">Estagiário</option>
                <option value="Efetivo">Efetivo</option>

                <option value="Aprendiz">Aprendiz</option>
                <option value="Outros">Outros</option>
              </select>
            </div>
            <div className="relative justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Cargo</label>

              <select
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer h-max-[10vh]"
                name="Cargo"
                id="2"
                onChange={(e) => setFuncaoSelecionada(e.target.value)}
                required
              >
                <option value=""></option>
                <option
                  className="bg-gray-100 hover:bg-gray-200"
                  value="ADICIONAR NOVO CARGO"
                >
                  ADICIONAR NOVO CARGO
                </option>

                {funcaos !== null &&
                  funcaos?.map((funcao: string, index: number) => (
                    <option key={index} value={funcao}>
                      {funcao}
                    </option>
                  ))}
              </select>
              {funcaoSelecionada === "ADICIONAR NOVO CARGO" && (
                <input
                  className="absolute bg-white left-px bottom-px h-[53%] rounded-md w-[95%] pl-2 outline-gray-200 "
                  placeholder="Digite o Novo Cargo..."
                  type="text"
                  name="NovoCargo"
                  id="NovoCargo"
                  required
                />
              )}
            </div>
            <div className="relative justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Centro De Custo
              </label>

              <select
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer h-max-[10vh]"
                name="CentroCusto"
                id="3"
                onChange={(e) => setCentroSelecionado(e.target.value)}
                required
              >
                <option value=""></option>
                <option
                  className="bg-gray-100 hover:bg-gray-200"
                  value="ADICIONAR NOVO CENTRO"
                >
                  ADICIONAR NOVO CENTRO
                </option>
                {Array.isArray(centrosCustos) &&
                  centrosCustos.map((centro: string, index: number) => (
                    <option key={index} value={centro}>
                      {centro}
                    </option>
                  ))}
              </select>
              {centroSelecionado === "ADICIONAR NOVO CENTRO" && (
                <input
                  className="absolute bg-white left-px bottom-px h-[53%] rounded-md w-[95%] pl-2 outline-gray-200 "
                  placeholder="Digite o Novo Centro de Custo..."
                  type="text"
                  name="NovoCentro"
                  id="NovaCentro"
                  required
                />
              )}
            </div>
            <div className=" justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Setor de Trabalho
              </label>

              <select
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="SetorTrabalho"
                id="4"
                required
              >
                <option value=" "></option>
                <option value="FINANCEIRO">FINANCEIRO</option>
                <option value="ADMISTRAÇÃO">ADMISTRAÇÃO</option>
                <option value="LOGISTICA">LOGISTICA</option>
                <option value="ATENDIMENTO">ATENDIMENTO</option>
                <option value="RECURSOS HUMANOS">RECURSOS HUMANOS</option>
                <option value="OPERACIONAL">OPERACIONAL</option>
              </select>
            </div>
            <div className=" justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Modalidade de Trabalho
              </label>

              <select
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="ModalidadeTrabalho"
                id="5"
              >
                <option value=" "></option>
                <option value="HOME OFFICE">HOME OFFICE</option>
                <option value="HÍBRIDO">HÍBRIDO</option>
                <option value="PRESENCIAL">PRESENCIAL</option>
                <option value="OUTROS">OUTROS</option>
              </select>
            </div>
            <div className=" justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Motivo de Contratação
              </label>

              <select
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                onChange={(e) => setMotivoSelecionado(e.target.value)}
                name="MotivoContratacao"
                id="6"
                required
              >
                <option value=" "></option>
                <option value="EXPANÇÂO">EXPANÇÃO</option>
                <option value="SUBSTITUIÇÃO">SUBSTITUIÇÃO</option>
                <option value="NOVO PROJETO">NOVO PROJETO</option>
                <option value="OUTROS">OUTROS</option>
              </select>
            </div>
            <div className=" justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Escala de Trabalho
              </label>

              <select
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="EscalaTrabalho"
                id="7"
                required
              >
                <option value=" "></option>
                <option value="Escala 2x2">Escala 2x2</option>
                <option value="Escala 4x2">Escala 4x2</option>
                <option value="Escala 4×4">Escala 4×4</option>
                <option value="Escala 5×1">Escala 5×1</option>
                <option value="Escala 5×2">Escala 5×2</option>
                <option value="Escala 6×1">Escala 6×1</option>
                <option value="Escala 6×2">Escala 6×2</option>
                <option value="Escala 12×36">Escala 12×36</option>
                <option value="Escala 12×60">Escala 12×60</option>
                <option value="Escala 12×72">Escala 12×72</option>
                <option value="Escala 24×48">Escala 24×48</option>
                <option value="Escala 24×72">Escala 24×72</option>
                <option value="Escala 40×48">Escala 40×48</option>
              </select>
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Local de Trabalho
              </label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="LocalTrabalho"
                id="8"
                required
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Salário</label>
              <NumericFormat
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="Salario"
                id="9"
                thousandSeparator="."
                decimalSeparator=","
                prefix="R$ "
                fixedDecimalScale
                decimalScale={2}
                allowNegative={false}
                required
              />
            </div>
            <div className="col-span-3 justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">
                Descrição do Cargo
              </label>
              <textarea
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer min-h-[100px]"
                name="DescricaoCargo"
                id="10"
                required
              ></textarea>
            </div>
            <div className="col-span-3 justify-start grid grid-cols-1 items-center">
              <div className="flex gap-2 items-center">
                <input
                  type="checkbox"
                  className="cursor-pointer h-4 w-10"
                  name="PrecisaEPI"
                  id="11"
                  checked={prescisaEPI}
                  onChange={(e) => setPrecisaEPI(e.target.checked)}
                />
                <label className="text-gray-800 font-medium ">
                  EPI, Uniforme e Crachá (somente se for aplicado para esta
                  contratação)
                </label>
              </div>
              <AnimatePresence>
                <motion.div
                  key="AnimationDescricaoEPI"
                  initial={{ backgroundColor: "#f3f4f6", height: "5vh" }}
                  animate={{
                    backgroundColor: prescisaEPI ? "#ffffff" : "#f3f4f6",
                    height: prescisaEPI ? "15vh" : "5vh",
                  }}
                  exit={{ backgroundColor: "#f3f4f6", height: "5vh" }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="grid grid-cols-3 w-[90vw]"
                >
                  <textarea
                    disabled={!prescisaEPI}
                    className={`col-span-3 p-2 border border-gray-200 inset-shadow-sm rounded-md resize-none focus:outline-none  ${
                      prescisaEPI
                        ? "bg-white"
                        : "bg-gray-100 cursor-not-allowed"
                    }`}
                    name="DescricaoEPI"
                    placeholder="Descreva os EPIs necessários"
                  ></textarea>
                </motion.div>
              </AnimatePresence>
            </div>
            <AnimatePresence>
              {motivoSelecionado === "SUBSTITUIÇÃO" && (
                <motion.div
                  key="substituicao"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                  className="grid grid-cols-3 w-[90vw] gap-5 overflow-hidden"
                >
                  <div className="col-span-3">
                    <hr className="text-gray-200" />
                    <h2 className="text-gray-800 font-bold mt-5 mb-2">
                      Colaborador Substituído
                    </h2>
                  </div>

                  <div className="justify-start grid grid-cols-1 items-center">
                    <label className="text-gray-800 font-medium">Nome</label>
                    <input
                      type="text"
                      className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                      name="NomeSubstituido"
                      id="13"
                    />
                  </div>

                  <div className="justify-start grid grid-cols-1 items-center">
                    <label className="text-gray-800 font-medium">CPF</label>
                    <input
                      type="text"
                      className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                      name="CPFSubstituido"
                      ref={inputCPF}
                      id="14"
                    />
                  </div>

                  <div className="justify-start grid grid-cols-1 items-center">
                    <label className="text-gray-800 font-medium">
                      Motivo da Substituição
                    </label>
                    <select
                      className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                      name="MotivoSubstituido"
                      id="15"
                    >
                      <option value=""></option>
                      <option value="BAIXO DESEMPENHO">BAIXO DESEMPENHO</option>
                      <option value="PROBLEMA DE COMPORTAMENTO">
                        PROBLEMA DE COMPORTAMENTO
                      </option>
                      <option value="SAÍDA VOLUNTÁRIA">SAÍDA VOLUNTÁRIA</option>
                      <option value="ACIDENTE DE TRABALHO">
                        ACIDENTE DE TRABALHO
                      </option>
                    </select>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div className="col-span-3">
              <hr className="text-gray-200" />
              <h2 className="text-gray-800 font-bold mt-5 mb-2">
                RH Responsável
              </h2>
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Nome</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="NomeResponsavelRH"
                id="16"
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">E-mail</label>
              <input
                type="email"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="EmailResponsavelRH"
                id="17"
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Telefone</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="TelefoneResponsavelRH"
                id="18"
                ref={inputTelefoneRHResponsavel}
              />
            </div>
            <div className="col-span-3">
              <hr className="text-gray-200" />
              <h2 className="text-gray-800 font-bold mt-5 mb-2">
                Gestor para Validação do Ponto
              </h2>
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Nome</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="NomeGestorPonto"
                id="19"
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">E-mail</label>
              <input
                type="email"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="EmailGestorPonto"
                id="20"
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Telefone</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="TelefoneGestorPonto"
                id="21"
                ref={inputGestorPonto}
              />
            </div>
            <div className="col-span-3">
              <hr className="text-gray-200" />
              <h2 className="text-gray-800 font-bold mt-5 mb-2">
                No Primeiro Dia Deverá Procurar Por Quem?
              </h2>
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Nome</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="NomePessoaPrimeiroDia"
                id="22"
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Departamento</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="DepartamentoPrimeiroDia"
                id="23"
              />
            </div>
            <div className="justify-start grid grid-cols-1 items-center">
              <label className="text-gray-800 font-medium">Horário</label>
              <input
                type="text"
                className="p-1 border border-gray-200 inset-shadow-sm rounded-md cursor-pointer"
                name="HorarioPrimeiroDia"
                id="24"
                ref={inputHorario}
              />
            </div>
          </div>

          <div className="flex justify-center mt-8 mb-4 p-5">
            <button
              type="submit"
              className="bg-gray-500 w-2xl text-white px-6 py-2 rounded-md hover:bg-gray-600 transition cursor-pointer"
            >
              Enviar Requisição
            </button>
          </div>
        </Form>
      </div>
    </div>
  );
}
