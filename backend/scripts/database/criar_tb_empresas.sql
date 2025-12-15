-- ================================================================
-- Script de Criação da Tabela TB_Empresas
-- ================================================================
-- Descrição: Tabela de domínio para armazenar empresas/filiais
--            Permite relacionar usuários com suas empresas e
--            filtrar dados financeiros (RPS, Notas Fiscais)
-- Autor: Sistema MetaRH Conecta
-- Data: 2025-01-29
-- ================================================================

USE [PortalCliente]
GO

-- Verificar se a tabela já existe
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TB_Empresas]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[TB_Empresas] (
        -- Chave Primária
        [ID] INT IDENTITY(1,1) NOT NULL,

        -- Campos de Identificação
        [CodigoCliente] NVARCHAR(50) NOT NULL,
        [CodigoEmpresaFat] INT NOT NULL,
        [CodigoFilialFat] INT NOT NULL,

        -- Dados da Empresa
        [RazaoSocial] NVARCHAR(200) NOT NULL,
        [CNPJ] NVARCHAR(18) NOT NULL,

        -- Controle de Status
        [Ativo] BIT NOT NULL DEFAULT 1,

        -- Timestamps
        [DataCadastro] DATETIME NOT NULL DEFAULT GETDATE(),
        [DataAtualizacao] DATETIME NOT NULL DEFAULT GETDATE(),

        -- Constraints
        CONSTRAINT [PK_TB_Empresas] PRIMARY KEY CLUSTERED ([ID] ASC),
        CONSTRAINT [UQ_TB_Empresas_EmpresaFilial] UNIQUE NONCLUSTERED (
            [CodigoEmpresaFat] ASC,
            [CodigoFilialFat] ASC
        )
    );

    -- Índice para busca por CodigoCliente (filtro principal nas queries)
    CREATE NONCLUSTERED INDEX [IX_TB_Empresas_CodigoCliente]
        ON [dbo].[TB_Empresas] ([CodigoCliente] ASC)
        INCLUDE ([Ativo], [RazaoSocial]);

    -- Índice para busca por CNPJ
    CREATE NONCLUSTERED INDEX [IX_TB_Empresas_CNPJ]
        ON [dbo].[TB_Empresas] ([CNPJ] ASC);

    -- Índice para busca por empresas ativas
    CREATE NONCLUSTERED INDEX [IX_TB_Empresas_Ativo]
        ON [dbo].[TB_Empresas] ([Ativo] ASC)
        INCLUDE ([RazaoSocial], [CNPJ]);

    -- Comentários nas Colunas
    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Tabela de domínio para empresas/filiais. Relaciona usuários com suas empresas para filtros de segurança.',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Identificador único da empresa (PK)',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'ID';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Código do cliente no sistema (vincula com TB_Duplicata.CodigoCliente)',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'CodigoCliente';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Código da empresa faturadora (vincula com TB_Duplicata.CodigoEmpresaFat)',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'CodigoEmpresaFat';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Código da filial faturadora (vincula com TB_Duplicata.CodigoFilialFat)',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'CodigoFilialFat';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Razão Social da empresa',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'RazaoSocial';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'CNPJ da empresa (formato: XX.XXX.XXX/XXXX-XX)',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'CNPJ';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Flag de ativo/inativo (1=Ativo, 0=Inativo)',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_Empresas',
        @level2type=N'COLUMN', @level2name=N'Ativo';

    PRINT 'Tabela TB_Empresas criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Empresas já existe.';
END
GO

-- Trigger para atualizar DataAtualizacao automaticamente
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Empresas_UpdateTimestamp')
BEGIN
    EXEC('
    CREATE TRIGGER [dbo].[TR_TB_Empresas_UpdateTimestamp]
    ON [dbo].[TB_Empresas]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;

        UPDATE [dbo].[TB_Empresas]
        SET [DataAtualizacao] = GETDATE()
        FROM [dbo].[TB_Empresas] t
        INNER JOIN inserted i ON t.ID = i.ID;
    END
    ');

    PRINT 'Trigger TR_TB_Empresas_UpdateTimestamp criado com sucesso!';
END
ELSE
BEGIN
    PRINT 'Trigger TR_TB_Empresas_UpdateTimestamp já existe.';
END
GO

PRINT '================================================================';
PRINT 'Script de criação da TB_Empresas concluído!';
PRINT '================================================================';
GO
