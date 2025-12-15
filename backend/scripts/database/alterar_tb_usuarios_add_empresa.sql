-- ================================================================
-- Script de Alteração da Tabela TB_Usuarios
-- ================================================================
-- Descrição: Adiciona campo IDEmpresa para relacionar usuários
--            com suas empresas/filiais
-- Autor: Sistema MetaRH Conecta
-- Data: 2025-01-29
-- ================================================================

USE [PortalCliente]
GO

PRINT '================================================================';
PRINT 'Iniciando alteração da TB_Usuarios...';
PRINT '================================================================';

-- Verificar se a coluna IDEmpresa já existe
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID(N'[dbo].[TB_Usuarios]')
    AND name = 'IDEmpresa'
)
BEGIN
    PRINT 'Adicionando coluna IDEmpresa...';

    -- Adicionar coluna IDEmpresa (nullable inicialmente)
    ALTER TABLE [dbo].[TB_Usuarios]
    ADD [IDEmpresa] INT NULL;

    PRINT 'Coluna IDEmpresa adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Coluna IDEmpresa já existe.';
END
GO

-- Verificar se a constraint FK já existe
IF NOT EXISTS (
    SELECT * FROM sys.foreign_keys
    WHERE name = 'FK_TB_Usuarios_Empresa'
)
BEGIN
    PRINT 'Adicionando constraint FK_TB_Usuarios_Empresa...';

    -- Adicionar Foreign Key para TB_Empresas
    ALTER TABLE [dbo].[TB_Usuarios]
    ADD CONSTRAINT [FK_TB_Usuarios_Empresa]
    FOREIGN KEY ([IDEmpresa])
    REFERENCES [dbo].[TB_Empresas]([ID]);

    PRINT 'Constraint FK_TB_Usuarios_Empresa adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Constraint FK_TB_Usuarios_Empresa já existe.';
END
GO

-- Verificar se o índice já existe
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_TB_Usuarios_IDEmpresa'
    AND object_id = OBJECT_ID(N'[dbo].[TB_Usuarios]')
)
BEGIN
    PRINT 'Criando índice IX_TB_Usuarios_IDEmpresa...';

    -- Criar índice para otimizar buscas por empresa
    CREATE NONCLUSTERED INDEX [IX_TB_Usuarios_IDEmpresa]
        ON [dbo].[TB_Usuarios] ([IDEmpresa] ASC)
        INCLUDE ([Nome], [Email], [TipoAcesso], [Status]);

    PRINT 'Índice IX_TB_Usuarios_IDEmpresa criado com sucesso!';
END
ELSE
BEGIN
    PRINT 'Índice IX_TB_Usuarios_IDEmpresa já existe.';
END
GO

-- Adicionar comentário na coluna
IF NOT EXISTS (
    SELECT * FROM sys.extended_properties
    WHERE major_id = OBJECT_ID(N'[dbo].[TB_Usuarios]')
    AND name = N'MS_Description'
    AND minor_id = (
        SELECT column_id FROM sys.columns
        WHERE object_id = OBJECT_ID(N'[dbo].[TB_Usuarios]')
        AND name = 'IDEmpresa'
    )
)
BEGIN
    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'ID da empresa à qual o usuário pertence (FK para TB_Empresas). Usado para filtros de segurança.',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Usuarios',
        @level2type=N'COLUMN', @level2name=N'IDEmpresa';

    PRINT 'Comentário adicionado à coluna IDEmpresa.';
END
GO

PRINT '================================================================';
PRINT 'Alteração da TB_Usuarios concluída com sucesso!';
PRINT '================================================================';
PRINT '';
PRINT 'PRÓXIMOS PASSOS:';
PRINT '1. Execute o script criar_tb_empresas.sql (se ainda não executou)';
PRINT '2. Popule a tabela TB_Empresas com os dados das empresas';
PRINT '3. Atualize o campo IDEmpresa dos usuários existentes:';
PRINT '   UPDATE TB_Usuarios SET IDEmpresa = [ID_DA_EMPRESA] WHERE Email = ''usuario@email.com''';
PRINT '';
PRINT 'EXEMPLO DE QUERY PARA VINCULAR USUÁRIOS:';
PRINT '   -- Vincular usuário a uma empresa específica';
PRINT '   UPDATE TB_Usuarios';
PRINT '   SET IDEmpresa = (SELECT ID FROM TB_Empresas WHERE CodigoCliente = ''1001'')';
PRINT '   WHERE Email = ''usuario@empresa.com'';';
PRINT '================================================================';
GO
