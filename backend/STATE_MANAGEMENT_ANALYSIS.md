# MetaRH PortalCliente - State Management & Persistence Analysis

## Executive Summary

The MetaRH PortalCliente has a **distributed state management architecture** combining:
- **Frontend**: React Context API (minimal) + React hooks (useState)
- **Backend**: SQLAlchemy ORM with SQL Server database
- **Session Persistence**: JWT tokens (cookies) + limited client-side storage
- **Audit/History**: Dedicated database tables (TB_AprovacaoRPS pattern)

This analysis identifies existing patterns and recommendations for conversation/progress tracking implementation.

---

## 1. FRONTEND STATE MANAGEMENT PATTERNS

### 1.1 React Context API - User Context

**Location**: `/frontend/src/app/contexts/UsuarioContext.tsx`

**Purpose**: Global user session management

**Structure**:
```typescript
interface UsuarioContext {
  usuario: {
    ID: number
    Nome: string
    Email: string
    CNPJ: string
    TipoAcesso: string
    PipedriveID: string
    CodigoCliente: string
    Status: boolean
    existeImagem: boolean
    urlImagem: string
    token: string
    CNPJS: string[]           // Array of company CNPJs
    CodigosCliente: string[]   // Array of client codes
  }
  setUsuario: (usuario: any) => void
  carregarUsuario: (tokenParam?: string) => Promise<void>
}
```

**Data Flow**:
1. On app mount, `getAuthToken()` retrieves JWT from cookies
2. Token is decoded to extract user email
3. API call to `/organizacao/empressas?Email={Email}` fetches user companies
4. CNPJs and CodigoConte are extracted and stored in context

**Limitations**:
- No complex state mutations
- No workflow state tracking
- No conversation history storage
- Simple user info only

**Usage**: 
- Accessed via `useUsuario()` hook in child components
- Wrapped at root level in `layout.tsx` via `UseProvider`

### 1.2 Component-Level State with React Hooks

**RPS Feature Example** (`/frontend/src/app/Financeiro/RPS/page.tsx`):

```typescript
// Page-level state
const [rps, setRPS] = useState<RPS[]>([])
const [resumo, setResumo] = useState<ResumoRPS>({...})
const [loading, setLoading] = useState(true)
const [erro, setErro] = useState<string | null>(null)

// Pagination state
const [paginaAtual, setPaginaAtual] = useState(1)
const [itensPorPagina, setItensPorPagina] = useState(10)
const [totalRegistros, setTotalRegistros] = useState(0)

// Filter state
const [filtros, setFiltros] = useState<FiltrosState>({
  dataEmissao: '',
  competencia: '',
  numeroRPS: '',
  valorTotal: '',
  vencimento: '',
  status: '',
})

// Debounced filter values (500ms debounce)
const numeroRPSDebounced = useDebounce(filtros.numeroRPS, 500)
const competenciaDebounced = useDebounce(filtros.competencia, 500)
const valorTotalDebounced = useDebounce(filtros.valorTotal, 500)
const dataEmissaoDebounced = useDebounce(filtros.dataEmissao, 500)
const vencimentoDebounced = useDebounce(filtros.vencimento, 500)
```

**Pattern Characteristics**:
- **Flat state structure** - no nested reducers
- **Multiple useState calls** - one per data type
- **Debounced filter values** - prevents API thrashing
- **Local pagination** - managed in component state
- **Filter conversation** - transforms Brazilian format ↔ API format

**Advantages**:
- Simple, easy to follow
- No build-time dependencies
- Direct component coupling

**Disadvantages**:
- Props drilling (filter handlers passed down)
- No persistent state across navigation
- Filter state lost on page refresh
- No ability to save/resume workflows

### 1.3 Client-Side Storage Usage

**localStorage Example** (`/frontend/src/components/Alerta/index.tsx`):

```typescript
useEffect(() => {
  const AlertaVisivel = localStorage.getItem('AlertaVisivel')
  if (AlertaVisivel == null || AlertaVisivel === 'true') {
    localStorage.setItem('AlertaVisivel', 'true')
    setVisivel(true)
  }
}, [])
```

**Current Usage**:
- Modal visibility state persistence
- Very minimal adoption

**Pattern**:
- Direct `localStorage.getItem()` / `setItem()` calls
- No abstraction layer
- No encryption or validation

### 1.4 Cookie-Based Session Storage

**Location**: `/frontend/src/lib/cockies.ts`

```typescript
const TOKEN_COOKIE_KEY = 'token-portal-metarh'

export const setAuthToken = (token: string, expiresDays: number = 7) => {
  Cookies.set(TOKEN_COOKIE_KEY, token)
}

export const getAuthToken = () => {
  const token = Cookies.get(TOKEN_COOKIE_KEY)
  return token
}
```

**Characteristics**:
- JWT token stored for 7 days
- Managed via `js-cookie` library
- Checked in middleware for route protection
- No custom claims tracking

---

## 2. BACKEND STATE MANAGEMENT PATTERNS

### 2.1 Database-Driven Architecture

**Technology Stack**:
- **ORM**: SQLAlchemy 2.0 with mapped dataclasses
- **Database**: SQL Server (PortalCliente)
- **Session Management**: FastAPI dependency injection

**Database Models** (`/backend/src/backend/models.py`):

```python
@TabelaRegistro.mapped_as_dataclass
class TB_Usuarios:
    __tablename__ = 'TB_Usuarios'
    ID: Mapped[int] = mapped_column(init=False, primary_key=True)
    Nome: Mapped[str]
    Email: Mapped[str] = mapped_column(unique=True)
    Senha: Mapped[str]  # Hashed with Argon2
    CNPJ: Mapped[str]
    TipoAcesso: Mapped[str]
    Acesso: Mapped[str]
    Status: Mapped[bool]
    DataCadastro: Mapped[datetime]
    DataAtualizacao: Mapped[datetime]

@TabelaRegistro.mapped_as_dataclass
class TB_Admissao:
    __tablename__ = 'TB_Admissao'
    ID: Mapped[int]
    ID_Usuario: Mapped[int] = mapped_column(ForeignKey('TB_Usuarios.ID'))
    # ... 30+ fields for hiring workflow
    DataInicio: Mapped[datetime]
    DataEncerramento: Mapped[datetime]
    Status: Mapped[str]  # 'Não Iniciado', 'Em Progresso', etc.
    Visivel: Mapped[bool]
    DataCadastro: Mapped[datetime]
    DataAtualizacao: Mapped[datetime]

@TabelaRegistro.mapped_as_dataclass
class TB_Demissao:
    __tablename__ = 'TB_Demissao'
    ID: Mapped[int]
    ID_Usuario: Mapped[int] = mapped_column(ForeignKey('TB_Usuarios.ID'))
    # ... 15+ fields for termination workflow
    Status: Mapped[str]
    DataInicio: Mapped[datetime]
    DataEncerramento: Mapped[datetime]
    DataCadastro: Mapped[datetime]
    DataAtualizacao: Mapped[datetime]
```

**Workflow State Tracking**:
- `TB_Admissao` and `TB_Demissao` use `Status` field with values like:
  - 'Não Iniciado' (Not Started)
  - 'Em Progresso' (In Progress)
  - 'Concluído' (Completed)
- `DataInicio` and `DataEncerramento` bracket workflow duration
- `DataCadastro` / `DataAtualizacao` timestamps for audit

### 2.2 Audit History Pattern - TB_AprovacaoRPS

**Location**: `/backend/scripts/database/criar_tb_aprovacao_rps.sql`

**Purpose**: Complete audit trail for RPS approval workflow (non-destructive)

**Schema**:
```sql
CREATE TABLE [dbo].[TB_AprovacaoRPS] (
    [ID] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    
    -- Foreign key to TB_Duplicata (read-only legacy table)
    [CodigoEmpresaFat] INT NOT NULL,
    [CodigoFilialFat] INT NOT NULL,
    [Duplicata] INT NOT NULL,
    [NumeroRPS] INT NOT NULL,
    
    -- Status and Action Type
    [StatusAprovacao] VARCHAR(20) NOT NULL,  -- 'pendente', 'aprovado', 'reprovado'
    [TipoAcao] VARCHAR(20) NOT NULL,         -- 'aprovacao', 'reprovacao', 'cancelamento'
    
    -- Rejection Details (nullable)
    [MotivoReprovacao] VARCHAR(100) NULL,
    [DescricaoReprovacao] VARCHAR(500) NULL,
    
    -- Audit Trail
    [ID_Usuario] INT NOT NULL FOREIGN KEY,
    [NomeUsuario] VARCHAR(200) NOT NULL,   -- Denormalized to preserve history
    [EmailUsuario] VARCHAR(200) NOT NULL,  -- Denormalized to preserve history
    
    -- Timestamps
    [DataAcao] DATETIME NOT NULL DEFAULT GETDATE(),
    [DataCadastro] DATETIME NOT NULL DEFAULT GETDATE(),
    [DataAtualizacao] DATETIME NOT NULL DEFAULT GETDATE()
);

-- Indexes for performance
CREATE NONCLUSTERED INDEX [IX_TB_AprovacaoRPS_Duplicata_DataAcao]
    ON [dbo].[TB_AprovacaoRPS] (
        [CodigoEmpresaFat] ASC,
        [CodigoFilialFat] ASC,
        [Duplicata] ASC,
        [DataAcao] DESC
    ) INCLUDE ([StatusAprovacao], [TipoAcao]);
```

**Key Design Patterns**:
- **Composite indexing** for fast status lookups
- **Denormalized user data** to preserve historical accuracy
- **Immutable records** - no updates, only inserts
- **1:N relationship** with TB_Duplicata (one invoice, many approval actions)
- **Temporal tracking** - full history preserved

**Query Pattern** (from financeiro.py):
```python
def obter_status_aprovacao_rps(session: Session, empresa: int, filial: int, duplicata: int):
    ultima_aprovacao = session.execute(
        select(TB_AprovacaoRPS.StatusAprovacao)
        .where(and_(
            TB_AprovacaoRPS.CodigoEmpresaFat == empresa,
            TB_AprovacaoRPS.CodigoFilialFat == filial,
            TB_AprovacaoRPS.Duplicata == duplicata
        ))
        .order_by(TB_AprovacaoRPS.DataAcao.desc())
        .limit(1)
    ).scalars().first()
    
    return ultima_aprovacao if ultima_aprovacao else 'pendente'
```

### 2.3 Session Management - FastAPI Dependency Injection

**Location**: `/backend/src/backend/database.py`

```python
engine = create_engine(Settings().DATABASE_URL)

def AtivarSession():
    """Cria uma nova sessão do banco de dados."""
    with Session(engine) as session:
        yield session
```

**Usage in Routes**:
```python
@router.get("/rps")
def listar_rps(
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    # session is auto-created and cleaned up
    duplicatas = session.execute(query).scalars().all()
    # session is auto-closed
```

**Pattern**:
- Each request gets fresh database session
- Automatic lifecycle management
- SQLAlchemy handles connection pooling

### 2.4 Server Action Pattern (Frontend-Backend Bridge)

**Location**: `/frontend/src/app/Financeiro/RPS/api.ts` (Server Action)

```typescript
'use server'

const API_BASE_URL = 'http://127.0.0.1:8000'

export async function buscarRPS(
  token: string | undefined,
  filtros?: FiltrosRPS
): Promise<ListaRPSResponse> {
  const params = new URLSearchParams()
  
  // Build query string from filters
  if (filtros?.codigo_cliente) params.append('codigo_cliente', ...)
  if (filtros?.competencia) params.append('competencia', ...)
  
  const queryString = params.toString()
  const url = `${API_BASE_URL}/financeiro/rps${queryString ? `?${queryString}` : ''}`
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    cache: 'no-store',
  })
  
  if (!response.ok) {
    throw new Error(...)
  }
  
  return response.json()
}

export async function reprovarRPS(
  token: string | undefined,
  rpsId: number,
  numeroRPS: string,
  motivoReprovacao: string,
  descricaoReprovacao: string
): Promise<AcaoRPSResponse> {
  const url = `${API_BASE_URL}/financeiro/rps/${rpsId}/reprovar`
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify({
      rps_id: rpsId,
      numero_rps: numeroRPS,
      motivo_reprovacao: motivoReprovacao,
      descricao_reprovacao: descricaoReprovacao,
    }),
    cache: 'no-store',
  })
  
  return response.json()
}
```

**Characteristics**:
- Executed on server-side via `'use server'` directive
- Encapsulates API calls and authentication
- Provides type-safe interface to frontend
- Automatically handles token injection

---

## 3. PERSISTENCE MECHANISMS SUMMARY

### 3.1 Data Persistence Layers

| Layer | Mechanism | TTL | Scope | Use Case |
|-------|-----------|-----|-------|----------|
| **Browser Cookies** | JWT Token | 7 days | User session | Authentication |
| **Browser localStorage** | Key-value pairs | Indefinite | Domain-wide | Modal state (minimal) |
| **React Context** | In-memory | Session | App-wide | User profile |
| **Component State** | useState hooks | Render cycle | Component | Form data, UI state |
| **SQL Server DB** | Tables | Indefinite | Application | Persistent records |
| **Request-scoped** | SQLAlchemy Session | Single request | Endpoint | Query execution |

### 3.2 Current Progress Tracking

The project **already uses the TB_AprovacaoRPS pattern** for workflow tracking:

**RPS Approval Workflow State Machine**:
```
Duplicata (read-only) ────┐
                           ├─→ TB_AprovacaoRPS (immutable audit log)
                           │   StatusAprovacao: 'pendente' → 'aprovado' or 'reprovado'
                           │   TipoAcao: 'aprovacao', 'reprovacao', 'cancelamento'
                           │   MotivoReprovacao: null (for approval) or text (for rejection)
                           │   DataAcao: timestamp of action
                           │   ID_Usuario: who performed it
```

**Backend Implementation** (`/backend/src/backend/routers/financeiro.py`):
1. Query `TB_AprovacaoRPS` for latest action per RPS
2. Filter by `(CodigoEmpresaFat, CodigoFilialFat, Duplicata)` composite key
3. Order by `DataAcao DESC LIMIT 1` to get current status
4. Join user info for "who" and "when"
5. Return `statusAprovacao` in API response

**Frontend Display** (`/frontend/src/app/Financeiro/RPS/TabelaRPS.tsx`):
```typescript
interface RPS {
  id: number
  statusAprovacao: 'pendente' | 'aprovado' | 'reprovado'
}
```

---

## 4. API RESPONSE STRUCTURE & SCHEMAS

### 4.1 Pydantic Response Schemas

**Location**: `/backend/src/backend/schema.py`

```python
# RPS Response
class RPSResponse(BaseModel):
    id: int
    dataEmissao: str
    competencia: str
    numeroRPS: Optional[str]
    valorTotal: float
    vencimento: str
    status: Literal['a_vencer', 'vencida', 'paga']
    statusAprovacao: str  # 'pendente', 'aprovado', 'reprovado'

# List with Pagination & Summary
class ListaRPSResponse(BaseModel):
    rps: list[RPSResponse]
    total: int
    resumo: ResumoRPSResponse

class ResumoRPSResponse(BaseModel):
    totalRPSAVencer: int
    valorRPSAVencer: float
    totalRPSVencidas: int
    valorRPSVencidas: float

# Action Response (for approval/rejection)
class AcaoRPSResponse(BaseModel):
    sucesso: bool
    mensagem: str
    status_atual: str
    data_acao: str

# History Entry
class HistoricoAprovacaoRPS(BaseModel):
    id: int
    status_aprovacao: str
    tipo_acao: str
    motivo_reprovacao: Optional[str]
    descricao_reprovacao: Optional[str]
    nome_usuario: str
    email_usuario: str
    data_acao: str
```

### 4.2 Type Safety Through the Stack

**Frontend Types** (`/frontend/src/app/Financeiro/RPS/types.ts`):
```typescript
export interface RPS {
  id: number
  dataEmissao: string
  competencia: string
  numeroRPS: string
  valorTotal: number
  vencimento: string
  status: 'a_vencer' | 'vencida' | 'paga'
  statusAprovacao: 'pendente' | 'aprovado' | 'reprovado'
}

export interface ResumoRPS {
  totalRPSAVencer: number
  valorRPSAVencer: number
  totalRPSVencidas: number
  valorRPSVencidas: number
}
```

**Pattern**: Backend schema defines source of truth, frontend maintains mirror types

---

## 5. PAGINATION & FILTERING STATE

### 5.1 Current Implementation (RPS Page)

```typescript
// Pagination state
const [paginaAtual, setPaginaAtual] = useState(1)
const [itensPorPagina, setItensPorPagina] = useState(10)
const [totalRegistros, setTotalRegistros] = useState(0)

// Filter state
const [filtros, setFiltros] = useState<FiltrosState>({
  dataEmissao: '',
  competencia: '',
  numeroRPS: '',
  valorTotal: '',
  vencimento: '',
  status: '',
})

// Debounced filter values
const numeroRPSDebounced = useDebounce(filtros.numeroRPS, 500)
const competenciaDebounced = useDebounce(filtros.competencia, 500)

// Dependencies for re-fetch
useEffect(() => {
  carregarRPS()
}, [
  paginaAtual,
  itensPorPagina,
  numeroRPSDebounced,
  competenciaDebounced,
  valorTotalDebounced,
  dataEmissaoDebounced,
  vencimentoDebounced,
  filtros.status
])
```

**Limitations**:
- Filter state lost on navigation
- No URL-based state (could use query params)
- No save/resume capability
- Search preferences not persistent

### 5.2 Backend Pagination Query

```python
@router.get("/rps")
def listar_rps(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    # Stateless pagination
    query_paginada = query.offset(offset).limit(limit)
    duplicatas = session.execute(query_paginada).scalars().all()
```

**Pattern**:
- Limit/offset (not cursor-based)
- No session state on backend
- Client responsible for tracking page position

---

## 6. RECOMMENDED ARCHITECTURE FOR CONVERSATION TRACKING

### 6.1 Proposed Table Schema (Following TB_AprovacaoRPS Pattern)

```sql
CREATE TABLE [dbo].[TB_ConversationProgress] (
    [ID] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    
    -- User & Session
    [ID_Usuario] INT NOT NULL FOREIGN KEY,
    [SessionID] NVARCHAR(100) NOT NULL,  -- UUID
    
    -- Conversation Context
    [TopicType] NVARCHAR(50) NOT NULL,  -- 'rps_approval', 'hiring', 'termination'
    [TopicID] INT NOT NULL,             -- FK to related entity (RPS ID, etc)
    [ConversationState] NVARCHAR(50) NOT NULL,  -- 'active', 'paused', 'completed'
    
    -- Message Storage
    [MessageSequence] INT NOT NULL,     -- Order in conversation
    [MessageRole] NVARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    [MessageContent] NVARCHAR(MAX) NOT NULL,
    [MessageMetadata] NVARCHAR(MAX) NULL,  -- JSON with tokens, sentiment, etc
    
    -- State Preservation
    [ContextSnapshot] NVARCHAR(MAX) NOT NULL,  -- JSON of current form/page state
    [UIState] NVARCHAR(MAX) NULL,  -- Last position, scroll, focused fields
    
    -- Audit
    [DataAcao] DATETIME NOT NULL DEFAULT GETDATE(),
    [DataCriacao] DATETIME NOT NULL DEFAULT GETDATE(),
    [DataAtualizacao] DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Indexes
    CONSTRAINT [FK_TB_ConversationProgress_Usuario] 
        FOREIGN KEY ([ID_Usuario]) REFERENCES [TB_Usuarios]([ID])
);

CREATE NONCLUSTERED INDEX [IX_ConversationProgress_SessionID]
    ON [TB_ConversationProgress] ([SessionID] ASC, [MessageSequence] ASC);

CREATE NONCLUSTERED INDEX [IX_ConversationProgress_Usuario_Topic]
    ON [TB_ConversationProgress] (
        [ID_Usuario] ASC, 
        [TopicType] ASC, 
        [TopicID] ASC, 
        [DataAcao] DESC
    );
```

### 6.2 Context API Extension for Conversation State

```typescript
// /frontend/src/app/contexts/ConversationContext.tsx

interface ConversationMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    tokens?: number
    sentiment?: string
  }
}

interface ConversationSession {
  sessionID: string
  topicType: string
  topicID: number
  state: 'active' | 'paused' | 'completed'
  messages: ConversationMessage[]
  contextSnapshot: Record<string, any>  // Form state, filters, etc
  createdAt: Date
  updatedAt: Date
}

interface ConversationContextType {
  session: ConversationSession | null
  isLoading: boolean
  startConversation: (topicType: string, topicID: number) => Promise<void>
  resumeConversation: (sessionID: string) => Promise<void>
  addMessage: (role: string, content: string, metadata?: any) => Promise<void>
  updateContextSnapshot: (snapshot: Record<string, any>) => Promise<void>
  completeConversation: () => Promise<void>
  pauseConversation: () => Promise<void>
}

export const ConversationContext = createContext<ConversationContextType | null>(null)
```

### 6.3 Server Actions for Conversation Persistence

```typescript
// /frontend/src/app/actions/conversation.ts
'use server'

export async function createConversationSession(
  token: string,
  topicType: string,
  topicID: number
): Promise<ConversationSession> {
  const response = await fetch(
    `${API_BASE_URL}/conversation/start`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ topicType, topicID }),
    }
  )
  return response.json()
}

export async function addConversationMessage(
  token: string,
  sessionID: string,
  role: string,
  content: string
): Promise<ConversationMessage> {
  const response = await fetch(
    `${API_BASE_URL}/conversation/${sessionID}/message`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ role, content }),
    }
  )
  return response.json()
}

export async function saveContextSnapshot(
  token: string,
  sessionID: string,
  snapshot: Record<string, any>
): Promise<void> {
  await fetch(`${API_BASE_URL}/conversation/${sessionID}/context`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ snapshot }),
  })
}
```

### 6.4 Backend Endpoints

```python
# /backend/src/backend/routers/conversation.py

@router.post("/conversation/start")
def start_conversation(
    request: StartConversationRequest,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """Start new conversation session"""
    session_id = str(uuid.uuid4())
    
    conversation = TB_ConversationProgress(
        ID_Usuario=usuario_atual.id,
        SessionID=session_id,
        TopicType=request.topicType,
        TopicID=request.topicID,
        ConversationState='active',
        MessageSequence=0,
        ContextSnapshot=json.dumps({}),
        MessageRole='system',
        MessageContent=f'Started {request.topicType}'
    )
    
    session.add(conversation)
    session.commit()
    
    return {"sessionID": session_id, "state": "active"}

@router.post("/conversation/{session_id}/message")
def add_message(
    session_id: str,
    request: AddMessageRequest,
    db_session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """Add message to conversation"""
    # Get current sequence
    last_message = db_session.execute(
        select(TB_ConversationProgress.MessageSequence)
        .where(TB_ConversationProgress.SessionID == session_id)
        .order_by(TB_ConversationProgress.MessageSequence.desc())
        .limit(1)
    ).scalar()
    
    new_sequence = (last_message or 0) + 1
    
    message = TB_ConversationProgress(
        ID_Usuario=usuario_atual.id,
        SessionID=session_id,
        MessageSequence=new_sequence,
        MessageRole=request.role,
        MessageContent=request.content,
        MessageMetadata=json.dumps(request.metadata or {}),
        ContextSnapshot='{}'
    )
    
    db_session.add(message)
    db_session.commit()
    
    return {
        "id": message.ID,
        "sequence": new_sequence,
        "timestamp": message.DataAcao.isoformat()
    }

@router.get("/conversation/{session_id}")
def get_conversation(
    session_id: str,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """Retrieve full conversation"""
    messages = session.execute(
        select(TB_ConversationProgress)
        .where(
            and_(
                TB_ConversationProgress.SessionID == session_id,
                TB_ConversationProgress.ID_Usuario == usuario_atual.id
            )
        )
        .order_by(TB_ConversationProgress.MessageSequence.asc())
    ).scalars().all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "sessionID": session_id,
        "messages": [
            {
                "id": m.ID,
                "role": m.MessageRole,
                "content": m.MessageContent,
                "timestamp": m.DataAcao.isoformat(),
                "sequence": m.MessageSequence
            }
            for m in messages
        ],
        "context": json.loads(messages[-1].ContextSnapshot or '{}')
    }
```

---

## 7. MIGRATION PATH & RECOMMENDATIONS

### 7.1 Phase 1: Database Preparation (2-3 days)

1. Create `TB_ConversationProgress` table following TB_AprovacaoRPS pattern
2. Add composite indexes for fast lookups
3. Create stored procedures for bulk operations
4. Test query performance with typical message volume

### 7.2 Phase 2: Backend API (3-5 days)

1. Add `conversation.py` router with CRUD endpoints
2. Implement message pagination (limit/offset)
3. Add context snapshot validation (JSON schema)
4. Implement session state machine (active → paused → completed)
5. Add audit logging for conversation lifecycle

### 7.3 Phase 3: Frontend Context & Hooks (3-5 days)

1. Create `ConversationContext` provider
2. Implement `useConversation()` hook
3. Create Server Actions for API calls
4. Add error handling and retry logic
5. Wrap existing modals with context

### 7.4 Phase 4: Integration with RPS Approval (2-3 days)

1. Wrap RPS approval flow with conversation tracking
2. Capture user decisions and form state
3. Allow resuming interrupted workflows
4. Display conversation history in UI

---

## 8. DATA LOSS PREVENTION STRATEGIES

### 8.1 Recommended Approach

**Layered Persistence**:
```
┌─────────────────────────────────────────┐
│ User Browser (Temporary)                │
│  - sessionStorage: Draft messages       │
│  - localStorage: Draft context state    │
│  - React state: Current UI state        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Backend Database (Persistent)           │
│  - TB_ConversationProgress              │
│  - Replicated to Azure Backup           │
│  - Query logs for debugging             │
└─────────────────────────────────────────┘
```

### 8.2 Implementation Details

**Client-Side Draft Saving** (every 30 seconds):
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    localStorage.setItem(
      `conversation_draft_${sessionID}`,
      JSON.stringify(currentDraft)
    )
  }, 30000)
  
  return () => clearInterval(interval)
}, [sessionID, currentDraft])
```

**Server-Side Batch Insert** (for high-frequency messages):
```python
@router.post("/conversation/{session_id}/batch")
def batch_add_messages(
    session_id: str,
    request: BatchMessagesRequest,  # List[message]
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    """Add multiple messages in single transaction"""
    messages = [
        TB_ConversationProgress(
            ID_Usuario=usuario_atual.id,
            SessionID=session_id,
            MessageSequence=idx,
            MessageRole=msg.role,
            MessageContent=msg.content
        )
        for idx, msg in enumerate(request.messages, start=get_next_sequence())
    ]
    
    session.add_all(messages)
    session.commit()
```

---

## 9. SECURITY CONSIDERATIONS

### 9.1 Access Control

✓ **Current Pattern** (TB_AprovacaoRPS):
- FK to TB_Usuarios.ID ensures user ownership
- `UsuarioAtual` dependency validates JWT token
- Queries filtered by user ID

**Recommended for Conversations**:
```python
@router.get("/conversation/{session_id}")
def get_conversation(
    session_id: str,
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    conversation = session.execute(
        select(TB_ConversationProgress)
        .where(
            and_(
                TB_ConversationProgress.SessionID == session_id,
                TB_ConversationProgress.ID_Usuario == usuario_atual.id  # ← Ownership check
            )
        )
    ).scalars().first()
    
    if not conversation:
        raise HTTPException(status_code=403, detail="Access denied")
```

### 9.2 Data Validation

- Validate `MessageContent` length (max 5000 chars)
- Validate JSON structure of `ContextSnapshot`
- Rate limit message submissions (e.g., 60/minute)
- Sanitize message content (XSS prevention)

### 9.3 Message Encryption (Optional)

For sensitive conversations (hiring details, salary info):
```python
from cryptography.fernet import Fernet

@router.post("/conversation/{session_id}/message")
def add_message(request, session: Session, usuario_atual):
    cipher = Fernet(settings.ENCRYPTION_KEY)
    
    encrypted_content = cipher.encrypt(
        request.content.encode('utf-8')
    ).decode('utf-8')
    
    message = TB_ConversationProgress(
        MessageContent=encrypted_content,
        # ...
    )
```

---

## 10. PERFORMANCE OPTIMIZATION

### 10.1 Indexing Strategy

```sql
-- Primary lookup: Get conversation for display
CREATE NONCLUSTERED INDEX [IX_Conv_SessionID_Sequence]
    ON [TB_ConversationProgress] (
        [SessionID] ASC, 
        [MessageSequence] ASC
    ) INCLUDE ([MessageRole], [MessageContent]);

-- User activity: Show user's conversations
CREATE NONCLUSTERED INDEX [IX_Conv_Usuario_Topic]
    ON [TB_ConversationProgress] (
        [ID_Usuario] ASC, 
        [TopicType] ASC, 
        [TopicID] ASC, 
        [DataAcao] DESC
    );

-- Cleanup: Find old conversations
CREATE NONCLUSTERED INDEX [IX_Conv_DataAcao]
    ON [TB_ConversationProgress] ([DataAcao] DESC);
```

### 10.2 Query Optimization

**For long conversations** (1000+ messages):
```python
# Pagination for message history
@router.get("/conversation/{session_id}/messages")
def get_conversation_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(AtivarSession),
    usuario_atual = Depends(UsuarioAtual)
):
    # Only fetch requested page
    messages = session.execute(
        select(TB_ConversationProgress)
        .where(TB_ConversationProgress.SessionID == session_id)
        .order_by(TB_ConversationProgress.MessageSequence.asc())
        .offset(offset)
        .limit(limit)
    ).scalars().all()
    
    # Get total for pagination
    total = session.execute(
        select(func.count())
        .select_from(TB_ConversationProgress)
        .where(TB_ConversationProgress.SessionID == session_id)
    ).scalar()
    
    return {
        "messages": [...],
        "total": total,
        "offset": offset,
        "limit": limit
    }
```

### 10.3 Database Maintenance

```sql
-- Archive old conversations (older than 90 days)
INSERT INTO TB_ConversationProgress_Archive
SELECT * FROM TB_ConversationProgress
WHERE DataAcao < DATEADD(day, -90, GETDATE());

DELETE FROM TB_ConversationProgress
WHERE DataAcao < DATEADD(day, -90, GETDATE());

-- Rebuild fragmented indexes
ALTER INDEX [IX_Conv_SessionID_Sequence]
ON [TB_ConversationProgress] REBUILD;
```

---

## 11. TESTING STRATEGY

### 11.1 Backend Tests (pytest)

```python
# /backend/tests/test_conversation.py

@pytest.fixture
def conversation_session(client, auth_headers):
    response = client.post(
        "/conversation/start",
        json={"topicType": "rps_approval", "topicID": 123},
        headers=auth_headers
    )
    return response.json()["sessionID"]

def test_start_conversation(client, auth_headers):
    response = client.post(
        "/conversation/start",
        json={"topicType": "rps_approval", "topicID": 123},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["state"] == "active"

def test_add_message(client, auth_headers, conversation_session):
    response = client.post(
        f"/conversation/{conversation_session}/message",
        json={"role": "user", "content": "Test message"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["sequence"] == 1

def test_get_full_conversation(client, auth_headers, conversation_session):
    # Add messages
    client.post(f"/conversation/{conversation_session}/message", ...)
    client.post(f"/conversation/{conversation_session}/message", ...)
    
    response = client.get(
        f"/conversation/{conversation_session}",
        headers=auth_headers
    )
    
    assert len(response.json()["messages"]) == 3  # system + 2 user
    assert response.json()["messages"][0]["role"] == "system"

def test_unauthorized_access_denied(client, auth_headers):
    # Start conversation with user A
    response = client.post(
        "/conversation/start",
        headers=auth_headers
    )
    session_id = response.json()["sessionID"]
    
    # Try to access with user B
    user_b_headers = get_auth_headers_for_user("user_b@example.com")
    
    response = client.get(
        f"/conversation/{session_id}",
        headers=user_b_headers
    )
    
    assert response.status_code == 403
```

### 11.2 Frontend Tests (Vitest)

```typescript
// /frontend/__tests__/contexts/ConversationContext.test.ts

describe('ConversationContext', () => {
  it('should start new conversation session', async () => {
    const { result } = renderHook(() => useConversation(), {
      wrapper: ConversationProvider,
    })
    
    await act(async () => {
      await result.current.startConversation('rps_approval', 123)
    })
    
    expect(result.current.session?.state).toBe('active')
    expect(result.current.session?.topicType).toBe('rps_approval')
  })
  
  it('should add message to conversation', async () => {
    const { result } = renderHook(() => useConversation(), {
      wrapper: ConversationProvider,
    })
    
    await act(async () => {
      await result.current.startConversation('rps_approval', 123)
      await result.current.addMessage('user', 'Test message')
    })
    
    expect(result.current.session?.messages).toHaveLength(2)  // system + user
    expect(result.current.session?.messages[1].content).toBe('Test message')
  })
})
```

---

## 12. SUMMARY TABLE: STATE MANAGEMENT PATTERNS

| Pattern | Location | Scope | Persistence | Use Case |
|---------|----------|-------|-------------|----------|
| **JWT Token** | Cookies | Session (7 days) | Browser | User authentication |
| **User Context** | React Context | App-wide | In-memory | User profile, companies |
| **Component State** | useState | Component | Render cycle | Form data, filters, UI |
| **Debounced State** | useDebounce custom hook | Component | Render cycle | Search input |
| **localStorage** | Browser API | Domain | Indefinite | Modal visibility (minimal) |
| **DB Sessions** | SQLAlchemy | Request | Request lifecycle | Query execution |
| **TB_Usuarios** | SQL Server | DB | Indefinite | User accounts |
| **TB_Admissao/Demissao** | SQL Server | DB | Indefinite | Workflow records |
| **TB_AprovacaoRPS** | SQL Server | DB | Indefinite | Approval audit trail |
| **Server Actions** | Next.js | Request | Stateless | API bridge |

---

## 13. IMPLEMENTATION CHECKLIST

- [ ] **Phase 1: Database**
  - [ ] Design TB_ConversationProgress schema
  - [ ] Create migration script
  - [ ] Add composite indexes
  - [ ] Create audit triggers

- [ ] **Phase 2: Backend API**
  - [ ] Create conversation.py router
  - [ ] Implement POST /conversation/start
  - [ ] Implement POST /conversation/{id}/message
  - [ ] Implement GET /conversation/{id}
  - [ ] Implement POST /conversation/{id}/context
  - [ ] Add error handling
  - [ ] Write endpoint tests

- [ ] **Phase 3: Frontend**
  - [ ] Create ConversationContext
  - [ ] Create useConversation hook
  - [ ] Create Server Actions
  - [ ] Add error boundaries
  - [ ] Implement optimistic updates
  - [ ] Write context tests

- [ ] **Phase 4: Integration**
  - [ ] Integrate with RPS approval flow
  - [ ] Capture form state
  - [ ] Display conversation history
  - [ ] Add resume functionality
  - [ ] Implement draft saving

- [ ] **Phase 5: Security & Performance**
  - [ ] Add access control validation
  - [ ] Implement rate limiting
  - [ ] Add message sanitization
  - [ ] Optimize queries
  - [ ] Add database archival logic
  - [ ] Load test with high volume

---

## 14. CONCLUSION

The MetaRH PortalCliente uses a **hybrid state management approach**:

1. **Lightweight frontend**: React hooks + Context (minimal complexity)
2. **Database-centric backend**: SQLAlchemy ORM + SQL Server
3. **Audit-first design**: TB_AprovacaoRPS pattern for immutable history
4. **Stateless API**: Request-scoped sessions, no server-side memory

**For conversation/progress tracking**, follow the **TB_AprovacaoRPS pattern**:
- Immutable append-only log
- Composite indexing for fast lookups
- Denormalized user data for historical accuracy
- Full audit trail with timestamps
- Layered persistence (client draft + server persistent)

This maintains architectural consistency while adding conversation capabilities.
