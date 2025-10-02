'use client'

export default function Loading() {
  // Or a custom loading skeleton component
  return (
    <div className="absolute z-50 flex h-screen w-screen items-center justify-center bg-red-600">
      <h1 className="text-2xl font-bold text-gray-700">Carregando....</h1>
    </div>
  )
}
