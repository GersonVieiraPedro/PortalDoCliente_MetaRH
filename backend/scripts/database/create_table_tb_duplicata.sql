-- ========================================
-- Script: Criação da Tabela TB_Duplicata
-- Total de colunas: 115
-- ========================================
--
-- IMPORTANTE: Este script apenas CRIA a estrutura da tabela.
-- Para popular os dados, execute o script 'insert_tb_duplicata.sql'
-- ========================================

USE [NomeDoBanco]; -- ALTERE PARA O NOME DO SEU BANCO DE DADOS
GO

-- ========================================
-- 1. DROP DA TABELA SE EXISTIR
-- ========================================
IF OBJECT_ID('dbo.TB_Duplicata', 'U') IS NOT NULL
BEGIN
    PRINT 'Removendo tabela TB_Duplicata existente...';
    DROP TABLE dbo.TB_Duplicata;
    PRINT 'Tabela removida com sucesso.';
END
GO

-- ========================================
-- 2. CRIAÇÃO DA TABELA TB_Duplicata
-- ========================================
PRINT 'Criando tabela TB_Duplicata...';
GO

CREATE TABLE dbo.TB_Duplicata (
    -- Chaves e Identificadores
    CodigoEmpresaFat INT NULL,
    CodigoFilialFat INT NULL,
    Duplicata INT NULL,
    Ordem VARCHAR(10) NULL,
    CodigoEmpresa INT NULL,
    CodigoFilial INT NULL,
    CodigoCliente INT NULL,
    CodigoContrato INT NULL,
    TipoFat INT NULL,
    CodigoCentroCusto INT NULL,
    CodigoVendedor INT NULL,
    CodigoSelecionador INT NULL,
    CodigoRecrutador INT NULL,
    CodigoBanco INT NULL,

    -- Datas
    DataEmissao DATETIME NULL,
    DataVecto DATETIME NULL,
    DataBaixa DATETIME NULL,
    DataCredito DATETIME NULL,
    DataCompetencia VARCHAR(10) NULL,
    DataCompetencia2 VARCHAR(10) NULL,
    DataVectoImp DATETIME NULL,
    DataCadastro DATETIME NULL,
    DataEnvioAviso DATETIME NULL,

    -- Valores Principais
    ValorPagoFolha DECIMAL(18,2) NULL,
    ValorReembolso DECIMAL(18,2) NULL,
    ValorTaxa DECIMAL(18,2) NULL,
    ValorBruto DECIMAL(18,2) NULL,
    ValorLiquido DECIMAL(18,2) NULL,
    ValorLiquidoDS DECIMAL(18,2) NULL,
    ValorLiquidoOri DECIMAL(18,2) NULL,
    ValorBaixa DECIMAL(18,2) NULL,
    ValorBoleto DECIMAL(18,2) NULL,
    ValorBeneficio DECIMAL(18,2) NULL,

    -- Bases de Cálculo
    BaseIRF DECIMAL(18,2) NULL,
    BaseINSS DECIMAL(18,2) NULL,
    BaseISS DECIMAL(18,2) NULL,
    BaseIPI DECIMAL(18,2) NULL,
    BaseTributo DECIMAL(18,2) NULL,
    BasePis DECIMAL(18,2) NULL,
    BaseCofins DECIMAL(18,2) NULL,
    BaseCSLL DECIMAL(18,2) NULL,
    BaseISSReal DECIMAL(18,2) NULL,
    BaseCaucao DECIMAL(18,2) NULL,

    -- Valores de Impostos e Taxas
    ValorIRF DECIMAL(18,2) NULL,
    ValorINSS DECIMAL(18,2) NULL,
    ValorISS DECIMAL(18,2) NULL,
    ValorIPI DECIMAL(18,2) NULL,
    ValorTributo DECIMAL(18,2) NULL,
    ValorPis DECIMAL(18,2) NULL,
    ValorCofins DECIMAL(18,2) NULL,
    ValorCSLL DECIMAL(18,2) NULL,
    ValorCaucao DECIMAL(18,2) NULL,

    -- Valores Adicionais
    ValorJuros DECIMAL(18,2) NULL,
    ValorDesconto DECIMAL(18,2) NULL,
    ValorMulta DECIMAL(18,2) NULL,
    ValorJurosNegociado DECIMAL(18,2) NULL,
    ValorMultaNegociada DECIMAL(18,2) NULL,
    ValorAbatimentoNDB DECIMAL(18,2) NULL,
    ValorVariacaoCambial DECIMAL(18,2) NULL,

    -- Valores Originais
    ValorInssOri DECIMAL(18,2) NULL,
    ValorCsllOri DECIMAL(18,2) NULL,
    ValorPisOri DECIMAL(18,2) NULL,
    ValorIrfOri DECIMAL(18,2) NULL,
    ValorCofinsOri DECIMAL(18,2) NULL,
    ValorIssRetido DECIMAL(18,2) NULL,
    ValorIssRecolhido DECIMAL(18,2) NULL,

    -- Valores de Devolução
    ValorIrfDevBX DECIMAL(18,2) NULL,
    ValorPisDevBX DECIMAL(18,2) NULL,
    ValorCofDevBX DECIMAL(18,2) NULL,
    ValorCsllDevBX DECIMAL(18,2) NULL,
    ValorIssDevBX DECIMAL(18,2) NULL,
    ValorInssDevBX DECIMAL(18,2) NULL,
    ValorOutrasDevBX DECIMAL(18,2) NULL,

    -- Valores de Parcelamento
    ValorBrutoAntesParcelamento DECIMAL(18,2) NULL,
    ValorLiquidoAntesParcelamento DECIMAL(18,2) NULL,
    ValorCompensadoAntecipacao DECIMAL(18,2) NULL,
    ValorDescontoAntecipacao DECIMAL(18,2) NULL,
    QtdParcelas INT NULL,

    -- Status e Flags
    Status VARCHAR(5) NULL,
    TipoDuplicata VARCHAR(5) NULL,
    InclusaoOK BIT NULL,
    NF13oSalario BIT NULL,
    FlagExportacao BIT NULL,
    ProvisaoIntegrada BIT NULL,
    BaixaIntegrada BIT NULL,
    NfeExportada BIT NULL,
    Tri_Tri BIT NULL,
    ContratoMulti BIT NULL,
    LiqNFe BIT NULL,
    APISinc BIT NULL,
    APISincExterno BIT NULL,

    -- Informações de Nota Fiscal
    NumeroBoleto VARCHAR(50) NULL,
    NroNFe INT NULL,
    CodigoVerificacaoNFe VARCHAR(100) NULL,
    NumeroRPS INT NULL,
    NroNotaDB INT NULL,
    NossoNumero INT NULL,
    NFeXML VARCHAR(MAX) NULL,
    NFeResultadoEnvio VARCHAR(MAX) NULL,
    NFeRetorno VARCHAR(MAX) NULL,
    Situacao INT NULL,

    -- Descrições e Observações
    Descricao VARCHAR(255) NULL,
    Observacao VARCHAR(500) NULL,
    Obs1Emissao VARCHAR(255) NULL,
    Obs2Emissao VARCHAR(255) NULL,
    Obs3Emissao VARCHAR(255) NULL,
    MotivoCancelamento VARCHAR(255) NULL,
    FormularioOrigem VARCHAR(100) NULL,

    -- Códigos Adicionais
    ChaveMovtoBanco INT NULL,
    ChaveMovtoBancoJD INT NULL,
    CodigoBancoOriginal INT NULL,
    CodigoCR INT NULL,
    CodigoCRJD INT NULL,
    CodigoDepto VARCHAR(50) NULL,
    IDSistemaAnterior VARCHAR(100) NULL,
    FaseEnvioCobr INT NULL,
    TipoBaixaRemessa INT NULL,

    -- Alíquotas
    AlqISS DECIMAL(10,6) NULL,
    AlqTriBnf DECIMAL(10,6) NULL,
    AlqTriFol DECIMAL(10,6) NULL,

    -- Controle
    UsuarioInclusao VARCHAR(100) NULL
);
GO

PRINT 'Tabela TB_Duplicata criada com sucesso.';
GO

-- ========================================
-- 3. CRIAÇÃO DE ÍNDICES PARA PERFORMANCE
-- ========================================
PRINT 'Criando índices...';
GO

-- Índice na chave primária composta
CREATE CLUSTERED INDEX IX_TB_Duplicata_PK
ON dbo.TB_Duplicata (CodigoEmpresaFat, CodigoFilialFat, Duplicata);
GO

-- Índice para consultas por cliente
CREATE NONCLUSTERED INDEX IX_TB_Duplicata_Cliente
ON dbo.TB_Duplicata (CodigoCliente, CodigoContrato)
INCLUDE (DataEmissao, DataVecto, ValorBruto, ValorLiquido, Status);
GO

-- Índice para consultas por data de vencimento
CREATE NONCLUSTERED INDEX IX_TB_Duplicata_DataVecto
ON dbo.TB_Duplicata (DataVecto, Status)
INCLUDE (CodigoCliente, ValorBruto, ValorLiquido, NumeroRPS, NroNFe);
GO

-- Índice para consultas por data de emissão
CREATE NONCLUSTERED INDEX IX_TB_Duplicata_DataEmissao
ON dbo.TB_Duplicata (DataEmissao)
INCLUDE (CodigoCliente, ValorBruto, ValorLiquido, Status);
GO

-- Índice para consultas por competência
CREATE NONCLUSTERED INDEX IX_TB_Duplicata_Competencia
ON dbo.TB_Duplicata (DataCompetencia, CodigoCliente);
GO

-- Índice para consultas por status
CREATE NONCLUSTERED INDEX IX_TB_Duplicata_Status
ON dbo.TB_Duplicata (Status, DataVecto)
INCLUDE (CodigoCliente, ValorBruto, ValorLiquido);
GO

PRINT 'Índices criados com sucesso.';
GO

-- ========================================
-- 4. ESTATÍSTICAS E VALIDAÇÃO
-- ========================================
PRINT 'Gerando estatísticas...';
GO

-- Total de registros na tabela
DECLARE @TotalRegistros INT;
SELECT @TotalRegistros = COUNT(*) FROM dbo.TB_Duplicata;
PRINT 'Total de registros na tabela: ' + CAST(@TotalRegistros AS VARCHAR(10));
GO

-- Registros por status
PRINT 'Distribuição por Status:';
SELECT
    Status,
    COUNT(*) AS Quantidade,
    SUM(ValorBruto) AS ValorTotalBruto,
    SUM(ValorLiquido) AS ValorTotalLiquido
FROM dbo.TB_Duplicata
GROUP BY Status
ORDER BY Status;
GO

-- Registros por ano
PRINT 'Distribuição por Ano:';
SELECT
    YEAR(DataEmissao) AS Ano,
    COUNT(*) AS Quantidade,
    SUM(ValorBruto) AS ValorTotalBruto
FROM dbo.TB_Duplicata
WHERE DataEmissao IS NOT NULL
GROUP BY YEAR(DataEmissao)
ORDER BY Ano;
GO

PRINT '========================================';
PRINT 'Script executado com sucesso!';
PRINT '========================================';
GO
