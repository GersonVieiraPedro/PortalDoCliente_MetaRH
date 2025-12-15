-- =============================================
-- Script de Diagnóstico: Problema "Empresa não encontrada"
-- =============================================
--
-- Este script diagnostica e corrige o problema onde:
-- - Usuário tem IDEmpresa preenchido
-- - Mas a empresa não existe em TB_Empresas
--
-- RESULTADO: Erro "Empresa não encontrada no sistema"
-- =============================================

USE PortalCliente;
GO

PRINT '========================================';
PRINT 'DIAGNÓSTICO: Empresa não encontrada';
PRINT '========================================';
PRINT '';

-- =============================================
-- 1. VERIFICAR SE TABELA TB_EMPRESAS EXISTE
-- =============================================
PRINT '1. Verificando se TB_Empresas existe...';
IF OBJECT_ID('dbo.TB_Empresas', 'U') IS NOT NULL
    PRINT '   ✓ TB_Empresas existe';
ELSE
BEGIN
    PRINT '   ✗ ERRO: TB_Empresas NÃO EXISTE!';
    PRINT '';
    PRINT '   SOLUÇÃO: Execute o script criar_tb_empresas.sql';
    PRINT '   Caminho: scripts/database/criar_tb_empresas.sql';
    RETURN;
END
PRINT '';

-- =============================================
-- 2. VERIFICAR SE EXISTEM EMPRESAS CADASTRADAS
-- =============================================
PRINT '2. Verificando empresas cadastradas...';
DECLARE @TotalEmpresas INT;
SELECT @TotalEmpresas = COUNT(*) FROM TB_Empresas;

IF @TotalEmpresas = 0
BEGIN
    PRINT '   ✗ ERRO: TB_Empresas está VAZIA!';
    PRINT '';
    PRINT '   SOLUÇÃO: Execute o script seed_empresas.sql';
    PRINT '   Caminho: scripts/database/seed_empresas.sql';
    PRINT '';
    PRINT '   OU cadastre empresas manualmente:';
    PRINT '   INSERT INTO TB_Empresas (CodigoCliente, CodigoEmpresaFat, CodigoFilialFat, RazaoSocial, CNPJ, Ativo)';
    PRINT '   VALUES (''1001'', 1, 1, ''Minha Empresa LTDA'', ''12.345.678/0001-90'', 1);';
    RETURN;
END
ELSE
BEGIN
    PRINT '   ✓ Total de empresas: ' + CAST(@TotalEmpresas AS VARCHAR);
END
PRINT '';

-- =============================================
-- 3. LISTAR EMPRESAS CADASTRADAS
-- =============================================
PRINT '3. Empresas cadastradas:';
SELECT
    ID,
    CodigoCliente,
    RazaoSocial,
    CNPJ,
    Ativo,
    DataCadastro
FROM TB_Empresas
ORDER BY ID;
PRINT '';

-- =============================================
-- 4. VERIFICAR USUÁRIOS COM IDEMPRESA INVÁLIDO
-- =============================================
PRINT '4. Verificando usuários com IDEmpresa inválido...';
PRINT '';

-- Usuários com IDEmpresa que não existe em TB_Empresas
SELECT
    u.ID AS UsuarioID,
    u.Nome,
    u.Email,
    u.IDEmpresa AS IDEmpresaInvalido,
    '✗ EMPRESA NÃO ENCONTRADA' AS Problema
FROM TB_Usuarios u
WHERE u.IDEmpresa IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TB_Empresas e WHERE e.ID = u.IDEmpresa);

IF @@ROWCOUNT = 0
    PRINT '   ✓ Nenhum usuário com IDEmpresa inválido';
ELSE
    PRINT '   ✗ Usuários acima têm IDEmpresa que não existe em TB_Empresas!';

PRINT '';

-- =============================================
-- 5. VERIFICAR USUÁRIOS SEM EMPRESA
-- =============================================
PRINT '5. Verificando usuários sem empresa vinculada...';
SELECT
    ID AS UsuarioID,
    Nome,
    Email,
    IDEmpresa,
    '⚠ SEM EMPRESA' AS Problema
FROM TB_Usuarios
WHERE IDEmpresa IS NULL;

IF @@ROWCOUNT = 0
    PRINT '   ✓ Todos os usuários têm empresa vinculada';
ELSE
    PRINT '   ⚠ Usuários acima precisam ter empresa vinculada';

PRINT '';

-- =============================================
-- 6. VERIFICAR USUÁRIOS COM EMPRESA CORRETA
-- =============================================
PRINT '6. Usuários com empresa vinculada corretamente:';
SELECT
    u.ID AS UsuarioID,
    u.Nome,
    u.Email,
    u.IDEmpresa,
    e.CodigoCliente,
    e.RazaoSocial,
    e.CNPJ,
    e.Ativo AS EmpresaAtiva
FROM TB_Usuarios u
INNER JOIN TB_Empresas e ON u.IDEmpresa = e.ID
ORDER BY u.ID;

IF @@ROWCOUNT = 0
    PRINT '   ⚠ Nenhum usuário com empresa vinculada corretamente';
ELSE
    PRINT '   ✓ Usuários acima estão configurados corretamente';

PRINT '';
PRINT '========================================';
PRINT 'FIM DO DIAGNÓSTICO';
PRINT '========================================';
PRINT '';

-- =============================================
-- SOLUÇÕES RÁPIDAS (DESCOMENTE PARA EXECUTAR)
-- =============================================

-- SOLUÇÃO 1: Criar empresa de teste se não existir
/*
IF NOT EXISTS (SELECT 1 FROM TB_Empresas WHERE CodigoCliente = '1001')
BEGIN
    INSERT INTO TB_Empresas (CodigoCliente, CodigoEmpresaFat, CodigoFilialFat, RazaoSocial, CNPJ, Ativo)
    VALUES ('1001', 1, 1, 'Empresa de Teste LTDA', '12.345.678/0001-90', 1);
    PRINT 'Empresa de teste criada (ID = SCOPE_IDENTITY())';
END
*/

-- SOLUÇÃO 2: Vincular usuários sem empresa à primeira empresa disponível
/*
DECLARE @PrimeiraEmpresaID INT;
SELECT TOP 1 @PrimeiraEmpresaID = ID FROM TB_Empresas WHERE Ativo = 1 ORDER BY ID;

IF @PrimeiraEmpresaID IS NOT NULL
BEGIN
    UPDATE TB_Usuarios
    SET IDEmpresa = @PrimeiraEmpresaID
    WHERE IDEmpresa IS NULL;

    PRINT 'Usuários sem empresa foram vinculados à empresa ID ' + CAST(@PrimeiraEmpresaID AS VARCHAR);
END
*/

-- SOLUÇÃO 3: Limpar IDEmpresa inválidos (deixar NULL)
/*
UPDATE TB_Usuarios
SET IDEmpresa = NULL
WHERE IDEmpresa IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM TB_Empresas WHERE ID = TB_Usuarios.IDEmpresa);

PRINT 'IDEmpresa inválidos foram limpos (definidos como NULL)';
*/

GO
