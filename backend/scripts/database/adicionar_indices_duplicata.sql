-- ================================================================
-- Script de Performance - Índices para Busca por Duplicata
-- ================================================================
-- Descrição: Adiciona índices para otimizar buscas por número da RPS
--            (campo Duplicata) na tabela TB_Duplicata
-- Autor: Sistema MetaRH Conecta
-- Data: 2025-01-26
-- Versão: 1.0
-- ================================================================

USE [PortalCliente]
GO

PRINT '========================================';
PRINT 'Iniciando criação de índices...';
PRINT '========================================';
PRINT '';

-- ================================================================
-- VERIFICAR E CRIAR ÍNDICE PARA DUPLICATA
-- ================================================================

PRINT 'Processando índice IX_TB_Duplicata_Duplicata...';

-- Verificar se já existe índice para Duplicata isoladamente
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_TB_Duplicata_Duplicata'
    AND object_id = OBJECT_ID('dbo.TB_Duplicata')
)
BEGIN
    PRINT '  - Criando índice IX_TB_Duplicata_Duplicata...';

    CREATE NONCLUSTERED INDEX [IX_TB_Duplicata_Duplicata]
        ON [dbo].[TB_Duplicata] ([Duplicata] ASC)
        INCLUDE (
            [CodigoEmpresaFat],
            [CodigoFilialFat],
            [DataEmissao],
            [DataVecto],
            [NroNFe],
            [ValorBruto],
            [Status]
        );

    PRINT '  ✅ Índice IX_TB_Duplicata_Duplicata criado com sucesso!';
    PRINT '';
    PRINT '  📊 Benefícios:';
    PRINT '    - Busca rápida por número da RPS (Duplicata)';
    PRINT '    - Campos incluídos (INCLUDE) evitam Key Lookup';
    PRINT '    - Melhora performance das APIs de listagem e detalhes';
END
ELSE
BEGIN
    PRINT '  ℹ️ Índice IX_TB_Duplicata_Duplicata já existe';

    -- Verificar se o índice tem os campos INCLUDE corretos
    DECLARE @IncludeColumns NVARCHAR(MAX);

    SELECT @IncludeColumns = STUFF((
        SELECT ', ' + c.name
        FROM sys.index_columns ic
        INNER JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
        WHERE ic.object_id = OBJECT_ID('dbo.TB_Duplicata')
            AND ic.index_id = (SELECT index_id FROM sys.indexes WHERE name = 'IX_TB_Duplicata_Duplicata' AND object_id = OBJECT_ID('dbo.TB_Duplicata'))
            AND ic.is_included_column = 1
        ORDER BY ic.key_ordinal
        FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '');

    IF @IncludeColumns IS NOT NULL
    BEGIN
        PRINT '  📋 Colunas incluídas no índice: ' + @IncludeColumns;
    END
    ELSE
    BEGIN
        PRINT '  ⚠️ Índice não possui colunas INCLUDE';
        PRINT '  💡 Considere recriar o índice com colunas INCLUDE para melhor performance';
    END
END

PRINT '';

-- ================================================================
-- VERIFICAR ÍNDICE COMPOSTO (Chave Primária Completa)
-- ================================================================

PRINT 'Verificando índice para chave composta...';

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_TB_Duplicata_ChaveComposta'
    AND object_id = OBJECT_ID('dbo.TB_Duplicata')
)
BEGIN
    PRINT '  - Criando índice IX_TB_Duplicata_ChaveComposta...';

    CREATE NONCLUSTERED INDEX [IX_TB_Duplicata_ChaveComposta]
        ON [dbo].[TB_Duplicata] (
            [CodigoEmpresaFat] ASC,
            [CodigoFilialFat] ASC,
            [Duplicata] ASC
        )
        INCLUDE (
            [DataEmissao],
            [DataVecto],
            [NroNFe],
            [ValorBruto],
            [Status]
        );

    PRINT '  ✅ Índice IX_TB_Duplicata_ChaveComposta criado com sucesso!';
    PRINT '';
    PRINT '  📊 Benefícios:';
    PRINT '    - Busca otimizada usando chave primária completa';
    PRINT '    - Útil para endpoints de aprovação/reprovação';
    PRINT '    - Melhora performance de JOINs com TB_AprovacaoRPS';
END
ELSE
BEGIN
    PRINT '  ℹ️ Índice IX_TB_Duplicata_ChaveComposta já existe';
END

PRINT '';

-- ================================================================
-- VERIFICAR STATUS DOS ÍNDICES
-- ================================================================

PRINT 'Status dos índices em TB_Duplicata:';
PRINT '';

SELECT
    i.name AS IndexName,
    i.type_desc AS IndexType,
    i.is_unique AS IsUnique,
    STUFF((
        SELECT ', ' + c.name + CASE WHEN ic.is_descending_key = 1 THEN ' DESC' ELSE ' ASC' END
        FROM sys.index_columns ic
        INNER JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
        WHERE ic.object_id = i.object_id
            AND ic.index_id = i.index_id
            AND ic.is_included_column = 0
        ORDER BY ic.key_ordinal
        FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS KeyColumns,
    STUFF((
        SELECT ', ' + c.name
        FROM sys.index_columns ic
        INNER JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
        WHERE ic.object_id = i.object_id
            AND ic.index_id = i.index_id
            AND ic.is_included_column = 1
        ORDER BY ic.key_ordinal
        FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS IncludeColumns
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.TB_Duplicata')
    AND i.name IS NOT NULL
    AND i.name LIKE '%Duplicata%'
ORDER BY i.name;

PRINT '';
PRINT '========================================';
PRINT '✅ ÍNDICES PROCESSADOS COM SUCESSO!';
PRINT '========================================';
PRINT '';
PRINT '📝 RECOMENDAÇÕES:';
PRINT '  1. Monitorar uso dos índices após deploy';
PRINT '  2. Analisar planos de execução das queries';
PRINT '  3. Ajustar colunas INCLUDE se necessário';
PRINT '  4. Considerar reorganizar/rebuild após carga de dados';
PRINT '';
PRINT '✅ Script executado com sucesso!';
PRINT '';

GO

-- ================================================================
-- Queries de Análise (opcional)
-- ================================================================

-- Descomentar para analisar uso dos índices após algum tempo em produção

/*
PRINT 'Estatísticas de uso dos índices em TB_Duplicata:';
SELECT
    OBJECT_NAME(s.object_id) AS TableName,
    i.name AS IndexName,
    s.user_seeks AS UserSeeks,
    s.user_scans AS UserScans,
    s.user_lookups AS UserLookups,
    s.user_updates AS UserUpdates,
    s.last_user_seek AS LastUserSeek,
    s.last_user_scan AS LastUserScan
FROM sys.dm_db_index_usage_stats s
INNER JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE s.database_id = DB_ID()
    AND OBJECT_NAME(s.object_id) = 'TB_Duplicata'
    AND i.name LIKE '%Duplicata%'
ORDER BY i.name;
*/
