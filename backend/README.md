# Portal do Cliente - MetaRH

Sistema web de atendimento a clientes da empresa MetaRH. Os clientes fazem login na plataforma e podem solicitar tarefas diretamente para a equipe.

## Tecnologias Utilizadas

### Frontend

- Next.js (React Framework)
- JavaScript / TypeScript
- TailwindCSS
- fech

### Backend

- FastAPI (Python)
- JWT Authentication
- SQL
- SQLite (Ambiente de desenvolvimenti)

## Estrutura do Projeto

```
/backend         # Código do servidor (API FastAPI)
/frontend        # Código do cliente (Next.js)
/.vscode         # Configurações de workspace
.gitignore       # Arquivos e pastas ignoradas no Git
README.md        # Este documento
```

## Funcionalidades principais

- Autenticação segura com JWT.
- Cadastro e login de usuários clientes.
- Solicitação de tarefas pelos clientes.
- Painel administrativo para gestão de tarefas.
- Integração futura com ERP leve para conciliação de notas fiscais.

## Como rodar o projeto localmente

### Backend

1. Acesse a pasta do backend:
   ```bash
   cd backend
   ```
2. (Recomendado) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Rode o servidor:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Acesse a pasta do frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências:
   ```bash
   npm install
   # ou
   yarn install
   ```
3. Rode o projeto:
   ```bash
   npm run dev
   # ou
   yarn dev
   ```

O frontend estará disponível em `http://localhost:3000` O backend estará disponível em `http://localhost:8000`

## Observações

- Configurar variáveis de ambiente como a URL da API no frontend (`.env.local`).
- Garantir que o CORS esteja habilitado no FastAPI para permitir acesso pelo frontend.
- Em produção, considerar deploy separado para frontend (Vercel, Netlify) e backend (Render, Railway, AWS, etc.).

## Status atual

🚧 Em desenvolvimento... Próximas tarefas:

- Finalizar fluxo de autenticação.
- Criar dashboard de tarefas.
- Integrar API de conciliação de notas fiscais.

## Licença

Este projeto é privado e de uso exclusivo da MetaRH.
