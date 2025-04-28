import Form from "next/form";
import Link from "next/link";
import resgistrarUsuario from "./registrarUsuario";
import FormRegistrar from "./formRegistrar";

export default function Registrar() {
  return (
    <div className="h-full w-full grid grid-cols-3 text-gray-800">
      <div className="grid h-screen bg-white justify-center items-center grid-rows-3 pt-15 col-start-2">
        <div className="grid justify-center content-center items-center gap-2 mb-6">
          <img
            className="ml-8 h-24 w-24 bg-purple-400 p-2 rounded-full "
            src="/LogoMetaRH.png"
            alt=""
          />
          <h2 className="text-2xl font-medium text-center">Portal MetaRH</h2>
        </div>
        <FormRegistrar />

        <div className=""></div>
      </div>
    </div>
  );
}
