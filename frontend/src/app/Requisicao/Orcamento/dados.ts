'use server'

export async function getISS() {
  let url = `http://127.0.0.1:8000/simulacoes/iss`
  //console.log(url)
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Network response was not ok')
  }

  const data = await response.json()
  return data
}

export const getContratosAtivos = async (CodigoCliente: number[]) => {
  let url = `http://127.0.0.1:8000/simulacoes/contratos-ativos`
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(CodigoCliente),
  })

  if (!response.ok) {
    throw new Error('Network response was not ok')
  }

  const data = await response.json()
  return data
}
