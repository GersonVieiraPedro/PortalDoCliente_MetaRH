'use client'
import { useEffect, useState, Fragment } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import encargos from '../encargos.json'
import beneficiosJson from '../beneficios.json'
import { NumericFormat } from 'react-number-format'
import { getISS } from '../dados'

type Encargo = {
  nome: string
  percentual: number
}

type TipoContratacao = keyof typeof encargos

interface Beneficio {
  quantidade: number
  valor_unitario: number
  desconto: number
  fornecido: number
  repasse: number
  dias: number
}

const Tributos = {
  // ISS Dinamico conforme o município
  PIS: 1.65,
  COFINS: 7.6,
  IRPJ: 1.0,
  CSLL: 1.0,
}

export default function Page() {
  const [tipoContratacao, setTipoContratacao] = useState<string>('')
  const [salario, setSalario] = useState<number>(0)
  const [salarioBruto, setSalarioBruto] = useState<number>(0)
  const [total, setTotal] = useState<Record<string, { percentual: number; valor: number }>>({})
  const [periculosidade, setPericulosidade] = useState<string>('')
  const [insalubridade, setInsalubridade] = useState<number>(0)
  const [tabelaISS, setTabelaISS] = useState<any>(null)
  const [municipioISS, setMunicipioISS] = useState<any>({})
  const [taxaAdministrativa, setTaxaAdministrativa] = useState<number>(0.15)
  const [valorAdministrativa, setValorAdministrativa] = useState<number>(0)

  const [encargosSelecionados, setEncargosSelecionados] = useState<
    (typeof encargos)[TipoContratacao] | undefined
  >(undefined)

  const [beneficios, setBeneficios] = useState<any>(undefined)
  const [checkBoxStatus, setCheckBoxStatus] = useState<{ [key: string]: boolean }>({})
  const [checkBoxExame, setCheckBoxExame] = useState<boolean>(false)
  const [beneficiosCalculos, setBeneficiosCalculos] = useState<Record<string, Beneficio>>({})
  const [totaisBeneficios, setTotaisBeneficios] = useState<{ repasse: number; fornecido: number }>({
    repasse: 0,
    fornecido: 0,
  })

  const [encargosTrabalhistas, setEncargosTrabalhistas] = useState<number>(0)
  const [subtotalNotaFiscal, setSubtotalNotaFiscal] = useState<number>(0)
  const [valorTotalFinal, setValorTotalFinal] = useState<number>(0)
  const [quantidadeColaboradores, setQuantidadeColaboradores] = useState<number>(1)
  const [valorProjecaoTotalFinal, setValorProjecaoTotalFinal] = useState<number>(0)
  const [contratos, setContratos] = useState<any>([])
  const [simular, setSimular] = useState<boolean>(false)
  const onCheckBoxStatus = (key: string) => {
    setCheckBoxStatus((prev: { [key: string]: boolean }) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  const onChargeValoresBeneficios = (
    key: string,
    fild: 'quantidade' | 'valor_unitario' | 'desconto',
    valor: number
  ) => {
    setBeneficiosCalculos((prev) => {
      const updated = {
        ...prev,
        [key]: {
          ...prev[key],
          [fild]: valor,
          fornecido:
            fild === 'quantidade'
              ? valor * prev[key].valor_unitario * (prev[key]?.dias || 1)
              : valor * prev[key].quantidade * (prev[key]?.dias || 1),
          repasse: Math.max(
            0,
            key === '0'
              ? ((fild === 'quantidade' ? valor : prev[key].quantidade) || 0) *
                  ((fild === 'valor_unitario' ? valor : prev[key].valor_unitario) || 0) *
                  (prev[key]?.dias || 1) -
                  (((fild === 'desconto' ? valor : prev[key].desconto) / 100) * salario || 0)
              : ((fild === 'quantidade' ? valor : prev[key].quantidade) || 0) *
                  ((fild === 'valor_unitario' ? valor : prev[key].valor_unitario) || 0) *
                  (prev[key]?.dias || 1)
          ),
        },
      }
      return updated
    })
  }

  useEffect(() => {
    setEncargosSelecionados(encargos['Terceirizado'])
    setBeneficios(beneficiosJson)
    const pegarDados = async () => {
      try {
        const data = await getISS()

        setTabelaISS(data)
      } catch (error) {
        console.error('Erro ao buscar ISS:', error)
      }
    }
    pegarDados()
  }, [])

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
          (acc, encargo: Encargo) => acc + (encargo.percentual / 100) * salarioBruto,
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
  }, [encargosSelecionados, salarioBruto])

  useEffect(() => {
    let novoSalario = salario

    // aplica periculosidade (30%)
    if (periculosidade === 'Sim') {
      novoSalario += salario * 0.3
    }

    // aplica insalubridade (percentual sobre 1518)
    if (insalubridade) {
      novoSalario += 1518 * (insalubridade / 100)
    }

    setSalarioBruto(parseFloat(novoSalario.toFixed(2)))
  }, [salario, periculosidade, insalubridade])

  useEffect(() => {
    // Inicializa checkBoxStatus com false para cada benefício
    const initialCheckBoxStatus = Object.keys(beneficiosJson).reduce(
      (acc, key) => ({ ...acc, [key]: false }),
      {}
    )
    setCheckBoxStatus(initialCheckBoxStatus)

    // Calculando os valores iniciais dos beneficos passados pelo json
    let valoresInicialBeneficios = {}
    if (salario !== 0) {
      valoresInicialBeneficios = Object.entries(beneficiosJson).reduce(
        (acc, [key, b]: [string, any]) => ({
          ...acc,
          [key]: {
            quantidade: b.quantidade || 0,
            valor_unitario: b.valor_unitario || 0,
            desconto: b.desconto.valor || 0,
            fornecido: (b.quantidade || 0) * (b.valor_unitario || 0) * (b?.dias || 0),
            repasse: Math.max(
              0,
              b.id === 'vale_transporte'
                ? (b.quantidade || 0) * (b.valor_unitario || 0) * (b?.dias || 1) -
                    ((b.desconto?.valor / 100) * salario || 0)
                : (b.quantidade || 0) * (b.valor_unitario || 0) * (b?.dias || 1)
            ),
            dias: b?.dias || 1,
          },
        }),
        {}
      )
    }

    setBeneficiosCalculos(valoresInicialBeneficios)
  }, [beneficios, salario])

  useEffect(() => {
    const totais = Object.entries(beneficiosCalculos).reduce(
      (acc, [key, beneficio]: [string, Beneficio]) => {
        if (checkBoxStatus[key]) {
          return {
            fornecido: acc.fornecido + beneficio.fornecido,
            repasse: acc.repasse + beneficio.repasse,
          }
        }
        return acc
      },
      { fornecido: 0, repasse: 0 }
    )

    setTotaisBeneficios(totais)
  }, [checkBoxStatus, beneficiosCalculos])

  useEffect(() => {
    if (municipioISS && municipioISS.ISS) {
      const percentual = (
        parseFloat(municipioISS.ISS) + Object.values(Tributos).reduce((acc, curr) => acc + curr, 0)
      ).toFixed(2)

      setEncargosTrabalhistas(parseFloat(percentual))
    }
  }, [municipioISS])

  useEffect(() => {
    const subtotal =
      salarioBruto +
      totaisBeneficios.repasse +
      (checkBoxExame ? 62.35 : 0) +
      Object.values(total).reduce((acc, grupo: any) => acc + grupo.valor, 0)

    setSubtotalNotaFiscal(subtotal)
  }, [salarioBruto, totaisBeneficios, checkBoxExame, total])

  useEffect(() => {
    // Subtotal + taxa administrativa
    setValorAdministrativa(subtotalNotaFiscal * (1 + taxaAdministrativa))
  }, [subtotalNotaFiscal, taxaAdministrativa])

  useEffect(() => {
    const divisor = 1 - encargosTrabalhistas / 100
    const valor = valorAdministrativa / divisor

    setValorTotalFinal(valor.toFixed(2) as unknown as number)
  }, [valorAdministrativa])

  useEffect(() => {
    setValorProjecaoTotalFinal(valorTotalFinal * quantidadeColaboradores)
  }, [valorTotalFinal, quantidadeColaboradores])
  return (
    <div className="mt-15 ml-15 h-full max-w-dvw bg-gray-200 p-5 text-gray-800">
      <div className="mb-5 flex items-center gap-3">
        <div className="h-full w-full rounded-md border border-gray-300 bg-white">
          <h1 className="justify-center p-2 text-center text-2xl font-bold text-gray-800">
            Simulação de Orçamento Terceirizado
          </h1>
          <hr className="text-gray-300" />
          <div className="flex h-full w-full flex-col p-5">
            <div className="mb-5 grid h-full w-full grid-cols-4 grid-rows-2 gap-4">
              <div className="relative col-span-2 grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Cargo</label>
                <input
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="text-cargo"
                  id="input-text-cargo"
                  required
                ></input>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Salário</label>
                <NumericFormat
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="number-salario"
                  id="input-number-salario"
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
                <label className="font-medium text-gray-800">Quantidade Colaboradores</label>
                <input
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="number-quantidade-colaboradores"
                  id="input-number-quantidade-colaboradores"
                  type="number"
                  min={1}
                  defaultValue={1}
                  required
                  onChangeCapture={(e) =>
                    setQuantidadeColaboradores(Number((e.target as HTMLInputElement).value))
                  }
                ></input>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Periculosidade</label>
                <select
                  className="h-9 cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="select-periculosidade"
                  id="input-select-periculosidade"
                  required
                  value={periculosidade}
                  onChange={(e) => setPericulosidade(e.target.value)}
                >
                  <option value="">Selecione a periculosidade</option>
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
                  className="h-9 cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="select-insalubridade"
                  id="input-select-insalubridade"
                  required
                  onChange={(e) => {
                    setInsalubridade(Number(e.target.value))
                  }}
                >
                  <option value="">Selecione a insalubridade</option>
                  <option value="10">Grau Mínimo</option>
                  <option value="20">Grau Médio</option>
                  <option value="40">Grau Máximo</option>
                </select>
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <div>
                  <label className="font-medium text-gray-800">Insalubridade (Percentual)</label>
                </div>
                <input
                  className="h-max-[10vh] cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="text-insalubridade-percentual"
                  id="input-text-insalubridade-percentual"
                  type="text"
                  required
                  value={insalubridade + ' %'}
                  readOnly
                />
              </div>
              <div className="relative grid grid-cols-1 items-center justify-start">
                <label className="font-medium text-gray-800">Município</label>
                <select
                  className="h-9 cursor-pointer rounded-md border border-gray-200 p-1 inset-shadow-sm"
                  name="select-municipio-iss"
                  id="input-select-municipio-iss"
                  onChange={(e) => {
                    const selectedOption = tabelaISS.find(
                      (item: any) => item.ID === parseFloat(e.target.value)
                    )
                    if (selectedOption) {
                      const parsedISS = parseFloat(selectedOption.ISS.replace(',', '.')).toFixed(2)
                      setMunicipioISS({ ...selectedOption, ISS: parsedISS })
                    }
                  }}
                  required
                >
                  <option value="">Selecione o município</option>
                  {tabelaISS &&
                    tabelaISS.map((item: any) => (
                      <option key={item.ID} value={item.ID} className="text-gray-800">
                        {item.Label}
                      </option>
                    ))}
                </select>
              </div>
            </div>
            <div className="my-5 grid h-14 w-full grid-cols-4 items-center justify-center rounded-md border border-purple-500 bg-purple-300">
              <h2 className="col-span-3 p-2 text-lg font-bold text-gray-800">Salário Bruto</h2>
              <NumericFormat
                className="right-0 text-center text-lg font-bold text-gray-800"
                name="number-salario-bruto"
                id="input-number-salario-bruto"
                thousandSeparator="."
                decimalSeparator=","
                prefix="R$ "
                fixedDecimalScale
                decimalScale={2}
                allowNegative={false}
                required
                value={salarioBruto === 0 ? '' : salarioBruto}
                readOnly
              />
            </div>
            {encargosSelecionados && (
              <div>
                {Object.entries(encargosSelecionados).map(
                  ([grupo, lista]: [string, number | { nome: string; percentual: number }[]]) => (
                    <div key={grupo} className="mb-5 grid w-full grid-flow-row grid-cols-4">
                      <div className="col-span-2">
                        <h2 className="rounded-tl-md border border-purple-300 bg-purple-100 p-2 text-lg font-bold text-gray-800">
                          {grupo}
                        </h2>
                      </div>
                      <div className="border border-purple-300 bg-purple-100">
                        <h2 className="p-2 text-center text-lg font-bold text-gray-800">%</h2>
                      </div>
                      <div className="rounded-tr-md border border-purple-300 bg-purple-100">
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
                                {encargo.percentual.toFixed(2).replace('.', ',')}%
                              </div>
                              <NumericFormat
                                className="border border-gray-300 p-2 text-center text-gray-800"
                                name={`number-taxa-${encargo.nome.toLowerCase().replace(/\s+/g, '-')}`}
                                id={`input-number-taxa-${encargo.nome.toLowerCase().replace(/\s+/g, '-')}`}
                                thousandSeparator="."
                                decimalSeparator=","
                                prefix="R$ "
                                fixedDecimalScale
                                decimalScale={2}
                                allowNegative={false}
                                required
                                value={(encargo.percentual / 100) * salarioBruto}
                                disabled
                              />
                            </Fragment>
                          ))}
                          <div className="col-span-2">
                            <h2 className="rounded-bl-md border border-purple-300 bg-purple-100 p-2 text-lg font-bold text-gray-800">
                              Total {grupo}
                            </h2>
                          </div>
                          <div className="border border-purple-300 bg-purple-100">
                            <h2 className="p-2 text-center text-lg font-bold text-gray-800">
                              {lista
                                .reduce((acc, encargo) => acc + encargo.percentual, 0)
                                .toFixed(2)
                                .replace('.', ',')}
                              %
                            </h2>
                          </div>
                          <NumericFormat
                            className="rounded-br-md border border-purple-300 bg-purple-100 p-2 text-center text-lg font-bold text-gray-800 outline-none"
                            name={`number-total-taxa-${grupo.toLowerCase().replace(/\s+/g, '-')}`}
                            id={`input-number-total-taxa-${grupo.toLowerCase().replace(/\s+/g, '-')}`}
                            thousandSeparator="."
                            decimalSeparator=","
                            prefix="R$ "
                            fixedDecimalScale
                            decimalScale={2}
                            allowNegative={false}
                            required
                            value={lista
                              .reduce(
                                (acc, encargo) => acc + (encargo.percentual / 100) * salarioBruto,
                                0
                              )
                              .toFixed(2)}
                            readOnly
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
            {total && Object.keys(total).length === 2 && (
              <div className="mb-5 grid h-[60%] w-full grid-flow-row grid-cols-4 gap-y-5">
                <div className="col-span-2">
                  <h2 className="rounded-l-md border border-purple-500 bg-purple-300 p-2 text-lg font-bold text-gray-800">
                    Total de Encargos Trabalistas
                  </h2>
                </div>
                <div className="border border-purple-500 bg-purple-300">
                  <h2 className="p-2 text-center text-lg font-bold text-gray-800">
                    {Object.values(total)
                      .reduce((acc, grupo: any) => acc + grupo.percentual, 0)
                      .toFixed(2)
                      .replace('.', ',')}
                    %
                  </h2>
                </div>
                <div className="flex justify-center rounded-r-md border border-purple-500 bg-purple-300">
                  <NumericFormat
                    className="justify-center p-2 text-center text-lg font-bold text-gray-800"
                    name="number-total-encargos-trabalhistas"
                    id="input-number-total-encargos-trabalhistas"
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                    fixedDecimalScale
                    decimalScale={2}
                    allowNegative={false}
                    required
                    value={Object.values(total)
                      .reduce((acc, grupo: any) => acc + grupo.valor, 0)
                      .toFixed(2)}
                    readOnly
                  />
                </div>
                <div className="col-span-3">
                  <h2 className="rounded-l-md border border-purple-500 bg-purple-300 p-2 text-lg font-bold text-gray-800">
                    Total Salário Bruto + Encargos
                  </h2>
                </div>
                <div className="flex justify-center rounded-r-md border border-purple-500 bg-purple-300">
                  <NumericFormat
                    className="p-2 text-center text-lg font-bold text-gray-800 outline-none"
                    name="number-total-salario-bruto-encargos"
                    id="input-number-total-salario-bruto-encargos"
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                    fixedDecimalScale
                    decimalScale={2}
                    allowNegative={false}
                    required
                    value={(
                      salarioBruto +
                      Object.values(total).reduce((acc, grupo: any) => acc + grupo.valor, 0)
                    ).toFixed(2)}
                    readOnly
                  />
                </div>
              </div>
            )}
            <div className="grid h-full w-full grid-cols-8">
              {beneficios && salario > 0 && (
                <Fragment>
                  <div className="col-span-4">
                    <h2 className="rounded-tl-md border border-purple-300 bg-purple-100 p-2 text-lg font-bold text-gray-800">
                      Benefícios & Outros Custos Diretos
                      <div className="group relative inline-block">
                        <i className="bi bi-info-circle-fill ml-3 cursor-pointer text-purple-700 hover:text-gray-400"></i>
                        <p className="text-info absolute bottom-full mb-2 hidden max-h-[110px] min-w-[500px] rounded-lg bg-gray-800 px-3 py-1 text-sm text-white shadow-lg group-hover:block">
                          Os valores dos benefícios neste painel são calculados com base em
                          periodicidades mensal e diária. Benefícios mensais refletem o custo total
                          para o período de um mês. Benefícios diários são calculados por dia de
                          uso, multiplicados por 22 dias úteis, conforme as quantidades e valores
                          unitários informados.
                        </p>
                      </div>
                    </h2>
                  </div>
                  <div className="border border-purple-300 bg-purple-100">
                    <h2 className="p-2 text-center text-lg font-bold text-gray-800">Quantidade</h2>
                  </div>
                  <div className="border border-purple-300 bg-purple-100">
                    <h2 className="p-2 text-center text-lg font-bold text-gray-800">
                      Valor Unitário
                    </h2>
                  </div>
                  <div className="border border-purple-300 bg-purple-100">
                    <h2 className="p-2 text-center text-lg font-bold text-gray-800">Fornecido</h2>
                  </div>
                  <div className="rounded-tr-md border border-purple-300 bg-purple-100">
                    <h2 className="p-2 text-center text-lg font-bold text-gray-800">Repasse</h2>
                  </div>
                </Fragment>
              )}
              {beneficios &&
                salario > 0 &&
                Object.entries(beneficios).map(([key, b]: [string, any]) => (
                  <div
                    key={key}
                    className={`col-span-6 grid grid-cols-subgrid gap-4 ${
                      checkBoxStatus[key] ? 'bg-white' : 'bg-gray-100'
                    }`}
                    style={{ display: 'contents' }}
                  >
                    <div className="relative col-span-4 flex items-center gap-5 border border-gray-300 bg-inherit p-2 text-center text-gray-800">
                      <input
                        type="checkbox"
                        id={`input-checkbox-beneficio-${b.id}`}
                        name={`checkbox-beneficio-${b.id}`}
                        className="h-5 w-5 cursor-pointer outline-gray-200"
                        checked={checkBoxStatus[key] || false}
                        onChange={() => onCheckBoxStatus(key)}
                      />
                      <h2 className={checkBoxStatus[key] ? 'text-gray-800' : 'text-gray-400'}>
                        {b.nome}
                      </h2>
                      {checkBoxStatus[key] && (
                        <h3
                          className={`text-md absolute right-2 rounded-full px-2 ${b.frequencia === 'Mensal' ? 'bg-purple-300' : 'bg-pink-300'}`}
                        >
                          {b.frequencia}
                        </h3>
                      )}
                    </div>
                    <div className="border border-gray-300 bg-inherit p-2 text-gray-800">
                      <input
                        type="number"
                        name={`number-quantidade-beneficio-${b.id}`}
                        min={0}
                        className="h-full w-full text-center outline-gray-200"
                        value={checkBoxStatus[key] ? beneficiosCalculos[key]?.quantidade || '' : ''}
                        onChange={(e) => {
                          onChargeValoresBeneficios(key, 'quantidade', Number(e.target.value))
                        }}
                        disabled={!checkBoxStatus[key]}
                      />
                    </div>
                    <div className="relative border border-gray-300 bg-inherit p-2 text-gray-800">
                      <NumericFormat
                        className="max-w-[98%] text-center outline-gray-200"
                        name={`number-valor-unitario-beneficio-${b.id}`}
                        id={`input-number-valor-unitario-beneficio-${b.id}`}
                        thousandSeparator="."
                        decimalSeparator=","
                        prefix="R$ "
                        fixedDecimalScale
                        decimalScale={2}
                        allowNegative={false}
                        value={
                          checkBoxStatus[key] ? beneficiosCalculos[key]?.valor_unitario || '' : ''
                        }
                        onValueChange={(values) => {
                          if (values.floatValue !== undefined) {
                            onChargeValoresBeneficios(
                              key,
                              'valor_unitario',
                              Number(values.floatValue)
                            )
                          }
                          console.log('Input Valor Unitario:', values)
                        }}
                        disabled={!checkBoxStatus[key]}
                      />
                    </div>
                    <div className="border border-gray-300 bg-inherit p-2 text-gray-800">
                      <NumericFormat
                        className="max-w-[98%] text-center outline-none"
                        name={`number-fornecido-beneficio-${b.id}`}
                        id={`input-number-fornecido-beneficio-${b.id}`}
                        thousandSeparator="."
                        decimalSeparator=","
                        prefix="R$ "
                        fixedDecimalScale
                        decimalScale={2}
                        allowNegative={false}
                        value={checkBoxStatus[key] ? beneficiosCalculos[key]?.fornecido || '' : ''}
                        readOnly
                      />
                    </div>
                    <div className="border border-gray-300 bg-inherit p-2 text-gray-800">
                      <NumericFormat
                        className="max-w-[98%] text-center outline-none"
                        name={`number-repasse-beneficio-${b.id}`}
                        id={`input-number-repasse-beneficio-${b.id}`}
                        thousandSeparator="."
                        decimalSeparator=","
                        prefix="R$ "
                        fixedDecimalScale
                        decimalScale={2}
                        allowNegative={false}
                        value={checkBoxStatus[key] ? beneficiosCalculos[key]?.repasse || 0 : ''}
                        readOnly
                      />
                    </div>
                  </div>
                ))}
              <div className="col-span-6 rounded-bl-md border border-purple-300 bg-purple-100">
                <h2 className="p-2 text-lg font-bold text-gray-800">Total Benefícios</h2>
              </div>
              <div className="border border-purple-300 bg-purple-100">
                <NumericFormat
                  className="max-w-[98%] p-2 text-center text-lg font-bold text-gray-800 outline-gray-200"
                  name="number-total-fornecido-beneficios"
                  id="input-number-total-fornecido-beneficios"
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  fixedDecimalScale
                  decimalScale={2}
                  allowNegative={false}
                  value={totaisBeneficios.fornecido || 0}
                  disabled={true}
                />
              </div>
              <div className="rounded-br-md border border-purple-300 bg-purple-100">
                <NumericFormat
                  className="max-w-[98%] p-2 text-center text-lg font-bold text-gray-800 outline-gray-200"
                  name="number-total-repasse-beneficios"
                  id="input-number-total-repasse-beneficios"
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  fixedDecimalScale
                  decimalScale={2}
                  allowNegative={false}
                  value={totaisBeneficios.repasse || 0}
                  disabled={true}
                />
              </div>
              <div className="col-span-6 mt-5 rounded-tl-md border border-purple-300 bg-purple-100">
                <h2 className="p-2 text-lg font-bold text-gray-800">Exames Clínicos - ASO</h2>
              </div>
              <div className="col-span-2 mt-5 rounded-tr-md border border-purple-300 bg-purple-100">
                <h2 className="p-2 text-center text-lg font-bold text-gray-800">R$</h2>
              </div>
              <div
                className={`col-span-6 flex h-10.5 items-center gap-5 rounded-bl-md border border-gray-300 p-2 text-gray-800 ${checkBoxExame ? 'bg-white' : 'bg-gray-100'}`}
              >
                <input
                  className={`h-5 w-5 cursor-pointer outline-gray-200`}
                  type="checkbox"
                  name="checkbox-exames-clinicos-aso"
                  id="input-checkbox-exames-clinicos-aso"
                  checked={checkBoxExame}
                  onChange={() => setCheckBoxExame(!checkBoxExame)}
                />
                <h3 className={`p-2 ${checkBoxExame ? 'text-gray-800' : 'text-gray-400'}`}>
                  Exames médicos - ASO
                </h3>
              </div>
              <div
                className={`${checkBoxExame ? 'bg-white' : 'bg-gray-100'} col-span-2 flex h-10.5 items-center justify-center rounded-br-md border border-gray-300 p-2 text-gray-800`}
              >
                {checkBoxExame && (
                  <NumericFormat
                    id="input-number-exames-clinicos-aso"
                    name="number-exames-clinicos-aso"
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                    fixedDecimalScale
                    decimalScale={2}
                    allowNegative={false}
                    value={62.35}
                    className="justify-center p-2 text-center text-gray-800 outline-none"
                    readOnly
                  />
                )}
              </div>
              <div className="col-span-8 mt-5 grid h-14 w-full grid-cols-subgrid items-center justify-center rounded-md border border-purple-500 bg-purple-300">
                <h2 className="col-span-6 p-2 text-lg font-bold text-gray-800">
                  Subtotal Nota Fiscal de Serviço
                </h2>
                <NumericFormat
                  className="right-0 col-span-2 text-center text-lg font-bold text-gray-800 outline-none"
                  name="number-subtotal-nota-fiscal"
                  id="input-number-subtotal-nota-fiscal"
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  fixedDecimalScale
                  decimalScale={2}
                  allowNegative={false}
                  required
                  value={subtotalNotaFiscal}
                  readOnly
                />
              </div>
              <AnimatePresence>
                {simular && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 1, ease: 'easeInOut' }}
                    className="col-span-8 grid grid-cols-subgrid overflow-hidden"
                  >
                    <div className="col-span-4 mt-5 rounded-tl-md border border-purple-300 bg-purple-100">
                      <h2 className="p-2 text-lg font-bold text-gray-800">Encargos Tributários</h2>
                    </div>
                    <div className="col-span-2 mt-5 border border-purple-300 bg-purple-100">
                      <h2 className="p-2 text-center text-lg font-bold text-gray-800">%</h2>
                    </div>
                    <div className="col-span-2 mt-5 rounded-tr-md border border-purple-300 bg-purple-100">
                      <h2 className="p-2 text-center text-lg font-bold text-gray-800">R$</h2>
                    </div>
                    <div className="col-span-4 flex h-10.5 items-center justify-between border border-gray-300 bg-inherit p-2 text-gray-800">
                      <h3 className="p-2 text-gray-800">ISS</h3>
                    </div>
                    <div className="col-span-2 flex h-10.5 items-center justify-center border border-gray-300 p-2 text-gray-800">
                      <h3 className="p-2 text-gray-800">{municipioISS?.ISS?.replace('.', ',')}%</h3>
                    </div>
                    <div className="col-span-2 flex h-10.5 items-center justify-center border border-gray-300 bg-inherit p-2 text-center text-gray-800">
                      <NumericFormat
                        className="flex justify-center p-2 text-center text-gray-800"
                        value={(municipioISS.ISS / 100) * salario}
                        displayType="text"
                        thousandSeparator="."
                        decimalSeparator=","
                        prefix="R$ "
                        fixedDecimalScale
                        decimalScale={2}
                        allowNegative={false}
                      />
                    </div>
                    {Object.entries(Tributos).map(([nome, percentual]: [string, number]) => (
                      <Fragment key={nome}>
                        <div className="col-span-4 flex h-10.5 items-center border border-gray-300 bg-inherit p-2 text-gray-800">
                          <h3 className="p-2 text-gray-800">{nome}</h3>
                        </div>
                        <div className="col-span-2 flex h-10.5 items-center justify-center border border-gray-300 p-2 text-gray-800">
                          <h3 className="p-2 text-gray-800">
                            {percentual.toFixed(2).replace('.', ',')}%
                          </h3>
                        </div>
                        <div className="col-span-2 flex h-10.5 items-center justify-center border border-gray-300 bg-inherit p-2 text-center text-gray-800">
                          <NumericFormat
                            className="flex justify-center p-2 text-center text-gray-800"
                            value={(percentual / 100) * valorTotalFinal}
                            displayType="text"
                            thousandSeparator="."
                            decimalSeparator=","
                            prefix="R$ "
                            fixedDecimalScale
                            decimalScale={2}
                            allowNegative={false}
                          />
                        </div>
                      </Fragment>
                    ))}
                    <div className="col-span-4 h-11 rounded-bl-md border border-purple-300 bg-purple-100">
                      <h2 className="p-2 text-lg font-bold text-gray-800">
                        Total Encargos Tributários
                      </h2>
                    </div>
                    <div className="col-span-2 h-11 border border-purple-300 bg-purple-100">
                      <h2 className="p-2 text-center text-lg font-bold text-gray-800">
                        {(
                          parseFloat(municipioISS.ISS) ||
                          0 + Object.values(Tributos).reduce((acc, curr) => acc + curr, 0)
                        )
                          .toFixed(2)
                          .replace('.', ',')}
                        %
                      </h2>
                    </div>
                    <div className="col-span-2 h-11 rounded-br-md border border-purple-300 bg-purple-100">
                      <NumericFormat
                        className="flex justify-center p-2 text-center text-lg font-bold text-gray-800"
                        value={Object.values(Tributos).reduce(
                          (acc, curr) => acc + (curr / 100) * valorTotalFinal,
                          0
                        )}
                        displayType="text"
                        thousandSeparator="."
                        decimalSeparator=","
                        prefix="R$ "
                        fixedDecimalScale
                        decimalScale={2}
                        allowNegative={false}
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div className="col-span-8 mt-5 grid h-14 w-full grid-cols-subgrid items-center justify-center rounded-md border border-purple-500 bg-purple-300">
                <h2 className="col-span-6 p-2 text-lg font-bold text-gray-800">
                  Projeção por Temporário Administrado
                </h2>
                {simular ? (
                  <NumericFormat
                    className="right-0 col-span-2 text-center text-lg font-bold text-gray-800 outline-none"
                    name="number-projecao-temporario-administrado"
                    id="input-number-projecao-temporario-administrado"
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                    fixedDecimalScale
                    decimalScale={2}
                    allowNegative={false}
                    required
                    value={simular ? valorTotalFinal : 0}
                    readOnly
                  />
                ) : (
                  <input
                    type="text"
                    value="-----------"
                    className="right-0 col-span-2 text-center text-lg font-bold text-gray-800 outline-none"
                  />
                )}
              </div>
              <div className="col-span-8 mt-5 grid h-14 w-full grid-cols-subgrid items-center justify-center rounded-md border border-purple-500 bg-purple-300">
                <h2 className="col-span-6 p-2 text-lg font-bold text-gray-800">
                  Projeção Total de Nota Fiscal de Serviço
                </h2>
                {simular ? (
                  <NumericFormat
                    className="right-0 col-span-2 text-center text-lg font-bold text-gray-800 outline-none"
                    name="number-projecao-total-nota-fiscal"
                    id="input-number-projecao-total-nota-fiscal"
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                    fixedDecimalScale
                    decimalScale={2}
                    allowNegative={false}
                    required
                    value={simular ? valorProjecaoTotalFinal : 0}
                    readOnly
                  />
                ) : (
                  <input
                    type="text"
                    value="-----------"
                    className="right-0 col-span-2 text-center text-lg font-bold text-gray-800 outline-none"
                  />
                )}
              </div>
              <div className="col-span-8 my-5 grid h-full w-full items-center justify-center gap-1 rounded-md border border-gray-200 bg-gray-50 p-2 text-sm text-gray-700 italic">
                <strong>Observação: </strong>
                <p>
                  Os custos com Adicional Noturno, Insalubridade, Periculosidade, Horas Extras, DSR,
                  Bônus e Prêmios são considerados como remuneração, tendo incidências de todos os
                  encargos sociais, previdenciários, tributários e Taxa administrativa. * De acordo
                  com o disposto no artigo 3º, inciso XX (item 17.05) , da Lei Complementar 116, as
                  notas fiscais - faturas da prestação de serviços serão emitidas ao tomador de
                  serviços (cliente) e o ISS deverá ser retido em favor do município da prestação de
                  serviços. O valor da exame médico admissional será cobrado apenas na primeira
                  fatura.
                </p>
                <p>
                  Esta é uma estimativa de custos sujeita a alterações. Todos os valores indicados
                  poderão sofrer ajustes após a contratação, levando em consideração a realidade e
                  especificidade de cada profissional.
                </p>
              </div>
            </div>
            <button
              type="button"
              className="mt-10 cursor-pointer rounded-md bg-purple-400 px-4 py-2 text-white hover:bg-purple-600"
              onClick={() => setSimular(!simular)}
            >
              Simular
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
