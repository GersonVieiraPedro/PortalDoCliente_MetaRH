# Scripts de Refatoração RPS - Guia de Execução

**Data de Criação:** 2025-01-26
**Versão:** 1.0
**Objetivo:** Corrigir confusão entre campos Duplicata (número da RPS) e NumeroRPS (legacy)

---

## 📋 Visão Geral

Este conjunto de scripts SQL corrige a confusão conceitual entre os campos relacionados a RPS na base de dados:

- **Duplicata** = Número da RPS (identificador correto)
- **NroNFe** = Número da Nota Fiscal (emitida após aprovação)
- **NumeroRPS** = Campo legacy (deprecated em TB_Duplicata, removido de TB_AprovacaoRPS)

---

## 📦 Scripts Disponíveis

### 1. `adicionar_comentarios_rps.sql` ✅ OBRIGATÓRIO

**Descrição:** Adiciona comentários explicativos nas colunas para documentar o uso correto dos campos.

**Impacto:** Nenhum (apenas documentação)

**Tempo estimado:** < 1 minuto

**Rollback:** Não necessário (sem alterações estruturais)

**Executar em:**
- ✅ Desenvolvimento
- ✅ Homologação
- ✅ Produção

---

### 2. `adicionar_indices_duplicata.sql` ✅ OBRIGATÓRIO

**Descrição:** Adiciona índices para otimizar buscas por número da RPS (campo Duplicata).

**Impacto:** Melhora de performance (pode causar leve lentidão durante criação dos índices)

**Tempo estimado:** 1-5 minutos (depende do volume de dados)

**Rollback:**
```sql
DROP INDEX [IX_TB_Duplicata_Duplicata] ON [dbo].[TB_Duplicata];
DROP INDEX [IX_TB_Duplicata_ChaveComposta] ON [dbo].[TB_Duplicata];
```

**Executar em:**
- ✅ Desenvolvimento
- ✅ Homologação
- ✅ Produção (em horário de baixo uso)

---

### 3. `remover_numero_rps_aprovacao.sql` ⚠️ IMPORTANTE (BREAKING CHANGE)

**Descrição:** Remove o campo `NumeroRPS` da tabela `TB_AprovacaoRPS` (campo redundante).

**Impacto:** **BREAKING CHANGE** - Requer backend atualizado

**Tempo estimado:** < 1 minuto

**Rollback:**
```sql
-- Adicionar coluna de volta (se necessário)
ALTER TABLE [dbo].[TB_AprovacaoRPS]
ADD [NumeroRPS] INT NULL;

-- Recriar índice (se necessário)
CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_NumeroRPS]
ON [dbo].[TB_AprovacaoRPS] ([NumeroRPS] ASC);
```

**⚠️ IMPORTANTE:**
- Executar **SOMENTE APÓS** atualizar o código backend
- Backend deve estar sem referências ao campo `NumeroRPS` da `TB_AprovacaoRPS`
- Campo é redundante - chave composta já identifica a RPS

**Executar em:**
- ✅ Desenvolvimento (após deploy do backend)
- ✅ Homologação (após deploy do backend)
- ✅ Produção (após deploy do backend)

---

## 🔄 Ordem de Execução

### Ordem Recomendada:

```
1. ✅ adicionar_comentarios_rps.sql
2. ✅ adicionar_indices_duplicata.sql
3. ✅ Deploy do backend atualizado
4. ⚠️ remover_numero_rps_aprovacao.sql (APÓS deploy do backend)
5. ✅ Testes completos (aprovação/reprovação de RPS)
```

**Notas Importantes:**
- A tabela `TB_Duplicata` não será alterada estruturalmente
- O campo `NumeroRPS` permanece em `TB_Duplicata` (campo legacy)
- O campo `NumeroRPS` é **removido** de `TB_AprovacaoRPS` (redundante)
- **Script 3 só pode ser executado APÓS o deploy do backend atualizado**

---

## 💻 Como Executar os Scripts

### Opção 1: SQL Server Management Studio (SSMS)

1. Abrir SSMS
2. Conectar ao servidor `PortalCliente`
3. Abrir o script desejado
4. **IMPORTANTE:** Verificar se está no banco correto: `USE [PortalCliente]`
5. Executar (F5)
6. Verificar mensagens de sucesso no painel de resultados

### Opção 2: Azure Data Studio

1. Abrir Azure Data Studio
2. Conectar ao servidor
3. Abrir o script
4. Selecionar o banco `PortalCliente`
5. Executar
6. Verificar output

### Opção 3: sqlcmd (linha de comando)

```bash
# Script 1 - Comentários
sqlcmd -S <server> -d PortalCliente -i adicionar_comentarios_rps.sql -o log_comentarios.txt

# Script 2 - Índices
sqlcmd -S <server> -d PortalCliente -i adicionar_indices_duplicata.sql -o log_indices.txt

# Script 3 - Remover NumeroRPS (SOMENTE APÓS deploy do backend!)
sqlcmd -S <server> -d PortalCliente -i remover_numero_rps_aprovacao.sql -o log_remocao.txt
```

---

## 📊 Verificações Pós-Execução

### Verificar Comentários

```sql
SELECT
    c.name AS ColumnName,
    ep.value AS Description
FROM sys.columns c
LEFT JOIN sys.extended_properties ep
    ON ep.major_id = c.object_id
    AND ep.minor_id = c.column_id
    AND ep.name = 'MS_Description'
WHERE c.object_id = OBJECT_ID('dbo.TB_Duplicata')
    AND c.name IN ('Duplicata', 'NroNFe', 'NumeroRPS')
ORDER BY c.column_id;
```

### Verificar Índices

```sql
SELECT
    i.name AS IndexName,
    i.type_desc AS IndexType,
    STUFF((
        SELECT ', ' + c.name
        FROM sys.index_columns ic
        INNER JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
        WHERE ic.object_id = i.object_id
            AND ic.index_id = i.index_id
            AND ic.is_included_column = 0
        FOR XML PATH('')), 1, 2, '') AS KeyColumns
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.TB_Duplicata')
    AND i.name LIKE '%Duplicata%'
ORDER BY i.name;
```

### Verificar Estrutura da Tabela

```sql
EXEC sp_help 'dbo.TB_Duplicata';
EXEC sp_help 'dbo.TB_AprovacaoRPS';
```

---

## 🔙 Plano de Rollback

### Se Script 1 (Comentários) falhar:
Não há necessidade de rollback - apenas adiciona metadados de documentação.

### Se Script 2 (Índices) falhar:

**Rollback dos índices:**
```sql
DROP INDEX [IX_TB_Duplicata_Duplicata] ON [dbo].[TB_Duplicata];
DROP INDEX [IX_TB_Duplicata_ChaveComposta] ON [dbo].[TB_Duplicata];
```

**Nota:** Nenhum script faz alterações estruturais nas tabelas (renomeação de colunas, etc.).

---

## ⚠️ Checklist Pré-Execução

### Para Scripts 1 e 2

- [ ] Conectado ao banco `PortalCliente`
- [ ] Permissões adequadas (ALTER, CREATE INDEX)
- [ ] Janela de execução identificada (opcional, recomendado para Script 2 em produção)

---

## 📞 Suporte

**Dúvidas ou problemas durante a execução:**
- Verificar logs de erro do SQL Server
- Consultar documentação completa em `/PLANO_REFATORACAO_RPS.md`
- Contatar DBA responsável

---

## 📝 Log de Execução

| Ambiente | Script | Data | Executado Por | Status | Observações |
|----------|--------|------|---------------|--------|-------------|
| DEV | Script 1 | - | - | ⏳ Pendente | Comentários de documentação |
| DEV | Script 2 | - | - | ⏳ Pendente | Índices de performance |
| DEV | Script 3 | - | - | ⏳ Pendente | Remover NumeroRPS (após deploy backend) |
| HML | Script 1 | - | - | ⏳ Pendente | - |
| HML | Script 2 | - | - | ⏳ Pendente | - |
| HML | Script 3 | - | - | ⏳ Pendente | - |
| PROD | Script 1 | - | - | ⏳ Pendente | - |
| PROD | Script 2 | - | - | ⏳ Pendente | - |
| PROD | Script 3 | - | - | ⏳ Pendente | - |

**Preencher após cada execução!**

**Notas:**
- Script 3 (`remover_numero_rps_aprovacao.sql`) só pode ser executado após deploy do backend
- O campo `NumeroRPS` permanece em `TB_Duplicata` (campo legacy, não será renomeado)
- O campo `NumeroRPS` é removido de `TB_AprovacaoRPS` (redundante)
