import { jwtDecode } from 'jwt-decode'

interface JwtPayload {
  sub: string
  email: string
  exp: number
  nome: string
}

export function VerificarTipoAcesso(token: string): string | null {
  try {
    const decoded = jwtDecode<JwtPayload>(token)
    return decoded.sub || null
  } catch (error) {
    console.error('Token inválido:', error)
    return null
  }
}

export function VerificarEmail(token: string): string | null {
  try {
    const decoded = jwtDecode<JwtPayload>(token)
    return decoded.email || null
  } catch (error) {
    console.error('Token inválido:', error)
    return null
  }
}

export function VerificarNome(token: string): string | null {
  try {
    const decoded = jwtDecode<JwtPayload>(token)
    return decoded.nome || null
  } catch (error) {
    console.error('Token inválido:', error)
    return null
  }
}
