-- ================================================================
-- Script de Criação da Tabela TB_AprovacaoRPS
-- ================================================================
-- Descrição: Tabela para controle de aprovações e reprovações de RPS
--            Mantém histórico completo de todas as ações (relação 1:N)
--            Não modifica a tabela TB_Duplicata (sistema legado)
-- Autor: Sistema MetaRH Conecta
-- Data: 2025-01-17
-- ================================================================

-- Verificar se a tabela já existe antes de criar
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TB_AprovacaoRPS]') AND type in (N'U'))
BEGIN

    CREATE TABLE [dbo].[TB_AprovacaoRPS] (
        -- Chave Primária
        [ID] INT IDENTITY(1,1) NOT NULL,

        -- Relacionamento com TB_Duplicata (chave composta)
        -- Estes campos fazem referência à chave composta de TB_Duplicata
        [CodigoEmpresaFat] INT NOT NULL,
        [CodigoFilialFat] INT NOT NULL,
        [Duplicata] INT NOT NULL,
        [NumeroRPS] INT NOT NULL,  -- Redundância intencional para facilitar buscas

        -- Status e Tipo de Ação
        [StatusAprovacao] VARCHAR(20) NOT NULL,  -- 'pendente', 'aprovado', 'reprovado'
        [TipoAcao] VARCHAR(20) NOT NULL,         -- 'aprovacao', 'reprovacao', 'cancelamento'

        -- Motivo da Reprovação (obrigatório quando TipoAcao = 'reprovacao')
        [MotivoReprovacao] VARCHAR(100) NULL,
        [DescricaoReprovacao] VARCHAR(500) NULL,

        -- Rastreabilidade - Quem executou a ação
        [ID_Usuario] INT NOT NULL,
        [NomeUsuario] VARCHAR(200) NOT NULL,  -- Denormalizado para preservar histórico
        [EmailUsuario] VARCHAR(200) NOT NULL, -- Denormalizado para preservar histórico

        -- Timestamps
        [DataAcao] DATETIME NOT NULL DEFAULT GETDATE(),
        [DataCadastro] DATETIME NOT NULL DEFAULT GETDATE(),
        [DataAtualizacao] DATETIME NOT NULL DEFAULT GETDATE(),

        -- Constraints
        CONSTRAINT [PK_TB_AprovacaoRPS] PRIMARY KEY CLUSTERED ([ID] ASC),
        CONSTRAINT [FK_TB_AprovacaoRPS_Usuario] FOREIGN KEY ([ID_Usuario])
            REFERENCES [dbo].[TB_Usuarios]([ID]),

        -- Validações de Status
        CONSTRAINT [CK_TB_AprovacaoRPS_StatusAprovacao]
            CHECK ([StatusAprovacao] IN ('pendente', 'aprovado', 'reprovado')),
        CONSTRAINT [CK_TB_AprovacaoRPS_TipoAcao]
            CHECK ([TipoAcao] IN ('aprovacao', 'reprovacao', 'cancelamento'))
    );

    -- ================================================================
    -- Índices para Performance
    -- ================================================================

    -- Índice composto para buscar status atual de um RPS específico
    -- Este é o índice mais importante para a query "pegar última aprovação"
    CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_Duplicata_DataAcao]
        ON [dbo].[TB_AprovacaoRPS] (
            [CodigoEmpresaFat] ASC,
            [CodigoFilialFat] ASC,
            [Duplicata] ASC,
            [DataAcao] DESC
        )
        INCLUDE ([StatusAprovacao], [TipoAcao]);

    -- Índice para busca por NumeroRPS
    CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_NumeroRPS]
        ON [dbo].[TB_AprovacaoRPS] ([NumeroRPS] ASC)
        INCLUDE ([StatusAprovacao], [DataAcao]);

    -- Índice para busca por usuário (auditoria)
    CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_Usuario]
        ON [dbo].[TB_AprovacaoRPS] ([ID_Usuario] ASC, [DataAcao] DESC);

    -- Índice para busca por status (relatórios)
    CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_Status]
        ON [dbo].[TB_AprovacaoRPS] ([StatusAprovacao] ASC, [DataAcao] DESC);

    -- ================================================================
    -- Comentários nas Colunas
    -- ================================================================

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Tabela de controle de aprovações e reprovações de RPS. Mantém histórico completo de todas as ações (1:N). Não modifica TB_Duplicata (tabela legado).',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Chave primária auto-incremento',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
        @level2type=N'COLUMN', @level2name=N'ID';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Status atual: pendente, aprovado ou reprovado',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
        @level2type=N'COLUMN', @level2name=N'StatusAprovacao';

    EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @value=N'Tipo de ação executada: aprovacao, reprovacao ou cancelamento',
        @level0type=N'SCHEMA', @level0name=N'dbo',
        @level1type=N'TABLE', @level1name=N'TB_AprovacaoRPS',
        @level2type=N'COLUMN', @level2name=N'TipoAcao';

    PRINT 'Tabela TB_AprovacaoRPS criada com sucesso!';
    PRINT 'Índices criados para otimização de performance.';

END
ELSE
BEGIN
    PRINT 'Tabela TB_AprovacaoRPS já existe. Nenhuma alteração foi feita.';
END
GO

-- ================================================================
-- Trigger para atualizar DataAtualizacao automaticamente
-- ================================================================

IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_AprovacaoRPS_UpdateTimestamp')
BEGIN
    EXEC('
    CREATE TRIGGER [dbo].[TR_TB_AprovacaoRPS_UpdateTimestamp]
    ON [dbo].[TB_AprovacaoRPS]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;

        UPDATE [dbo].[TB_AprovacaoRPS]
        SET [DataAtualizacao] = GETDATE()
        FROM [dbo].[TB_AprovacaoRPS] t
        INNER JOIN inserted i ON t.ID = i.ID;
    END
    ');

    PRINT 'Trigger TR_TB_AprovacaoRPS_UpdateTimestamp criado com sucesso!';
END
GO

-- ================================================================
-- Queries de Teste (comentadas)
-- ================================================================

-- Descomentar para testar após criação da tabela

/*
-- Verificar estrutura da tabela
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'TB_AprovacaoRPS'
ORDER BY ORDINAL_POSITION;

-- Verificar índices criados
SELECT
    i.name AS IndexName,
    i.type_desc AS IndexType,
    COL_NAME(ic.object_id, ic.column_id) AS ColumnName
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
WHERE i.object_id = OBJECT_ID('TB_AprovacaoRPS')
ORDER BY i.name, ic.key_ordinal;

-- Inserir registro de teste
INSERT INTO TB_AprovacaoRPS (
    CodigoEmpresaFat, CodigoFilialFat, Duplicata, NumeroRPS,
    StatusAprovacao, TipoAcao,
    ID_Usuario, NomeUsuario, EmailUsuario
)
VALUES (
    2, 1, 12345, 93614,
    'aprovado', 'aprovacao',
    1, 'Usuário Teste', 'teste@metarh.com.br'
);

-- Consultar registros
SELECT * FROM TB_AprovacaoRPS ORDER BY DataAcao DESC;

-- Buscar status atual de um RPS específico (query mais comum)
SELECT TOP 1
    StatusAprovacao,
    TipoAcao,
    NomeUsuario,
    DataAcao
FROM TB_AprovacaoRPS
WHERE CodigoEmpresaFat = 2
  AND CodigoFilialFat = 1
  AND Duplicata = 12345
ORDER BY DataAcao DESC;
*/
