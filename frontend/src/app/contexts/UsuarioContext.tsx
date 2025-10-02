'use client'

import { ConsultarUsuario, ExisteImagem } from '@/src/components/Navegador/imagemUsuario'
import { getAuthToken } from '@/src/lib/cockies'
import { VerificarEmail, VerificarNome } from '@/src/lib/decode'
import { createContext, useContext, useState, useEffect, use } from 'react'
import { PropsWithChildren } from 'react'
import { MinhasEmpresas } from './MeusDados'

export const UsuarioContext = createContext<any>(null)

export function UseProvider({ children }: PropsWithChildren<{}>) {
  const [usuario, setUsuario] = useState<any>(null)
  const [token, setToken] = useState<string>('')
  const [dados, setDados] = useState<any>(null)

  useEffect(() => {
    const varToken = getAuthToken()
    if (varToken) {
      setToken(varToken)
      carregarUsuario(varToken)
    }
  }, [])

  const carregarUsuario = async (tokenParam?: string) => {
    const T = tokenParam || getAuthToken()
    if (!T) return

    const nome = await VerificarNome(T)
    const email = await VerificarEmail(T)
    let user = null

    if (email) {
      user = await ConsultarUsuario(T, email)
    }

    if (user) {
      const existe = await ExisteImagem(user.ID)
      const urlImagem = `https://storagecorpprod001.blob.core.windows.net/portal-web/fotos/usuarios/${user.ID}.png`

      setUsuario({
        ...user,
        nome,
        email,
        existeImagem: existe,
        urlImagem,
        token: T,
      })

      const pegarEmpresas = async () => {
        const dados = await MinhasEmpresas(email)

        const CNPJS = [
          ...new Set(
            dados?.map((d: { CNPJ: any }) => d.CNPJ).filter((cnpj: any) => cnpj != null) // remove null e undefined
          ),
        ]
        const CodigoCliente = [
          ...new Set(
            dados
              ?.map((d: { ['COD Contrato G.I']: any }) => d['COD Contrato G.I'])
              .filter((codigo: any) => codigo != null) // remove null e undefined
          ),
        ]
        if (CNPJS === usuario?.CNPJS || CodigoCliente === usuario?.CodigosCliente) return
        setUsuario((prev: any) => ({
          ...prev,
          CNPJS,
          CodigosCliente: CodigoCliente,
        }))
      }
      pegarEmpresas()
    }
  }

  return (
    <UsuarioContext.Provider value={{ usuario, setUsuario, carregarUsuario }}>
      {children}
    </UsuarioContext.Provider>
  )
}

export const useUsuario = () => useContext(UsuarioContext)
