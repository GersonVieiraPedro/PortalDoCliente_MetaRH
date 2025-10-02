import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const Rotas_Publicas = ['/Login', '/Registrar']
const Chave_Token = 'token-portal-metarh'

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Permitir acesso aos assets estáticos e rotas públicas
  const extensoesLiberadas = ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.ico', '.gif']

  const isAsset =
    pathname.startsWith('/_next/') ||
    pathname === '/favicon.ico' ||
    pathname === '/robots.txt' ||
    extensoesLiberadas.some((ext) => pathname.endsWith(ext))

  if (isAsset || Rotas_Publicas.includes(pathname)) {
    return NextResponse.next()
  }
  const token = request.cookies.get(Chave_Token)?.value

  // se o token não existir, redirecionar para a página de login
  if (!token) {
    const loginUrl = request.nextUrl.clone()
    loginUrl.pathname = '/Login'
  }

  // Caso tenha token ou seja rota pública, permite continuar
  return NextResponse.next()
}

// Pegando todos os arquivos da pasta
export const config = {
  matcher: ['/:path*'],
}
