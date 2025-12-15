-- ========================================
-- TABELA: TB_MotivoReprovacaoRPS
-- Descrição: Armazena os motivos de reprovação de RPS
-- Data: 2025-01-22
-- Objetivo: Padronizar os motivos de reprovação com dropdown
-- ========================================

CREATE TABLE TB_MotivoReprovacaoRPS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(50) NOT NULL UNIQUE,         -- Código único do motivo (ex: 'VALORES_DIVERGENTES')
    Descricao VARCHAR(200) NOT NULL,            -- Descrição curta (ex: 'Valores divergentes')
    DescricaoDetalhada VARCHAR(500) NULL,       -- Descrição longa/orientações
    Ativo BIT NOT NULL DEFAULT 1,               -- Flag de deleção lógica (1=ativo, 0=inativo)
    Ordem INT NOT NULL DEFAULT 999,             -- Ordem de exibição no dropdown
    DataCadastro DATETIME NOT NULL DEFAULT GETDATE(),
    DataAtualizacao DATETIME NOT NULL DEFAULT GETDATE()
);

-- Índices para performance
CREATE INDEX IX_MotivoReprovacaoRPS_Ativo ON TB_MotivoReprovacaoRPS(Ativo);
CREATE INDEX IX_MotivoReprovacaoRPS_Ordem ON TB_MotivoReprovacaoRPS(Ordem);

-- ========================================
-- DADOS INICIAIS
-- ========================================

INSERT INTO TB_MotivoReprovacaoRPS (Codigo, Descricao, DescricaoDetalhada, Ordem) VALUES
('VALORES_DIVERGENTES', 'Valores divergentes', 'Os valores informados no RPS não conferem com os registros contábeis', 1),
('FALTA_DOCUMENTACAO', 'Falta de documentação', 'Documentação obrigatória não foi anexada ou está incompleta', 2),
('DADOS_INCORRETOS', 'Dados incorretos', 'Informações cadastrais ou fiscais estão incorretas ou desatualizadas', 3),
('SERVICO_NAO_PRESTADO', 'Serviço não prestado', 'O serviço descrito no RPS não foi efetivamente prestado', 4),
('DUPLICIDADE', 'Duplicidade de RPS', 'RPS já foi emitido anteriormente para o mesmo serviço', 5),
('VENCIMENTO_INCORRETO', 'Vencimento incorreto', 'Data de vencimento está fora do prazo permitido ou incorreta', 6),
('COMPETENCIA_INCORRETA', 'Competência incorreta', 'Mês/ano de competência não corresponde ao período do serviço', 7),
('OUTROS', 'Outros motivos', 'Outros motivos não listados acima (detalhar na descrição)', 999);

GO
