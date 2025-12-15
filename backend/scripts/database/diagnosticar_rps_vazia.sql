-- ============================================================================
-- SCRIPT DE DIAGNÓSTICO: Tela de RPS Vazia
-- ============================================================================
-- Este script identifica problemas quando a tela de RPS não carrega dados
-- Execute este script substituindo @EmailUsuario pelo email do usuário afetado
-- ============================================================================

DECLARE @EmailUsuario NVARCHAR(255) = 'email.do.usuario@dominio.com'; -- ← ALTERE AQUI

PRINT '============================================================================';
PRINT 'DIAGNÓSTICO: Tela de RPS Vazia';
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
DECLARE @CodigoClienteUsuario NVARCHAR(50);

SELECT
    @IdUsuario = ID,
    @NomeUsuario = Nome,
    @IDEmpresaUsuario = IDEmpresa,
    @CodigoClienteUsuario = CodigoCliente
FROM TB_Usuarios
WHERE Email = @EmailUsuario;

IF @IdUsuario IS NULL
BEGIN
    PRINT '❌ ERRO: Usuário não encontrado com email: ' + @EmailUsuario;
    PRINT 'Verifique se o email está correto.';
    RETURN;
END

PRINT '✅ Usuário encontrado:';
PRINT '   ID: ' + CAST(@IdUsuario AS NVARCHAR);
PRINT '   Nome: ' + @NomeUsuario;
PRINT '   IDEmpresa: ' + ISNULL(CAST(@IDEmpresaUsuario AS NVARCHAR), 'NULL ⚠️');
PRINT '   CodigoCliente (legado, ignorado): ' + ISNULL(@CodigoClienteUsuario, 'NULL');
PRINT '';

-- ============================================================================
-- ETAPA 2: Validar Empresa do Usuário
-- ============================================================================
PRINT '--- ETAPA 2: Validar Empresa do Usuário ---';
PRINT '';

IF @IDEmpresaUsuario IS NULL
BEGIN
    PRINT '❌ PROBLEMA ENCONTRADO: IDEmpresa está NULL';
    PRINT '';
    PRINT 'SOLUÇÃO:';
    PRINT 'Execute o comando abaixo para vincular o usuário a uma empresa:';
    PRINT '';
    PRINT 'UPDATE TB_Usuarios';
    PRINT 'SET IDEmpresa = (SELECT ID FROM TB_Empresas WHERE CodigoCliente = ''SEU_CODIGO_CLIENTE'')';
    PRINT 'WHERE Email = ''' + @EmailUsuario + ''';';
    PRINT '';
    PRINT 'Liste empresas disponíveis com:';
    PRINT 'SELECT ID, CodigoCliente, RazaoSocial, CNPJ, Ativo FROM TB_Empresas WHERE Ativo = 1;';
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
    PRINT '❌ ERRO: Empresa ID=' + CAST(@IDEmpresaUsuario AS NVARCHAR) + ' não encontrada em TB_Empresas';
    PRINT '';
    PRINT 'SOLUÇÃO:';
    PRINT 'Insira a empresa na TB_Empresas ou corrija o IDEmpresa do usuário.';
    RETURN;
END

PRINT '✅ Empresa do usuário encontrada:';
PRINT '   ID: ' + CAST(@IDEmpresaUsuario AS NVARCHAR);
PRINT '   CodigoCliente: ' + @CodigoClienteEmpresa + ' ← ESTE é usado no filtro!';
PRINT '   Razão Social: ' + @RazaoSocial;
PRINT '   CNPJ: ' + @CNPJ;
PRINT '   Ativo: ' + CASE WHEN @EmpresaAtiva = 1 THEN 'Sim ✅' ELSE 'Não ❌' END;
PRINT '';

IF @EmpresaAtiva = 0
BEGIN
    PRINT '❌ PROBLEMA ENCONTRADO: Empresa está INATIVA';
    PRINT '';
    PRINT 'SOLUÇÃO:';
    PRINT 'UPDATE TB_Empresas SET Ativo = 1 WHERE ID = ' + CAST(@IDEmpresaUsuario AS NVARCHAR) + ';';
    RETURN;
END

-- ============================================================================
-- ETAPA 3: Validar Conversão de CodigoCliente (NVARCHAR → INT)
-- ============================================================================
PRINT '--- ETAPA 3: Validar Conversão de CodigoCliente ---';
PRINT '';

DECLARE @CodigoClienteInt INT;

BEGIN TRY
    SET @CodigoClienteInt = CAST(@CodigoClienteEmpresa AS INT);
    PRINT '✅ Conversão de CodigoCliente para INT: ' + CAST(@CodigoClienteInt AS NVARCHAR);
END TRY
BEGIN CATCH
    PRINT '❌ ERRO: CodigoCliente da empresa não é numérico: ''' + @CodigoClienteEmpresa + '''';
    PRINT 'TB_Duplicata.CodigoCliente é INT, mas TB_Empresas.CodigoCliente é NVARCHAR(50)';
    PRINT '';
    PRINT 'SOLUÇÃO:';
    PRINT 'Corrija o CodigoCliente na TB_Empresas para um valor numérico válido.';
    RETURN;
END CATCH
PRINT '';

-- ============================================================================
-- ETAPA 4: Verificar Duplicatas (RPS) para este CodigoCliente
-- ============================================================================
PRINT '--- ETAPA 4: Verificar Duplicatas (RPS) para CodigoCliente ---';
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

PRINT 'Filtro aplicado: TB_Duplicata.CodigoCliente = ' + CAST(@CodigoClienteInt AS NVARCHAR);
PRINT '';
PRINT 'Total de duplicatas encontradas: ' + CAST(@TotalDuplicatas AS NVARCHAR);
PRINT '   - Ativas (Status=''A''): ' + CAST(@TotalAtivas AS NVARCHAR) + ' ← Apenas estas aparecem na tela';
PRINT '   - Inativas (Status<>''A''): ' + CAST(@TotalInativas AS NVARCHAR);
PRINT '';

IF @TotalDuplicatas = 0
BEGIN
    PRINT '❌ PROBLEMA ENCONTRADO: Nenhuma duplicata encontrada para CodigoCliente=' + CAST(@CodigoClienteInt AS NVARCHAR);
    PRINT '';
    PRINT 'Possíveis causas:';
    PRINT '1. CodigoCliente incorreto na TB_Empresas';
    PRINT '2. Não existem duplicatas para este cliente no sistema';
    PRINT '3. Os dados ainda não foram importados da base legada';
    PRINT '';
    PRINT 'SOLUÇÃO 1: Verificar se o CodigoCliente está correto';
    PRINT 'Liste todos os CodigoCliente distintos na TB_Duplicata:';
    PRINT '';
    PRINT 'SELECT DISTINCT CodigoCliente, COUNT(*) AS TotalRPS';
    PRINT 'FROM TB_Duplicata';
    PRINT 'WHERE Status = ''A''';
    PRINT 'GROUP BY CodigoCliente';
    PRINT 'ORDER BY TotalRPS DESC;';
    PRINT '';
    PRINT 'SOLUÇÃO 2: Se encontrar o CodigoCliente correto, atualize TB_Empresas:';
    PRINT '';
    PRINT 'UPDATE TB_Empresas';
    PRINT 'SET CodigoCliente = ''CODIGO_CORRETO''  -- Substitua pelo código encontrado';
    PRINT 'WHERE ID = ' + CAST(@IDEmpresaUsuario AS NVARCHAR) + ';';
    RETURN;
END

IF @TotalAtivas = 0
BEGIN
    PRINT '⚠️ AVISO: Existem duplicatas, mas TODAS estão inativas (Status<>''A'')';
    PRINT 'O endpoint /financeiro/rps filtra apenas Status=''A''';
    PRINT '';
    PRINT 'Verifique os status das duplicatas:';
    PRINT '';
    PRINT 'SELECT Status, COUNT(*) AS Total';
    PRINT 'FROM TB_Duplicata';
    PRINT 'WHERE CodigoCliente = ' + CAST(@CodigoClienteInt AS NVARCHAR);
    PRINT 'GROUP BY Status;';
    RETURN;
END

PRINT '✅ Duplicatas ativas encontradas!';
PRINT '';

-- ============================================================================
-- ETAPA 5: Mostrar Amostra das Duplicatas
-- ============================================================================
PRINT '--- ETAPA 5: Amostra das Duplicatas (Top 5) ---';
PRINT '';

SELECT TOP 5
    Duplicata AS NumeroRPS,
    NroNFe AS NumeroNFE,
    CodigoEmpresaFat,
    CodigoFilialFat,
    CONVERT(VARCHAR, DataEmissao, 103) AS DataEmissao,
    DataCompetencia AS Competencia,
    CONVERT(VARCHAR, DataVecto, 103) AS Vencimento,
    FORMAT(ValorBruto, 'C', 'pt-BR') AS ValorTotal,
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
-- ETAPA 6: Verificar Status de Aprovação
-- ============================================================================
PRINT '--- ETAPA 6: Verificar Status de Aprovação (Top 5 RPS) ---';
PRINT '';

SELECT TOP 5
    d.Duplicata AS NumeroRPS,
    d.CodigoEmpresaFat,
    d.CodigoFilialFat,
    ISNULL(s.Codigo, 'pendente') AS StatusAprovacao,
    CONVERT(VARCHAR, a.DataAcao, 120) AS UltimaAcao,
    a.NomeUsuario AS UltimoUsuario
FROM TB_Duplicata d
LEFT JOIN (
    SELECT
        CodigoEmpresaFat,
        CodigoFilialFat,
        Duplicata,
        IdStatusAprovacao,
        DataAcao,
        NomeUsuario,
        ROW_NUMBER() OVER (
            PARTITION BY CodigoEmpresaFat, CodigoFilialFat, Duplicata
            ORDER BY DataAcao DESC
        ) AS rn
    FROM TB_AprovacaoRPS
) a ON d.CodigoEmpresaFat = a.CodigoEmpresaFat
   AND d.CodigoFilialFat = a.CodigoFilialFat
   AND d.Duplicata = a.Duplicata
   AND a.rn = 1
LEFT JOIN TB_StatusAprovacao s ON a.IdStatusAprovacao = s.ID
WHERE d.CodigoCliente = @CodigoClienteInt
  AND d.Status = 'A'
ORDER BY d.DataVecto DESC;

PRINT '';

-- ============================================================================
-- ETAPA 7: Resumo Final
-- ============================================================================
PRINT '--- RESUMO FINAL ---';
PRINT '';

DECLARE @TotalPendentes INT, @ValorPendentes DECIMAL(18,2);
DECLARE @TotalAprovados INT, @ValorAprovados DECIMAL(18,2);
DECLARE @TotalReprovados INT, @ValorReprovados DECIMAL(18,2);

WITH StatusAtual AS (
    SELECT
        d.Duplicata,
        d.ValorBruto,
        ISNULL(s.Codigo, 'pendente') AS StatusAprovacao
    FROM TB_Duplicata d
    LEFT JOIN (
        SELECT
            CodigoEmpresaFat,
            CodigoFilialFat,
            Duplicata,
            IdStatusAprovacao,
            ROW_NUMBER() OVER (
                PARTITION BY CodigoEmpresaFat, CodigoFilialFat, Duplicata
                ORDER BY DataAcao DESC
            ) AS rn
        FROM TB_AprovacaoRPS
    ) a ON d.CodigoEmpresaFat = a.CodigoEmpresaFat
       AND d.CodigoFilialFat = a.CodigoFilialFat
       AND d.Duplicata = a.Duplicata
       AND a.rn = 1
    LEFT JOIN TB_StatusAprovacao s ON a.IdStatusAprovacao = s.ID
    WHERE d.CodigoCliente = @CodigoClienteInt
      AND d.Status = 'A'
)
SELECT
    @TotalPendentes = SUM(CASE WHEN StatusAprovacao = 'pendente' THEN 1 ELSE 0 END),
    @ValorPendentes = SUM(CASE WHEN StatusAprovacao = 'pendente' THEN ValorBruto ELSE 0 END),
    @TotalAprovados = SUM(CASE WHEN StatusAprovacao = 'aprovado' THEN 1 ELSE 0 END),
    @ValorAprovados = SUM(CASE WHEN StatusAprovacao = 'aprovado' THEN ValorBruto ELSE 0 END),
    @TotalReprovados = SUM(CASE WHEN StatusAprovacao = 'reprovado' THEN 1 ELSE 0 END),
    @ValorReprovados = SUM(CASE WHEN StatusAprovacao = 'reprovado' THEN ValorBruto ELSE 0 END)
FROM StatusAtual;

PRINT 'RPS Pendentes: ' + CAST(ISNULL(@TotalPendentes, 0) AS NVARCHAR) + ' | Valor: ' + FORMAT(ISNULL(@ValorPendentes, 0), 'C', 'pt-BR');
PRINT 'RPS Aprovados: ' + CAST(ISNULL(@TotalAprovados, 0) AS NVARCHAR) + ' | Valor: ' + FORMAT(ISNULL(@ValorAprovados, 0), 'C', 'pt-BR');
PRINT 'RPS Reprovados: ' + CAST(ISNULL(@TotalReprovados, 0) AS NVARCHAR) + ' | Valor: ' + FORMAT(ISNULL(@ValorReprovados, 0), 'C', 'pt-BR');
PRINT '';

-- ============================================================================
-- ETAPA 8: Testar Query Exata do Backend
-- ============================================================================
PRINT '--- ETAPA 8: Simular Query do Backend /financeiro/rps ---';
PRINT '';

PRINT 'Esta é a query SQL que o backend executa (simplificada):';
PRINT '';

SELECT TOP 10
    d.Duplicata,
    d.NroNFe AS numeroNFE,
    d.CodigoEmpresaFat,
    d.CodigoFilialFat,
    d.DataEmissao,
    CONCAT(SUBSTRING(d.DataCompetencia, 5, 2), '/', SUBSTRING(d.DataCompetencia, 1, 4)) AS Competencia,
    d.DataVecto AS Vencimento,
    d.ValorBruto AS ValorTotal,
    CASE
        WHEN d.DataBaixa IS NOT NULL THEN 'paga'
        WHEN d.DataVecto < GETDATE() THEN 'vencida'
        ELSE 'a_vencer'
    END AS Status,
    ISNULL(s.Codigo, 'pendente') AS StatusAprovacao
FROM TB_Duplicata d
LEFT JOIN (
    SELECT
        CodigoEmpresaFat,
        CodigoFilialFat,
        Duplicata,
        IdStatusAprovacao,
        ROW_NUMBER() OVER (
            PARTITION BY CodigoEmpresaFat, CodigoFilialFat, Duplicata
            ORDER BY DataAcao DESC
        ) AS rn
    FROM TB_AprovacaoRPS
) a ON d.CodigoEmpresaFat = a.CodigoEmpresaFat
   AND d.CodigoFilialFat = a.CodigoFilialFat
   AND d.Duplicata = a.Duplicata
   AND a.rn = 1
LEFT JOIN TB_StatusAprovacao s ON a.IdStatusAprovacao = s.ID
WHERE d.Status = 'A'
  AND d.CodigoCliente = @CodigoClienteInt
ORDER BY d.DataVecto DESC;

PRINT '';
PRINT '============================================================================';
PRINT 'FIM DO DIAGNÓSTICO';
PRINT '============================================================================';
