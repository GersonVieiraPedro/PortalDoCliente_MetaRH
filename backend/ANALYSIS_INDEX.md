# MetaRH PortalCliente - Codebase Analysis Index

## Overview

This analysis provides a comprehensive exploration of the MetaRH PortalCliente state management and persistence mechanisms, with recommendations for implementing conversation progress tracking.

**Generated**: October 22, 2025
**Scope**: Full-stack codebase analysis (Frontend + Backend + Database)
**Focus**: State management patterns, persistence layers, and audit trail design

---

## Available Documents

### 1. ARCHITECTURE_SUMMARY.md (START HERE)
**Purpose**: Quick visual overview with diagrams
**Length**: 18 KB, ~500 lines
**Best For**: 
- Getting a quick mental model
- Understanding state flow diagrams
- File location cheat sheets
- Command reference

**Key Sections**:
- Frontend state layers (cookies, localStorage, React Context)
- Backend models and session management
- Data flow diagrams
- Current workflow example (RPS approval)
- File locations and testing checklist

---

### 2. STATE_MANAGEMENT_ANALYSIS.md (COMPREHENSIVE REFERENCE)
**Purpose**: Deep technical analysis with code examples
**Length**: 37 KB, ~1,260 lines
**Best For**:
- Understanding detailed implementation patterns
- Finding specific code examples
- Planning new features
- Security and performance considerations

**Key Sections**:
1. Frontend State Management Patterns
   - UsuarioContext (React Context API)
   - Component-level state with hooks
   - Client-side storage usage
   - Cookie-based session storage

2. Backend State Management Patterns
   - Database-driven architecture
   - Audit history (TB_AprovacaoRPS pattern)
   - Session management with FastAPI
   - Server Actions pattern

3. Persistence Mechanisms
   - Data persistence layers table
   - Current progress tracking analysis
   - API response structures and schemas

4. Pagination & Filtering State
   - Current RPS page implementation
   - Stateless pagination design

5. Recommended Architecture for Conversation Tracking
   - Proposed table schema
   - Context API extension
   - Server Actions implementation
   - Backend endpoints

6. Migration Path & Recommendations
   - Phase-by-phase implementation roadmap
   - Data loss prevention strategies
   - Security considerations
   - Performance optimization

7. Testing Strategy
   - Backend tests (pytest examples)
   - Frontend tests (Vitest examples)
   - Integration test scenarios

8. Implementation Checklist
   - Phase 1-5 breakdown
   - Task dependencies

---

## Key Findings

### Existing Strengths
✓ **Clean Architecture**: Clear separation between frontend, API, and backend
✓ **Type Safety**: TypeScript + Pydantic ensure compile-time safety
✓ **Audit Trail Pattern**: TB_AprovacaoRPS shows mature audit design
✓ **Stateless API**: Request-scoped sessions enable horizontal scaling
✓ **JWT Authentication**: Secure token-based auth with 7-day expiration
✓ **Debounced Input**: Prevents API thrashing from user interactions

### Data Persistence Layers
```
Temporary (Session/Request)
├─ React useState() hooks
├─ localStorage (minimal use)
└─ SQLAlchemy request-scoped sessions

Persistent (Indefinite)
├─ Cookies (7-day JWT token)
└─ SQL Server Database
   ├─ TB_Usuarios (user accounts)
   ├─ TB_Admissao/TB_Demissao (workflows)
   ├─ TB_AprovacaoRPS (approval audit trail)
   ├─ TB_Duplicata (invoices - legacy, read-only)
   └─ [Future] TB_ConversationProgress (conversations)
```

### Recommended Pattern for Conversations

**Follow the TB_AprovacaoRPS model** but with differences:

| Aspect | TB_AprovacaoRPS | TB_ConversationProgress |
|--------|-----------------|--------------------------|
| **Purpose** | Immutable approval actions | Message history tracking |
| **Key Field** | StatusAprovacao | MessageSequence |
| **Write Pattern** | INSERT only (immutable) | INSERT only (immutable) |
| **Query Pattern** | ORDER BY DataAcao DESC LIMIT 1 | ORDER BY MessageSequence ASC LIMIT N |
| **Context** | Single entity status | Full conversation state |
| **Use Case** | Approval workflow audit | Conversation resume |

---

## File Location Reference

### Frontend Key Files
```
/frontend/src/
├── app/layout.tsx                          # Root layout, UseProvider
├── app/contexts/UsuarioContext.tsx         # Global user state
├── app/Financeiro/RPS/                     # RPS approval feature
│   ├── page.tsx                            # Page with component state
│   ├── api.ts                              # Server Actions
│   ├── types.ts                            # Type definitions
│   ├── TabelaRPS.tsx                       # Table component
│   ├── FiltrosTabela.tsx                   # Filter inputs
│   ├── Paginacao.tsx                       # Pagination
│   ├── ModalAprovarRPS.tsx                 # Approval modal
│   ├── ModalReprovarRPS.tsx                # Rejection modal
│   ├── ModalMotivoReprovacao.tsx           # Reason selector
│   └── useDebounce.ts                      # Debounce custom hook
├── lib/
│   ├── cockies.ts                          # JWT token management
│   └── decode.ts                           # Token parsing
└── components/
    ├── Alerta/                             # Modal (uses localStorage)
    ├── MenuLateral/                        # Sidebar
    └── Navegador/                          # Navigation
```

### Backend Key Files
```
/backend/src/backend/
├── main.py                                 # FastAPI app, CORS, routers
├── database.py                             # SQLAlchemy engine, AtivarSession
├── models.py                               # ORM models (9 tables)
├── schema.py                               # Pydantic schemas
├── security.py                             # JWT, UsuarioAtual dependency
├── settings.py                             # Environment config
├── routers/
│   ├── auth.py                             # Login/register
│   ├── financeiro.py                       # RPS/invoice (1,174 lines)
│   ├── requisicoes.py                      # Hiring/termination workflows
│   ├── usuarios.py                         # User CRUD
│   ├── organizacao.py                      # Company/employee lookup
│   ├── simulacoes.py                       # Salary quotes
│   └── imagens.py                          # User photo uploads
├── TabelasGI.py                            # ERP database (ODBC)
├── TabelasLocais.py                        # CSV processing (Azure Data Lake)
└── aruze_storage.py                        # Azure Blob Storage client

/backend/scripts/database/
├── criar_tb_aprovacao_rps.sql              # Audit table creation
├── create_table_tb_duplicata.sql           # Invoice table
├── create_database.sql                     # DB creation
├── insert_tb_duplicata.sql                 # Sample data
└── seed_data.sql                           # Initial data
```

### Database Tables (22 total)
```
Core
├─ TB_Usuarios (11 columns)             - User accounts
├─ TB_Admissao (27 columns)             - Hiring workflows
├─ TB_Demissao (16 columns)             - Termination workflows

Financial
├─ TB_Duplicata (12 columns, legacy)    - Read-only invoices
├─ TB_AprovacaoRPS (14 columns)         - Approval audit trail [PATTERN]

Configuration
├─ TB_ISS (4 columns)                   - Tax rates by municipality
├─ TB_Encargo (7 columns)               - Service charges
├─ TB_Beneficio (9 columns)             - Benefits catalog

[Future]
├─ TB_ConversationProgress (16 columns) - Conversation tracking
```

---

## Implementation Roadmap for Conversation Tracking

### Phase 1: Database (2-3 days)
1. Design `TB_ConversationProgress` schema
2. Create migration script
3. Add performance indexes
4. Test query performance

### Phase 2: Backend API (3-5 days)
1. Create `conversation.py` router
2. Implement CRUD endpoints
3. Add state machine (active → paused → completed)
4. Implement pagination for long conversations
5. Add validation and error handling

### Phase 3: Frontend Context (3-5 days)
1. Create `ConversationContext` provider
2. Implement `useConversation()` hook
3. Create Server Actions for API calls
4. Add error boundaries and retry logic

### Phase 4: Integration (2-3 days)
1. Integrate with RPS approval workflow
2. Capture form state snapshots
3. Implement conversation resume
4. Display history in UI

### Phase 5: Production (1-2 days)
1. Security: access control, rate limiting
2. Performance: optimize queries, add caching
3. Testing: unit + integration tests
4. Documentation: API docs, frontend hooks

**Total Estimate**: 11-18 days (2-3 weeks)

---

## Quick Decision Guide

### "I need to understand..."

**What are the main state management patterns?**
→ See ARCHITECTURE_SUMMARY.md, Section 1-4

**How is the RPS approval workflow implemented?**
→ See ARCHITECTURE_SUMMARY.md, Section 6

**How should I implement conversation tracking?**
→ See STATE_MANAGEMENT_ANALYSIS.md, Section 6

**Where is TB_AprovacaoRPS and how does it work?**
→ See STATE_MANAGEMENT_ANALYSIS.md, Section 2.2

**What's the migration path for a new feature?**
→ See STATE_MANAGEMENT_ANALYSIS.md, Section 7

**How do I test the new conversation feature?**
→ See STATE_MANAGEMENT_ANALYSIS.md, Section 11

**What are the security considerations?**
→ See STATE_MANAGEMENT_ANALYSIS.md, Section 9

**How should I handle data loss prevention?**
→ See STATE_MANAGEMENT_ANALYSIS.md, Section 8

---

## Technical Stack Summary

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS 4
- **State**: React Context API + useState hooks
- **Form Handling**: Next.js Form + useActionState
- **Animations**: Framer Motion
- **Input Masking**: IMask
- **Number Formatting**: react-number-format
- **Dev Server**: Turbopack
- **Auth Storage**: js-cookie

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 with mapped dataclasses
- **Database**: SQL Server (PortalCliente)
- **Password Hashing**: Argon2 (via pwdlib)
- **Auth**: JWT (HS256, 600min expiration)
- **Dependency Injection**: FastAPI's built-in system
- **Admin Tasks**: Alembic (migrations)
- **Data Processing**: Pandas, NumPy
- **Cloud**: Azure Blob Storage, Azure Data Lake
- **Legacy Integration**: ODBC for ERP database

### Database
- **Primary**: SQL Server (PortalCliente) - Main application
- **Legacy ERP**: SQL Server (INTEGRA_METASP) - Read-only via ODBC
- **Data Lake**: Azure Data Lake Gen2 - CSV files for Pipedrive CRM

---

## Deployment Considerations

### Scaling
- **Stateless API** → Horizontal scaling (multiple backend instances)
- **JWT tokens** → No server-side session storage needed
- **Database indexes** → Composite indexes on TB_AprovacaoRPS for performance
- **Connection pooling** → SQLAlchemy handles automatically

### Security
- **JWT** → Secure token with 600min expiration
- **CORS** → Configured in main.py (restrict origins in production)
- **Passwords** → Argon2 hashing (slow, resistant to GPU attacks)
- **File uploads** → Converted to PNG (prevents executables)
- **Sensitive data** → Consider encryption for hiring/salary data

### Backup & Recovery
- **Database** → SQL Server backups + Azure managed backup
- **Azure Blob** → Geo-redundant storage configured
- **Data Lake** → CSV versioning via Azure snapshots
- **Conversation logs** → Consider archival after 90 days

---

## Next Steps

1. **For Quick Understanding**: Read ARCHITECTURE_SUMMARY.md (20 min)
2. **For Implementation**: Reference STATE_MANAGEMENT_ANALYSIS.md (ongoing)
3. **For Coding**: Use file locations cheat sheet + existing patterns
4. **For New Features**: Follow the TB_AprovacaoRPS pattern + roadmap

---

## Document Statistics

| Document | Size | Lines | Purpose |
|----------|------|-------|---------|
| ARCHITECTURE_SUMMARY.md | 18 KB | 500 | Visual overview + diagrams |
| STATE_MANAGEMENT_ANALYSIS.md | 37 KB | 1,260 | Comprehensive technical guide |
| This index | 8 KB | 300 | Navigation and quick reference |

**Total Analysis**: 63 KB, 2,060 lines of detailed documentation

---

## Questions & Answers

**Q: Where should I store conversation messages?**
A: Create TB_ConversationProgress table following the TB_AprovacaoRPS pattern (immutable append-only log). See Section 6 of STATE_MANAGEMENT_ANALYSIS.md.

**Q: How do I preserve form state between page reloads?**
A: Use ContextSnapshot field in TB_ConversationProgress to store JSON of current page state. See Section 6.1.

**Q: What if the user closes the browser mid-conversation?**
A: Auto-save drafts to localStorage every 30 seconds. Resume from DB when they return. See Section 8.2.

**Q: How do I ensure user can only see their own conversations?**
A: Filter by `ID_Usuario == usuario_atual.id` in all queries. See Section 9.1.

**Q: Should messages be encrypted?**
A: Optional. For sensitive workflows (hiring, salary), use Fernet encryption. See Section 9.3.

**Q: How do I handle long conversations (1000+ messages)?**
A: Use paginated query with limit/offset. See Section 10.2.

**Q: Can I run multiple backend instances?**
A: Yes! The API is stateless. Use load balancer with JWT auth. See Scaling section.

---

## Related Documentation

- **CLAUDE.md**: Project guidelines and development commands
- **README.md**: Project setup and running instructions

---

## Document Version

**Created**: 2025-10-22
**Author**: Claude Code Analysis
**Format**: Markdown
**Status**: Complete and ready for reference

---

## How to Use These Docs

1. **For Architecture Decisions**: Start with ARCHITECTURE_SUMMARY.md
2. **For Technical Details**: Consult STATE_MANAGEMENT_ANALYSIS.md
3. **For File Navigation**: Use the cheat sheets in both documents
4. **For Implementation**: Follow the migration roadmap and patterns
5. **For Problem-Solving**: Search this index for relevant sections

---

End of Index
