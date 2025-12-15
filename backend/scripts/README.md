# 📜 Scripts do Portal MetaRH

Esta pasta contém todos os scripts auxiliares do projeto, organizados por categoria.

---

## 📂 Estrutura de Pastas

```
scripts/
├── database/           # Scripts SQL e utilitários de banco de dados
│   ├── create_database.sql
│   ├── create_table_tb_duplicata.sql
│   ├── insert_tb_duplicata.sql
│   ├── seed_data.sql
│   ├── csv_to_sql_inserts.py
│   └── README.md
│
└── README.md          # Este arquivo
```

---

## 📁 Categorias

### **🗄️ Database** (`/database`)

Scripts relacionados ao banco de dados SQL Server:

- **Criação de estruturas** - Tabelas, índices, constraints
- **População de dados** - INSERTs em massa, seed data
- **Utilitários** - Scripts Python para conversão de dados

**[Ver documentação completa →](database/README.md)**

---

## 🚀 Quick Start

### **Setup Completo do Banco de Dados**

```bash
cd scripts/database

# 1. Criar estrutura
sqlcmd -S servidor -d NomeDoBanco -i create_table_tb_duplicata.sql

# 2. Popular dados
sqlcmd -S servidor -d NomeDoBanco -i insert_tb_duplicata.sql
```

---

## 📚 Documentações Detalhadas

Cada pasta contém seu próprio README com instruções específicas:

- **[Database README](database/README.md)** - Detalhes sobre scripts SQL

---

## 🔧 Requisitos

### **Para Scripts SQL:**
- SQL Server 2016+ ou Azure SQL Database
- sqlcmd instalado (ou SSMS / Azure Data Studio)
- Permissões de CREATE TABLE e INSERT

### **Para Scripts Python:**
- Python 3.8+
- pandas (`pip install pandas`)

---

## 📝 Convenções

### **Nomenclatura de Arquivos:**
- `create_*.sql` - Scripts de criação (DDL)
- `insert_*.sql` - Scripts de inserção de dados (DML)
- `seed_*.sql` - Scripts de dados iniciais
- `*_to_*.py` - Scripts de conversão/transformação

### **Formato dos Scripts SQL:**
- Encoding: UTF-8
- Line endings: LF (Unix)
- Comentários em português
- Sempre incluir `GO` após blocos lógicos

---

## ⚠️ Avisos Importantes

1. **Backup primeiro!** - Sempre faça backup antes de executar scripts em produção
2. **Teste em DEV** - Execute primeiro em ambiente de desenvolvimento
3. **Revise os scripts** - Ajuste nomes de banco, servidor, etc. antes de executar
4. **Credenciais** - Nunca commite credenciais nos scripts

---

## 📞 Suporte

Para questões sobre os scripts:

1. Consulte o README da categoria específica
2. Verifique a documentação da API em `/backend/API_NOTAS_FISCAIS.md`
3. Abra uma issue no repositório

---

**Última atualização:** 2025-10-13
