"use server";

export async function MinhasEmpresas(Email: any) {
  let url = `http://127.0.0.1:8000/organizacao/empressas/?Email=${Email}`;
  //console.log(url)
  const response = await fetch(url, {
    method: "POST",
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  return data.tabela;
}

export async function MeusFuncionarios(CNPJ: any, CodigoCliente: any) {
  let url = "http://127.0.0.1:8000/organizacao/Funcionarios";

  const response = await fetch(url, {
    method: "POST",
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      CNPJ: CNPJ,
      CodigoCliente: CodigoCliente,
    }),
  });

  const data = await response.json();

  return data.tabela;
}
