import Form from 'next/form'
import Link from 'next/link'
import resgistrarUsuario from './registrarUsuario'
import FormRegistrar from './formRegistrar'

export default function Registrar() {
  return (
    <div className="grid h-full w-full grid-cols-3 text-gray-800">
      <div className="col-start-2 grid h-screen grid-rows-3 items-center justify-center bg-white pt-15">
        <div className="mb-6 grid content-center items-center justify-center gap-2">
          <img
            className="ml-8 h-24 w-24 rounded-full bg-purple-400 p-2"
            src="/LogoMetaRH.png"
            alt=""
          />
          <h2 className="text-center text-2xl font-medium">Portal MetaRH</h2>
        </div>
        <FormRegistrar />

        <div className=""></div>
      </div>
    </div>
  )
}
