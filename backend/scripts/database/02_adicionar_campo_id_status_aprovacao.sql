-- =====================================================
-- Script: Adicionar Campo IdStatusAprovacao e Migrar Dados
-- Descrição: Adiciona campo de chave estrangeira para TB_StatusAprovacao
--            e migra os dados existentes do campo texto para o novo campo
-- Data: 2025-10-29
-- ⚠️ IMPORTANTE: Execute 01_criar_tb_status_aprovacao.sql antes deste!
-- =====================================================

USE PortalCliente;
GO

PRINT '================================================';
PRINT 'Iniciando migração para IdStatusAprovacao';
PRINT '================================================';
PRINT '';

-- Verificar se a tabela TB_StatusAprovacao existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_StatusAprovacao')
BEGIN
    PRINT '❌ ERRO: Tabela TB_StatusAprovacao não existe!';
    PRINT '   Execute o script 01_criar_tb_status_aprovacao.sql primeiro.';
    RAISERROR('Pré-requisito não atendido: TB_StatusAprovacao não existe', 16, 1);
    RETURN;
END
PRINT '✓ TB_StatusAprovacao encontrada';
GO

-- Verificar se o campo StatusAprovacao existe na TB_AprovacaoRPS
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('TB_AprovacaoRPS')
    AND name = 'StatusAprovacao'
)
BEGIN
    PRINT '❌ ERRO: Campo StatusAprovacao não existe na TB_AprovacaoRPS!';
    RAISERROR('Campo StatusAprovacao não encontrado', 16, 1);
    RETURN;
END
PRINT '✓ Campo StatusAprovacao encontrado';
GO

-- 1. Adicionar novo campo IdStatusAprovacao (permite NULL temporariamente)
PRINT '';
PRINT 'PASSO 1: Adicionando campo IdStatusAprovacao...';

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('TB_AprovacaoRPS')
    AND name = 'IdStatusAprovacao'
)
BEGIN
    ALTER TABLE TB_AprovacaoRPS
    ADD IdStatusAprovacao INT NULL;

    PRINT '✓ Campo IdStatusAprovacao adicionado';
END
ELSE
BEGIN
    PRINT '⚠ Campo IdStatusAprovacao já existe';
END
GO

-- 2. Verificar dados inconsistentes antes da migração
PRINT '';
PRINT 'PASSO 2: Verificando dados inconsistentes...';

DECLARE @RegistrosInconsistentes INT;

SELECT @RegistrosInconsistentes = COUNT(*)
FROM TB_AprovacaoRPS
WHERE StatusAprovacao NOT IN ('pendente', 'aprovado', 'reprovado')
   OR StatusAprovacao IS NULL;

IF @RegistrosInconsistentes > 0
BEGIN
    PRINT '⚠ Encontrados ' + CAST(@RegistrosInconsistentes AS VARCHAR) + ' registros com status inválido/nulo:';

    SELECT TOP 10
        ID,
        StatusAprovacao,
        TipoAcao,
        DataAcao
    FROM TB_AprovacaoRPS
    WHERE StatusAprovacao NOT IN ('pendente', 'aprovado', 'reprovado')
       OR StatusAprovacao IS NULL
    ORDER BY DataAcao DESC;

    PRINT '';
    PRINT 'Esses registros serão marcados como "pendente" por padrão.';
END
ELSE
BEGIN
    PRINT '✓ Todos os registros possuem status válidos';
END
GO

-- 3. Migrar dados do campo texto para o campo numérico
PRINT '';
PRINT 'PASSO 3: Migrando dados de StatusAprovacao para IdStatusAprovacao...';

DECLARE @RegistrosMigrados INT = 0;

-- Atualizar registros com status 'pendente'
UPDATE TB_AprovacaoRPS
SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'pendente')
WHERE LOWER(LTRIM(RTRIM(StatusAprovacao))) = 'pendente';

SET @RegistrosMigrados = @@ROWCOUNT;
PRINT '  - Migrados ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros com status "pendente"';

-- Atualizar registros com status 'aprovado'
UPDATE TB_AprovacaoRPS
SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'aprovado')
WHERE LOWER(LTRIM(RTRIM(StatusAprovacao))) = 'aprovado';

SET @RegistrosMigrados = @@ROWCOUNT;
PRINT '  - Migrados ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros com status "aprovado"';

-- Atualizar registros com status 'reprovado'
UPDATE TB_AprovacaoRPS
SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'reprovado')
WHERE LOWER(LTRIM(RTRIM(StatusAprovacao))) = 'reprovado';

SET @RegistrosMigrados = @@ROWCOUNT;
PRINT '  - Migrados ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros com status "reprovado"';

-- Tratar registros NULL ou inválidos (definir como 'pendente')
UPDATE TB_AprovacaoRPS
SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'pendente')
WHERE IdStatusAprovacao IS NULL;

SET @RegistrosMigrados = @@ROWCOUNT;
IF @RegistrosMigrados > 0
BEGIN
    PRINT '  - Corrigidos ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros nulos/inválidos (definidos como "pendente")';
END

PRINT '';
PRINT '✓ Migração de dados concluída!';
GO

-- 4. Validar migração
PRINT '';
PRINT 'PASSO 4: Validando migração...';

DECLARE @TotalRegistros INT, @RegistrosNaoMigrados INT;

SELECT @TotalRegistros = COUNT(*) FROM TB_AprovacaoRPS;
SELECT @RegistrosNaoMigrados = COUNT(*) FROM TB_AprovacaoRPS WHERE IdStatusAprovacao IS NULL;

IF @RegistrosNaoMigrados > 0
BEGIN
    PRINT '❌ ERRO: ' + CAST(@RegistrosNaoMigrados AS VARCHAR) + ' registros não foram migrados!';

    SELECT TOP 10
        ID,
        StatusAprovacao,
        IdStatusAprovacao,
        TipoAcao
    FROM TB_AprovacaoRPS
    WHERE IdStatusAprovacao IS NULL;

    RAISERROR('Migração incompleta', 16, 1);
    RETURN;
END

PRINT '✓ Todos os ' + CAST(@TotalRegistros AS VARCHAR) + ' registros foram migrados com sucesso!';
GO

-- 5. Tornar campo obrigatório (NOT NULL)
PRINT '';
PRINT 'PASSO 5: Tornando campo IdStatusAprovacao obrigatório...';

ALTER TABLE TB_AprovacaoRPS
ALTER COLUMN IdStatusAprovacao INT NOT NULL;

PRINT '✓ Campo IdStatusAprovacao agora é NOT NULL';
GO

-- 6. Adicionar Foreign Key
PRINT '';
PRINT 'PASSO 6: Adicionando Foreign Key...';

IF NOT EXISTS (
    SELECT * FROM sys.foreign_keys
    WHERE name = 'FK_TB_AprovacaoRPS_StatusAprovacao'
)
BEGIN
    ALTER TABLE TB_AprovacaoRPS
    ADD CONSTRAINT FK_TB_AprovacaoRPS_StatusAprovacao
    FOREIGN KEY (IdStatusAprovacao)
    REFERENCES TB_StatusAprovacao(ID);

    PRINT '✓ Foreign Key criada com sucesso';
END
ELSE
BEGIN
    PRINT '⚠ Foreign Key FK_TB_AprovacaoRPS_StatusAprovacao já existe';
END
GO

-- 7. Adicionar índice para melhorar performance de consultas
PRINT '';
PRINT 'PASSO 7: Adicionando índice no campo IdStatusAprovacao...';

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_TB_AprovacaoRPS_IdStatusAprovacao'
    AND object_id = OBJECT_ID('TB_AprovacaoRPS')
)
BEGIN
    CREATE INDEX IX_TB_AprovacaoRPS_IdStatusAprovacao
    ON TB_AprovacaoRPS(IdStatusAprovacao);

    PRINT '✓ Índice IX_TB_AprovacaoRPS_IdStatusAprovacao criado';
END
ELSE
BEGIN
    PRINT '⚠ Índice IX_TB_AprovacaoRPS_IdStatusAprovacao já existe';
END
GO

-- 8. Adicionar comentários
PRINT '';
PRINT 'PASSO 8: Adicionando comentários...';

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Chave estrangeira para TB_StatusAprovacao. Substitui o campo texto StatusAprovacao para melhorar performance.',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_AprovacaoRPS',
    @level2type = N'COLUMN', @level2name = 'IdStatusAprovacao';
GO

PRINT '✓ Comentários adicionados';
GO

-- 9. Exibir resumo da migração
PRINT '';
PRINT '================================================';
PRINT 'RESUMO DA MIGRAÇÃO';
PRINT '================================================';

SELECT
    s.Codigo AS Status,
    s.Descricao,
    COUNT(a.ID) AS TotalRegistros,
    CAST(COUNT(a.ID) * 100.0 / (SELECT COUNT(*) FROM TB_AprovacaoRPS) AS DECIMAL(5,2)) AS Percentual
FROM TB_StatusAprovacao s
LEFT JOIN TB_AprovacaoRPS a ON a.IdStatusAprovacao = s.ID
GROUP BY s.ID, s.Codigo, s.Descricao, s.Ordem
ORDER BY s.Ordem;

PRINT '';
PRINT '================================================';
PRINT '✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!';
PRINT '================================================';
PRINT '';
PRINT '⚠️ PRÓXIMOS PASSOS:';
PRINT '   1. Atualizar código backend (models.py) para usar IdStatusAprovacao';
PRINT '   2. Testar todas as funcionalidades de RPS';
PRINT '   3. Executar 03_remover_campo_status_aprovacao_texto.sql';
PRINT '';
GO
