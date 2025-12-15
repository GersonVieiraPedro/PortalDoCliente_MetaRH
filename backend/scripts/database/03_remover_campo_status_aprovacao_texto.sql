-- =====================================================
-- Script: Remover Campo StatusAprovacao (Texto)
-- Descrição: Remove o campo texto StatusAprovacao após migração
--            bem-sucedida para IdStatusAprovacao
-- Data: 2025-10-29
-- ⚠️ CRÍTICO: Execute este script APENAS APÓS:
--    1. Executar scripts 01 e 02
--    2. Atualizar código backend (models.py, routers)
--    3. Fazer deploy do backend atualizado
--    4. Testar TODAS as funcionalidades de RPS
--    5. Confirmar que tudo funciona 100%
-- =====================================================

USE PortalCliente;
GO

PRINT '================================================';
PRINT '⚠️ REMOÇÃO DO CAMPO TEXTO StatusAprovacao';
PRINT '================================================';
PRINT '';
PRINT '⚠️ ATENÇÃO: Este é um passo IRREVERSÍVEL!';
PRINT '';
PRINT 'Pré-requisitos:';
PRINT '  ✓ Scripts 01 e 02 executados';
PRINT '  ✓ Backend atualizado e em produção';
PRINT '  ✓ Todas as funcionalidades testadas';
PRINT '';
PRINT 'Aguardando 10 segundos antes de continuar...';
WAITFOR DELAY '00:00:10';
GO

-- 1. Verificar se IdStatusAprovacao existe e está populado
PRINT '';
PRINT 'PASSO 1: Verificando pré-requisitos...';

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('TB_AprovacaoRPS')
    AND name = 'IdStatusAprovacao'
)
BEGIN
    PRINT '❌ ERRO: Campo IdStatusAprovacao não existe!';
    PRINT '   Execute o script 02_adicionar_campo_id_status_aprovacao.sql primeiro.';
    RAISERROR('Pré-requisito não atendido', 16, 1);
    RETURN;
END

DECLARE @RegistrosNaoMigrados INT;

SELECT @RegistrosNaoMigrados = COUNT(*)
FROM TB_AprovacaoRPS
WHERE IdStatusAprovacao IS NULL;

IF @RegistrosNaoMigrados > 0
BEGIN
    PRINT '❌ ERRO: ' + CAST(@RegistrosNaoMigrados AS VARCHAR) + ' registros com IdStatusAprovacao NULL!';
    PRINT '   A migração não foi concluída corretamente.';
    RAISERROR('Migração incompleta', 16, 1);
    RETURN;
END

PRINT '✓ Campo IdStatusAprovacao existe e está populado';
GO

-- 2. Verificar se o campo StatusAprovacao existe
PRINT '';
PRINT 'PASSO 2: Verificando campo StatusAprovacao...';

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('TB_AprovacaoRPS')
    AND name = 'StatusAprovacao'
)
BEGIN
    PRINT '⚠ Campo StatusAprovacao já foi removido anteriormente.';
    PRINT '✓ Script concluído (nada a fazer).';
    RETURN;
END

PRINT '✓ Campo StatusAprovacao encontrado';
GO

-- 3. Criar backup da coluna antes de remover (tabela temporária)
PRINT '';
PRINT 'PASSO 3: Criando backup de segurança...';

IF OBJECT_ID('tempdb..#BackupStatusAprovacao') IS NOT NULL
    DROP TABLE #BackupStatusAprovacao;

SELECT
    ID,
    StatusAprovacao AS StatusAprovacao_OLD,
    IdStatusAprovacao,
    DataAcao,
    CURRENT_TIMESTAMP AS DataBackup
INTO #BackupStatusAprovacao
FROM TB_AprovacaoRPS;

DECLARE @RegistrosBackup INT = @@ROWCOUNT;

PRINT '✓ Backup criado: ' + CAST(@RegistrosBackup AS VARCHAR) + ' registros em #BackupStatusAprovacao';
PRINT '  (Backup temporário - será descartado ao fechar a sessão)';
GO

-- 4. Comparar consistência entre campos antes de remover
PRINT '';
PRINT 'PASSO 4: Validando consistência dos dados...';

DECLARE @Inconsistencias INT;

SELECT @Inconsistencias = COUNT(*)
FROM TB_AprovacaoRPS a
INNER JOIN TB_StatusAprovacao s ON a.IdStatusAprovacao = s.ID
WHERE LOWER(LTRIM(RTRIM(a.StatusAprovacao))) != s.Codigo;

IF @Inconsistencias > 0
BEGIN
    PRINT '⚠ AVISO: ' + CAST(@Inconsistencias AS VARCHAR) + ' registros com inconsistência entre campos!';

    SELECT TOP 10
        a.ID,
        a.StatusAprovacao AS StatusTexto,
        s.Codigo AS StatusNovo,
        a.DataAcao
    FROM TB_AprovacaoRPS a
    INNER JOIN TB_StatusAprovacao s ON a.IdStatusAprovacao = s.ID
    WHERE LOWER(LTRIM(RTRIM(a.StatusAprovacao))) != s.Codigo;

    PRINT '';
    PRINT '⚠ Revise esses registros antes de continuar.';
    PRINT '  Deseja continuar mesmo assim? (Script continuará em 15 segundos)';
    WAITFOR DELAY '00:00:15';
END
ELSE
BEGIN
    PRINT '✓ Dados consistentes entre StatusAprovacao e IdStatusAprovacao';
END
GO

-- 5. Remover índices que dependem do campo StatusAprovacao (se existirem)
PRINT '';
PRINT 'PASSO 5: Verificando índices dependentes...';

DECLARE @IndexName NVARCHAR(128);
DECLARE index_cursor CURSOR FOR
SELECT i.name
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID('TB_AprovacaoRPS')
  AND c.name = 'StatusAprovacao'
  AND i.name IS NOT NULL;

OPEN index_cursor;
FETCH NEXT FROM index_cursor INTO @IndexName;

IF @@FETCH_STATUS = 0
BEGIN
    PRINT '  Removendo índices dependentes:';

    WHILE @@FETCH_STATUS = 0
    BEGIN
        DECLARE @DropIndexSQL NVARCHAR(500);
        SET @DropIndexSQL = 'DROP INDEX ' + @IndexName + ' ON TB_AprovacaoRPS';

        PRINT '    - Removendo índice: ' + @IndexName;
        EXEC sp_executesql @DropIndexSQL;

        FETCH NEXT FROM index_cursor INTO @IndexName;
    END
END
ELSE
BEGIN
    PRINT '✓ Nenhum índice dependente encontrado';
END

CLOSE index_cursor;
DEALLOCATE index_cursor;
GO

-- 6. Remover comentários do campo (Extended Properties)
PRINT '';
PRINT 'PASSO 6: Removendo metadados...';

IF EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID('TB_AprovacaoRPS')
    AND minor_id = (SELECT column_id FROM sys.columns WHERE object_id = OBJECT_ID('TB_AprovacaoRPS') AND name = 'StatusAprovacao')
    AND name = 'MS_Description'
)
BEGIN
    EXEC sp_dropextendedproperty
        @name = N'MS_Description',
        @level0type = N'SCHEMA', @level0name = 'dbo',
        @level1type = N'TABLE',  @level1name = 'TB_AprovacaoRPS',
        @level2type = N'COLUMN', @level2name = 'StatusAprovacao';

    PRINT '✓ Comentários removidos';
END
GO

-- 7. Remover o campo StatusAprovacao
PRINT '';
PRINT 'PASSO 7: Removendo campo StatusAprovacao...';
PRINT '';
PRINT '⚠️ ÚLTIMA CHANCE DE CANCELAR!';
PRINT '   Pressione Ctrl+C nos próximos 5 segundos para abortar.';
WAITFOR DELAY '00:00:05';

ALTER TABLE TB_AprovacaoRPS
DROP COLUMN StatusAprovacao;

PRINT '';
PRINT '✓ Campo StatusAprovacao removido com sucesso!';
GO

-- 8. Verificar estrutura final
PRINT '';
PRINT '================================================';
PRINT 'ESTRUTURA FINAL DA TABELA';
PRINT '================================================';

SELECT
    c.name AS Campo,
    t.name AS Tipo,
    c.max_length AS Tamanho,
    c.is_nullable AS Nulo,
    CASE WHEN pk.column_id IS NOT NULL THEN 'Sim' ELSE 'Não' END AS ChavePrimaria,
    CASE WHEN fk.parent_column_id IS NOT NULL THEN 'Sim' ELSE 'Não' END AS ChaveEstrangeira
FROM sys.columns c
INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
LEFT JOIN (
    SELECT ic.object_id, ic.column_id
    FROM sys.indexes i
    INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    WHERE i.is_primary_key = 1
) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
LEFT JOIN sys.foreign_key_columns fk ON c.object_id = fk.parent_object_id AND c.column_id = fk.parent_column_id
WHERE c.object_id = OBJECT_ID('TB_AprovacaoRPS')
ORDER BY c.column_id;

PRINT '';
PRINT '================================================';
PRINT '✓ REMOÇÃO CONCLUÍDA COM SUCESSO!';
PRINT '================================================';
PRINT '';
PRINT 'Ações realizadas:';
PRINT '  ✓ Backup criado em #BackupStatusAprovacao (temporário)';
PRINT '  ✓ Índices dependentes removidos';
PRINT '  ✓ Metadados removidos';
PRINT '  ✓ Campo StatusAprovacao removido';
PRINT '';
PRINT 'A tabela TB_AprovacaoRPS agora usa apenas IdStatusAprovacao.';
PRINT '';
GO
