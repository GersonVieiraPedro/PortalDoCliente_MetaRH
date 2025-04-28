"use client";
import { useRouter } from "next/navigation";
import { MenuLateral } from "../components/MenuLateral";
import { Navegador } from "../components/Navegador";
import { use, useEffect, useState } from "react";
import { getToken } from "../lib/token";

export default function Home() {
  const router = useRouter();

  const [token, setToken] = useState<string>("");

  useEffect(() => {
    const token = getToken();

    setToken(token);

    //console.log("token :", token);
    if (!token) {
      router.push("/Login");
    }
  }, []);

  return (
    <div>
      <MenuLateral />
      <Navegador />
      <div className="h-screen w-full grid grid-cols-5 gap-5 text-gray-600 pt-20 pl-20 pr-5 pb-5">
        <div className="grid col-span-3 bg-white border border-gray-300 rounded-lg  overflow-y-auto content-start z-0">
          <div className="sticky top-0 h-15 w-full text-2xl font-medium border-b border-b-gray-200 p-2 bg-white items-center flex pl-5">
            <h2>Solicitações</h2>
          </div>
          <ul className="gap-2 grid pl-6 pr-1 List-border mt-2 w-full">
            <li className="flex justify-between">
              <div className="">
                <h2 className="font-medium text-lg pb-2">
                  Solicitação de Admissão
                </h2>
                <h5 className="text-xs pb-1">11/09 12:55</h5>
              </div>
              <div className="flex items-center gap-5">
                <div className=" px-2 py-1 bg-green-500 rounded-full">
                  <i className="bi bi-check text-white text-2xl"></i>
                </div>
                <button className="h-full px-4 p-2 hover:bg-gray-200 rounded-md cursor-pointer">
                  <i className="bi bi-trash-fill text-red-600"></i>
                </button>
              </div>
            </li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 1</li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 3</li>
            <li>Notificação 1</li>
            <li>Notificação 2</li>
            <li>Notificação 3</li>
          </ul>
        </div>
        <div className="grid col-span-2  grid-rows-3 gap-4 max-h-screen">
          <div className="h-50 w-full bg-white border border-gray-300 rounded-lg relative overflow-hidden">
            <img
              className="object-cover rounded-lg absolute z-0 "
              src="/RH-Estrategico-Gestao-negocio-Horizontal.jpg"
              alt=""
            />
            <button className="bi bi-images text-white font-bold absolute right-0 bg-cinza-transparente  py-2 px-5 cursor-pointer"></button>
          </div>
          <div className="h-full w-full bg-white border border-gray-300 rounded-lg"></div>
          <div className="h-full w-full bg-white border border-gray-300 rounded-lg"></div>
        </div>
      </div>
    </div>
  );
}
