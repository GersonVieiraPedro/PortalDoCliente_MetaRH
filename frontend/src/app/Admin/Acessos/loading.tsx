"use client";

export default function Loading() {
  // Or a custom loading skeleton component
  return (
    <div className="absolute w-screen h-screen bg-red-600 z-50 flex justify-center items-center">
      <h1 className="text-2xl font-bold text-gray-700">Carregando....</h1>
    </div>
  );
}
