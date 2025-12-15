-- =====================================================
-- SCRIPT CONSOLIDADO: Migração TB_StatusAprovacao
-- =====================================================
--
-- Este script executa TODOS os passos necessários para migrar
-- o campo StatusAprovacao (texto) para IdStatusAprovacao (FK).
--
-- IMPORTANTE: Execute este script SE E SOMENTE SE você estiver
-- recebendo o erro relacionado a TB_StatusAprovacao no endpoint
-- /financeiro/rps.
--
-- O QUE ESTE SCRIPT FAZ:
-- 1. Cria a tabela TB_StatusAprovacao (domínio: pendente, aprovado, reprovado)
-- 2. Adiciona campo IdStatusAprovacao na TB_AprovacaoRPS
-- 3. Migra dados existentes do campo texto para o campo numérico
-- 4. Adiciona Foreign Key e índices
-- 5. (Opcional) Remove o campo texto antigo
--
-- TEMPO ESTIMADO: 1-2 minutos
-- =====================================================

USE PortalCliente;
GO

SET NOCOUNT ON;

PRINT '';
PRINT '========================================================';
PRINT '  MIGRAÇÃO: TB_StatusAprovacao';
PRINT '========================================================';
PRINT '';
PRINT 'Iniciando migração em ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- =====================================================
-- PASSO 1: Criar TB_StatusAprovacao
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 1: Criar Tabela TB_StatusAprovacao          │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_StatusAprovacao')
BEGIN
    CREATE TABLE TB_StatusAprovacao (
        ID INT IDENTITY(1,1) NOT NULL,
        Codigo VARCHAR(20) NOT NULL,
        Descricao VARCHAR(100) NOT NULL,
        Ativo BIT NOT NULL DEFAULT 1,
        Ordem INT NOT NULL,
        DataCadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        DataAtualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT PK_TB_StatusAprovacao PRIMARY KEY (ID),
        CONSTRAINT UQ_TB_StatusAprovacao_Codigo UNIQUE (Codigo)
    );

    PRINT '✓ Tabela TB_StatusAprovacao criada';

    -- Inserir valores de domínio
    INSERT INTO TB_StatusAprovacao (Codigo, Descricao, Ativo, Ordem)
    VALUES
        ('pendente', 'Pendente de Aprovação', 1, 1),
        ('aprovado', 'Aprovado', 1, 2),
        ('reprovado', 'Reprovado', 1, 3);

    PRINT '✓ Valores de domínio inseridos (pendente, aprovado, reprovado)';
END
ELSE
BEGIN
    PRINT '⚠ TB_StatusAprovacao já existe';
END

PRINT '';

-- =====================================================
-- PASSO 2: Adicionar campo IdStatusAprovacao
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 2: Adicionar Campo IdStatusAprovacao        │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

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

PRINT '';

-- =====================================================
-- PASSO 3: Migrar dados existentes
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 3: Migrar Dados Existentes                  │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

DECLARE @TotalRegistros INT;
SELECT @TotalRegistros = COUNT(*) FROM TB_AprovacaoRPS;

IF @TotalRegistros = 0
BEGIN
    PRINT '⚠ Tabela TB_AprovacaoRPS está vazia (nenhum dado para migrar)';
END
ELSE
BEGIN
    DECLARE @RegistrosMigrados INT;

    -- Verificar se campo StatusAprovacao existe (pode não existir em bancos novos)
    IF EXISTS (
        SELECT * FROM sys.columns
        WHERE object_id = OBJECT_ID('TB_AprovacaoRPS')
        AND name = 'StatusAprovacao'
    )
    BEGIN
        PRINT 'Total de registros na TB_AprovacaoRPS: ' + CAST(@TotalRegistros AS VARCHAR);
        PRINT '';

        -- Migrar 'pendente'
        UPDATE TB_AprovacaoRPS
        SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'pendente')
        WHERE LOWER(LTRIM(RTRIM(StatusAprovacao))) = 'pendente'
          AND IdStatusAprovacao IS NULL;

        SET @RegistrosMigrados = @@ROWCOUNT;
        PRINT '  ✓ Migrados ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros "pendente"';

        -- Migrar 'aprovado'
        UPDATE TB_AprovacaoRPS
        SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'aprovado')
        WHERE LOWER(LTRIM(RTRIM(StatusAprovacao))) = 'aprovado'
          AND IdStatusAprovacao IS NULL;

        SET @RegistrosMigrados = @@ROWCOUNT;
        PRINT '  ✓ Migrados ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros "aprovado"';

        -- Migrar 'reprovado'
        UPDATE TB_AprovacaoRPS
        SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'reprovado')
        WHERE LOWER(LTRIM(RTRIM(StatusAprovacao))) = 'reprovado'
          AND IdStatusAprovacao IS NULL;

        SET @RegistrosMigrados = @@ROWCOUNT;
        PRINT '  ✓ Migrados ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros "reprovado"';

        -- Tratar NULL/inválidos como 'pendente'
        UPDATE TB_AprovacaoRPS
        SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'pendente')
        WHERE IdStatusAprovacao IS NULL;

        SET @RegistrosMigrados = @@ROWCOUNT;
        IF @RegistrosMigrados > 0
            PRINT '  ✓ Corrigidos ' + CAST(@RegistrosMigrados AS VARCHAR) + ' registros NULL/inválidos → "pendente"';
    END
    ELSE
    BEGIN
        -- Campo StatusAprovacao não existe, definir todos como 'pendente'
        PRINT '⚠ Campo StatusAprovacao não existe (banco novo)';
        PRINT '  Definindo todos os registros como "pendente"...';

        UPDATE TB_AprovacaoRPS
        SET IdStatusAprovacao = (SELECT ID FROM TB_StatusAprovacao WHERE Codigo = 'pendente')
        WHERE IdStatusAprovacao IS NULL;

        PRINT '  ✓ ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros definidos como "pendente"';
    END
END

PRINT '';

-- =====================================================
-- PASSO 4: Validar migração
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 4: Validar Migração                         │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

DECLARE @RegistrosNaoMigrados INT;
SELECT @RegistrosNaoMigrados = COUNT(*) FROM TB_AprovacaoRPS WHERE IdStatusAprovacao IS NULL;

IF @RegistrosNaoMigrados > 0
BEGIN
    PRINT '❌ ERRO: ' + CAST(@RegistrosNaoMigrados AS VARCHAR) + ' registros não foram migrados!';

    SELECT TOP 5
        ID,
        TipoAcao,
        DataAcao,
        IdStatusAprovacao
    FROM TB_AprovacaoRPS
    WHERE IdStatusAprovacao IS NULL;

    PRINT '';
    PRINT 'MIGRAÇÃO FALHOU! Corrija os dados acima e execute novamente.';
    RETURN;
END
ELSE
BEGIN
    PRINT '✓ Todos os registros foram migrados com sucesso!';
END

PRINT '';

-- =====================================================
-- PASSO 5: Tornar campo obrigatório
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 5: Tornar Campo Obrigatório (NOT NULL)      │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

-- Verificar se o campo já é NOT NULL
DECLARE @IsNullable BIT;
SELECT @IsNullable = is_nullable
FROM sys.columns
WHERE object_id = OBJECT_ID('TB_AprovacaoRPS')
  AND name = 'IdStatusAprovacao';

IF @IsNullable = 1
BEGIN
    ALTER TABLE TB_AprovacaoRPS
    ALTER COLUMN IdStatusAprovacao INT NOT NULL;

    PRINT '✓ Campo IdStatusAprovacao agora é NOT NULL';
END
ELSE
BEGIN
    PRINT '⚠ Campo IdStatusAprovacao já é NOT NULL';
END

PRINT '';

-- =====================================================
-- PASSO 6: Adicionar Foreign Key
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 6: Adicionar Foreign Key                    │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

IF NOT EXISTS (
    SELECT * FROM sys.foreign_keys
    WHERE name = 'FK_TB_AprovacaoRPS_StatusAprovacao'
)
BEGIN
    ALTER TABLE TB_AprovacaoRPS
    ADD CONSTRAINT FK_TB_AprovacaoRPS_StatusAprovacao
    FOREIGN KEY (IdStatusAprovacao)
    REFERENCES TB_StatusAprovacao(ID);

    PRINT '✓ Foreign Key criada';
END
ELSE
BEGIN
    PRINT '⚠ Foreign Key já existe';
END

PRINT '';

-- =====================================================
-- PASSO 7: Adicionar índice
-- =====================================================
PRINT '┌────────────────────────────────────────────────────┐';
PRINT '│ PASSO 7: Adicionar Índice                         │';
PRINT '└────────────────────────────────────────────────────┘';
PRINT '';

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_TB_AprovacaoRPS_IdStatusAprovacao'
    AND object_id = OBJECT_ID('TB_AprovacaoRPS')
)
BEGIN
    CREATE INDEX IX_TB_AprovacaoRPS_IdStatusAprovacao
    ON TB_AprovacaoRPS(IdStatusAprovacao);

    PRINT '✓ Índice criado';
END
ELSE
BEGIN
    PRINT '⚠ Índice já existe';
END

PRINT '';

-- =====================================================
-- RESUMO FINAL
-- =====================================================
PRINT '';
PRINT '========================================================';
PRINT '  RESUMO DA MIGRAÇÃO';
PRINT '========================================================';
PRINT '';

SELECT
    s.Codigo AS Status,
    s.Descricao,
    COUNT(a.ID) AS TotalRegistros,
    CASE
        WHEN (SELECT COUNT(*) FROM TB_AprovacaoRPS) = 0 THEN 0
        ELSE CAST(COUNT(a.ID) * 100.0 / (SELECT COUNT(*) FROM TB_AprovacaoRPS) AS DECIMAL(5,2))
    END AS Percentual
FROM TB_StatusAprovacao s
LEFT JOIN TB_AprovacaoRPS a ON a.IdStatusAprovacao = s.ID
GROUP BY s.ID, s.Codigo, s.Descricao, s.Ordem
ORDER BY s.Ordem;

PRINT '';
PRINT '========================================================';
PRINT '  ✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!';
PRINT '========================================================';
PRINT '';
PRINT 'Concluída em: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';
PRINT '⚠️ PRÓXIMOS PASSOS:';
PRINT '   1. Reiniciar o servidor backend (uvicorn)';
PRINT '   2. Testar endpoint GET /financeiro/rps';
PRINT '   3. Verificar se os RPS estão carregando corretamente';
PRINT '';

SET NOCOUNT OFF;
GO
