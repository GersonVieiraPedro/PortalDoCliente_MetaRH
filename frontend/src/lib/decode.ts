import { jwtDecode } from "jwt-decode";

interface JwtPayload {
  sub: string;
  exp: number;
  nome: string;
}

export function VerificarTipoAcesso(token: string): string | null {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.sub || null;
  } catch (error) {
    console.error("Token inválido:", error);
    return null;
  }
}
