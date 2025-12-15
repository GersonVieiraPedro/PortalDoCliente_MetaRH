-- ================================================================
-- Script de Criação da Tabela TB_Contratos
-- ================================================================
-- Descrição: Tabela para gestão de contratos dos clientes
-- Sistema: Portal do Cliente MetaRH
-- Data: 2025-01-30
-- ================================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TB_Contratos]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[TB_Contratos] (
        -- ============================================================
        -- Chave Primária
        -- ============================================================
        [ID] INT IDENTITY(1,1) NOT NULL,

        -- ============================================================
        -- Relacionamento com Cliente/Empresa
        -- ============================================================
        [CodigoCliente] INT NOT NULL,

        -- ============================================================
        -- Campos Principais do Contrato
        -- ============================================================
        [NumeroContrato] NVARCHAR(50) NOT NULL,
        [CNPJ] NVARCHAR(18) NOT NULL,
        [RazaoSocial] NVARCHAR(200) NOT NULL,
        [ServicosContemplados] NVARCHAR(MAX) NOT NULL,

        -- ============================================================
        -- Datas e Vigência
        -- ============================================================
        [DataAssinatura] DATE NOT NULL,
        [Vigencia] NVARCHAR(100) NULL,  -- Ex: "12 meses", "Indeterminado", "24 meses"
        [DataVencimento] DATE NULL,

        -- ============================================================
        -- Informações Financeiras
        -- ============================================================
        [Valor] DECIMAL(18,2) NULL,

        -- ============================================================
        -- Status e Controle
        -- ============================================================
        [Status] VARCHAR(20) NOT NULL DEFAULT 'A',  -- A=Ativo, I=Inativo

        -- ============================================================
        -- Arquivo PDF (Azure Blob Storage)
        -- ============================================================
        [ArquivoPDF] NVARCHAR(500) NULL,  -- URL do arquivo no Azure Blob

        -- ============================================================
        -- Auditoria
        -- ============================================================
        [DataCadastro] DATETIME NOT NULL DEFAULT GETDATE(),
        [DataAtualizacao] DATETIME NOT NULL DEFAULT GETDATE(),

        -- ============================================================
        -- Constraints
        -- ============================================================
        CONSTRAINT [PK_TB_Contratos] PRIMARY KEY CLUSTERED ([ID] ASC),
        CONSTRAINT [CK_TB_Contratos_Status]
            CHECK ([Status] IN ('A', 'I'))  -- A=Ativo, I=Inativo
    );

    PRINT 'Tabela TB_Contratos criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Contratos já existe.';
END
GO

-- ================================================================
-- Índices para Performance
-- ================================================================

-- Índice principal: filtro por cliente
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TB_Contratos_CodigoCliente' AND object_id = OBJECT_ID('TB_Contratos'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TB_Contratos_CodigoCliente]
        ON [dbo].[TB_Contratos] ([CodigoCliente] ASC)
        INCLUDE ([Status], [DataAssinatura], [CNPJ], [NumeroContrato]);

    PRINT 'Índice IX_TB_Contratos_CodigoCliente criado.';
END
GO

-- Índice composto: filtros comuns (cliente + data)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TB_Contratos_Cliente_Data' AND object_id = OBJECT_ID('TB_Contratos'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TB_Contratos_Cliente_Data]
        ON [dbo].[TB_Contratos] ([CodigoCliente] ASC, [DataAssinatura] DESC)
        INCLUDE ([Status], [Valor], [CNPJ]);

    PRINT 'Índice IX_TB_Contratos_Cliente_Data criado.';
END
GO

-- Índice para busca por CNPJ
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TB_Contratos_CNPJ' AND object_id = OBJECT_ID('TB_Contratos'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TB_Contratos_CNPJ]
        ON [dbo].[TB_Contratos] ([CNPJ] ASC)
        INCLUDE ([Status], [CodigoCliente]);

    PRINT 'Índice IX_TB_Contratos_CNPJ criado.';
END
GO

-- Índice para filtro por status
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TB_Contratos_Status' AND object_id = OBJECT_ID('TB_Contratos'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TB_Contratos_Status]
        ON [dbo].[TB_Contratos] ([Status] ASC, [DataAssinatura] DESC)
        INCLUDE ([CodigoCliente], [CNPJ]);

    PRINT 'Índice IX_TB_Contratos_Status criado.';
END
GO

-- ================================================================
-- Trigger para atualizar DataAtualizacao automaticamente
-- ================================================================

IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Contratos_UpdateTimestamp')
BEGIN
    EXEC('
    CREATE TRIGGER [dbo].[TR_TB_Contratos_UpdateTimestamp]
    ON [dbo].[TB_Contratos]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;

        UPDATE [dbo].[TB_Contratos]
        SET [DataAtualizacao] = GETDATE()
        FROM [dbo].[TB_Contratos] t
        INNER JOIN inserted i ON t.ID = i.ID;
    END
    ');

    PRINT 'Trigger TR_TB_Contratos_UpdateTimestamp criado com sucesso!';
END
GO

-- ================================================================
-- Comentários sobre a tabela
-- ================================================================

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Tabela de contratos dos clientes do Portal MetaRH',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'TB_Contratos';
GO

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Código do cliente (FK lógica para TB_Empresas.CodigoCliente)',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'TB_Contratos',
    @level2type = N'COLUMN', @level2name = N'CodigoCliente';
GO

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Status do contrato: A=Ativo, I=Inativo',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'TB_Contratos',
    @level2type = N'COLUMN', @level2name = N'Status';
GO

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'URL do arquivo PDF do contrato no Azure Blob Storage',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'TB_Contratos',
    @level2type = N'COLUMN', @level2name = N'ArquivoPDF';
GO

PRINT '';
PRINT '================================================================';
PRINT 'Script concluído com sucesso!';
PRINT 'Tabela: TB_Contratos';
PRINT 'Índices: 4 índices criados';
PRINT 'Trigger: TR_TB_Contratos_UpdateTimestamp';
PRINT '================================================================';
GO
