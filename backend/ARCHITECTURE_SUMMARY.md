# MetaRH PortalCliente - State Management Architecture Overview

## Quick Reference: Current Architecture

### Frontend State Layers
```
┌─────────────────────────────────────────────────────────────┐
│ BROWSER LAYER                                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Cookies (7 days)                                            │
│  └─ JWT Token: token-portal-metarh                           │
│     (Used for API authentication)                            │
│                                                               │
│  localStorage (Indefinite)                                   │
│  └─ AlertaVisivel: true/false (modal state)                  │
│  └─ [Future] conversation_draft_{sessionID} (drafts)         │
│                                                               │
│  sessionStorage (Session only)                               │
│  └─ [Future] Recent searches, filters                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### React Component State Hierarchy
```
┌─────────────────────────────────────────────────────────────┐
│ APP LEVEL (Root Layout)                                     │
├─────────────────────────────────────────────────────────────┤
│  UseProvider (UsuarioContext)                                │
│  ├─ usuario: User profile                                    │
│  ├─ token: JWT from cookies                                  │
│  ├─ CNPJS: Company list                                      │
│  └─ CodigosCliente: Client codes                             │
│                                                               │
│ PAGE LEVEL (e.g., RPS Page)                                  │
│ └─ rps: RPS[]                                                │
│ └─ filtros: FiltrosState                                     │
│ └─ paginaAtual: number                                       │
│ └─ itensPorPagina: number                                    │
│                                                               │
│ COMPONENT LEVEL (Table, Modal, Form)                         │
│ └─ Modal visibility, form state, UI flags                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Request → Response → State Update
```
User Action (e.g., filter RPS)
    ↓
[Client] React Component State Updates (debounced)
    ↓
[Server Action] buscarRPS() called (POST /financeiro/rps?...)
    ↓
[Backend] FastAPI Route Handler
    ├─ Check JWT (UsuarioAtual dependency)
    ├─ Build SQLAlchemy query with filters
    ├─ Execute query against SQL Server
    └─ Return ListaRPSResponse (JSON)
    ↓
[Client] JSON → Component State (setRPS, setResumo, setTotal)
    ↓
React Re-render → User sees updated table
```

---

## 1. Frontend: React Context + Hooks

### UsuarioContext (Global)
```typescript
// Shared across entire app
const { usuario, setUsuario, carregarUsuario } = useUsuario()

// Contains
usuario = {
  ID, Nome, Email, CNPJ, TipoAcesso, PipedriveID, CodigoCliente, Status,
  token, existeImagem, urlImagem, CNPJS[], CodigosCliente[]
}

// Loaded on: App mount (via useEffect in layout.tsx)
// Persisted: JWT in cookies (7 days)
// Scope: App-wide
```

### Component-Level State (Local)
```typescript
// RPS Page Example
const [rps, setRPS] = useState<RPS[]>()           // Current page data
const [resumo, setResumo] = useState<ResumoRPS>   // Summary cards
const [filtros, setFiltros] = useState<Filtros>   // Search criteria
const [paginaAtual, setPaginaAtual] = useState(1) // Pagination position
const [loading, setLoading] = useState(true)      // UI state

// Debouncing (500ms delay on search input)
const numeroRPSDebounced = useDebounce(filtros.numeroRPS, 500)

// Re-fetch when any dependency changes
useEffect(() => {
  carregarRPS()
}, [paginaAtual, numeroRPSDebounced, competenciaDebounced, ...])
```

---

## 2. Backend: SQLAlchemy ORM + SQL Server

### Database Models (ORM Mapped Dataclasses)
```python
@TabelaRegistro.mapped_as_dataclass
class TB_Usuarios:
    ID: Mapped[int]
    Nome: Mapped[str]
    Email: Mapped[str]  # Unique
    Senha: Mapped[str]  # Argon2 hashed
    Status: Mapped[bool]
    DataCadastro: Mapped[datetime]
    DataAtualizacao: Mapped[datetime]

@TabelaRegistro.mapped_as_dataclass  
class TB_AprovacaoRPS:           # ← Audit trail example
    ID: Mapped[int]              # Auto-increment
    CodigoEmpresaFat: Mapped[int] # From TB_Duplicata (read-only)
    StatusAprovacao: Mapped[str]  # 'pendente' → 'aprovado' or 'reprovado'
    MotivoReprovacao: Optional[str]
    ID_Usuario: Mapped[int]      # Who did it
    NomeUsuario: Mapped[str]     # Denormalized for history
    DataAcao: Mapped[datetime]   # When
```

### Session Management (Per-Request)
```python
def AtivarSession():
    with Session(engine) as session:  # Create session
        yield session                 # Use in route handler
        # Auto-cleanup: session closed, connection returned to pool

# In route handler
@router.get("/rps")
def listar_rps(
    session: Session = Depends(AtivarSession),  # Injected
    usuario_atual = Depends(UsuarioAtual)       # JWT validated
):
    query = select(TB_Duplicata)...
    results = session.execute(query).scalars().all()
    # Session auto-closed after response
```

---

## 3. API Layer: Server Actions Bridge

### Next.js Server Action (Frontend Boundary)
```typescript
'use server'  // ← Executed on server, token handled securely

export async function buscarRPS(
  token: string,
  filtros: FiltrosRPS
): Promise<ListaRPSResponse> {
  
  // Build query with filters
  const params = new URLSearchParams()
  if (filtros.numeroRPS) params.append('numero_rps', filtros.numeroRPS)
  
  // Call backend FastAPI
  const response = await fetch(
    `http://127.0.0.1:8000/financeiro/rps?${params}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    }
  )
  
  return response.json()
}
```

**Why Server Actions?**
- Token never exposed to client
- Type-safe API calls
- Automatic caching control (cache: 'no-store')
- Error handling on server

---

## 4. Key Design Patterns Already Implemented

### Pattern 1: Audit Trail (TB_AprovacaoRPS)
```
Workflow:
  TB_Duplicata (Legacy, Read-Only)
            ↓
            ↓ (Reference, never modify)
            ↓
  TB_AprovacaoRPS (Audit Log, Append-Only)
  
  ├─ ID: 1, StatusAprovacao: 'pendente', DataAcao: 2025-01-17 10:00
  ├─ ID: 2, StatusAprovacao: 'reprovado', DataAcao: 2025-01-17 10:30, MotivoReprovacao: 'Missing data'
  └─ ID: 3, StatusAprovacao: 'aprovado', DataAcao: 2025-01-17 11:00

Latest Status = ORDER BY DataAcao DESC LIMIT 1 = 'aprovado'
Full History = All 3 records preserved for audit
```

**Key Benefits:**
- Non-destructive (original data untouched)
- Complete audit trail (every action recorded)
- User attribution (who, when, why)
- Temporal queries possible (state at any point in time)

### Pattern 2: Debounced Search
```typescript
// Raw filter input (fires on every keystroke)
const [numeroRPS, setNumeroRPS] = useState('')

// Debounced version (fires 500ms after last keystroke)
const numeroRPSDebounced = useDebounce(numeroRPS, 500)

// Re-fetch only when debounced value changes
useEffect(() => {
  carregarRPS()
}, [numeroRPSDebounced])

Result: 100 keystrokes → 1 API call (instead of 100)
```

### Pattern 3: Stateless Pagination
```python
# Backend doesn't remember page state
@router.get("/rps")
def listar_rps(
    limit: int = Query(10),   # How many
    offset: int = Query(0)    # Starting from
):
    # offset=0, limit=10 → get records 0-9
    # offset=10, limit=10 → get records 10-19
    # etc.
    
    query = select(TB_Duplicata).offset(offset).limit(limit)

# Client manages page number
const [paginaAtual, setPaginaAtual] = useState(1)
const offset = (paginaAtual - 1) * itensPorPagina  // Calculate each time
```

### Pattern 4: Immutable Record Storage
```sql
-- TB_AprovacaoRPS: INSERT only, never UPDATE or DELETE
INSERT INTO TB_AprovacaoRPS (...)
INSERT INTO TB_AprovacaoRPS (...)  -- New record, old stays
-- Can't accidentally overwrite or delete history

-- Cleanup is via archive + delete after N days
INSERT INTO Archive SELECT * FROM TB_AprovacaoRPS WHERE DataAcao < NOW() - 90 days
DELETE FROM TB_AprovacaoRPS WHERE DataAcao < NOW() - 90 days
```

---

## 5. Data Persistence Stack

### Temporary (Session/Request Scope)
```
React Component State (useState)
  ↑↓ Re-render cycle
Browser sessionStorage (cleared on tab close)
  ↑↓ [Future] Draft messages
SQLAlchemy Request Session
  ↑↓ Single HTTP request
```

### Persistent (Indefinite)
```
Browser Cookies (7-day TTL)
  ├─ JWT Token
  └─ Used for auth on every API call

SQL Server Database
  ├─ TB_Usuarios (user accounts)
  ├─ TB_Admissao / TB_Demissao (workflows)
  ├─ TB_AprovacaoRPS (approval history)
  ├─ TB_Duplicata (invoices)
  └─ [Future] TB_ConversationProgress (conversations)
```

---

## 6. Current Workflow Example: RPS Approval

### User's Perspective
1. Navigate to /Financeiro/RPS
2. Page loads with RPS list (statusAprovacao: 'pendente')
3. Click "Reject RPS" button
4. Modal opens asking for reason
5. User types reason and clicks "Confirm"
6. Backend creates TB_AprovacaoRPS record
7. List refreshes, statusAprovacao now shows 'reprovado'
8. User can see full approval history

### System's Perspective (State Changes)
```
┌─ Frontend (React)
│  ├─ RPS Page state: [rps[], loading, filtros]
│  ├─ Modal component state: [visible, modalData]
│  └─ UI state: [isSubmitting]
│
├─ Network
│  ├─ Server Action: reprovarRPS(...)
│  └─ POST /financeiro/rps/{id}/reprovar
│
└─ Backend (Python + SQL)
   ├─ Validate JWT token
   ├─ INSERT into TB_AprovacaoRPS
   │  └─ StatusAprovacao: 'reprovado'
   │  └─ MotivoReprovacao: user's reason
   │  └─ ID_Usuario: current user
   │  └─ DataAcao: NOW()
   ├─ Query TB_AprovacaoRPS for latest status
   └─ Return AcaoRPSResponse
   
┌─ Frontend (React) - Refresh
│  ├─ Call carregarRPS() again
│  ├─ Update state with new data
│  └─ Display updated statusAprovacao
└─ User sees change instantly
```

---

## 7. Recommendations for Conversation Tracking

### Proposed: TB_ConversationProgress Table
```sql
CREATE TABLE TB_ConversationProgress (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Session
    ID_Usuario INT FOREIGN KEY → TB_Usuarios,
    SessionID NVARCHAR(100),           -- UUID for this conversation
    
    -- Context
    TopicType NVARCHAR(50),            -- 'rps_approval', 'hiring', etc
    TopicID INT,                       -- Linked entity ID
    ConversationState NVARCHAR(50),    -- 'active', 'paused', 'completed'
    
    -- Messages
    MessageSequence INT,               -- Order (1, 2, 3, ...)
    MessageRole NVARCHAR(20),          -- 'user', 'assistant', 'system'
    MessageContent NVARCHAR(MAX),      -- The actual message
    
    -- State Preservation
    ContextSnapshot NVARCHAR(MAX),     -- JSON of form state, filters, etc
    
    -- Audit
    DataAcao DATETIME DEFAULT GETDATE()
);

-- Indexes
CREATE INDEX IX_SessionID_Sequence ON TB_ConversationProgress
    (SessionID, MessageSequence);

CREATE INDEX IX_Usuario_Topic ON TB_ConversationProgress
    (ID_Usuario, TopicType, TopicID, DataAcao DESC);
```

### Frontend Integration
```typescript
// New Context (similar to UsuarioContext)
export const ConversationContext = createContext(...)

// New Hook
export const useConversation = () => {
  return {
    session: ConversationSession,
    startConversation: async (topicType, topicID) => {...},
    resumeConversation: async (sessionID) => {...},
    addMessage: async (role, content) => {...},
    updateContextSnapshot: async (snapshot) => {...},
    completeConversation: async () => {...}
  }
}

// Usage in RPS Page
const { session, addMessage, updateContextSnapshot } = useConversation()

<ModalReprovarRPS
  onReject={(reason) => {
    // Save to conversation + send rejection
    await addMessage('user', `Rejecting for: ${reason}`)
    await reprovarRPS(...)
    await updateContextSnapshot(currentPageState)
  }}
/>
```

---

## 8. Key Insights

### What's Already Good
✓ Clean separation of concerns (Frontend ↔ API ↔ Backend)
✓ Type safety through Pydantic + TypeScript
✓ Audit trail pattern (TB_AprovacaoRPS)
✓ Stateless API (easy to scale)
✓ JWT-based auth (secure, no server sessions)
✓ Debounced input (prevents API thrashing)

### What Could Improve
- No URL-based state (filters lost on navigation)
- Limited client-side caching
- No offline-first capability
- Component state not persisted
- No draft save mechanism

### For Conversation Tracking
- Follow TB_AprovacaoRPS pattern (append-only, immutable)
- Add LayeredContext provider for conversation state
- Use Server Actions for API calls
- Auto-save drafts to localStorage every 30s
- Implement conversation resume functionality

---

## 9. File Locations Cheat Sheet

### Frontend
```
/frontend/src/
├── app/
│   ├── layout.tsx                    ← App root, UseProvider wrapper
│   ├── contexts/UsuarioContext.tsx   ← Global user state
│   ├── Financeiro/RPS/
│   │   ├── page.tsx                  ← Page component with state
│   │   ├── api.ts                    ← Server Actions
│   │   ├── types.ts                  ← Type definitions
│   │   └── [modal/table components]
│   └── [other features]
├── lib/
│   ├── cockies.ts                    ← JWT token management
│   └── decode.ts                     ← Token parsing utilities
└── components/
    ├── Alerta/index.tsx              ← Modal (uses localStorage)
    └── [shared components]
```

### Backend
```
/backend/src/backend/
├── main.py                           ← FastAPI app, CORS setup
├── database.py                       ← SQLAlchemy engine, AtivarSession
├── models.py                         ← ORM models (TB_Usuarios, TB_Duplicata, etc)
├── schema.py                         ← Pydantic request/response schemas
├── security.py                       ← JWT validation, UsuarioAtual dependency
├── settings.py                       ← Environment variables
└── routers/
    ├── auth.py                       ← Login endpoint
    ├── financeiro.py                 ← RPS/Invoice endpoints (1174 lines)
    ├── requisicoes.py                ← Hiring/Termination workflow
    ├── usuarios.py                   ← User CRUD
    └── [other routers]
```

### Database Scripts
```
/backend/scripts/database/
├── criar_tb_aprovacao_rps.sql        ← Audit table creation
├── create_table_tb_duplicata.sql     ← Invoice table
└── [other migrations]
```

---

## 10. Testing Checklist

### Frontend
- [ ] UsuarioContext loads on mount
- [ ] JWT token persists across navigation
- [ ] RPS filters trigger API calls on debounce
- [ ] Pagination state updates correctly
- [ ] Modal states persist in localStorage

### Backend
- [ ] JWT validation in UsuarioAtual dependency
- [ ] Queries return paginated results
- [ ] TB_AprovacaoRPS records are immutable
- [ ] Status query returns latest action
- [ ] Error handling returns proper HTTP codes

### Integration
- [ ] End-to-end: Filter → API → State → UI
- [ ] Approval workflow: Create record → Query status → Update UI
- [ ] Multi-user: User A's session isolated from User B

---

## 11. Quick Command Reference

### Frontend Development
```bash
cd frontend
npm install
npm run dev                # Run on localhost:3000
npm run lint
npm run format
```

### Backend Development
```bash
cd backend
poetry install
uvicorn src.backend.main:app --reload  # Run on localhost:8000
pytest                     # Run tests
pytest --cov              # Coverage report
```

### View API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Conclusion

The MetaRH PortalCliente uses a **clean, scalable architecture**:

1. **Frontend**: React + hooks (simple, localized state)
2. **Backend**: FastAPI + SQLAlchemy (typed, ORM-based)
3. **Persistence**: Multi-layered (cookies → localStorage → SQL Server)
4. **Audit**: Immutable append-only tables (TB_AprovacaoRPS pattern)
5. **Communication**: Server Actions + TypeScript (type-safe bridge)

For conversation tracking, **replicate the TB_AprovacaoRPS pattern** but with:
- Mutable message content (unlike immutable approval actions)
- Richer context preservation (form state, filters)
- Resume capability (session-based recovery)
- Layered persistence (browser draft + server persistent)

This maintains architectural consistency while adding AI conversation capabilities.
