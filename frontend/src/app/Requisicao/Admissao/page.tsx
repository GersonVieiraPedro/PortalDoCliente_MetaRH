export default function Admissao() {
  return (
    <div className="bg-gray-200 ml-15 mt-15 max-w-dvw h-auto p-5">
      <div className="bg-white h-full max-w-dvw rounded-md border border-gray-300 ">
        <h1 className="text-2xl text-gray-800 text-center justify-center p-2 font-bold">
          Requisição de Admissão
        </h1>
        <hr />
        <h2 className="p-5 text-gray-800">Datalhes da posição</h2>
        <div className="grid grid-cols-3 gap-5 p-5 text-gray-500">
          <div className=" justify-start grid grid-cols-1 items-center">
            <label htmlFor="TipoVaga" className="text-gray-800 font-medium">
              Tipo de Vaga
            </label>

            <select
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="TipoVaga"
              id="1"
            >
              <option value=" "></option>
              <option value="Temporario">Temporário</option>
              <option value="Terceiro">Terceiro</option>
              <option value="Estagiario">Estagiário</option>
              <option value="Efetivo">Efetivo</option>

              <option value="Aprendiz">Aprendiz</option>
              <option value="Outros">Outros</option>
            </select>
          </div>
          <div className=" justify-start grid grid-cols-1 items-center">
            <label htmlFor="TipoVaga" className="text-gray-800 font-medium">
              Cargo
            </label>

            <select
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="Cargo"
              id="2"
            >
              <option value=" "></option>
              <option value="ANALISTA BI JUNIOR">ANALISTA BI JUNIOR</option>
              <option value="ANALISTA BI PLENO">ANALISTA BI PLENO</option>
              <option value="ANALISTA BI SENIOR">ANALISTA BI SENIOR</option>
              <option value="ANALISTA DE DADOS JUNIOR">
                ANALISTA DE DADOS JUNIOR
              </option>
            </select>
          </div>
          <div className=" justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Centro de Custo</label>

            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="CentroDeCusto"
              id="3"
            ></input>
          </div>
          <div className=" justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Setor de Trabalho
            </label>

            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="SretorDeTrabalho"
              id="4"
            ></input>
          </div>
          <div className=" justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Modalidade de Trabalho
            </label>

            <select
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="ModalidadeDeTrabalho"
              id="5"
            >
              <option value=" "></option>
              <option value="HOME OFFICE">HOME OFFICE</option>
              <option value="HÍBRIDO">HÍBRIDO</option>
              <option value="PRESENCIAL">PRESENCIAL</option>
              <option value="OUTROS">OUTROS</option>
            </select>
          </div>
          <div className=" justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Motivo de Contratação
            </label>

            <select
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="ModalidadeDeTrabalho"
              id="6"
            >
              <option value=" "></option>
              <option value="EXPANÇÂO">EXPANÇÂO</option>
              <option value="SUBSTITUIÇÃO">SUBSTITUIÇÃO</option>
              <option value="NOVO PROJETO">NOVO PROJETO</option>
              <option value="OUTROS">OUTROS</option>
            </select>
          </div>
          <div className=" justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Escala de Trabalho
            </label>

            <select
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name=""
              id="7"
            >
              <option value=" "></option>
              <option value="Escala 2x2">Escala 2x2</option>
              <option value="Escala 4x2">Escala 4x2</option>
              <option value="Escala 4×4">Escala 4×4</option>
              <option value="Escala 5×1">Escala 5×1</option>
              <option value="Escala 5×2">Escala 5×2</option>
              <option value="Escala 6×1">Escala 6×1</option>
              <option value="Escala 6×2">Escala 6×2</option>
              <option value="Escala 12×36">Escala 12×36</option>
              <option value="Escala 12×60">Escala 12×60</option>
              <option value="Escala 12×72">Escala 12×72</option>
              <option value="Escala 24×48">Escala 24×48</option>
              <option value="Escala 24×72">Escala 24×72</option>
              <option value="Escala 40×48">Escala 40×48</option>
            </select>
          </div>
          {/* Local de Trabalho */}
          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Local de Trabalho
            </label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="LocalDeTrabalho"
              id="8"
            />
          </div>

          {/* Salário */}
          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Salário</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="Salario"
              id="9"
            />
          </div>

          {/* Descrição do Cargo */}
          <div className="col-span-3 justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Descrição do Cargo
            </label>
            <textarea
              className="p-1 border border-gray-200 rounded-md cursor-pointer min-h-[100px]"
              name="DescricaoCargo"
              id="10"
            ></textarea>
          </div>

          {/* Nome */}
          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Nome</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="Nome"
              id="11"
            />
          </div>

          {/* CPF */}
          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">CPF</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="CPF"
              id="12"
            />
          </div>

          {/* Motivo da Substituição */}
          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">
              Motivo da Substituição
            </label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="MotivoSubstituicao"
              id="13"
            />
          </div>

          {/* Checkbox - EPI, Uniforme e Crachá */}
          <div className="col-span-3 justify-start grid grid-cols-1 items-center">
            <div className="flex gap-2 ">
              <input
                type="checkbox"
                className="cursor-pointer "
                name="EpiUniformeCracha"
                id="14"
              />
              <label className="text-gray-800 font-medium">
                EPI, Uniforme e Crachá (somente se for aplicado para esta
                contratação)
              </label>
            </div>

            <textarea
              className="p-1 border border-gray-200 rounded-md cursor-pointer min-h-[100px]"
              name="DescricaoCargo"
              id="10"
            ></textarea>
          </div>

          {/* RH Responsável */}
          <div className="col-span-3">
            <h2 className="text-gray-800 font-bold mt-5 mb-2">
              RH Responsável
            </h2>
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Nome</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="NomeRH"
              id="15"
            />
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">E-mail</label>
            <input
              type="email"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="EmailRH"
              id="16"
            />
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Telefone</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="TelefoneRH"
              id="17"
            />
          </div>

          {/* Gestor para Validação do Ponto */}
          <div className="col-span-3">
            <h2 className="text-gray-800 font-bold mt-5 mb-2">
              Gestor para Validação do Ponto
            </h2>
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Nome</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="NomeGestor"
              id="18"
            />
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">E-mail</label>
            <input
              type="email"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="EmailGestor"
              id="19"
            />
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Telefone</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="TelefoneGestor"
              id="20"
            />
          </div>
          <hr className="col-span-3 mt-5 text-gray-200" />
          {/* No Primeiro Dia Procurar Por Quem */}
          <div className="col-span-3">
            <h2 className="text-gray-800 font-bold mt-5 mb-2">
              No Primeiro Dia Deverá Procurar Por Quem?
            </h2>
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Nome</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="NomePrimeiroDia"
              id="21"
            />
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Departamento</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="DepartamentoPrimeiroDia"
              id="22"
            />
          </div>

          <div className="justify-start grid grid-cols-1 items-center">
            <label className="text-gray-800 font-medium">Horário</label>
            <input
              type="text"
              className="p-1 border border-gray-200 rounded-md cursor-pointer"
              name="HorarioPrimeiroDia"
              id="23"
            />
          </div>
        </div>

        {/* Botão Final */}
        <div className="flex justify-center mt-8 mb-4 p-5">
          <button className="bg-gray-500 w-2xl text-white px-6 py-2 rounded-md hover:bg-gray-600 transition cursor-pointer">
            Enviar Requisição
          </button>
        </div>
      </div>
    </div>
  );
}
