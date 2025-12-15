-- ================================================================
-- Script: Remover campo NumeroRPS da tabela TB_AprovacaoRPS
-- ================================================================
-- Data: 2025-01-27
-- Autor: Refatoração RPS
-- Objetivo: Remover campo legacy NumeroRPS da TB_AprovacaoRPS
--
-- CONTEXTO:
-- O campo NumeroRPS era uma cópia redundante do campo da TB_Duplicata
-- Com a refatoração, o campo Duplicata é o identificador correto da RPS
-- Este campo não é mais necessário e deve ser removido
--
-- IMPACTO:
-- - Remoção de coluna (breaking change para queries diretas ao banco)
-- - Backend já atualizado para não usar este campo
-- - Índice IX_TB_AprovacaoRPS_NumeroRPS será removido automaticamente
--
-- PRÉ-REQUISITOS:
-- 1. Backend atualizado e deployado
-- 2. Backup do banco de dados realizado
-- ================================================================

USE [PortalCliente]
GO

SET NOCOUNT ON;

PRINT '========================================';
PRINT 'Remoção do campo NumeroRPS';
PRINT 'Tabela: TB_AprovacaoRPS';
PRINT '========================================';
PRINT '';

-- ================================================================
-- VALIDAÇÕES PRÉ-EXECUÇÃO
-- ================================================================

PRINT 'Validando pré-requisitos...';
PRINT '';

-- Verificar se a tabela existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_AprovacaoRPS')
BEGIN
    PRINT '❌ ERRO: Tabela TB_AprovacaoRPS não encontrada';
    RAISERROR('Tabela TB_AprovacaoRPS não existe', 16, 1);
    RETURN;
END

-- Verificar se a coluna existe
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
    AND name = 'NumeroRPS'
)
BEGIN
    PRINT '⚠️ AVISO: Coluna NumeroRPS não existe em TB_AprovacaoRPS';
    PRINT 'Script já foi executado anteriormente ou coluna nunca existiu.';
    PRINT '';
    PRINT '✅ Nenhuma ação necessária';
    RETURN;
END

PRINT '✅ Tabela e coluna encontradas';
PRINT '';

-- ================================================================
-- INÍCIO DA TRANSAÇÃO
-- ================================================================

BEGIN TRANSACTION RemoverNumeroRPS;

BEGIN TRY

    PRINT 'Iniciando remoção da coluna NumeroRPS...';
    PRINT '';

    -- ================================================================
    -- PASSO 1: Verificar e remover índices que usam a coluna
    -- ================================================================

    PRINT '📋 Passo 1: Verificando índices...';
    PRINT '';

    -- Listar índices que usam NumeroRPS
    DECLARE @NomeIndice NVARCHAR(200);
    DECLARE cursor_indices CURSOR FOR
        SELECT DISTINCT i.name
        FROM sys.indexes i
        INNER JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
        INNER JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
        WHERE i.object_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
            AND c.name = 'NumeroRPS'
            AND i.name IS NOT NULL;

    OPEN cursor_indices;
    FETCH NEXT FROM cursor_indices INTO @NomeIndice;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        PRINT '  - Removendo índice: ' + @NomeIndice;

        DECLARE @SqlDropIndex NVARCHAR(500);
        SET @SqlDropIndex = 'DROP INDEX [' + @NomeIndice + '] ON [dbo].[TB_AprovacaoRPS]';

        EXEC sp_executesql @SqlDropIndex;

        PRINT '    ✅ Índice removido';

        FETCH NEXT FROM cursor_indices INTO @NomeIndice;
    END

    CLOSE cursor_indices;
    DEALLOCATE cursor_indices;

    PRINT '';
    PRINT '✅ Índices verificados e removidos (se existiam)';
    PRINT '';

    -- ================================================================
    -- PASSO 2: Remover a coluna NumeroRPS
    -- ================================================================

    PRINT '📋 Passo 2: Removendo coluna NumeroRPS...';
    PRINT '';

    ALTER TABLE [dbo].[TB_AprovacaoRPS]
    DROP COLUMN [NumeroRPS];

    PRINT '  ✅ Coluna NumeroRPS removida com sucesso';
    PRINT '';

    -- ================================================================
    -- PASSO 3: Verificar índice composto (deve continuar existindo)
    -- ================================================================

    PRINT '📋 Passo 3: Verificando índice composto...';
    PRINT '';

    IF EXISTS (
        SELECT * FROM sys.indexes
        WHERE object_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
        AND name = 'IX_TB_AprovacaoRPS_ChaveComposta'
    )
    BEGIN
        PRINT '  ✅ Índice composto IX_TB_AprovacaoRPS_ChaveComposta está intacto';
    END
    ELSE
    BEGIN
        PRINT '  ⚠️ AVISO: Índice composto não encontrado';
        PRINT '  Criando índice composto para performance...';

        CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_ChaveComposta]
        ON [dbo].[TB_AprovacaoRPS] (
            [CodigoEmpresaFat] ASC,
            [CodigoFilialFat] ASC,
            [Duplicata] ASC,
            [DataAcao] DESC
        )
        INCLUDE ([StatusAprovacao], [TipoAcao]);

        PRINT '  ✅ Índice composto criado';
    END

    PRINT '';

    -- ================================================================
    -- COMMIT DA TRANSAÇÃO
    -- ================================================================

    COMMIT TRANSACTION RemoverNumeroRPS;

    PRINT '========================================';
    PRINT '✅ REMOÇÃO CONCLUÍDA COM SUCESSO!';
    PRINT '========================================';
    PRINT '';
    PRINT '📊 ALTERAÇÕES REALIZADAS:';
    PRINT '  ✅ Coluna NumeroRPS removida de TB_AprovacaoRPS';
    PRINT '  ✅ Índices dependentes removidos';
    PRINT '  ✅ Índice composto verificado/criado';
    PRINT '';
    PRINT '⚠️ PRÓXIMOS PASSOS:';
    PRINT '  1. Verificar que o backend está funcionando corretamente';
    PRINT '  2. Testar aprovação/reprovação de RPS';
    PRINT '  3. Verificar histórico de aprovações';
    PRINT '';
    PRINT '✅ Script executado com sucesso!';
    PRINT '';

END TRY
BEGIN CATCH

    -- ================================================================
    -- ROLLBACK EM CASO DE ERRO
    -- ================================================================

    ROLLBACK TRANSACTION RemoverNumeroRPS;

    PRINT '';
    PRINT '========================================';
    PRINT '❌ ERRO DURANTE A REMOÇÃO!';
    PRINT '========================================';
    PRINT '';
    PRINT 'TRANSAÇÃO REVERTIDA (ROLLBACK)';
    PRINT '';
    PRINT 'Detalhes do erro:';
    PRINT '  Número: ' + CAST(ERROR_NUMBER() AS VARCHAR(10));
    PRINT '  Mensagem: ' + ERROR_MESSAGE();
    PRINT '  Linha: ' + CAST(ERROR_LINE() AS VARCHAR(10));
    PRINT '  Procedimento: ' + ISNULL(ERROR_PROCEDURE(), 'Script principal');
    PRINT '';
    PRINT '🔄 O banco de dados foi revertido ao estado anterior';
    PRINT '📞 Contate o DBA se o problema persistir';
    PRINT '';

    -- Re-throw do erro
    THROW;

END CATCH

GO

-- ================================================================
-- Queries de Verificação (executar após sucesso)
-- ================================================================

PRINT 'Verificando estrutura da tabela após remoção...';
PRINT '';

-- Verificar colunas restantes
SELECT
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable
FROM sys.columns c
INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
    AND c.name IN ('CodigoEmpresaFat', 'CodigoFilialFat', 'Duplicata', 'NumeroRPS')
ORDER BY c.column_id;

PRINT '';

-- Verificar índices
SELECT
    i.name AS IndexName,
    i.type_desc AS IndexType
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
    AND i.name IS NOT NULL
ORDER BY i.name;

GO
