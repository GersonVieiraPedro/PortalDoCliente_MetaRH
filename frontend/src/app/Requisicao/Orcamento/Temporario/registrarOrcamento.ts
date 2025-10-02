export default async function RegistrarOcamento(prevState: any, formData: FormData) {
  const entries = Array.from(formData.entries())
  const objeto = Object.fromEntries(entries)

  return objeto
}
