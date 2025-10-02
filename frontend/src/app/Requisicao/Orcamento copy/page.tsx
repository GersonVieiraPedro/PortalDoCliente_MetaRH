'use client'
import { use, useEffect, useState, Fragment } from 'react'
import encargos from './encargos.json'
import { NumericFormat } from 'react-number-format'
import { set } from 'date-fns'

type Encargo = {
  nome: string
  percentual: number
}

type TipoContratacao = keyof typeof encargos

export default function Page() {
  const [tipoContratacao, setTipoContratacao] = useState<string>('')
  const [salario, setSalario] = useState<number>(0)
  const [salarioBruto, setSalarioBruto] = useState<number>(0)
  const [total, setTotal] = useState<any>({})
  const [periculosidade, setPericulosidade] = useState<string>('')

  const [encargosSelecionados, setEncargosSelecionados] = useState<
    (typeof encargos)[TipoContratacao] | undefined
  >(undefined)

  useEffect(() => {
    if (tipoContratacao !== '') {
      setEncargosSelecionados(encargos[tipoContratacao as TipoContratacao])
    }
  }, [tipoContratacao])

  useEffect(() => {
    if (!encargosSelecionados) return

    let totalPercentualGeral = 0
    let totalValorGeral = 0
    const totaisPorGrupo: Record<string, { percentual: number; valor: number }> = {}

    Object.entries(encargosSelecionados).forEach(([grupo, lista]) => {
      if (Array.isArray(lista)) {
        const totalPercentualGrupo = lista.reduce(
          (acc, encargo: Encargo) => acc + encargo.percentual,
          0
        )
        const totalValorGrupo = lista.reduce(
          (acc, encargo: Encargo) => acc + (encargo.percentual / 100) * salario,
          0
        )

        totaisPorGrupo[grupo] = {
          percentual: totalPercentualGrupo,
          valor: totalValorGrupo,
        }

        totalPercentualGeral += totalPercentualGrupo
        totalValorGeral += totalValorGrupo
      }
    })
    setTotal(totaisPorGrupo)
  }, [encargosSelecionados, salario])

  useEffect(() => {
    console.log('Totais:', total)
  }, [total])

  useEffect(() => {
    if (periculosidade === 'Sim') {
      const valorPericulosidade = (salario * 0.3).toFixed(2)
      const salarioComPericulosidade = salario + parseFloat(valorPericulosidade)
      setSalarioBruto(salarioComPericulosidade)
    } else {
      setSalarioBruto(salario)
    }
  }, [salario, periculosidade])

  return (
    <div className="mt-15 ml-15 h-full max-w-dvw bg-gray-200 p-5 text-gray-800">
      <div className="mb-5 flex items-center gap-3">
        <div className="h-full w-full rounded-md border border-gray-300 bg-white">
          <h1 className="justify-center p-2 text-center text-2xl font-bold text-gray-800">
            Simulação de Orçamento
          </h1>
          <hr className="text-gray-300" />
          <div className="flex h-full w-full flex-col p-5">
            <h2 className="p-2 text-lg font-bold text-gray-800">Selecione o tipo de contratação</h2>
            <div className="mb-5 flex h-full w-full justify-center gap-[10%] p-2">
              <div
                className={
                  (tipoContratacao === 'Temporário' ? 'scale-105 bg-purple-200 ' : 'bg-gray-100 ') +
                  'h-[50%] w-[20%] cursor-pointer rounded-md caret-transparent shadow-md hover:scale-105'
                }
                onClick={() => {
                  if (tipoContratacao === 'Temporário') {
                    setTipoContratacao('')
                    setEncargosSelecionados(undefined)
                  } else {
                    setTipoContratacao('Temporário')
                  }
                }}
              >
                <img
                  src="/Temporario.jpg"
                  alt="Temporário"
                  className="pointer-events-none rounded-t-md object-cover"
                />
                <div className="pointer-events-none flex h-1/6 w-full flex-col gap-2 p-2 text-center">
                  <h2 className="font-bold">Temporário</h2>
                  <hr className="text-gray-300" />
                  <p className="p-2 text-sm">
                    Contratação flexível para demandas sazonais ou emergenciais, assegurando rapidez
                    na substituição de profissionais e atendimento imediato às necessidades da sua
                    empresa.
                  </p>
                </div>
              </div>
              <div
                className={
                  (tipoContratacao === 'Terceirizado'
                    ? 'scale-105 bg-purple-200 '
                    : 'bg-gray-100 ') +
                  'h-[50%] w-[20%] cursor-pointer rounded-md caret-transparent shadow-md hover:scale-105'
                }
                onClick={() => {
                  if (tipoContratacao === 'Terceirizado') {
                    setTipoContratacao('')
                    setEncargosSelecionados(undefined)
                  } else {
                    setTipoContratacao('Terceirizado')
                  }
                }}
              >
                <img
                  src="/Terceirizado.jpg"
                  alt="Terceirizado"
                  className="pointer-events-none rounded-t-md object-cover"
                />
                <div className="pointer-events-none flex h-1/6 w-full flex-col gap-2 p-2 text-center">
                  <h2 className="font-bold">Terceirizado</h2>
                  <hr className="text-gray-300" />
                  <p className="p-2 text-sm">
                    Solução completa para a gestão de mão de obra contínua, com responsabilidade
                    trabalhista e administrativa sob nossa equipe, garantindo agilidade e
                    conformidade legal.
                  </p>
                </div>
              </div>
              <div
                className={
                  (tipoContratacao === 'Recrutamento & Seleção'
                    ? 'scale-105 bg-purple-200 '
                    : 'bg-gray-100 ') +
                  'h-[50%] w-[20%] cursor-pointer rounded-md caret-transparent shadow-md hover:scale-105'
                }
                onClick={() => {
                  if (tipoContratacao === 'Recrutamento & Seleção') {
                    setTipoContratacao('')
                    setEncargosSelecionados(undefined)
                  } else {
                    setTipoContratacao('Recrutamento & Seleção')
                  }
                }}
              >
                <img
                  src="/Recrutamento&Selecao.jpg"
                  alt="Recrutamento & Seleção"
                  className="pointer-events-none rounded-t-md object-cover"
                />
                <div className="pointer-events-none flex h-1/6 w-full flex-col gap-2 p-2 text-center">
                  <h2 className="font-bold">Recrutamento & Seleção</h2>
                  <hr className="text-gray-300" />
                  <p className="p-2 text-sm">
                    Processo seletivo especializado para encontrar talentos alinhados ao perfil da
                    sua vaga, reduzindo tempo de contratação e aumentando a assertividade na
                    escolha.
                  </p>
                </div>
              </div>
            </div>
            <hr className="text-gray-300" />
            <h2 className="mb-5 p-2 text-lg font-bold text-gray-800">Dados da posição</h2>
            <div className="mb-5 grid h-full w-full grid-cols-4 grid-rows-2 gap-4">
              <div className="relative col-span-4 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Cargo</label>

                <select
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Cargo"
                  id="1"
                  required
                >
                  <option value="" disabled selected>
                    Selecione o cargo
                  </option>
                  <option value="1">Auxiliar Administrativo</option>
                </select>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Salário</label>
                <NumericFormat
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Salario"
                  id="2"
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  fixedDecimalScale
                  decimalScale={2}
                  allowNegative={false}
                  required
                  value={salario === 0 ? '' : salario}
                  onValueChange={(values: { floatValue?: number }) => {
                    const { floatValue } = values
                    setSalario(floatValue || 0)
                  }}
                />
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Periculosidade</label>

                <select
                  className="h-9 cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Periculosidade"
                  id="3"
                  required
                  value={periculosidade}
                  onChange={(e) => setPericulosidade(e.target.value)}
                >
                  <option value="" disabled>
                    Selecione a periculosidade
                  </option>
                  <option value="Sim">Sim</option>
                  <option value="Não">Não</option>
                </select>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <div>
                  <label className="mr-3 font-medium text-gray-800">Insalubridade</label>
                  <div className="group relative inline-block">
                    <i className="bi bi-info-circle cursor-pointer hover:text-gray-400"></i>
                    <div className="text-info absolute bottom-full mb-2 hidden rounded-lg bg-gray-800 px-3 py-1 text-sm whitespace-nowrap text-white shadow-lg group-hover:block">
                      Base salário mínimo
                    </div>
                  </div>
                </div>

                <select
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Insalubridade"
                  id="4"
                  required
                >
                  <option value="" disabled selected>
                    Selecione a insalubridade
                  </option>
                  <option value="1">Grau Mínimo</option>
                  <option value="2">Grau Médio</option>
                  <option value="3">Grau Máximo</option>
                </select>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <div>
                  <label className="font-medium text-gray-800">Insalubridade (Percentual)</label>
                </div>

                <input
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="Insalubridade"
                  id="5"
                  type="text"
                  required
                  readOnly
                />
              </div>
            </div>
            <div className="my-5 flex h-[20%] w-full justify-between bg-purple-300 p-2">
              <h2 className="ml-10 p-2 text-center text-lg font-bold text-gray-800">
                Salário Bruto
              </h2>
              <NumericFormat
                className="right-0 text-center text-lg font-bold text-gray-800"
                name="SalarioBruto"
                id="6"
                thousandSeparator="."
                decimalSeparator=","
                prefix="R$ "
                fixedDecimalScale
                decimalScale={2}
                allowNegative={false}
                required
                value={salarioBruto === 0 ? '' : salarioBruto}
                disabled
              />
            </div>
            {encargosSelecionados && (
              <div>
                {Object.entries(encargosSelecionados).map(
                  ([grupo, lista]: [string, number | { nome: string; percentual: number }[]]) => (
                    <div key={grupo} className="mb-5 grid w-full grid-flow-row grid-cols-4">
                      <div className="col-span-2">
                        <h2 className="border border-purple-300 bg-purple-100 p-2 text-lg font-bold text-gray-800">
                          {grupo}
                        </h2>
                      </div>
                      <div className="border border-purple-300 bg-purple-100">
                        <h2 className="p-2 text-center text-lg font-bold text-gray-800">%</h2>
                      </div>
                      <div className="border border-purple-300 bg-purple-100">
                        <h2 className="p-2 text-center text-lg font-bold text-gray-800">R$</h2>
                      </div>
                      {Array.isArray(lista) ? (
                        <>
                          {lista.map((encargo, idx) => (
                            <Fragment key={idx}>
                              <div className="col-span-2 border border-gray-300 p-2 text-gray-800">
                                {encargo.nome}
                              </div>
                              <div className="border border-gray-300 p-2 text-center text-gray-800">
                                {encargo.percentual.toFixed(2)}%
                              </div>

                              <NumericFormat
                                className="border border-gray-300 p-2 text-center text-gray-800"
                                name={'Taxa_' + encargo.nome}
                                id={'Taxa_' + idx}
                                thousandSeparator="."
                                decimalSeparator=","
                                prefix="R$ "
                                fixedDecimalScale
                                decimalScale={2}
                                allowNegative={false}
                                required
                                value={(encargo.percentual / 100) * salario}
                                disabled
                              />
                            </Fragment>
                          ))}
                          <div className="col-span-2">
                            <h2 className="border border-purple-300 bg-purple-100 p-2 text-lg font-bold text-gray-800">
                              Total {grupo}
                            </h2>
                          </div>
                          <div className="border border-purple-300 bg-purple-100">
                            <h2 className="p-2 text-center text-lg font-bold text-gray-800">
                              {lista
                                .reduce((acc, encargo) => acc + encargo.percentual, 0)
                                .toFixed(2)}{' '}
                              %
                            </h2>
                          </div>
                          <NumericFormat
                            className="border border-purple-300 bg-purple-100 p-2 text-center text-lg font-bold text-gray-800"
                            name={'TotalTaxa_' + grupo}
                            id="10"
                            thousandSeparator="."
                            decimalSeparator=","
                            prefix="R$ "
                            fixedDecimalScale
                            decimalScale={2}
                            allowNegative={false}
                            required
                            value={lista
                              .reduce(
                                (acc, encargo) => acc + (encargo.percentual / 100) * salario,
                                0
                              )
                              .toFixed(2)}
                            disabled
                          />
                        </>
                      ) : (
                        <div>
                          <h3>Nenhum encargo selecionado</h3>
                        </div>
                      )}
                    </div>
                  )
                )}
              </div>
            )}

            {encargosSelecionados && Object.keys(encargosSelecionados).length === 2 && (
              <div className="mb-5 grid h-[60%] w-full grid-flow-row grid-cols-4">
                <div className="col-span-2">
                  <h2 className="border border-purple-500 bg-purple-300 p-2 text-lg font-bold text-gray-800">
                    Encargos Sociais Obrigatórios - Grupo A
                  </h2>
                </div>
                <div className="border border-purple-500 bg-purple-300">
                  <h2 className="p-2 text-center text-lg font-bold text-gray-800">{}</h2>
                </div>
                <div className="border border-purple-500 bg-purple-300">
                  <h2 className="p-2 text-center text-lg font-bold text-gray-800">R$</h2>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
// Removed getElementById function as it's no longer needed.
