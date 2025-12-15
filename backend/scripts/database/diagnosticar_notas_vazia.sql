-- ============================================================================
-- SCRIPT DE DIAGNÓSTICO: Tela de Notas Fiscais Vazia
-- ============================================================================
-- Este script identifica problemas quando a tela de Notas Fiscais não carrega dados
-- Execute este script substituindo @EmailUsuario pelo email do usuário afetado
-- ============================================================================

DECLARE @EmailUsuario NVARCHAR(255) = 'email.do.usuario@dominio.com'; -- ← ALTERE AQUI

PRINT '============================================================================';
PRINT 'DIAGNÓSTICO: Tela de Notas Fiscais Vazia';
PRINT 'Usuario: ' + @EmailUsuario;
PRINT 'Data: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '============================================================================';
PRINT '';

-- ============================================================================
-- ETAPA 1: Validar Usuário
-- ============================================================================
PRINT '--- ETAPA 1: Validar Usuário ---';
PRINT '';

DECLARE @IdUsuario INT;
DECLARE @NomeUsuario NVARCHAR(255);
DECLARE @IDEmpresaUsuario INT;

SELECT
    @IdUsuario = ID,
    @NomeUsuario = Nome,
    @IDEmpresaUsuario = IDEmpresa
FROM TB_Usuarios
WHERE Email = @EmailUsuario;

IF @IdUsuario IS NULL
BEGIN
    PRINT '❌ ERRO: Usuário não encontrado com email: ' + @EmailUsuario;
    RETURN;
END

PRINT '✅ Usuário encontrado:';
PRINT '   ID: ' + CAST(@IdUsuario AS NVARCHAR);
PRINT '   Nome: ' + @NomeUsuario;
PRINT '   IDEmpresa: ' + ISNULL(CAST(@IDEmpresaUsuario AS NVARCHAR), 'NULL ⚠️');
PRINT '';

-- ============================================================================
-- ETAPA 2: Validar Empresa do Usuário
-- ============================================================================
PRINT '--- ETAPA 2: Validar Empresa do Usuário ---';
PRINT '';

IF @IDEmpresaUsuario IS NULL
BEGIN
    PRINT '❌ PROBLEMA: IDEmpresa está NULL';
    PRINT '';
    PRINT 'SOLUÇÃO:';
    PRINT 'UPDATE TB_Usuarios';
    PRINT 'SET IDEmpresa = (SELECT ID FROM TB_Empresas WHERE CodigoCliente = ''SEU_CODIGO'')';
    PRINT 'WHERE Email = ''' + @EmailUsuario + ''';';
    RETURN;
END

DECLARE @CodigoClienteEmpresa NVARCHAR(50);
DECLARE @RazaoSocial NVARCHAR(200);
DECLARE @CNPJ NVARCHAR(18);
DECLARE @EmpresaAtiva BIT;

SELECT
    @CodigoClienteEmpresa = CodigoCliente,
    @RazaoSocial = RazaoSocial,
    @CNPJ = CNPJ,
    @EmpresaAtiva = Ativo
FROM TB_Empresas
WHERE ID = @IDEmpresaUsuario;

IF @CodigoClienteEmpresa IS NULL
BEGIN
    PRINT '❌ ERRO: Empresa ID=' + CAST(@IDEmpresaUsuario AS NVARCHAR) + ' não encontrada';
    RETURN;
END

PRINT '✅ Empresa encontrada:';
PRINT '   CodigoCliente: ' + @CodigoClienteEmpresa;
PRINT '   Razão Social: ' + @RazaoSocial;
PRINT '   CNPJ: ' + @CNPJ;
PRINT '   Ativo: ' + CASE WHEN @EmpresaAtiva = 1 THEN 'Sim ✅' ELSE 'Não ❌' END;
PRINT '';

IF @EmpresaAtiva = 0
BEGIN
    PRINT '❌ PROBLEMA: Empresa INATIVA';
    PRINT 'SOLUÇÃO: UPDATE TB_Empresas SET Ativo = 1 WHERE ID = ' + CAST(@IDEmpresaUsuario AS NVARCHAR);
    RETURN;
END

-- ============================================================================
-- ETAPA 3: Converter CodigoCliente (NVARCHAR → INT)
-- ============================================================================
PRINT '--- ETAPA 3: Validar Conversão de CodigoCliente ---';
PRINT '';

DECLARE @CodigoClienteInt INT;

BEGIN TRY
    SET @CodigoClienteInt = CAST(@CodigoClienteEmpresa AS INT);
    PRINT '✅ CodigoCliente convertido para INT: ' + CAST(@CodigoClienteInt AS NVARCHAR);
END TRY
BEGIN CATCH
    PRINT '❌ ERRO: CodigoCliente não é numérico: ''' + @CodigoClienteEmpresa + '''';
    RETURN;
END CATCH
PRINT '';

-- ============================================================================
-- ETAPA 4: Verificar Duplicatas (Notas Fiscais)
-- ============================================================================
PRINT '--- ETAPA 4: Verificar Duplicatas para CodigoCliente ---';
PRINT '';

DECLARE @TotalDuplicatas INT;
DECLARE @TotalAtivas INT;
DECLARE @TotalInativas INT;

SELECT
    @TotalDuplicatas = COUNT(*),
    @TotalAtivas = SUM(CASE WHEN Status = 'A' THEN 1 ELSE 0 END),
    @TotalInativas = SUM(CASE WHEN Status <> 'A' THEN 1 ELSE 0 END)
FROM TB_Duplicata
WHERE CodigoCliente = @CodigoClienteInt;

PRINT 'Filtro: TB_Duplicata.CodigoCliente = ' + CAST(@CodigoClienteInt AS NVARCHAR);
PRINT '';
PRINT 'Total de duplicatas: ' + CAST(@TotalDuplicatas AS NVARCHAR);
PRINT '   - Ativas (Status=''A''): ' + CAST(@TotalAtivas AS NVARCHAR);
PRINT '   - Inativas: ' + CAST(@TotalInativas AS NVARCHAR);
PRINT '';

IF @TotalDuplicatas = 0
BEGIN
    PRINT '❌ PROBLEMA: Nenhuma duplicata encontrada';
    PRINT '';
    PRINT 'SOLUÇÃO: Verificar CodigoCliente correto';
    PRINT '';
    PRINT 'SELECT DISTINCT CodigoCliente, COUNT(*) AS Total';
    PRINT 'FROM TB_Duplicata WHERE Status = ''A''';
    PRINT 'GROUP BY CodigoCliente ORDER BY Total DESC;';
    RETURN;
END

IF @TotalAtivas = 0
BEGIN
    PRINT '⚠️ AVISO: Todas as duplicatas estão INATIVAS (Status<>''A'')';
    PRINT '';
    PRINT 'SELECT Status, COUNT(*) FROM TB_Duplicata';
    PRINT 'WHERE CodigoCliente = ' + CAST(@CodigoClienteInt AS NVARCHAR);
    PRINT 'GROUP BY Status;';
    RETURN;
END

PRINT '✅ Duplicatas ativas encontradas!';
PRINT '';

-- ============================================================================
-- ETAPA 5: Amostra das Notas Fiscais (Top 5)
-- ============================================================================
PRINT '--- ETAPA 5: Amostra das Notas Fiscais (Top 5) ---';
PRINT '';

SELECT TOP 5
    Duplicata AS ID,
    NroNFe AS NumeroNFE,
    CONVERT(VARCHAR, DataEmissao, 103) AS DataEmissao,
    CONCAT(SUBSTRING(DataCompetencia, 5, 2), '/', SUBSTRING(DataCompetencia, 1, 4)) AS Competencia,
    CONVERT(VARCHAR, DataVecto, 103) AS Vencimento,
    FORMAT(ValorBruto, 'C', 'pt-BR') AS Valor,
    Status,
    CASE
        WHEN DataBaixa IS NOT NULL THEN 'paga'
        WHEN DataVecto < GETDATE() THEN 'vencida'
        ELSE 'a_vencer'
    END AS StatusCalculado
FROM TB_Duplicata
WHERE CodigoCliente = @CodigoClienteInt
  AND Status = 'A'
ORDER BY DataVecto DESC;

PRINT '';

-- ============================================================================
-- ETAPA 6: Resumo de Status
-- ============================================================================
PRINT '--- ETAPA 6: Resumo de Status ---';
PRINT '';

DECLARE @TotalAVencer INT, @ValorAVencer DECIMAL(18,2);
DECLARE @TotalVencidas INT, @ValorVencidas DECIMAL(18,2);
DECLARE @TotalPagas INT, @ValorPagas DECIMAL(18,2);

SELECT
    @TotalAVencer = SUM(CASE WHEN DataBaixa IS NULL AND DataVecto >= GETDATE() THEN 1 ELSE 0 END),
    @ValorAVencer = SUM(CASE WHEN DataBaixa IS NULL AND DataVecto >= GETDATE() THEN ValorBruto ELSE 0 END),
    @TotalVencidas = SUM(CASE WHEN DataBaixa IS NULL AND DataVecto < GETDATE() THEN 1 ELSE 0 END),
    @ValorVencidas = SUM(CASE WHEN DataBaixa IS NULL AND DataVecto < GETDATE() THEN ValorBruto ELSE 0 END),
    @TotalPagas = SUM(CASE WHEN DataBaixa IS NOT NULL THEN 1 ELSE 0 END),
    @ValorPagas = SUM(CASE WHEN DataBaixa IS NOT NULL THEN ValorBruto ELSE 0 END)
FROM TB_Duplicata
WHERE CodigoCliente = @CodigoClienteInt
  AND Status = 'A';

PRINT 'Notas a Vencer: ' + CAST(ISNULL(@TotalAVencer, 0) AS NVARCHAR) + ' | Valor: ' + FORMAT(ISNULL(@ValorAVencer, 0), 'C', 'pt-BR');
PRINT 'Notas Vencidas: ' + CAST(ISNULL(@TotalVencidas, 0) AS NVARCHAR) + ' | Valor: ' + FORMAT(ISNULL(@ValorVencidas, 0), 'C', 'pt-BR');
PRINT 'Notas Pagas: ' + CAST(ISNULL(@TotalPagas, 0) AS NVARCHAR) + ' | Valor: ' + FORMAT(ISNULL(@ValorPagas, 0), 'C', 'pt-BR');
PRINT '';

PRINT '============================================================================';
PRINT 'FIM DO DIAGNÓSTICO';
PRINT '============================================================================';
