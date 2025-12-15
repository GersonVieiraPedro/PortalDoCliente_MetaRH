# 📮 Guia de Importação - Postman

## 📦 Arquivos Disponíveis

- **`Postman_Collection_Notas_Fiscais.json`** - Collection completa com todos os endpoints
- **`Postman_Environment_Local.json`** - Environment configurado para ambiente local

---

## 🚀 Como Importar no Postman

### **Passo 1: Importar a Collection**

1. Abra o Postman
2. Clique no botão **"Import"** (canto superior esquerdo)
3. Clique em **"Upload Files"**
4. Selecione o arquivo: `Postman_Collection_Notas_Fiscais.json`
5. Clique em **"Import"**

✅ A collection "**MetaRH - Financeiro (Notas Fiscais)**" será criada

---

### **Passo 2: Importar o Environment**

1. No Postman, clique no ícone de **"Environments"** (canto superior direito, ícone de engrenagem)
2. Clique em **"Import"**
3. Selecione o arquivo: `Postman_Environment_Local.json`
4. Clique em **"Import"**

✅ O environment "**MetaRH - Local**" será criado

---

### **Passo 3: Configurar o Environment**

1. No Postman, selecione o environment **"MetaRH - Local"** no dropdown (canto superior direito)
2. Clique no ícone de "olho" ao lado do dropdown
3. Clique em **"Edit"** no environment selecionado
4. Configure as variáveis:

| Variável | Valor Inicial | Descrição |
|----------|---------------|-----------|
| `baseURL` | `http://localhost:8000` | URL base da API |
| `email` | `seu.email@exemplo.com` | ⚠️ **Substitua pelo seu email real** |
| `senha` | `sua_senha` | ⚠️ **Substitua pela sua senha real** |
| `codigo_cliente` | `123` | ⚠️ **Substitua pelo código de cliente real** |
| `token` | (vazio) | Será preenchido automaticamente após login |
| `token_type` | `Bearer` | Tipo do token JWT |

5. Clique em **"Save"**

---

## 🔐 Como Usar a Collection

### **1. Fazer Login (Obrigatório)**

Antes de testar os endpoints de Notas Fiscais, você precisa fazer login:

1. Na collection, expanda a pasta **"Auth"**
2. Clique em **"Login"**
3. Verifique o body da request e substitua email/senha se necessário:
   ```json
   {
     "email": "seu.email@exemplo.com",
     "senha": "sua_senha"
   }
   ```
4. Clique em **"Send"**
5. ✅ Se o login for bem-sucedido, o **token JWT** será salvo automaticamente na variável `{{token}}`

**Script Automático:** A request de login possui um script que salva o token automaticamente nas variáveis de ambiente!

---

### **2. Testar os Endpoints de Notas Fiscais**

Após fazer login, você pode testar qualquer endpoint da pasta **"Financeiro - Notas Fiscais"**:

#### **Endpoints Disponíveis:**

| Endpoint | Descrição |
|----------|-----------|
| **Listar Notas Fiscais (Todas)** | Lista todas as notas fiscais sem filtros |
| **Listar Notas Fiscais (Por Cliente)** | Filtra por código de cliente |
| **Listar Notas Fiscais (Por Competência)** | Filtra por competência (YYYYMM) |
| **Listar Notas Fiscais (A Vencer)** | Apenas notas a vencer |
| **Listar Notas Fiscais (Vencidas)** | Apenas notas vencidas |
| **Listar Notas Fiscais (Por Período)** | Filtra por período de datas |
| **Listar Notas Fiscais (Com Paginação)** | Exemplo com limit/offset |
| **Obter Resumo de Notas Fiscais** | Retorna apenas resumo (cards) |
| **Obter Resumo (Por Competência)** | Resumo filtrado por competência |

---

### **3. Personalizar os Filtros**

Cada request possui query parameters que você pode modificar:

**Exemplo: Listar Notas Fiscais (Por Cliente)**
```
GET {{baseURL}}/financeiro/notas-fiscais?codigo_cliente=123
```

Você pode:
- Alterar o valor de `codigo_cliente` diretamente na URL
- Ou usar a variável: `{{codigo_cliente}}`
- Adicionar mais parâmetros: `?codigo_cliente=123&limit=50&status_nota=vencida`

---

## 🧪 Testando os Endpoints

### **Exemplo Completo de Teste:**

1. **Fazer Login**
   - Request: `Auth > Login`
   - Response esperado: 200 OK com `access_token`

2. **Listar Todas as Notas**
   - Request: `Financeiro - Notas Fiscais > Listar Notas Fiscais (Todas)`
   - Response esperado: 200 OK com array de notas

3. **Obter Resumo**
   - Request: `Financeiro - Notas Fiscais > Obter Resumo de Notas Fiscais`
   - Response esperado: 200 OK com totais e valores

---

## 📊 Exemplo de Response Esperado

### **Listar Notas Fiscais:**
```json
{
  "notas": [
    {
      "id": 12345,
      "dataEmissao": "2025-01-15T00:00:00",
      "competencia": "01/2025",
      "numeroNFe": "67890",
      "valorTotal": 20192.64,
      "vencimento": "2025-02-15T00:00:00",
      "status": "a_vencer"
    }
  ],
  "total": 1,
  "resumo": {
    "totalNotasAVencer": 1,
    "valorNotasAVencer": 20192.64,
    "totalNotasVencidas": 0,
    "valorNotasVencidas": 0.0
  }
}
```

### **Obter Resumo:**
```json
{
  "totalNotasAVencer": 100,
  "valorNotasAVencer": 1500000.00,
  "totalNotasVencidas": 50,
  "valorNotasVencidas": 800000.00
}
```

---

## ⚠️ Troubleshooting

### **Erro 401 - Unauthorized**
- **Causa:** Token JWT inválido ou expirado
- **Solução:** Faça login novamente (request `Auth > Login`)

### **Erro 404 - Not Found**
- **Causa:** Endpoint incorreto ou API não está rodando
- **Solução:**
  - Verifique se a API está rodando: `http://localhost:8000/docs`
  - Verifique a variável `baseURL` no environment

### **Erro 400 - Bad Request**
- **Causa:** Parâmetros inválidos (ex: formato de data incorreto)
- **Solução:** Verifique os formatos:
  - Datas: `YYYY-MM-DD`
  - Competência: `YYYYMM`

### **Nenhum resultado retornado**
- **Causa:** Não há dados na tabela ou filtros muito restritivos
- **Solução:**
  - Verifique se a tabela `TB_Duplicata` foi criada e populada
  - Remova os filtros para testar

---

## 🔄 Atualizando a Collection

Se houver atualizações na API:

1. Delete a collection antiga no Postman
2. Reimporte o arquivo `.json` atualizado
3. O environment pode ser mantido

---

## 📚 Recursos Adicionais

- **Documentação da API:** `http://localhost:8000/docs` (Swagger)
- **Documentação Alternativa:** `http://localhost:8000/redoc`
- **Guia Completo:** Veja o arquivo `API_NOTAS_FISCAIS.md`

---

## ✅ Checklist de Testes

- [ ] Collection importada com sucesso
- [ ] Environment configurado com credenciais reais
- [ ] Login realizado (token salvo automaticamente)
- [ ] Listar todas as notas funciona
- [ ] Filtro por cliente funciona
- [ ] Filtro por competência funciona
- [ ] Filtro por status funciona
- [ ] Resumo retorna dados corretos
- [ ] Paginação funciona

---

**Última atualização:** 2025-10-13
