-- =============================================
-- Script de Validação: Filtro de Empresa
-- =============================================
--
-- Este script valida a implementação do filtro automático de empresa
-- nas consultas de RPS e Notas Fiscais.
--
-- OBJETIVO: Verificar que o JOIN entre TB_Usuarios → TB_Empresas → TB_Duplicata
--           está correto e que os filtros de segurança funcionam adequadamente.
--
-- USO: Execute cada seção sequencialmente e analise os resultados.
-- =============================================

USE PortalCliente;
GO

PRINT '========================================';
PRINT 'VALIDAÇÃO DE FILTRO DE EMPRESA';
PRINT '========================================';
PRINT '';

-- =============================================
-- 1. VALIDAR ESTRUTURA DAS TABELAS
-- =============================================
PRINT '1. VALIDANDO ESTRUTURA DAS TABELAS...';
PRINT '';

-- Verificar se TB_Empresas existe
IF OBJECT_ID('dbo.TB_Empresas', 'U') IS NOT NULL
    PRINT '✓ TB_Empresas existe';
ELSE
    PRINT '✗ ERRO: TB_Empresas não encontrada! Execute criar_tb_empresas.sql';
GO

-- Verificar se coluna IDEmpresa existe em TB_Usuarios
IF COL_LENGTH('dbo.TB_Usuarios', 'IDEmpresa') IS NOT NULL
    PRINT '✓ Coluna TB_Usuarios.IDEmpresa existe';
ELSE
    PRINT '✗ ERRO: Coluna IDEmpresa não encontrada em TB_Usuarios! Execute alterar_tb_usuarios_add_empresa.sql';
GO

-- Verificar Foreign Key
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_TB_Usuarios_Empresa')
    PRINT '✓ Foreign Key FK_TB_Usuarios_Empresa existe';
ELSE
    PRINT '✗ AVISO: Foreign Key FK_TB_Usuarios_Empresa não encontrada';
GO

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 2. VALIDAR DADOS DE EMPRESAS
-- =============================================
PRINT '2. VALIDANDO DADOS DE EMPRESAS...';
PRINT '';

-- Total de empresas cadastradas
SELECT
    COUNT(*) AS TotalEmpresas,
    SUM(CASE WHEN Ativo = 1 THEN 1 ELSE 0 END) AS EmpresasAtivas,
    SUM(CASE WHEN Ativo = 0 THEN 1 ELSE 0 END) AS EmpresasInativas
FROM TB_Empresas;

PRINT '';
PRINT 'Lista de empresas cadastradas:';
SELECT
    ID,
    CodigoCliente,
    CodigoEmpresaFat,
    CodigoFilialFat,
    RazaoSocial,
    CNPJ,
    Ativo,
    DataCadastro
FROM TB_Empresas
ORDER BY ID;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 3. VALIDAR VINCULAÇÃO DE USUÁRIOS
-- =============================================
PRINT '3. VALIDANDO VINCULAÇÃO DE USUÁRIOS...';
PRINT '';

-- Estatísticas de vinculação
SELECT
    COUNT(*) AS TotalUsuarios,
    SUM(CASE WHEN IDEmpresa IS NOT NULL THEN 1 ELSE 0 END) AS UsuariosVinculados,
    SUM(CASE WHEN IDEmpresa IS NULL THEN 1 ELSE 0 END) AS UsuariosSemVinculo
FROM TB_Usuarios;

PRINT '';
PRINT 'Usuários SEM empresa vinculada (BLOQUEADOS para RPS/Notas):';
SELECT
    ID,
    Nome,
    Email,
    IDEmpresa,
    'ACESSO NEGADO' AS Status
FROM TB_Usuarios
WHERE IDEmpresa IS NULL;

PRINT '';
PRINT 'Usuários COM empresa vinculada:';
SELECT
    u.ID AS UsuarioID,
    u.Nome AS UsuarioNome,
    u.Email,
    u.IDEmpresa,
    e.CodigoCliente,
    e.RazaoSocial AS EmpresaNome,
    e.CNPJ,
    e.Ativo AS EmpresaAtiva
FROM TB_Usuarios u
INNER JOIN TB_Empresas e ON u.IDEmpresa = e.ID
ORDER BY u.ID;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 4. VALIDAR JOIN COMPLETO (Usuários → Empresas → Duplicatas)
-- =============================================
PRINT '4. VALIDANDO JOIN COMPLETO (TB_Usuarios → TB_Empresas → TB_Duplicata)...';
PRINT '';

PRINT 'Quantidade de duplicatas por usuário (via JOIN):';
SELECT
    u.ID AS UsuarioID,
    u.Nome AS UsuarioNome,
    u.Email,
    e.CodigoCliente,
    e.RazaoSocial AS EmpresaNome,
    COUNT(d.Duplicata) AS TotalDuplicatas,
    SUM(d.Valor) AS ValorTotal
FROM TB_Usuarios u
INNER JOIN TB_Empresas e ON u.IDEmpresa = e.ID
LEFT JOIN INTEGRA_METASP.dbo.TB_Duplicata d
    ON CAST(d.CodigoCliente AS INT) = CAST(e.CodigoCliente AS INT)
    AND d.Status = 'A'  -- Apenas duplicatas ativas
GROUP BY
    u.ID,
    u.Nome,
    u.Email,
    e.CodigoCliente,
    e.RazaoSocial
ORDER BY u.ID;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 5. VALIDAR FILTRO DE RPS (StatusAprovacao IS NULL)
-- =============================================
PRINT '5. VALIDANDO FILTRO DE RPS (TB_Duplicata WHERE StatusAprovacao IS NULL)...';
PRINT '';

PRINT 'RPS por usuário (StatusAprovacao IS NULL):';
SELECT
    u.ID AS UsuarioID,
    u.Nome AS UsuarioNome,
    e.CodigoCliente,
    e.RazaoSocial AS EmpresaNome,
    COUNT(d.Duplicata) AS TotalRPS,
    SUM(d.Valor) AS ValorTotalRPS,
    SUM(CASE WHEN d.DataVencimento >= CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS RPSPendentes,
    SUM(CASE WHEN d.DataVencimento >= CAST(GETDATE() AS DATE) THEN d.Valor ELSE 0 END) AS ValorPendentes,
    SUM(CASE WHEN d.DataVencimento < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS RPSVencidos,
    SUM(CASE WHEN d.DataVencimento < CAST(GETDATE() AS DATE) THEN d.Valor ELSE 0 END) AS ValorVencidos
FROM TB_Usuarios u
INNER JOIN TB_Empresas e ON u.IDEmpresa = e.ID
LEFT JOIN INTEGRA_METASP.dbo.TB_Duplicata d
    ON CAST(d.CodigoCliente AS INT) = CAST(e.CodigoCliente AS INT)
    AND d.Status = 'A'
    AND d.StatusAprovacao IS NULL  -- Apenas RPS (não aprovados)
GROUP BY
    u.ID,
    u.Nome,
    e.CodigoCliente,
    e.RazaoSocial
ORDER BY u.ID;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 6. VALIDAR FILTRO DE NOTAS FISCAIS (NumeroNFE IS NOT NULL)
-- =============================================
PRINT '6. VALIDANDO FILTRO DE NOTAS FISCAIS (TB_Duplicata WHERE NumeroNFE IS NOT NULL)...';
PRINT '';

PRINT 'Notas Fiscais por usuário (NumeroNFE IS NOT NULL):';
SELECT
    u.ID AS UsuarioID,
    u.Nome AS UsuarioNome,
    e.CodigoCliente,
    e.RazaoSocial AS EmpresaNome,
    COUNT(d.Duplicata) AS TotalNotasFiscais,
    SUM(d.Valor) AS ValorTotalNotas,
    SUM(CASE WHEN d.DataVencimento >= CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS NotasAVencer,
    SUM(CASE WHEN d.DataVencimento >= CAST(GETDATE() AS DATE) THEN d.Valor ELSE 0 END) AS ValorAVencer,
    SUM(CASE WHEN d.DataVencimento < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS NotasVencidas,
    SUM(CASE WHEN d.DataVencimento < CAST(GETDATE() AS DATE) THEN d.Valor ELSE 0 END) AS ValorVencidas
FROM TB_Usuarios u
INNER JOIN TB_Empresas e ON u.IDEmpresa = e.ID
LEFT JOIN INTEGRA_METASP.dbo.TB_Duplicata d
    ON CAST(d.CodigoCliente AS INT) = CAST(e.CodigoCliente AS INT)
    AND d.Status = 'A'
    AND d.NumeroNFE IS NOT NULL  -- Apenas Notas Fiscais
GROUP BY
    u.ID,
    u.Nome,
    e.CodigoCliente,
    e.RazaoSocial
ORDER BY u.ID;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 7. VALIDAR DADOS DE DUPLICATAS POR EMPRESA
-- =============================================
PRINT '7. VALIDANDO DADOS DE DUPLICATAS POR EMPRESA...';
PRINT '';

PRINT 'Resumo de duplicatas por CodigoCliente:';
SELECT
    d.CodigoCliente,
    e.RazaoSocial AS EmpresaNome,
    e.CNPJ,
    COUNT(d.Duplicata) AS TotalDuplicatas,
    SUM(d.Valor) AS ValorTotal,
    COUNT(CASE WHEN d.StatusAprovacao IS NULL THEN 1 END) AS TotalRPS,
    SUM(CASE WHEN d.StatusAprovacao IS NULL THEN d.Valor END) AS ValorRPS,
    COUNT(CASE WHEN d.NumeroNFE IS NOT NULL THEN 1 END) AS TotalNotasFiscais,
    SUM(CASE WHEN d.NumeroNFE IS NOT NULL THEN d.Valor END) AS ValorNotasFiscais
FROM INTEGRA_METASP.dbo.TB_Duplicata d
LEFT JOIN TB_Empresas e ON CAST(d.CodigoCliente AS INT) = CAST(e.CodigoCliente AS INT)
WHERE d.Status = 'A'
GROUP BY
    d.CodigoCliente,
    e.RazaoSocial,
    e.CNPJ
ORDER BY d.CodigoCliente;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 8. VALIDAR CONFLITOS DE CODIGOCLIENTE
-- =============================================
PRINT '8. VALIDANDO POSSÍVEIS CONFLITOS DE CODIGOCLIENTE...';
PRINT '';

PRINT 'Verificar se TB_Usuarios.CodigoCliente difere de TB_Empresas.CodigoCliente:';
PRINT '(TB_Usuarios.CodigoCliente é IGNORADO - apenas TB_Empresas.CodigoCliente é usado)';
SELECT
    u.ID AS UsuarioID,
    u.Nome AS UsuarioNome,
    u.CodigoCliente AS CodigoClienteUsuario_IGNORADO,
    e.CodigoCliente AS CodigoClienteEmpresa_USADO,
    CASE
        WHEN u.CodigoCliente = e.CodigoCliente THEN '✓ Valores coincidem'
        WHEN u.CodigoCliente <> e.CodigoCliente THEN '⚠ VALORES DIFERENTES (normal, empresa prevalece)'
        ELSE 'N/A'
    END AS Status
FROM TB_Usuarios u
LEFT JOIN TB_Empresas e ON u.IDEmpresa = e.ID
WHERE u.IDEmpresa IS NOT NULL
ORDER BY u.ID;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 9. TESTE DE QUERY SIMULANDO ENDPOINT
-- =============================================
PRINT '9. SIMULANDO QUERY DO ENDPOINT /financeiro/rps...';
PRINT '';

-- Declare um ID de usuário para teste (ajuste conforme necessário)
DECLARE @UsuarioTesteID INT = 1;  -- Altere para um ID válido do seu sistema

PRINT 'Teste para UsuarioID: ' + CAST(@UsuarioTesteID AS VARCHAR);
PRINT '';

-- Query que simula o que o endpoint /financeiro/rps executa
SELECT
    d.Duplicata,
    d.CodigoEmpresaFat,
    d.CodigoFilialFat,
    d.DataEmissao,
    d.Competencia,
    d.DataVencimento,
    d.Valor AS ValorTotal,
    d.NumeroNFE,
    d.StatusAprovacao,
    e.CodigoCliente AS CodigoClienteFiltro,
    e.RazaoSocial AS EmpresaNome,
    u.Nome AS UsuarioNome
FROM TB_Usuarios u
INNER JOIN TB_Empresas e ON u.IDEmpresa = e.ID  -- JOIN que obtém CodigoCliente
INNER JOIN INTEGRA_METASP.dbo.TB_Duplicata d
    ON CAST(d.CodigoCliente AS INT) = CAST(e.CodigoCliente AS INT)  -- Filtro por empresa
WHERE u.ID = @UsuarioTesteID
    AND d.Status = 'A'
    AND d.StatusAprovacao IS NULL  -- RPS: sem aprovação
ORDER BY d.DataVencimento DESC;

PRINT '';
PRINT '----------------------------------------';
PRINT '';

-- =============================================
-- 10. RESUMO FINAL
-- =============================================
PRINT '========================================';
PRINT 'RESUMO DA VALIDAÇÃO';
PRINT '========================================';
PRINT '';

PRINT 'Checklist de Validação:';
PRINT '';
PRINT '[ ] 1. TB_Empresas existe e contém empresas cadastradas';
PRINT '[ ] 2. TB_Usuarios.IDEmpresa existe e FK está configurada';
PRINT '[ ] 3. Usuários estão vinculados a empresas (IDEmpresa NOT NULL)';
PRINT '[ ] 4. JOIN TB_Usuarios → TB_Empresas → TB_Duplicata retorna dados';
PRINT '[ ] 5. Filtro por CodigoCliente funciona corretamente';
PRINT '[ ] 6. RPS (StatusAprovacao IS NULL) são filtrados por empresa';
PRINT '[ ] 7. Notas Fiscais (NumeroNFE IS NOT NULL) são filtradas por empresa';
PRINT '[ ] 8. TB_Usuarios.CodigoCliente é IGNORADO (TB_Empresas prevalece)';
PRINT '';

PRINT 'IMPORTANTE:';
PRINT '- Cada usuário deve ter IDEmpresa preenchido para acessar RPS/Notas';
PRINT '- O filtro usa TB_Empresas.CodigoCliente obtido via JOIN';
PRINT '- TB_Usuarios.CodigoCliente é mantido por compatibilidade mas NÃO é usado';
PRINT '- Usuários sem IDEmpresa receberão erro 403 Forbidden nos endpoints';
PRINT '';

PRINT '========================================';
PRINT 'FIM DA VALIDAÇÃO';
PRINT '========================================';
GO
