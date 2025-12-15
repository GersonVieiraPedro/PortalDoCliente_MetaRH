-- =====================================================
-- Script: Criar Tabela de Domínio para Status de Aprovação
-- Descrição: Cria TB_StatusAprovacao para normalizar os status
--            e melhorar performance em consultas e filtros
-- Data: 2025-10-29
-- =====================================================

USE PortalCliente;
GO

-- Criar tabela de domínio para status de aprovação
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

    PRINT 'Tabela TB_StatusAprovacao criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela TB_StatusAprovacao já existe.';
END
GO

-- Adicionar comentários nas colunas (SQL Server Extended Properties)
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Tabela de domínio para status de aprovação de RPS. Normaliza os valores de status para melhorar performance.',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_StatusAprovacao';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Identificador único do status (chave primária)',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_StatusAprovacao',
    @level2type = N'COLUMN', @level2name = 'ID';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Código do status (pendente, aprovado, reprovado) - usado nas queries',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_StatusAprovacao',
    @level2type = N'COLUMN', @level2name = 'Codigo';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Descrição legível do status',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_StatusAprovacao',
    @level2type = N'COLUMN', @level2name = 'Descricao';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Indica se o status está ativo no sistema',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_StatusAprovacao',
    @level2type = N'COLUMN', @level2name = 'Ativo';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Ordem de exibição do status (para ordenação em interfaces)',
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'TB_StatusAprovacao',
    @level2type = N'COLUMN', @level2name = 'Ordem';
GO

-- Inserir valores de domínio
INSERT INTO TB_StatusAprovacao (Codigo, Descricao, Ativo, Ordem)
VALUES
    ('pendente', 'Pendente de Aprovação', 1, 1),
    ('aprovado', 'Aprovado', 1, 2),
    ('reprovado', 'Reprovado', 1, 3);
GO

PRINT 'Valores de domínio inseridos com sucesso!';
PRINT '';
PRINT 'Status disponíveis:';
SELECT ID, Codigo, Descricao, Ordem FROM TB_StatusAprovacao ORDER BY Ordem;
GO
