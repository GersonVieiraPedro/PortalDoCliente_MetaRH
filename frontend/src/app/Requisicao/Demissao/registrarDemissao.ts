export default async function RegistrarDemissao(prevState: any, formData: FormData) {
  const entries = Array.from(formData.entries())
  const data = Object.fromEntries(entries)
  console.log('Dados do formulário:', data)
  const CamposNessessarios = [
    'CodigoFuncionario',
    'NomeFuncionario',
    'Cargo',
    'CentroCusto',
    'Empresa',
    'Gestor',
    'Salario',
    'DataAdmissao',
    'DataDemissao',
    'MotivoDemissao',
    'FeriasVencidas',
    'AvisoPrevio',
    'ConhecimentoDesligamento',
    'ComunicadoPresencial',
    'Endereco',
    'Horario',
  ]
  console.log('Dados do formulário:', data)

  for (const campo of CamposNessessarios) {
    if (!data[campo]) {
      return { status: 'Erro', mensagem: `Campo obrigatório: ${campo}` }
    }
  }

  const emailString = typeof data.Email === 'string' ? data.Email : ''
  const url = `http://127.0.0.1:8000/requisicoes/Demissao/Cadastro?Email=${encodeURIComponent(
    emailString
  )}`

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...data,
      }),
    })

    // console.log("Status HTTP:", response.status);

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Erro HTTP ${response.status}: ${errorText}`)
    }

    const res = await response.json()
    //console.log("Resposta da API:", res);
    return res
  } catch (error: any) {
    console.error('Erro na requisição fetch:', error)
    return {
      status: 'Erro',
      mensagem: `Erro na requisição: ${error.message}`,
    }
  }
}
