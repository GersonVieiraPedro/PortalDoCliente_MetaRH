export default async function RegistrarAdmissao(prevState: any, formData: FormData) {
  const entries = Array.from(formData.entries())
  const data = Object.fromEntries(entries)

  if (data.Cargo === 'ADICIONAR NOVO CARGO') {
    data['Cargo'] = data.NovoCargo
  }
  if (data.CentroCusto === 'ADICIONAR NOVO CENTRO') {
    data['CentroCusto'] = data.NovoCentro
  }

  const PrecisaEPI = data.PrecisaEPI == 'true'

  const CamposNessessarios = [
    'TipoVaga',
    'Cargo',
    'CentroCusto',
    'SetorTrabalho',
    'ModalidadeTrabalho',
    'MotivoContratacao',
    'EscalaTrabalho',
    'LocalTrabalho',
    'Salario',
    'DescricaoCargo',
    'NomeResponsavelRH',
    'EmailResponsavelRH',
    'TelefoneResponsavelRH',
    'NomeGestorPonto',
    'EmailGestorPonto',
    'TelefoneGestorPonto',
    'NomePessoaPrimeiroDia',
    'DepartamentoPrimeiroDia',
    'HorarioPrimeiroDia',
  ]

  const CamposSubstituicao = ['NomeSubstituido', 'CPFSubstituido', 'MotivoSubstituido']

  for (const campo of CamposNessessarios) {
    if (!data[campo]) {
      return { status: 'Erro', mensagem: `Campo obrigatório: ${campo}` }
    }
  }

  if (data.MotivoContratacao === 'SUBSTITUIÇÃO') {
    for (const campo of CamposSubstituicao) {
      if (!data[campo]) {
        return {
          status: 'Erro',
          mensagem: `Você precisa passar os dados da pessoa substituída. Campo obrigatório: ${campo}`,
        }
      }
    }
  }

  if (PrecisaEPI && (data.DescricaoEPI === '' || !data.DescricaoEPI)) {
    return {
      status: 'Erro',
      mensagem: 'Você precisa descrever quais EPIs são necessários!',
    }
  }

  const emailString = typeof data.Email === 'string' ? data.Email : ''
  const url = `http://127.0.0.1:8000/requisicoes/Admissao/Cadastro?Email=${encodeURIComponent(
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
        TipoVaga: data.TipoVaga,
        Cargo: data.Cargo,
        CentroCusto: data.CentroCusto,
        SetorTrabalho: data.SetorTrabalho,
        ModalidadeTrabalho: data.ModalidadeTrabalho,
        MotivoContratacao: data.MotivoContratacao,
        EscalaTrabalho: data.EscalaTrabalho,
        LocalTrabalho: data.LocalTrabalho,
        Salario: data.Salario,
        DescricaoCargo: data.DescricaoCargo,
        PrecisaEPI: PrecisaEPI,
        DescricaoEPI: data.DescricaoEPI || ' ',
        NomeSubstituido: data.NomeSubstituido || ' ',
        CPFSubstituido: data.CPFSubstituido || ' ',
        MotivoSubstituido: data.MotivoSubstituido || ' ',
        NomeResponsavelRH: data.NomeResponsavelRH,
        EmailResponsavelRH: data.EmailResponsavelRH,
        TelefoneResponsavelRH: data.TelefoneResponsavelRH,
        NomeGestorPonto: data.NomeGestorPonto,
        EmailGestorPonto: data.EmailGestorPonto,
        TelefoneGestorPonto: data.TelefoneGestorPonto,
        NomePessoaPrimeiroDia: data.NomePessoaPrimeiroDia,
        DepartamentoPrimeiroDia: data.DepartamentoPrimeiroDia,
        HorarioPrimeiroDia: data.HorarioPrimeiroDia,
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
