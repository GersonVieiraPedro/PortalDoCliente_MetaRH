import Form from "next/form";
import Link from "next/link";
import FormLogin from "./formLogin";

export default function Login() {
  return (
    <div className="h-full w-full grid grid-cols-3 text-gray-800">
      <div className="grid h-screen bg-white justify-center items-center grid-rows-3 pt-15 border-2 border-gray-300 ">
        <div className="grid justify-center content-center items-center gap-2 mb-6">
          <img
            className="ml-8 h-24 w-24 bg-purple-400 p-2 rounded-full "
            src="/LogoMetaRH.png"
            alt=""
          />
          <h2 className="text-2xl font-medium text-center">Portal MetaRH</h2>
        </div>
        <FormLogin />

        <div className="bg-lime-100"></div>
      </div>
      <div className="h-full w-full  bg-gradiante  col-span-2 flex justify-end ">
        <img className="h-full object-contain " src="/Fundo_Login.jpg" alt="" />
      </div>
    </div>
  );
}
