'use client'
import { useEffect, useState } from 'react'
import encargos from './encargos.json'

import Link from 'next/link'

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
    <div className="relative h-screen w-screen overflow-hidden bg-gray-200 text-gray-800">
      <div className="absolute m-5 mt-20 ml-20 h-[85dvh] rounded-md border border-gray-300 bg-white">
        <h1 className="justify-center p-2 text-center text-2xl font-bold text-gray-800">
          Selecione o tipo de contratação
        </h1>
        <hr className="text-gray-300" />
        <div className="flex h-full w-full flex-col p-5">
          <div className="mt-10 flex h-full w-full justify-center gap-[10%] p-2">
            <div
              className={
                (tipoContratacao === 'Temporário' ? 'scale-105 bg-purple-200 ' : 'bg-gray-100 ') +
                'flex max-h-[85%] min-h-[350px] w-[20%] cursor-pointer flex-col rounded-md caret-transparent shadow-md hover:scale-105'
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
              <Link href="/Requisicao/Orcamento/Temporario">
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
              </Link>
            </div>
            <div
              className={
                (tipoContratacao === 'Terceirizado' ? 'scale-105 bg-purple-200 ' : 'bg-gray-100 ') +
                'flex max-h-[85%] min-h-[350px] w-[20%] cursor-pointer flex-col rounded-md caret-transparent shadow-md hover:scale-105'
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
              <Link href="/Requisicao/Orcamento/Terceirizado">
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
              </Link>
            </div>
            <div
              className={
                (tipoContratacao === 'Recrutamento & Seleção'
                  ? 'scale-105 bg-purple-200 '
                  : 'bg-gray-100 ') +
                'flex max-h-[85%] min-h-[350px] w-[20%] cursor-pointer flex-col rounded-md caret-transparent shadow-md hover:scale-105'
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
                  Processo seletivo especializado para encontrar talentos alinhados ao perfil da sua
                  vaga, reduzindo tempo de contratação e aumentando a assertividade na escolha.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
