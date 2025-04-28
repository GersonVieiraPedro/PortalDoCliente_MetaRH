"use server";

export default async function Entrar(_prevState: any, formData: FormData) {
  const entries = Array.from(formData.entries());

  const data = Object.fromEntries(entries);

  if (!data.email || !data.senha) {
    throw new Error("Precisa preencher todos os campos");

    //Chamar um alerta
  } else {
    const res = await fetch("http://127.0.0.1:8000/usuarios/login", {
      method: "POST",
      body: JSON.stringify({
        email: data.email,
        senha: data.senha,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const dados = await res.json();

    if (res.ok) {
      return {
        status: "Sucesso",
        mensagem: "Login realizado com sucesso",
        token: dados.access_token,
      };
    } else {
      return {
        status: "Erro",
        mensagem: dados.detail?.mensagem || "Erro ao fazer login",
      };
    }
  }
}
