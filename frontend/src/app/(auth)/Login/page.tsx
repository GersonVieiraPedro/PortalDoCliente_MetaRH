import Form from 'next/form'
import Link from 'next/link'
import FormLogin from './formLogin'

export default function Login() {
  return (
    <div className="grid h-full w-full grid-cols-3 text-gray-800">
      <div className="grid h-screen grid-rows-3 items-center justify-center border-2 border-gray-300 bg-white pt-15">
        <div className="mb-6 grid content-center items-center justify-center gap-2">
          <img
            className="ml-8 h-24 w-24 rounded-full bg-purple-400 p-2"
            src="/LogoMetaRH.png"
            alt=""
          />
          <h2 className="text-center text-2xl font-medium">Portal MetaRH</h2>
        </div>
        <FormLogin />

        <div className="bg-lime-100"></div>
      </div>
      <div className="bg-gradiante col-span-2 flex h-full w-full justify-end">
        <img className="h-full object-contain" src="/Fundo_Login.jpg" alt="" />
      </div>
    </div>
  )
}
