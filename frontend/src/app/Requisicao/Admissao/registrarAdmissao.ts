

export default async function RegistrarAdmissao(
    prevState: any,
    formData: FormData
) {
    const entries = Array.from(formData.entries());

    const data = Object.fromEntries(entries);

    console.log(data)
    
}