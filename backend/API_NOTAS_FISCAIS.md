# 📋 API de Notas Fiscais - Documentação

## 🎯 Overview

API para consulta de Notas Fiscais (Duplicatas) do sistema MetaRH.

**Base URL**: `/financeiro`

---

## 🔐 Autenticação

Todos os endpoints requerem autenticação via **JWT Bearer Token**.

```http
Authorization: Bearer <seu_token_jwt>
```

---

## 📍 Endpoints

### 1. Listar Notas Fiscais

```http
GET /financeiro/notas-fiscais
```

#### Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `codigo_cliente` | integer | Não | Código do cliente para filtrar |
| `competencia` | string | Não | Competência no formato YYYYMM (ex: 202501) |
| `status_nota` | string | Não | Filtro por status: `a_vencer`, `vencida`, `paga` |
| `data_inicio` | string | Não | Data de **vencimento** início (YYYY-MM-DD) |
| `data_fim` | string | Não | Data de **vencimento** fim (YYYY-MM-DD) |
| `data_emissao_inicio` | string | Não | Data de **emissão** início (YYYY-MM-DD) |
| `data_emissao_fim` | string | Não | Data de **emissão** fim (YYYY-MM-DD) |
| `numero_nfe` | string | Não | Número da NFe (busca parcial, case-insensitive) |
| `valor_minimo` | float | Não | Valor mínimo da nota fiscal |
| `valor_maximo` | float | Não | Valor máximo da nota fiscal |
| `limit` | integer | Não | Limite de registros (1-500, padrão: 100) |
| `offset` | integer | Não | Offset para paginação (padrão: 0) |

#### Exemplo de Request

**Exemplo 1: Filtro básico por cliente**
```bash
curl -X GET "http://localhost:8000/financeiro/notas-fiscais?codigo_cliente=123&limit=10" \
  -H "Authorization: Bearer seu_token_jwt"
```

**Exemplo 2: Filtro por data de emissão específica**
```bash
curl -X GET "http://localhost:8000/financeiro/notas-fiscais?data_emissao_inicio=2025-01-15&data_emissao_fim=2025-01-15" \
  -H "Authorization: Bearer seu_token_jwt"
```

**Exemplo 3: Filtro por número da NFe e valor**
```bash
curl -X GET "http://localhost:8000/financeiro/notas-fiscais?numero_nfe=67890&valor_minimo=15000&valor_maximo=25000" \
  -H "Authorization: Bearer seu_token_jwt"
```

**Exemplo 4: Filtro combinado**
```bash
curl -X GET "http://localhost:8000/financeiro/notas-fiscais?competencia=202501&status_nota=vencida&data_inicio=2025-01-01&data_fim=2025-01-31" \
  -H "Authorization: Bearer seu_token_jwt"
```

#### Exemplo de Response

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
    },
    {
      "id": 12346,
      "dataEmissao": "2024-12-10T00:00:00",
      "competencia": "12/2024",
      "numeroNFe": "67891",
      "valorTotal": 15000.00,
      "vencimento": "2025-01-10T00:00:00",
      "status": "vencida"
    }
  ],
  "total": 2,
  "resumo": {
    "totalNotasAVencer": 1,
    "valorNotasAVencer": 20192.64,
    "totalNotasVencidas": 1,
    "valorNotasVencidas": 15000.00
  }
}
```

---

### 2. Obter Resumo

```http
GET /financeiro/notas-fiscais/resumo
```

#### Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `codigo_cliente` | integer | Não | Código do cliente para filtrar |
| `competencia` | string | Não | Competência no formato YYYYMM |

#### Exemplo de Request

```bash
curl -X GET "http://localhost:8000/financeiro/notas-fiscais/resumo?codigo_cliente=123" \
  -H "Authorization: Bearer seu_token_jwt"
```

#### Exemplo de Response

```json
{
  "totalNotasAVencer": 100,
  "valorNotasAVencer": 1500000.00,
  "totalNotasVencidas": 50,
  "valorNotasVencidas": 800000.00
}
```

---

### 3. Obter Arquivo da Nota Fiscal

```http
GET /financeiro/notas-fiscais/{nota_id}/arquivo
```

Retorna informações sobre o arquivo da nota fiscal.

⚠️ **Nota**: Este endpoint retorna apenas metadados do arquivo. A implementação de download real aguarda definição do repositório de arquivos.

#### Path Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `nota_id` | integer | Sim | ID da nota fiscal |

#### Exemplo de Request

```bash
curl -X GET "http://localhost:8000/financeiro/notas-fiscais/12345/arquivo" \
  -H "Authorization: Bearer seu_token_jwt"
```

#### Exemplo de Response

```json
{
  "nomeArquivo": "NFe_67890.xml",
  "numeroRps": 12345,
  "codigoEmpresaFat": 1,
  "codigoFilialFat": 1,
  "mensagem": "Arquivo encontrado"
}
```

---

## 📊 Modelos de Dados

### NotaFiscalResponse

```typescript
{
  id: number              // ID da duplicata
  dataEmissao: string     // Data de emissão (ISO 8601)
  competencia: string     // Competência (MM/YYYY)
  numeroNFe: string?      // Número da NFe (pode ser null)
  valorTotal: number      // Valor total da nota
  vencimento: string      // Data de vencimento (ISO 8601)
  status: string          // 'a_vencer' | 'vencida' | 'paga'
}
```

### ResumoNotasFiscaisResponse

```typescript
{
  totalNotasAVencer: number      // Quantidade de notas a vencer
  valorNotasAVencer: number      // Valor total a vencer
  totalNotasVencidas: number     // Quantidade de notas vencidas
  valorNotasVencidas: number     // Valor total vencido
}
```

---

## 🔍 Funcionalidades de Filtros

### Filtros por Data

A API suporta dois tipos de filtros de data:

1. **Data de Emissão** (`data_emissao_inicio` / `data_emissao_fim`)
   - Filtra pela data em que a nota foi emitida
   - Campo: `TB_Duplicata.DataEmissao`

2. **Data de Vencimento** (`data_inicio` / `data_fim`)
   - Filtra pela data de vencimento da nota
   - Campo: `TB_Duplicata.DataVecto`

### Filtro por Número da NFe

- Parâmetro: `numero_nfe`
- Busca parcial (LIKE)
- Case-insensitive
- Exemplo: `numero_nfe=678` encontra "67890", "16780", etc.

### Filtro por Valor

- Parâmetros: `valor_minimo` e `valor_maximo`
- Aceita valores decimais
- Exemplo: Para buscar notas entre R$ 15.000,00 e R$ 25.000,00:
  ```
  valor_minimo=15000&valor_maximo=25000
  ```

### Filtro Exato

Para buscar um valor exato de data ou valor, use o mesmo valor nos parâmetros início/fim:

```bash
# Data de emissão exata
data_emissao_inicio=2025-01-15&data_emissao_fim=2025-01-15

# Valor exato
valor_minimo=20192.64&valor_maximo=20192.64
```

### Combinação de Filtros

Todos os filtros podem ser combinados. A API aplica operador AND entre os filtros:

```bash
GET /financeiro/notas-fiscais?
  competencia=202501&
  status_nota=vencida&
  numero_nfe=678&
  valor_minimo=10000&
  data_emissao_inicio=2025-01-01&
  data_emissao_fim=2025-01-31
```

---

## 🔄 Lógica de Status

O status da nota é calculado dinamicamente:

| Condição | Status |
|----------|--------|
| `DataBaixa` preenchida | `paga` |
| `DataVecto < hoje` e sem `DataBaixa` | `vencida` |
| `DataVecto >= hoje` e sem `DataBaixa` | `a_vencer` |

---

## ⚠️ Regras de Negócio

1. **Apenas registros ativos**: Somente duplicatas com `Status = 'A'` são retornadas
2. **Autenticação obrigatória**: Todos os endpoints requerem JWT válido
3. **Paginação**: Máximo de 500 registros por requisição
4. **Formato de datas**: ISO 8601 para entrada e saída
5. **Formato de competência**:
   - Entrada: `YYYYMM` (ex: "202501")
   - Saída: `MM/YYYY` (ex: "01/2025")

---

## 🧪 Testando a API

### Swagger UI (Documentação Interativa)

Acesse: `http://localhost:8000/docs`

### Redoc

Acesse: `http://localhost:8000/redoc`

---

## 🐛 Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Requisição inválida (ex: formato de data incorreto) |
| 401 | Não autorizado (token inválido/ausente) |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## 📝 Exemplo de Integração no Frontend

```typescript
// services/notasFiscais.ts
const API_BASE = 'http://localhost:8000';

export async function buscarNotasFiscais(
  codigoCliente: number,
  token: string
): Promise<ListaNotasFiscaisResponse> {
  const response = await fetch(
    `${API_BASE}/financeiro/notas-fiscais?codigo_cliente=${codigoCliente}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error('Erro ao buscar notas fiscais');
  }

  return response.json();
}
```

---

## 🔧 Requisitos

- Python 3.10+
- FastAPI
- SQLAlchemy 2.x
- SQL Server com tabela `TB_Duplicata` criada

---

## 📦 Estrutura de Arquivos

```
backend/src/backend/
├── models.py              # Modelo TB_Duplicata
├── schema.py              # Schemas Pydantic
├── routers/
│   └── financeiro.py      # Endpoints de notas fiscais
├── database.py            # Conexão com banco
├── security.py            # Autenticação JWT
└── main.py                # Aplicação FastAPI
```

---

## ✅ Checklist de Deploy

- [ ] Tabela `TB_Duplicata` criada no banco
- [ ] Dados populados na tabela
- [ ] Índices criados para performance
- [ ] Variáveis de ambiente configuradas
- [ ] JWT funcionando
- [ ] CORS configurado para o frontend
- [ ] Testes realizados

---

**Última atualização**: 2025-10-15
