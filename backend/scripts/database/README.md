# 📂 Scripts de Banco de Dados

Esta pasta contém todos os scripts SQL e Python para criação e população do banco de dados do Portal MetaRH.

---

## 📋 Índice

1. [Scripts de Criação](#scripts-de-criação)
2. [Scripts de População](#scripts-de-população)
3. [Scripts Utilitários](#scripts-utilitários)
4. [Ordem de Execução](#ordem-de-execução)
5. [Como Executar](#como-executar)

---

## 📄 Scripts de Criação

### **1. create_database.sql** (12 KB)
**Descrição:** Cria a estrutura inicial do banco de dados

**Conteúdo:**
- Criação do banco de dados (se necessário)
- Tabelas principais do sistema
- Constraints e relacionamentos

**Quando usar:** Primeira vez configurando o banco de dados

**Como executar:**
```bash
sqlcmd -S servidor -U usuario -P senha -i create_database.sql
```

---

### **2. create_table_tb_duplicata.sql** (7.9 KB)
**Descrição:** Cria a tabela TB_Duplicata (Notas Fiscais)

**Conteúdo:**
- DROP da tabela (se existir)
- Criação da tabela TB_Duplicata com 115 colunas
- Criação de 6 índices para performance:
  - Índice clustered na chave primária composta
  - Índice por cliente
  - Índice por data de vencimento
  - Índice por data de emissão
  - Índice por competência
  - Índice por status
- Estatísticas e validação

**Quando usar:** Antes de popular a tabela TB_Duplicata

**Importante:** Lembre-se de ajustar o nome do banco na linha 10:
```sql
USE [NomeDoBanco]; -- ALTERE PARA O NOME DO SEU BANCO DE DADOS
```

**Como executar:**
```bash
sqlcmd -S servidor -d NomeDoBanco -i create_table_tb_duplicata.sql
```

---

## 📊 Scripts de População

### **3. seed_data.sql** (6.6 KB)
**Descrição:** Popula tabelas auxiliares com dados iniciais

**Conteúdo:**
- Dados de referência (UFs, municípios, etc.)
- Configurações iniciais
- Dados de teste (se aplicável)

**Quando usar:** Após criar as tabelas principais

**Como executar:**
```bash
sqlcmd -S servidor -d NomeDoBanco -i seed_data.sql
```

---

### **4. insert_tb_duplicata.sql** (158 MB)
**Descrição:** Insere 64.900 registros na tabela TB_Duplicata

**Conteúdo:**
- 64.900 comandos INSERT individuais
- Transações em lotes de 1.000 registros
- Mensagens de progresso a cada lote
- Validação ao final

**Origem dos dados:** Gerado a partir do arquivo CSV `20230620061719_TB_Duplicata.csv`

**Quando usar:** Após criar a tabela TB_Duplicata

**Tempo estimado:** 5-15 minutos (depende do hardware)

**Como executar:**
```bash
sqlcmd -S servidor -d NomeDoBanco -i insert_tb_duplicata.sql
```

**⚠️ Atenção:**
- Arquivo grande (158 MB)
- Não esqueça de ajustar o nome do banco na linha 7
- Se houver erro durante a execução, parte dos dados pode já estar inserida (commits parciais)

---

## 🛠️ Scripts Utilitários

### **5. csv_to_sql_inserts.py** (6.7 KB)
**Descrição:** Script Python para converter CSV em comandos INSERT SQL

**Funcionalidades:**
- Lê arquivo CSV com delimitador pipe (|)
- Formata valores de acordo com o tipo de dado:
  - Strings: escapa aspas simples
  - Números: remove espaços e converte
  - Datas: formata para SQL Server
  - Booleanos: converte para 0/1
  - NULL: identifica valores vazios
- Gera transações em lotes para performance
- Adiciona mensagens de progresso

**Dependências:**
```bash
pip install pandas
```

**Como usar:**
```bash
python csv_to_sql_inserts.py
```

**Saída:** Gera o arquivo `insert_tb_duplicata.sql`

**Quando usar:** Se precisar reprocessar o CSV ou adaptar para outro arquivo

**Configurações no código:**
```python
CSV_FILE = '20230620061719_TB_Duplicata.csv'  # Arquivo de entrada
OUTPUT_SQL = 'insert_tb_duplicata.sql'         # Arquivo de saída
BATCH_SIZE = 1000                              # Tamanho do lote
```

---

## 🔄 Ordem de Execução

### **Setup Inicial Completo:**

```bash
# 1. Criar banco de dados e estrutura inicial
sqlcmd -S servidor -i create_database.sql

# 2. Criar tabela TB_Duplicata
sqlcmd -S servidor -d NomeDoBanco -i create_table_tb_duplicata.sql

# 3. Popular tabelas auxiliares
sqlcmd -S servidor -d NomeDoBanco -i seed_data.sql

# 4. Popular TB_Duplicata
sqlcmd -S servidor -d NomeDoBanco -i insert_tb_duplicata.sql
```

### **Setup Apenas para TB_Duplicata:**

Se você já tem o banco criado e só precisa da tabela de duplicatas:

```bash
# 1. Criar tabela
sqlcmd -S servidor -d NomeDoBanco -i create_table_tb_duplicata.sql

# 2. Popular dados
sqlcmd -S servidor -d NomeDoBanco -i insert_tb_duplicata.sql
```

---

## 💻 Como Executar

### **Opção 1: SQL Server Management Studio (SSMS)**

1. Abra o SSMS
2. Conecte-se ao servidor
3. Clique em **File > Open > File**
4. Selecione o script
5. Ajuste o nome do banco (se necessário)
6. Pressione **F5** para executar

---

### **Opção 2: sqlcmd (Linha de Comando)**

**Windows:**
```cmd
sqlcmd -S servidor -U usuario -P senha -d NomeDoBanco -i script.sql
```

**Linux/Mac:**
```bash
sqlcmd -S servidor -U usuario -P senha -d NomeDoBanco -i script.sql
```

**Com autenticação Windows:**
```cmd
sqlcmd -S servidor -E -d NomeDoBanco -i script.sql
```

---

### **Opção 3: Azure Data Studio**

1. Abra o Azure Data Studio
2. Conecte-se ao servidor
3. Clique em **File > Open File**
4. Selecione o script
5. Clique em **Run**

---

## 🔍 Verificação

### **Verificar se a tabela foi criada:**
```sql
SELECT TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'TB_Duplicata';
```

### **Verificar quantidade de registros:**
```sql
SELECT COUNT(*) AS TotalRegistros FROM TB_Duplicata;
-- Esperado: 64900
```

### **Verificar índices criados:**
```sql
SELECT
    i.name AS IndexName,
    i.type_desc AS IndexType,
    c.name AS ColumnName
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID('TB_Duplicata')
ORDER BY i.name, ic.key_ordinal;
```

### **Verificar distribuição por status:**
```sql
SELECT
    Status,
    COUNT(*) AS Quantidade,
    SUM(ValorBruto) AS ValorTotal
FROM TB_Duplicata
GROUP BY Status;
```

---

## ⚠️ Troubleshooting

### **Erro: "Database does not exist"**
**Solução:** Execute primeiro o `create_database.sql`

### **Erro: "Table already exists"**
**Solução:** O script já faz DROP da tabela. Se persistir, execute manualmente:
```sql
DROP TABLE IF EXISTS TB_Duplicata;
```

### **Erro: "Cannot open backup device"**
**Solução:** Verifique se o arquivo CSV está no caminho correto (apenas para BULK INSERT, não usado aqui)

### **Script muito lento**
**Solução:**
- O arquivo `insert_tb_duplicata.sql` é grande (158 MB)
- Execute em horário de menor uso do servidor
- Considere aumentar a memória alocada para o SQL Server

### **Erro: "String or binary data would be truncated"**
**Solução:** Verifique se os tamanhos das colunas no script `create_table_tb_duplicata.sql` estão corretos

---

## 📦 Estrutura de Arquivos

```
scripts/database/
├── README.md                          # Este arquivo
├── create_database.sql                # Cria banco e estrutura inicial
├── create_table_tb_duplicata.sql     # Cria tabela TB_Duplicata
├── seed_data.sql                      # Popula dados auxiliares
├── insert_tb_duplicata.sql           # Insere 64.900 duplicatas
└── csv_to_sql_inserts.py             # Gerador de INSERTs
```

---

## 🔐 Segurança

- ⚠️ **Nunca commite** credenciais de banco nos scripts
- ⚠️ Use variáveis de ambiente para senhas
- ⚠️ Faça backup antes de executar scripts de DROP/TRUNCATE
- ⚠️ Teste primeiro em ambiente de desenvolvimento

---

## 📝 Logs e Monitoramento

Para monitorar a execução dos scripts longos:

```sql
-- Ver processos em execução
SELECT
    session_id,
    status,
    command,
    percent_complete,
    estimated_completion_time
FROM sys.dm_exec_requests
WHERE session_id = @@SPID;
```

---

## 🚀 Próximos Passos

Após executar estes scripts:

1. ✅ Verificar se todos os dados foram inseridos
2. ✅ Testar a API de Notas Fiscais
3. ✅ Configurar backups automáticos
4. ✅ Criar usuários e permissões
5. ✅ Documentar procedures e views (se houver)

---

**Última atualização:** 2025-10-13
