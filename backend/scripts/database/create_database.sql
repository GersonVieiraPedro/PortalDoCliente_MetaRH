-- ============================================
-- Script de Criação do Banco de Dados Portal Cliente
-- SQL Server Express
-- ============================================

-- Criar o banco de dados (se não existir)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'PortalCliente')
BEGIN
    CREATE DATABASE PortalCliente;
END
GO

USE PortalCliente;
GO

-- ============================================
-- Criar Login e Usuário
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'metarhApp')
BEGIN
    CREATE LOGIN metarhApp WITH PASSWORD = '123456';
END
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'metarhApp')
BEGIN
    CREATE USER metarhApp FOR LOGIN metarhApp;
    ALTER ROLE db_owner ADD MEMBER metarhApp;
END
GO

-- ============================================
-- TABELA: TB_Usuarios
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_Usuarios')
BEGIN
    CREATE TABLE TB_Usuarios (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Nome NVARCHAR(255) NOT NULL,
        Email NVARCHAR(255) NOT NULL UNIQUE,
        Senha NVARCHAR(500) NOT NULL,
        CNPJ NVARCHAR(18) NOT NULL,
        TipoAcesso NVARCHAR(50) NOT NULL DEFAULT 'Cliente',
        Acesso NVARCHAR(50) NULL,
        PipedriveID NVARCHAR(50) NOT NULL DEFAULT 'NãoMapeado',
        CodigoCliente NVARCHAR(50) NOT NULL DEFAULT 'NãoMapeado',
        Status BIT NOT NULL DEFAULT 0,
        DataCadastro DATETIME NOT NULL DEFAULT GETDATE(),
        DataAtualizacao DATETIME NOT NULL DEFAULT GETDATE()
    );

    -- Criar índices
    CREATE INDEX IX_TB_Usuarios_Email ON TB_Usuarios(Email);
    CREATE INDEX IX_TB_Usuarios_CNPJ ON TB_Usuarios(CNPJ);
    CREATE INDEX IX_TB_Usuarios_TipoAcesso ON TB_Usuarios(TipoAcesso);

    PRINT 'Tabela TB_Usuarios criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Usuarios já existe.';
END
GO

-- ============================================
-- TABELA: TB_Admissao
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_Admissao')
BEGIN
    CREATE TABLE TB_Admissao (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        ID_Usuario INT NOT NULL,
        TipoVaga NVARCHAR(100) NOT NULL,
        Cargo NVARCHAR(200) NOT NULL,
        CentroCusto NVARCHAR(200) NOT NULL,
        SetorTrabalho NVARCHAR(200) NOT NULL,
        ModalidadeTrabalho NVARCHAR(100) NOT NULL,
        MotivoContratacao NVARCHAR(500) NOT NULL,
        EscalaTrabalho NVARCHAR(200) NOT NULL,
        LocalTrabalho NVARCHAR(500) NOT NULL,
        Salario NVARCHAR(50) NOT NULL,
        DescricaoCargo NVARCHAR(MAX) NOT NULL,
        PrecisaEPI BIT NOT NULL,
        DescricaoEPI NVARCHAR(MAX) NULL,
        NomeSubstituido NVARCHAR(255) NULL,
        CPFSubstituido NVARCHAR(14) NULL,
        MotivoSubstituido NVARCHAR(500) NULL,
        NomeResponsavelRH NVARCHAR(255) NOT NULL,
        EmailResponsavelRH NVARCHAR(255) NOT NULL,
        TelefoneResponsavelRH NVARCHAR(20) NOT NULL,
        NomeGestorPonto NVARCHAR(255) NOT NULL,
        EmailGestorPonto NVARCHAR(255) NOT NULL,
        TelefoneGestorPonto NVARCHAR(20) NOT NULL,
        NomePessoaPrimeiroDia NVARCHAR(255) NOT NULL,
        DepartamentoPrimeiroDia NVARCHAR(255) NOT NULL,
        HorarioPrimeiroDia NVARCHAR(100) NOT NULL,
        Proprietario NVARCHAR(255) NULL,
        DataInicio DATETIME NULL,
        DataEncerramento DATETIME NULL,
        Status NVARCHAR(50) NOT NULL DEFAULT 'Não Iniciado',
        Visivel BIT NOT NULL DEFAULT 1,
        DataCadastro DATETIME NOT NULL DEFAULT GETDATE(),
        DataAtualizacao DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Admissao_Usuario FOREIGN KEY (ID_Usuario) REFERENCES TB_Usuarios(ID)
    );

    -- Criar índices
    CREATE INDEX IX_TB_Admissao_ID_Usuario ON TB_Admissao(ID_Usuario);
    CREATE INDEX IX_TB_Admissao_Status ON TB_Admissao(Status);
    CREATE INDEX IX_TB_Admissao_DataCadastro ON TB_Admissao(DataCadastro);

    PRINT 'Tabela TB_Admissao criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Admissao já existe.';
END
GO

-- ============================================
-- TABELA: TB_Demissao
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_Demissao')
BEGIN
    CREATE TABLE TB_Demissao (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        ID_Usuario INT NOT NULL,
        CodigoFuncionario INT NOT NULL,
        NomeFuncionario NVARCHAR(255) NOT NULL,
        Empresa NVARCHAR(255) NOT NULL,
        Cargo NVARCHAR(200) NOT NULL,
        CentroCusto NVARCHAR(200) NOT NULL,
        Gestor NVARCHAR(255) NOT NULL,
        Salario NVARCHAR(50) NOT NULL,
        DataAdmissao DATETIME NOT NULL,
        DataDemissao DATETIME NOT NULL,
        MotivoDemissao NVARCHAR(500) NOT NULL,
        FeriasVencidas NVARCHAR(100) NOT NULL,
        AvisoPrevio NVARCHAR(100) NOT NULL,
        ConhecimentoDesligamento NVARCHAR(100) NOT NULL,
        ComunicadoPresencial NVARCHAR(100) NOT NULL,
        Endereco NVARCHAR(500) NOT NULL,
        Horario NVARCHAR(100) NOT NULL,
        Proprietario NVARCHAR(255) NULL,
        DataInicio DATETIME NULL,
        DataEncerramento DATETIME NULL,
        Status NVARCHAR(50) NOT NULL DEFAULT 'Não Iniciado',
        Visivel BIT NOT NULL DEFAULT 1,
        DataCadastro DATETIME NOT NULL DEFAULT GETDATE(),
        DataAtualizacao DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Demissao_Usuario FOREIGN KEY (ID_Usuario) REFERENCES TB_Usuarios(ID)
    );

    -- Criar índices
    CREATE INDEX IX_TB_Demissao_ID_Usuario ON TB_Demissao(ID_Usuario);
    CREATE INDEX IX_TB_Demissao_CodigoFuncionario ON TB_Demissao(CodigoFuncionario);
    CREATE INDEX IX_TB_Demissao_Status ON TB_Demissao(Status);
    CREATE INDEX IX_TB_Demissao_DataCadastro ON TB_Demissao(DataCadastro);

    PRINT 'Tabela TB_Demissao criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Demissao já existe.';
END
GO

-- ============================================
-- TABELA: TB_ISS
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_ISS')
BEGIN
    CREATE TABLE TB_ISS (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        UF NVARCHAR(2) NOT NULL,
        Municipio NVARCHAR(255) NOT NULL,
        Label NVARCHAR(500) NOT NULL,
        ISS FLOAT NOT NULL
    );

    -- Criar índices
    CREATE INDEX IX_TB_ISS_UF ON TB_ISS(UF);
    CREATE INDEX IX_TB_ISS_Municipio ON TB_ISS(Municipio);

    PRINT 'Tabela TB_ISS criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela TB_ISS já existe.';
END
GO

-- ============================================
-- TABELA: TB_Encargo
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_Encargo')
BEGIN
    CREATE TABLE TB_Encargo (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        CodigoServico NVARCHAR(50) NOT NULL,
        Servico NVARCHAR(255) NOT NULL,
        Grupo NVARCHAR(255) NOT NULL,
        Nome NVARCHAR(255) NOT NULL,
        Percentual FLOAT NOT NULL,
        UltimoUsuario NVARCHAR(255) NOT NULL,
        DataCadastro DATETIME NOT NULL DEFAULT GETDATE(),
        DataAtualizacao DATETIME NOT NULL DEFAULT GETDATE()
    );

    -- Criar índices
    CREATE INDEX IX_TB_Encargo_CodigoServico ON TB_Encargo(CodigoServico);
    CREATE INDEX IX_TB_Encargo_Servico ON TB_Encargo(Servico);
    CREATE INDEX IX_TB_Encargo_Grupo ON TB_Encargo(Grupo);

    PRINT 'Tabela TB_Encargo criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Encargo já existe.';
END
GO

-- ============================================
-- TABELA: TB_Beneficio
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TB_Beneficio')
BEGIN
    CREATE TABLE TB_Beneficio (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Nome NVARCHAR(255) NOT NULL,
        Editavel BIT NOT NULL,
        Frequencia NVARCHAR(50) NOT NULL,
        Quantidade INT NOT NULL,
        Dias INT NOT NULL,
        ValorUnitario FLOAT NOT NULL,
        Desconto FLOAT NOT NULL,
        Categoria NVARCHAR(100) NOT NULL,
        UltimoUsuario NVARCHAR(255) NOT NULL,
        DataCadastro DATETIME NOT NULL DEFAULT GETDATE(),
        DataAtualizacao DATETIME NOT NULL DEFAULT GETDATE()
    );

    -- Criar índices
    CREATE INDEX IX_TB_Beneficio_Nome ON TB_Beneficio(Nome);
    CREATE INDEX IX_TB_Beneficio_Categoria ON TB_Beneficio(Categoria);

    PRINT 'Tabela TB_Beneficio criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela TB_Beneficio já existe.';
END
GO

-- ============================================
-- Criar Triggers para Atualização Automática de DataAtualizacao
-- ============================================

-- Trigger para TB_Usuarios
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Usuarios_Update')
BEGIN
    EXEC('
    CREATE TRIGGER TR_TB_Usuarios_Update
    ON TB_Usuarios
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE TB_Usuarios
        SET DataAtualizacao = GETDATE()
        FROM TB_Usuarios u
        INNER JOIN inserted i ON u.ID = i.ID;
    END
    ');
    PRINT 'Trigger TR_TB_Usuarios_Update criada com sucesso.';
END
GO

-- Trigger para TB_Admissao
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Admissao_Update')
BEGIN
    EXEC('
    CREATE TRIGGER TR_TB_Admissao_Update
    ON TB_Admissao
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE TB_Admissao
        SET DataAtualizacao = GETDATE()
        FROM TB_Admissao a
        INNER JOIN inserted i ON a.ID = i.ID;
    END
    ');
    PRINT 'Trigger TR_TB_Admissao_Update criada com sucesso.';
END
GO

-- Trigger para TB_Demissao
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Demissao_Update')
BEGIN
    EXEC('
    CREATE TRIGGER TR_TB_Demissao_Update
    ON TB_Demissao
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE TB_Demissao
        SET DataAtualizacao = GETDATE()
        FROM TB_Demissao d
        INNER JOIN inserted i ON d.ID = i.ID;
    END
    ');
    PRINT 'Trigger TR_TB_Demissao_Update criada com sucesso.';
END
GO

-- Trigger para TB_Encargo
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Encargo_Update')
BEGIN
    EXEC('
    CREATE TRIGGER TR_TB_Encargo_Update
    ON TB_Encargo
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE TB_Encargo
        SET DataAtualizacao = GETDATE()
        FROM TB_Encargo e
        INNER JOIN inserted i ON e.ID = i.ID;
    END
    ');
    PRINT 'Trigger TR_TB_Encargo_Update criada com sucesso.';
END
GO

-- Trigger para TB_Beneficio
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_TB_Beneficio_Update')
BEGIN
    EXEC('
    CREATE TRIGGER TR_TB_Beneficio_Update
    ON TB_Beneficio
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE TB_Beneficio
        SET DataAtualizacao = GETDATE()
        FROM TB_Beneficio b
        INNER JOIN inserted i ON b.ID = i.ID;
    END
    ');
    PRINT 'Trigger TR_TB_Beneficio_Update criada com sucesso.';
END
GO

PRINT '';
PRINT '============================================';
PRINT 'Script de criação finalizado com sucesso!';
PRINT '============================================';
PRINT 'Banco de dados: PortalCliente';
PRINT 'Usuário: metarhApp';
PRINT 'Senha: 123456';
PRINT '';
PRINT 'Tabelas criadas:';
PRINT '  - TB_Usuarios';
PRINT '  - TB_Admissao';
PRINT '  - TB_Demissao';
PRINT '  - TB_ISS';
PRINT '  - TB_Encargo';
PRINT '  - TB_Beneficio';
PRINT '============================================';
GO
