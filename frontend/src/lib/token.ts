export function getToken(): string {
  const cookies = document.cookie.split("; ");
  for (const cookie of cookies) {
    const [chave, valor] = cookie.split("=");
    if (chave === "token") return decodeURIComponent(valor);
  }
  return "";
}
