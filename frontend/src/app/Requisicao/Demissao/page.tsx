'use client'

import { useActionState, useEffect, useState } from 'react'
import { NumericFormat } from 'react-number-format'
import Form from 'next/form'
import { Alerta } from '@/src/components/Alerta'
import RegistrarDemissao from './registrarDemissao'
import { useUsuario } from '../../contexts/UsuarioContext'
import { MeusFuncionarios } from '../Admissao/MeusDados'

export default function Demissao() {
  const { usuario } = useUsuario()
  const CNPJS = usuario?.CNPJS ? [usuario.CNPJS] : []
  const CodigoCliente = usuario?.CodigoCliente ? [usuario.CodigoCliente] : []
  const [dados, setDados] = useState<any>(null)
  const [funcionarios, setFuncionarios] = useState<any>(null)
  const [email, setEmail] = useState<string | null>('')
  const [token, setToken] = useState<string>('')
  const [mensagemAlerta, setMensagemAlerta] = useState<any>([])
  const [alertaVisivel, setAlertaVisivel] = useState(false)
  const [funcionarioSelecionado, setFuncionarioSelecionado] = useState<any>(null)
  const [state, formAction, isPending] = useActionState(RegistrarDemissao, null)
  const [dataDemissao, setDataDemissao] = useState<string>('')

  useEffect(() => {
    if (usuario?.CNPJS !== dados?.CNPJ || usuario?.CodigoCliente !== dados?.CodigoCliente) {
      setDados(usuario)
    }
  }, [usuario])

  useEffect(() => {
    //Função assincrona que chama a consulta do backend
    const Funcionarios = async () => {
      if (CNPJS.length + CodigoCliente.length > 0) {
        const varFuncionarios = await MeusFuncionarios(CNPJS[0], CodigoCliente[0])
        setFuncionarios(varFuncionarios)
      }
    }

    if (CNPJS.length > 0 || CodigoCliente.length > 0) {
      Funcionarios()
    }
  }, [dados])

  useEffect(() => {
    if (funcionarios?.length > 0) {
      console.log('Funcionarios : ', funcionarios)
    }
  }, [funcionarios])

  useEffect(() => {
    if (state) {
      setMensagemAlerta(state)
      setAlertaVisivel(true)
    }
  }, [state])

  useEffect(() => {
    if (funcionarioSelecionado) {
      console.log('Funcionario Selecionado : ', funcionarioSelecionado)
    }
  }, [funcionarioSelecionado])

  const handleDemissaoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    const hoje = new Date().toISOString().split('T')[0]
    if (value < hoje) {
      setDataDemissao(hoje)
    } else {
      setDataDemissao(value)
    }
  }

  return (
    <div>
      {alertaVisivel && state && (
        <Alerta
          titulo={state.status === 'Sucesso' ? 'Solicitação Enviada' : 'Falha ao Salvar'}
          mensagem={<div>{state.mensagem}</div>}
          botoes={null}
          tipo="Simples"
          visivel={true}
          setMensagemALerta={(valor) => {
            setMensagemAlerta(valor)
            setAlertaVisivel(false)
          }}
        />
      )}
      <div className="mt-15 ml-15 h-auto max-w-dvw bg-gray-200 p-5">
        <div className="h-full max-w-dvw rounded-md border border-gray-300 bg-white">
          <h1 className="justify-center p-2 text-center text-2xl font-bold text-gray-800">
            Requisição de Demissão
          </h1>
          <hr />
          <h2 className="text- p-5 font-bold text-gray-800">Datalhes da posição</h2>
          <Form
            action={formAction}
            onSubmit={() => {
              setFuncionarioSelecionado(null)
              setDataDemissao('')
            }}
          >
            <div className="grid grid-cols-3 gap-5 p-5 text-gray-500">
              {/* campo oculto que recebe o e-mail do solicitante */}
              <input type="hidden" name="Email" value={email || ''} />

              <div className="col-span-2 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Nome Funcionário</label>

                <select
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="NomeFuncionario"
                  id="1"
                  required
                  onChange={(e) => {
                    const funcionarioSelecionado = funcionarios.find(
                      (f: any) => f.CodigoFuncionario.toString() === e.target.value
                    )
                    setFuncionarioSelecionado(funcionarioSelecionado)
                  }}
                >
                  <option value=" "></option>
                  {funcionarios &&
                    funcionarios.map((funcionario: any, CodigoFuncionario: number) => (
                      <option key={CodigoFuncionario} value={funcionario.CodigoFuncionario}>
                        {funcionario.Nome}
                      </option>
                    ))}
                </select>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Matrícula</label>

                <input
                  type="text"
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="CodigoFuncionario"
                  id="2"
                  required
                  value={funcionarioSelecionado ? funcionarioSelecionado.CodigoFuncionario : ''}
                  readOnly
                />
              </div>
              <div className="relative col-span-2 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Cargo</label>

                <input
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Cargo"
                  id="3"
                  type="text"
                  required
                  value={funcionarioSelecionado ? funcionarioSelecionado.Funcao : ''}
                  readOnly
                />
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Centro de Custo</label>

                <input
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="CentroCusto"
                  id="4"
                  type="text"
                  required
                  value={funcionarioSelecionado ? funcionarioSelecionado.NomeCentroCusto : ''}
                  readOnly
                />
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Empresa</label>

                <input
                  type="text"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Empresa"
                  id="5"
                  required
                  value={funcionarioSelecionado ? funcionarioSelecionado.RazaoSocial : ''}
                  readOnly
                />
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Gestor</label>

                <input
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Gestor"
                  id="6"
                  required
                />
              </div>

              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Salário</label>
                <NumericFormat
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Salario"
                  id="9"
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  fixedDecimalScale
                  decimalScale={2}
                  allowNegative={false}
                  required
                  value={funcionarioSelecionado ? funcionarioSelecionado.Salario : ''}
                  readOnly
                />
              </div>
              <div className="col-span-1 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Data Admissão</label>
                <input
                  type="date"
                  id="7"
                  name="DataAdmissao"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  value={
                    funcionarioSelecionado
                      ? new Date(funcionarioSelecionado.DataAdmissao).toISOString().split('T')[0]
                      : ''
                  }
                  readOnly
                />
              </div>

              <div className="col-span-1 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Data Demissão</label>
                <input
                  type="date"
                  id="8"
                  name="DataDemissao"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  min={new Date().toISOString().split('T')[0]}
                  value={dataDemissao}
                  onChange={handleDemissaoChange}
                />
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Motivo de Demissão</label>
                <select
                  name="MotivoDemissao"
                  id="MotivoDemissao"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                >
                  <option value=""></option>
                  <option value="Pedido do Colaborador">Pedido do Colaborador</option>
                  <option value="Término de Contrato">Término de Contrato</option>
                  <option value="Justa Causa">Justa Causa</option>
                  <option value="Outros">Outros</option>
                </select>
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Férias Vencidas</label>
                <input
                  type="text"
                  id="10"
                  name="FeriasVencidas"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                />
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Aviso Prévio</label>
                <select
                  name="AvisoPrevio"
                  id="AvisoPrevio"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                >
                  <option value=""></option>
                  <option value="Aviso Prévio Indenizado">Aviso Prévio Indenizado</option>
                  <option value="Aviso Prévio Trabalhado">Aviso Prévio Trabalhado</option>
                </select>
              </div>

              <div className="col-span-3">
                <hr className="text-gray-200" />
                <h2 className="mt-5 mb-2 font-bold text-gray-800">Detalhes Importantes</h2>
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">
                  O Colaborador já tem conhecimento do desligamento?
                </label>
                <select
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="ConhecimentoDesligamento"
                  id="16"
                  required
                >
                  <option value=""></option>
                  <option value="Sim">Sim</option>
                  <option value="Não">Não</option>
                </select>
              </div>
              <div className="col-span-2 grid items-center justify-start"></div>

              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">
                  O Comunicado será feito presencialmente?
                </label>
                <select
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="ComunicadoPresencial"
                  id="17"
                  required
                >
                  <option value=""></option>
                  <option value="Sim">Sim</option>
                  <option value="Não">Não</option>
                </select>
              </div>
              <div className="col-span-2 grid items-center justify-start"></div>
              <div className="col-span-2 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Endereço</label>
                <input
                  type="text"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Endereco"
                  id="20"
                  required
                />
              </div>
              <div className="grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Horario</label>
                <input
                  type="time"
                  className="cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Horario"
                  id="21"
                  required
                />
              </div>
            </div>

            <div className="mt-8 mb-4 flex justify-center p-5">
              <button
                type="submit"
                className="w-2xl cursor-pointer rounded-md bg-gray-500 px-6 py-2 text-white transition hover:bg-gray-600"
              >
                Enviar Requisição
              </button>
            </div>
          </Form>
        </div>
      </div>
    </div>
  )
}
