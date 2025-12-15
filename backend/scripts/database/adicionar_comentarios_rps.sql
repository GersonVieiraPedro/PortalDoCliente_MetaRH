-- ================================================================
-- Script de Documentação - Esclarecimento dos Campos RPS
-- ================================================================
-- Descrição: Adiciona comentários explicativos para evitar confusão
--            entre Duplicata (número da RPS) e NumeroRPS (legacy)
-- Autor: Sistema MetaRH Conecta
-- Data: 2025-01-26
-- Versão: 1.0
-- ================================================================

USE [PortalCliente]
GO

PRINT '========================================';
PRINT 'Iniciando adição de comentários...';
PRINT '========================================';
PRINT '';

-- ================================================================
-- TABELA TB_Duplicata - Esclarecimento dos campos
-- ================================================================

PRINT 'Processando TB_Duplicata...';

-- Campo Duplicata (parte da chave primária) - ESTE É O NÚMERO DA RPS
IF EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID('dbo.TB_Duplicata')
    AND minor_id = (SELECT column_id FROM sys.columns WHERE name = 'Duplicata' AND object_id = OBJECT_ID('dbo.TB_Duplicata'))
    AND name = 'MS_Description'
)
BEGIN
    EXEC sys.sp_dropextendedproperty
        @name=N'MS_Description',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Duplicata',
        @level2type=N'COLUMN', @level2name=N'Duplicata';
    PRINT '  - Comentário antigo de Duplicata removido';
END

EXEC sys.sp_addextendedproperty
    @name=N'MS_Description',
    @value=N'Número da RPS (Recibo Provisório de Serviço). Este é o identificador principal da RPS no sistema. Parte da chave primária composta junto com CodigoEmpresaFat e CodigoFilialFat.',
    @level0type=N'SCHEMA', @level0name=N'dbo',
    @level1type=N'TABLE', @level1name=N'TB_Duplicata',
    @level2type=N'COLUMN', @level2name=N'Duplicata';
PRINT '  ✅ Duplicata: Comentário adicionado (NÚMERO DA RPS)';

-- Campo NroNFe - Número da Nota Fiscal (emitida APÓS aprovação da RPS)
IF EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID('dbo.TB_Duplicata')
    AND minor_id = (SELECT column_id FROM sys.columns WHERE name = 'NroNFe' AND object_id = OBJECT_ID('dbo.TB_Duplicata'))
    AND name = 'MS_Description'
)
BEGIN
    EXEC sys.sp_dropextendedproperty
        @name=N'MS_Description',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Duplicata',
        @level2type=N'COLUMN', @level2name=N'NroNFe';
    PRINT '  - Comentário antigo de NroNFe removido';
END

EXEC sys.sp_addextendedproperty
    @name=N'MS_Description',
    @value=N'Número da Nota Fiscal Eletrônica (NFe). Preenchido APÓS a aprovação da RPS e emissão da NF. Campo diferente do número da RPS (que está no campo Duplicata).',
    @level0type=N'SCHEMA', @level0name=N'dbo',
    @level1type=N'TABLE', @level1name=N'TB_Duplicata',
    @level2type=N'COLUMN', @level2name=N'NroNFe';
PRINT '  ✅ NroNFe: Comentário adicionado (NÚMERO DA NOTA FISCAL)';

-- Campo NumeroRPS - DEPRECATED/LEGACY
IF EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID('dbo.TB_Duplicata')
    AND minor_id = (SELECT column_id FROM sys.columns WHERE name = 'NumeroRPS' AND object_id = OBJECT_ID('dbo.TB_Duplicata'))
    AND name = 'MS_Description'
)
BEGIN
    EXEC sys.sp_dropextendedproperty
        @name=N'MS_Description',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Duplicata',
        @level2type=N'COLUMN', @level2name=N'NumeroRPS';
    PRINT '  - Comentário antigo de NumeroRPS removido';
END

EXEC sys.sp_addextendedproperty
    @name=N'MS_Description',
    @value=N'[DEPRECATED] Campo legacy do sistema antigo. O número real da RPS está no campo Duplicata. Este campo é mantido apenas para compatibilidade temporária com sistemas legados.',
    @level0type=N'SCHEMA', @level0name=N'dbo',
    @level1type=N'TABLE', @level1name=N'TB_Duplicata',
    @level2type=N'COLUMN', @level2name=N'NumeroRPS';
PRINT '  ⚠️ NumeroRPS: Comentário adicionado (DEPRECATED/LEGACY)';

PRINT '';

-- ================================================================
-- TABELA TB_AprovacaoRPS - Esclarecimento do campo Duplicata
-- ================================================================

PRINT 'Processando TB_AprovacaoRPS...';

-- Campo Duplicata
IF EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
    AND minor_id = (SELECT column_id FROM sys.columns WHERE name = 'Duplicata' AND object_id = OBJECT_ID('dbo.TB_AprovacaoRPS'))
    AND name = 'MS_Description'
)
BEGIN
    EXEC sys.sp_dropextendedproperty
        @name=N'MS_Description',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
        @level2type=N'COLUMN', @level2name=N'Duplicata';
    PRINT '  - Comentário antigo de Duplicata removido';
END

EXEC sys.sp_addextendedproperty
    @name=N'MS_Description',
    @value=N'Número da Duplicata (que representa o número da RPS). Parte da chave composta que identifica a RPS na TB_Duplicata junto com CodigoEmpresaFat e CodigoFilialFat.',
    @level0type=N'SCHEMA', @level0name=N'dbo',
    @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
    @level2type=N'COLUMN', @level2name=N'Duplicata';
PRINT '  ✅ Duplicata: Comentário adicionado';

-- Campo NumeroRPS na TB_AprovacaoRPS
IF EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
    AND minor_id = (SELECT column_id FROM sys.columns WHERE name = 'NumeroRPS' AND object_id = OBJECT_ID('dbo.TB_AprovacaoRPS'))
    AND name = 'MS_Description'
)
BEGIN
    EXEC sys.sp_dropextendedproperty
        @name=N'MS_Description',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
        @level2type=N'COLUMN', @level2name=N'NumeroRPS';
    PRINT '  - Comentário antigo de NumeroRPS removido';
END

EXEC sys.sp_addextendedproperty
    @name=N'MS_Description',
    @value=N'[REDUNDANTE] Cópia do campo NumeroRPS da TB_Duplicata para facilitar buscas. O identificador principal da RPS é o campo Duplicata. Este campo pode ser removido em versões futuras.',
    @level0type=N'SCHEMA', @level0name=N'dbo',
    @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
    @level2type=N'COLUMN', @level2name=N'NumeroRPS';
PRINT '  ⚠️ NumeroRPS: Comentário adicionado (REDUNDANTE)';

PRINT '';
PRINT '========================================';
PRINT '✅ COMENTÁRIOS ADICIONADOS COM SUCESSO!';
PRINT '========================================';
PRINT '';
PRINT '📝 RESUMO:';
PRINT '  • TB_Duplicata.Duplicata = Número da RPS (identificador principal)';
PRINT '  • TB_Duplicata.NroNFe = Número da Nota Fiscal (emitida após aprovação)';
PRINT '  • TB_Duplicata.NumeroRPS = Campo legacy (deprecated)';
PRINT '  • TB_AprovacaoRPS.Duplicata = Referência ao número da RPS';
PRINT '  • TB_AprovacaoRPS.NumeroRPS = Campo redundante';
PRINT '';
PRINT '✅ Script executado com sucesso!';
PRINT '';

GO

-- ================================================================
-- Queries de Verificação (opcional)
-- ================================================================

-- Descomentar para verificar os comentários adicionados

/*
PRINT 'Verificando comentários em TB_Duplicata...';
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

PRINT '';
PRINT 'Verificando comentários em TB_AprovacaoRPS...';
SELECT
    c.name AS ColumnName,
    ep.value AS Description
FROM sys.columns c
LEFT JOIN sys.extended_properties ep
    ON ep.major_id = c.object_id
    AND ep.minor_id = c.column_id
    AND ep.name = 'MS_Description'
WHERE c.object_id = OBJECT_ID('dbo.TB_AprovacaoRPS')
    AND c.name IN ('Duplicata', 'NumeroRPS')
ORDER BY c.column_id;
*/
