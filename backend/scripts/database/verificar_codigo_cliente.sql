-- ================================================================
-- Script Auxiliar: Descobrir CodigoCliente para Seed
-- ================================================================
-- Descrição: Ajuda a identificar qual CodigoCliente usar no seed
-- Sistema: Portal do Cliente MetaRH
-- ================================================================

PRINT '';
PRINT '================================================================';
PRINT 'VERIFICAÇÃO DE EMPRESA E USUÁRIO';
PRINT '================================================================';
PRINT '';

-- ================================================================
-- 1. Listar empresas ativas no sistema
-- ================================================================

PRINT '1. EMPRESAS CADASTRADAS (ATIVAS):';
PRINT '-------------------------------------------------------------------';

SELECT
    ID,
    CodigoCliente,
    RazaoSocial,
    CNPJ,
    CASE WHEN Ativo = 1 THEN 'Sim' ELSE 'Não' END AS Ativo
FROM TB_Empresas
WHERE Ativo = 1
ORDER BY RazaoSocial;

PRINT '';
PRINT '-------------------------------------------------------------------';
PRINT '';

-- ================================================================
-- 2. Verificar usuários e suas empresas vinculadas
-- ================================================================

PRINT '2. USUÁRIOS E SUAS EMPRESAS:';
PRINT '-------------------------------------------------------------------';

SELECT
    u.ID AS UsuarioID,
    u.Nome AS NomeUsuario,
    u.Email,
    u.IDEmpresa,
    e.CodigoCliente,
    e.RazaoSocial,
    e.CNPJ,
    CASE WHEN u.Status = 1 THEN 'Ativo' ELSE 'Inativo' END AS StatusUsuario
FROM TB_Usuarios u
LEFT JOIN TB_Empresas e ON u.IDEmpresa = e.ID
WHERE u.TipoAcesso = 'Cliente'  -- Apenas clientes (não admins)
ORDER BY u.Nome;

PRINT '';
PRINT '-------------------------------------------------------------------';
PRINT '';

-- ================================================================
-- 3. Verificar se já existem contratos cadastrados
-- ================================================================

PRINT '3. CONTRATOS JÁ CADASTRADOS (POR EMPRESA):';
PRINT '-------------------------------------------------------------------';

IF EXISTS (SELECT 1 FROM TB_Contratos)
BEGIN
    SELECT
        c.CodigoCliente,
        e.RazaoSocial,
        COUNT(*) AS TotalContratos,
        SUM(CASE WHEN c.Status = 'A' THEN 1 ELSE 0 END) AS Ativos,
        SUM(CASE WHEN c.Status = 'I' THEN 1 ELSE 0 END) AS Inativos,
        SUM(CASE WHEN c.ArquivoPDF IS NOT NULL THEN 1 ELSE 0 END) AS ComPDF
    FROM TB_Contratos c
    LEFT JOIN TB_Empresas e ON CAST(c.CodigoCliente AS VARCHAR(50)) = e.CodigoCliente
    GROUP BY c.CodigoCliente, e.RazaoSocial
    ORDER BY c.CodigoCliente;
END
ELSE
BEGIN
    PRINT 'Nenhum contrato cadastrado ainda.';
END

PRINT '';
PRINT '-------------------------------------------------------------------';
PRINT '';

-- ================================================================
-- 4. Recomendação de qual CodigoCliente usar
-- ================================================================

PRINT '4. RECOMENDAÇÃO:';
PRINT '-------------------------------------------------------------------';
PRINT '';

DECLARE @RecomendacaoCodigoCliente VARCHAR(50);
DECLARE @RecomendacaoRazaoSocial NVARCHAR(200);

-- Pegar a primeira empresa ativa com usuário vinculado
SELECT TOP 1
    @RecomendacaoCodigoCliente = e.CodigoCliente,
    @RecomendacaoRazaoSocial = e.RazaoSocial
FROM TB_Empresas e
INNER JOIN TB_Usuarios u ON u.IDEmpresa = e.ID
WHERE e.Ativo = 1 AND u.Status = 1
ORDER BY u.DataCadastro ASC;

IF @RecomendacaoCodigoCliente IS NOT NULL
BEGIN
    PRINT 'Para o script de seed, use o seguinte CodigoCliente:';
    PRINT '';
    PRINT '    DECLARE @CodigoCliente INT = ' + @RecomendacaoCodigoCliente + ';';
    PRINT '';
    PRINT 'Empresa: ' + @RecomendacaoRazaoSocial;
    PRINT '';
END
ELSE
BEGIN
    PRINT 'ATENÇÃO: Nenhuma empresa ativa com usuário vinculado encontrada!';
    PRINT '';
    PRINT 'AÇÕES NECESSÁRIAS:';
    PRINT '1. Criar uma empresa em TB_Empresas';
    PRINT '2. Vincular um usuário a essa empresa (TB_Usuarios.IDEmpresa)';
    PRINT '3. Executar este script novamente';
    PRINT '';
END

PRINT '-------------------------------------------------------------------';
PRINT '';

-- ================================================================
-- 5. Instruções finais
-- ================================================================

PRINT '5. PRÓXIMOS PASSOS:';
PRINT '-------------------------------------------------------------------';
PRINT '';
PRINT '1. Copie o CodigoCliente recomendado acima';
PRINT '2. Abra o arquivo: seed_contratos_teste.sql';
PRINT '3. Altere a linha: DECLARE @CodigoCliente INT = ...';
PRINT '4. Execute o script seed_contratos_teste.sql';
PRINT '5. Faça login no portal com o usuário correspondente';
PRINT '6. Navegue até: Financeiro > Gestão de Contratos';
PRINT '7. Verifique se os 5 contratos de teste aparecem';
PRINT '';
PRINT '-------------------------------------------------------------------';
PRINT '';
PRINT '================================================================';
PRINT 'VERIFICAÇÃO CONCLUÍDA';
PRINT '================================================================';
GO
