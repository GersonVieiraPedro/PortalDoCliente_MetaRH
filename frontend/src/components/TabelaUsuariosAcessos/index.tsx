'use client'
import { useEffect, useRef, useState } from 'react'
import { ConsultarUsuarios, SalvarAlteracaoUsuarios } from '@/src/app/Admin/Acessos/tabelaUsuarios'
import { Alerta } from '@/src/components/Alerta'
import { format, set } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { table } from 'console'
import { get } from 'http'
import { getAuthToken } from '@/src/lib/cockies'
import { useUsuario } from '@/src/app/contexts/UsuarioContext'

interface Usuario {
  ID: number
  Nome: string
  Email: string
  CNPJ: string
  TipoAcesso: string
  PipedriveID: string
  CodigoCliente: string
  Status: boolean
  DataCadastro: string
  DataAtualizacao: string
}
interface AlertaSucesso {
  ID: number
  mensagem: string
  status: string
}

export function TabelaUsuariosAcessos() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [editados, setEditados] = useState<{ ID: number; [campo: string]: string | number }[]>([])
  const [editandoId, setEditandoId] = useState<number>() // ID do usuário sendo editado
  const [campoEditado, setCampoEditado] = useState<string>('') // Nome do campo que está sendo editado
  const [novoValor, setNovoValor] = useState<any>('') // Valor temporário para o campo editado
  const TipoFiltroRef = useRef<HTMLSelectElement>(null)
  const ValorFiltradoRef = useRef<HTMLInputElement>(null)
  const [mensagemAlerta, setMensagemAlerta] = useState<AlertaSucesso[]>([])
  const { usuario, setUsuario } = useUsuario()
  const [token, setToken] = useState<string>('')

  useEffect(() => {
    const token = usuario.token ? usuario.token : ''

    if (token !== '') {
      setToken(token)
    }
  }, [])

  const filtrarUsuarios = async (TipoFiltro: string, Filtro: string) => {
    const res = await ConsultarUsuarios(token, TipoFiltro, Filtro)
    setUsuarios(res)
  }

  const SalvarUsuarios = async (): Promise<any> => {
    const res = await SalvarAlteracaoUsuarios(token, editados)
    setEditados([])
    setMensagemAlerta(res)
  }

  // Função para salvar a alteração
  const EditarUsuarios = (ID: number, campo: string, valor: any) => {
    // Atualiza a lista principal
    const usuariosAtualizados = usuarios.map((usuario) =>
      usuario.ID === ID ? { ...usuario, [campo]: valor } : usuario
    )
    setUsuarios(usuariosAtualizados)

    // Atualiza a lista de alterados
    setEditados((prev) => {
      const index = prev.findIndex((item) => item.ID === ID)

      if (index !== -1) {
        // Já existe: atualiza o campo
        const usuariosEditados = {
          ...prev[index],
          [campo]: valor,
        }

        return [...prev.slice(0, index), usuariosEditados, ...prev.slice(index + 1)]
      } else {
        // Novo usuário na lista
        return [...prev, { ID, [campo]: valor }]
      }
    })
  }

  const EditarCampos = (ID: number, campo: string, valor: any) => {
    setEditandoId(ID)
    //console.log(`ID: ${ID} Campo: ${campo} valor: ${valor}`);
    setCampoEditado(campo)
    setNovoValor(valor)
  }

  useEffect(() => {
    if (editandoId) {
      EditarUsuarios(editandoId, campoEditado, novoValor)
      //console.log( ` EditarUsuarios = ID: ${editandoId} Campo: ${campoEditado} valor: ${novoValor}`);
    }
  }, [editandoId, campoEditado, novoValor])

  useEffect(() => {
    const buscarUsuarios = async () => {
      //const token = await getToken(); // agora é string
      // Verifica se o token está sendo definido corretamente
      if (token !== '') {
        //console.log("Token:", token);
        ConsultarUsuarios(token, null, null)
          .then(setUsuarios)
          .catch((err) => console.error('Erro ao buscar usuários:', err))
      }
    }

    buscarUsuarios()
  }, [token])
  return (
    <>
      {mensagemAlerta.length > 0 && (
        <Alerta
          titulo="Mensagem de Alerta"
          mensagem={
            <div className="grid h-full w-full items-center justify-center">
              <table>
                <thead>
                  <tr className="w-full bg-gray-200 p-2">
                    <th className="w-full p-2 px-20">ID</th>
                    <th className="w-full p-2 px-20">Mensagem</th>
                    <th className="w-full p-2 px-20">Status</th>
                  </tr>
                </thead>

                <tbody>
                  {mensagemAlerta.map((item, index) => (
                    <tr key={index} className="">
                      <th className="h-10 w-full text-sm">{item.ID}</th>
                      <th className="text-sm">{item.mensagem}</th>
                      <th
                        className={`text-sm ${
                          item.status == 'Sucesso'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {item.status}
                      </th>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          }
          tipo="Simples"
          botoes={null}
          visivel={true}
          setMensagemALerta={setMensagemAlerta}
        />
      )}
      <div className="relative grid h-full max-w-dvw content-start overflow-x-hidden overflow-y-auto rounded-md border border-gray-300 bg-white px-5 pb-10 text-left text-gray-800">
        <div className="mb-5 flex h-20 w-full grid-cols-3 items-center justify-center border-b border-gray-200">
          <div className="h-full w-full"></div>
          <div className="flex w-full items-center rounded-md border border-gray-100">
            <select
              className="h-10 w-17 cursor-pointer bg-gray-200 p-1 text-sm outline-0"
              name=""
              id="TipoFiltro"
              ref={TipoFiltroRef}
            >
              <option className="bg-white" value="Geral">
                Geral
              </option>
              <option className="bg-white" value="Nome">
                Nome
              </option>
              <option className="bg-white" value="Email">
                Email
              </option>
              <option className="bg-white" value="CNPJ">
                CNPJ
              </option>
              <option className="bg-white" value="Data">
                Data
              </option>
              <option className="bg-white" value="ID">
                ID
              </option>
            </select>
            <input
              className="h-10 w-full border border-gray-200 bg-white p-2 outline-gray-300"
              type="text"
              name=""
              id="ValorFiltro"
              placeholder="Pesquisar"
              ref={ValorFiltradoRef}
              onClick={() => {
                console.log(editados)
              }}
              onDoubleClick={() => {
                console.log(usuarios)
              }}
            />

            <button
              onClick={() => {
                const Tipo = TipoFiltroRef.current?.value || ''
                const Valor = ValorFiltradoRef.current?.value || ''
                filtrarUsuarios(Tipo, Valor)
              }}
              className="bi bi-search h-10 w-15 cursor-pointer bg-gray-200 hover:bg-gray-300"
            ></button>
          </div>
          <div className="flex h-full w-full items-center justify-end-safe gap-5">
            <button
              onClick={() => {
                SalvarUsuarios()
              }}
              className="flex h-10 cursor-pointer items-center gap-3 rounded-sm border-gray-100 bg-gray-200 p-5 text-gray-700 hover:bg-green-300"
            >
              <i
                className={`bi ${
                  editados.length
                    ? 'bi-circle-fill text-red-400'
                    : 'bi-check-circle-fill text-green-400'
                }`}
              ></i>
              Salvar
            </button>
          </div>
        </div>

        <table className="h-full w-full border border-gray-100 p-2">
          <thead className="sticky top-0 z-10 h-full w-full bg-white shadow">
            <tr className="relative z-10 h-10 bg-gray-200 p-2">
              <th className="h-10 w-10 p-2">Ativo</th>
              <th className="p-2">ID</th>
              <th className="p-2">Nome</th>
              <th className="p-2">E-mail</th>
              <th className="p-2">CNPJ</th>
              <th className="p-2">Tipo Acesso</th>
              <th className="p-2">PipedriveID</th>
              <th className="p-2">CodigoCliente</th>
              <th className="p-2">Data Cadastro</th>
            </tr>
          </thead>

          <tbody className="">
            {usuarios.map((usuarios, index) => (
              <tr key={index}>
                <td className="flex h-full justify-center border-0 p-2">
                  <input
                    key={usuarios.ID}
                    className="bi bi-check flex h-5 w-5 cursor-pointer appearance-none items-center justify-center rounded-sm border border-purple-200 text-white checked:border-purple-800 checked:bg-purple-500"
                    type="checkbox"
                    id=""
                    name={`${usuarios.ID}`}
                    defaultChecked={usuarios.Status}
                    onChange={(e) => {
                      const valorAtualizado = e.target.checked
                      EditarCampos(usuarios.ID, 'Status', valorAtualizado)
                    }}
                  />
                </td>
                <td className="p-2">{usuarios.ID}</td>
                <td className="p-2">{usuarios.Nome}</td>
                <td className="p-2">{usuarios.Email}</td>
                <td className="w-45 p-1">
                  <input
                    className="h-full w-full p-1 outline-gray-200"
                    type="text"
                    defaultValue={usuarios.CNPJ}
                    onChange={(e) => {
                      const valorAtualizado = e.target.value
                      EditarCampos(usuarios.ID, 'CNPJ', valorAtualizado)
                    }}
                  />
                </td>
                <td className="p-1">
                  {
                    <select
                      className="h-full w-full p-1 outline-gray-200"
                      name="TipoAcesso"
                      id="TipoAcesso"
                      onChange={(e) => {
                        const valorAtualizado = e.target.value
                        EditarCampos(usuarios.ID, 'TipoAcesso', valorAtualizado)
                      }}
                    >
                      <option value={usuarios.TipoAcesso}>{usuarios.TipoAcesso}</option>
                      <option value="Admin">Admin</option>
                      <option value="Cliente">Cliente</option>
                      <option value="Colaborador">Colaborador</option>
                    </select>
                  }
                </td>

                <td className="w-35 p-1">
                  <input
                    className="h-full w-full p-1 outline-gray-200"
                    type="text"
                    defaultValue={usuarios.PipedriveID}
                    onChange={(e) => {
                      const valorAtualizado = e.target.value
                      EditarCampos(usuarios.ID, 'PipedriveID', valorAtualizado)
                    }}
                  />
                </td>
                <td className="w-35 p-1">
                  <input
                    className="h-full w-full p-1 outline-gray-200"
                    type="text"
                    defaultValue={usuarios.CodigoCliente}
                    onChange={(e) => {
                      const valorAtualizado = e.target.value
                      EditarCampos(usuarios.ID, 'CodigoCliente', valorAtualizado)
                    }}
                  />
                </td>
                <td className="p-2">
                  {format(new Date(usuarios.DataCadastro), 'dd/MM/yy HH:mm', {
                    locale: ptBR,
                  })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
