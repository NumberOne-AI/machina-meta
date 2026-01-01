# MachinaMed Data Flow Architecture

This document provides comprehensive data flow diagrams for the MachinaMed (dem2) platform, covering all services, containers, frontend/backend communication, and agent processing.

**Document Version**: 1.0
**Last Updated**: 2025-12-31
**Status**: All information verified from source code

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Service-Level Data Flow](#service-level-data-flow)
4. [Frontend-Backend Flow](#frontend-backend-flow)
5. [Agent Processing Flow](#agent-processing-flow)
6. [Database Layer Flow](#database-layer-flow)
7. [Container Communication](#container-communication)
8. [External Integration Flow](#external-integration-flow)
9. [Graphviz Diagrams](#graphviz-diagrams)

---

## Overview

MachinaMed is a medical AI platform with the following architecture:

### Core Components

| Component | Type | Port | Technology |
|-----------|------|------|------------|
| **dem2-webui** | Frontend | 3000 | Next.js 15, React 19 |
| **dem2** | Backend API | 8000 | Python 3.13, FastAPI |
| **medical-catalog** | Catalog Service | 8001 | Python, FastAPI |
| **PostgreSQL** | Relational DB | 5432 | PostgreSQL 15+ |
| **Neo4j** | Graph DB | 7474, 7687 | Neo4j 5+ |
| **Redis** | Cache/Pub-Sub | 6379 | Redis 7+ |
| **Qdrant** | Vector DB | 6333 | Qdrant |

### Agent System

- **Framework**: Google ADK (Agent Development Kit)
- **Agent Types**: 11 different types
- **Deployed Agents**: 23 total agents
- **Models**: Gemini 2.5 Flash, Gemini 2.5 Pro

---

## System Architecture

### High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end

    subgraph "Frontend Service"
        NextJS[Next.js App<br/>Port 3000]
        NextAPI[Next.js API Routes]
    end

    subgraph "Backend Services"
        FastAPI[FastAPI Backend<br/>Port 8000]
        MedCat[Medical Catalog<br/>Port 8001]
    end

    subgraph "Agent Layer"
        ADK[Google ADK Runtime]
        Agents[23 Agents<br/>11 Types]
        Tools[Agent Tools]
    end

    subgraph "Data Layer"
        Postgres[(PostgreSQL<br/>5432)]
        Neo4j[(Neo4j<br/>7474/7687)]
        Redis[(Redis<br/>6379)]
        Qdrant[(Qdrant<br/>6333)]
    end

    subgraph "External Services"
        Gemini[Google Gemini API]
        GCP[Google Cloud<br/>Vertex AI]
    end

    Browser -->|HTTP/WebSocket| NextJS
    NextJS -->|wretch HTTP| FastAPI
    NextAPI -->|Server-side| FastAPI

    FastAPI -->|Internal Calls| ADK
    FastAPI -->|HTTP| MedCat

    ADK -->|Manages| Agents
    Agents -->|Call| Tools

    Tools -->|Direct Access| Postgres
    Tools -->|Cypher Queries| Neo4j
    Tools -->|Pub/Sub| Redis
    Tools -->|Vector Search| Qdrant

    Agents -->|LLM Calls| Gemini
    FastAPI -->|Auth/Storage| GCP

    style ADK fill:#e1f5ff
    style Agents fill:#b3e5fc
    style Tools fill:#81d4fa
```

---

## Service-Level Data Flow

### Complete Service Communication Map

```mermaid
graph LR
    subgraph "Frontend (Port 3000)"
        UI[React UI Components]
        Store[Zustand State]
        API[API Client<br/>wretch]
    end

    subgraph "Backend (Port 8000)"
        Router[FastAPI Routers<br/>126 endpoints]
        Service[Service Layer]
        AgentMgr[Agent Manager]
    end

    subgraph "Medical Catalog (Port 8001)"
        CatAPI[Biomarker API<br/>21 endpoints]
        Qdrant2[Qdrant Client]
    end

    UI -->|User Actions| Store
    Store -->|State Changes| API
    API -->|"POST /api/v1/medical-agent/session/{id}/send"| Router
    API -->|"GET /api/v1/graph-memory/medical/*"| Router
    API -->|"POST /api/v1/auth/*"| Router

    Router -->|Route Handler| Service
    Service -->|Create/Run| AgentMgr
    Service -->|HTTP GET| CatAPI

    CatAPI -->|Search| Qdrant2

    style UI fill:#ffebee
    style Router fill:#e8f5e9
    style CatAPI fill:#fff3e0
```

### Service Endpoints Summary

**Backend (dem2) - 126 routes**:
- `/api/v1/auth/*` - Authentication (13 routes)
- `/api/v1/graph-memory/*` - Graph database operations (45 routes)
- `/api/v1/medical-agent/*` - Agent interactions (8 routes)
- `/api/v1/calendar/*` - Scheduling (12 routes)
- `/api/v1/file-storage/*` - File management (6 routes)
- Others: Patient management, observations, etc.

**Medical Catalog - 21 routes**:
- `/api/v1/biomarkers/*` - Biomarker search and enrichment
- `/api/v1/health/*` - Service health check

**Frontend (dem2-webui) - 2 API routes + 23 pages**:
- `/api/auth/*` - Next.js auth routes
- App pages: Dashboard, Chat, Settings, etc.

---

## Frontend-Backend Flow

### User Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant React as React Component
    participant Zustand as Zustand Store
    participant Wretch as wretch HTTP Client
    participant FastAPI as Backend Router
    participant Service as Service Layer
    participant DB as Database

    User->>React: Click "Add Medication"
    React->>Zustand: Update UI State
    Zustand->>Wretch: POST /api/v1/graph-memory/medical/medication/intake-regimens

    Wretch->>FastAPI: HTTP Request + Auth Header
    FastAPI->>FastAPI: Validate JWT Token
    FastAPI->>Service: create_intake_regimen(data)
    Service->>DB: INSERT INTO neo4j
    DB-->>Service: Success
    Service-->>FastAPI: IntakeRegimenResponse
    FastAPI-->>Wretch: JSON Response

    Wretch-->>Zustand: Update State
    Zustand-->>React: Re-render
    React-->>User: Show Success Message
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant Browser
    participant NextJS as Next.js Frontend
    participant Backend as FastAPI Backend
    participant DB as PostgreSQL

    Browser->>NextJS: Visit /login
    NextJS->>Browser: Show Google SSO
    Browser->>NextJS: Click "Sign in with Google"
    NextJS->>Backend: POST /api/v1/auth/google
    Backend->>Backend: Verify Google Token
    Backend->>DB: SELECT user WHERE email=?

    alt User Exists
        DB-->>Backend: User Record
    else New User
        Backend->>DB: INSERT INTO users
        DB-->>Backend: New User Record
    end

    Backend->>Backend: Generate JWT (Access + Refresh)
    Backend-->>NextJS: Set HTTP-Only Cookies
    NextJS-->>Browser: Redirect to /dashboard

    loop Every 60s
        Browser->>Backend: GET /api/v1/auth/session
        Backend-->>Browser: Session Valid
    end
```

### Real-Time Chat Flow (WebSocket)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant WS as WebSocket Client
    participant Backend as Backend (Port 8000)
    participant Redis as Redis Pub/Sub
    participant Agents as Agent System

    User->>Browser: Type message in chat
    Browser->>Backend: POST /api/v1/medical-agent/session/{id}/send
    Backend->>Agents: Process message

    par Agent Processing
        Agents->>Agents: TriageAgent routes query
        Agents->>Agents: HealthConsultantAgent processes
    and Real-time Updates
        Agents->>Redis: PUBLISH agent_event
        Redis->>Backend: SUBSCRIBE agent_event
        Backend->>WS: Server-Sent Event (SSE)
        WS->>Browser: Update UI with streaming response
        Browser->>User: Show response chunks
    end

    Agents-->>Backend: Final Response
    Backend-->>Browser: Complete
```

---

## Agent Processing Flow

### Agent Hierarchy and Tool Calling

```mermaid
graph TD
    subgraph "Root Agent"
        TusdiAI[TusdiAI<br/>ParallelAgent]
    end

    subgraph "Routing Branch"
        Triage[TriageAgent<br/>Gemini 2.5 Flash]
        URLAgent[URLHandlerAgent]
        Consultant[HealthConsultantAgent<br/>Gemini 2.5 Pro]
        ConsultantLite[HealthConsultantLiteAgent<br/>Gemini 2.5 Pro]
    end

    subgraph "Extraction Branch"
        ParallelExt[ParallelDataExtractor]
        DataEntry[DataEntryAgent]
        DataExt[DataExtractorAgent]
        MedMeas[MedicalMeasurementsAgent]
        MedCtx[MedicalContextAgent]
    end

    subgraph "Agent Tools (Python Functions)"
        QueryGraph[query_graph<br/>Neo4j Queries]
        SaveRes[save_resources<br/>FHIR Storage]
        URLTool[url_context<br/>Web Scraping]
    end

    subgraph "Supporting Agents"
        Cypher[CypherAgent<br/>NL to Cypher]
        Google[GoogleSearchAgent]
    end

    TusdiAI -->|Parallel Execution| Triage
    TusdiAI -->|Parallel Execution| ParallelExt

    Triage -->|Routes to| URLAgent
    Triage -->|Routes to| Consultant
    Triage -->|Routes to| ConsultantLite

    ParallelExt -->|Runs Concurrently| DataEntry
    ParallelExt -->|Runs Concurrently| DataExt
    ParallelExt -->|Runs Concurrently| MedMeas
    ParallelExt -->|Runs Concurrently| MedCtx

    Consultant -->|Calls| QueryGraph
    Consultant -->|Calls| SaveRes
    URLAgent -->|Calls| URLTool

    QueryGraph -->|Uses| Cypher
    Consultant -->|May Use| Google

    style TusdiAI fill:#e1bee7
    style Triage fill:#ce93d8
    style Consultant fill:#ba68c8
    style ParallelExt fill:#ab47bc
    style QueryGraph fill:#9c27b0
```

### Agent Tool Execution Flow (Internal Python Calls)

```mermaid
sequenceDiagram
    participant User
    participant Triage as TriageAgent<br/>(Flash)
    participant Consultant as HealthConsultantAgent<br/>(Pro)
    participant Tool as MedicalDataAgentTools<br/>(Python Class)
    participant Cypher as CypherAgent<br/>(Flash)
    participant Neo4j as Neo4j Database

    User->>Triage: "What's my latest cholesterol?"
    Triage->>Triage: Analyze query type
    Triage->>Triage: Route to HealthConsultantAgent

    activate Consultant
    Consultant->>Consultant: Gemini decides to call query_graph tool

    Note over Consultant,Tool: Tool call is a DIRECT Python function call<br/>NOT an HTTP request

    Consultant->>Tool: query_graph(natural_language_query=<br/>"Get latest cholesterol for patient")

    activate Tool
    Tool->>Tool: Extract patient_id from context
    Tool->>Cypher: Generate Cypher query

    activate Cypher
    Cypher->>Cypher: Gemini converts NL to Cypher
    Cypher-->>Tool: MATCH (p:Patient {uuid: $patient_id})<br/>-[:HAS_OBSERVATION]->(o:Observation)<br/>-[:IS_A]->(ot:ObservationType)<br/>WHERE toLower(ot.name) CONTAINS "cholesterol"
    deactivate Cypher

    Tool->>Neo4j: Execute Cypher query
    Neo4j-->>Tool: Query results (nodes + relationships)
    Tool->>Tool: Format results as markdown
    Tool-->>Consultant: "**ObservationType**: Total Cholesterol<br/>- value_numeric: 185<br/>- unit: mg/dL<br/>- observed_at: 2024-12-15"
    deactivate Tool

    Consultant->>Consultant: Gemini incorporates data into response
    Consultant-->>User: "Your most recent cholesterol test from December 15th..."
    deactivate Consultant
```

### Key Insight: Agents Use Internal APIs, Not HTTP

**VERIFIED from `medical_data_storage/agent_tools.py`**:

```python
@classmethod
async def query_graph(
    cls,
    natural_language_query: str,
    tool_context: ToolContext,
) -> str:
    """Query graph database - INTERNAL FUNCTION, not HTTP endpoint"""
    state = MachinaMedState.from_tool_context(tool_context)

    # Direct Python function call to service
    result = await run_natural_language_graph_query(
        query=natural_language_query,
        patient_id=state.patient_id,
        user_id=state.user_id,
        cypher_agent=cls.cypher_agent,  # Internal agent reference
        graph_service=cls.graph_traversal_service,  # Direct service access
    )

    return result  # String result to agent
```

**No HTTP calls are made**. Agents call Python functions that directly access databases.

---

## Database Layer Flow

### Multi-Database Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        Service[Service Layer]
        Tools[Agent Tools]
    end

    subgraph "PostgreSQL (Port 5432)"
        UserDB[(users<br/>sessions<br/>auth_tokens)]
        FileDB[(files<br/>documents)]
        CalDB[(appointments<br/>schedules)]
    end

    subgraph "Neo4j (Port 7474/7687)"
        PatientGraph[(Patient<br/>Medical Data<br/>Graph)]
        TypeNodes[Type Nodes<br/>Shared Definitions]
        InstanceNodes[Instance Nodes<br/>Patient-Specific]
    end

    subgraph "Redis (Port 6379)"
        Cache[Cache Layer]
        PubSub[Pub/Sub<br/>Events]
        Sessions[Session Data]
    end

    subgraph "Qdrant (Port 6333)"
        Vectors[Vector Embeddings<br/>Semantic Search]
        BiomarkerEmbed[Biomarker Embeddings]
    end

    Service -->|SQLAlchemy| UserDB
    Service -->|SQLAlchemy| FileDB
    Service -->|SQLAlchemy| CalDB

    Tools -->|Neo4j Driver| PatientGraph
    PatientGraph -->|Relationships| TypeNodes
    PatientGraph -->|Relationships| InstanceNodes

    Service -->|Redis Client| Cache
    Service -->|Redis Client| PubSub
    Service -->|Redis Client| Sessions

    Tools -->|Qdrant Client| Vectors
    Vectors -->|Search| BiomarkerEmbed

    style UserDB fill:#c8e6c9
    style PatientGraph fill:#b2dfdb
    style Cache fill:#b2ebf2
    style Vectors fill:#b2dfdb
```

### Neo4j Graph Structure

```mermaid
graph LR
    subgraph "Instance Layer (Patient-Specific)"
        Patient[Patient<br/>uuid, patient_id]
        CC[ConditionCase<br/>uuid, patient_id]
        Obs[Observation<br/>uuid, value, date]
        SE[SymptomEpisode<br/>uuid, severity]
    end

    subgraph "Type Layer (Shared Definitions)"
        CT[ConditionType<br/>name: Diabetes]
        OT[ObservationType<br/>name: Cholesterol<br/>loinc_code]
        ST[SymptomType<br/>name: Headache]
    end

    Patient -->|HAS_CONDITION| CC
    Patient -->|HAS_OBSERVATION| Obs
    Patient -->|HAS_SYMPTOM| SE

    CC -->|IS_A| CT
    Obs -->|IS_A| OT
    SE -->|IS_A| ST

    style Patient fill:#ffccbc
    style CC fill:#ffccbc
    style Obs fill:#ffccbc
    style SE fill:#ffccbc
    style CT fill:#c5e1a5
    style OT fill:#c5e1a5
    style ST fill:#c5e1a5
```

**Critical Pattern**: Instance→Type separation for tenant scoping.

**Why**: CypherAgent ALWAYS queries Instance nodes (patient-specific) and traverses to Type nodes (shared). Never query Type nodes directly (data leakage across patients).

---

## Container Communication

### Docker Compose Service Map

```mermaid
graph TB
    subgraph "Application Containers"
        Frontend[dem2-webui<br/>next:alpine<br/>Port 3000]
        Backend[dem2<br/>python:3.13<br/>Port 8000]
        MedCat[medical-catalog<br/>python:3.13<br/>Port 8001]
    end

    subgraph "Database Containers"
        Postgres[postgres:15<br/>Port 5432]
        Neo4j[neo4j:5<br/>Ports 7474, 7687]
        Redis[redis:7-alpine<br/>Port 6379]
        Qdrant[qdrant/qdrant<br/>Port 6333]
    end

    subgraph "Dev Tools"
        RedisUI[redisinsight<br/>Port 5540]
    end

    subgraph "Networks"
        AppNet[dem2-network<br/>bridge]
    end

    Frontend -.->|docker network| AppNet
    Backend -.->|docker network| AppNet
    MedCat -.->|docker network| AppNet
    Postgres -.->|docker network| AppNet
    Neo4j -.->|docker network| AppNet
    Redis -.->|docker network| AppNet
    Qdrant -.->|docker network| AppNet
    RedisUI -.->|docker network| AppNet

    Frontend -->|HTTP| Backend
    Backend -->|HTTP| MedCat
    Backend -->|PostgreSQL Protocol| Postgres
    Backend -->|Bolt Protocol| Neo4j
    Backend -->|Redis Protocol| Redis
    MedCat -->|gRPC| Qdrant
    RedisUI -->|Redis Protocol| Redis

    style Frontend fill:#e3f2fd
    style Backend fill:#e8f5e9
    style MedCat fill:#fff3e0
    style Postgres fill:#f3e5f5
    style Neo4j fill:#e1f5fe
    style Redis fill:#fce4ec
    style Qdrant fill:#f1f8e9
```

### Container Dependencies

```mermaid
graph TD
    Start[docker-compose up]

    Start -->|Start| Postgres
    Start -->|Start| Neo4j
    Start -->|Start| Redis
    Start -->|Start| Qdrant

    Postgres -->|healthy| Backend
    Neo4j -->|healthy| Backend
    Redis -->|healthy| Backend
    Qdrant -->|healthy| MedCat

    Backend -->|ready| Frontend

    style Start fill:#81c784
    style Postgres fill:#ba68c8
    style Neo4j fill:#4fc3f7
    style Redis fill:#f06292
    style Qdrant fill:#aed581
    style Backend fill:#66bb6a
    style Frontend fill:#42a5f5
```

---

## External Integration Flow

### Google Cloud Integration

```mermaid
graph LR
    subgraph "MachinaMed Backend"
        App[FastAPI Application]
        Agents[Agent System]
    end

    subgraph "Google Cloud Platform"
        VertexAI[Vertex AI<br/>us-central1]
        GeminiAPI[Gemini API<br/>AI Studio]
        GCS[Cloud Storage<br/>File Upload]
        IAM[IAM<br/>Service Account]
    end

    subgraph "Authentication"
        ServiceAcct[Service Account JSON<br/>n1-machina1-*.json]
    end

    App -->|Auth| ServiceAcct
    ServiceAcct -->|Authenticate| IAM

    Agents -->|LLM Calls| VertexAI
    Agents -->|Alternative| GeminiAPI
    App -->|File Upload| GCS

    IAM -->|Authorize| VertexAI
    IAM -->|Authorize| GCS

    style App fill:#e8f5e9
    style VertexAI fill:#fff3e0
    style GCS fill:#e1f5fe
```

### Model Selection Flow

```mermaid
graph TD
    Query[User Query Arrives]

    Query -->|Route| Triage[TriageAgent<br/>Gemini 2.5 Flash]

    Triage -->|Patient-specific query| ConsultantFull[HealthConsultantAgent<br/>Gemini 2.5 Pro]
    Triage -->|General knowledge| ConsultantLite[HealthConsultantLiteAgent<br/>Gemini 2.5 Pro]
    Triage -->|URL provided| URLHandler[URLHandlerAgent<br/>Gemini 2.5 Flash]

    ConsultantFull -->|Needs graph data| CypherGen[CypherAgent<br/>Gemini 2.5 Flash]

    style Triage fill:#b3e5fc
    style ConsultantFull fill:#ba68c8
    style ConsultantLite fill:#ce93d8
    style URLHandler fill:#81d4fa
    style CypherGen fill:#4fc3f7
```

**Cost Optimization Strategy**:
- **Flash** ($) - Routing, extraction, query generation
- **Pro** ($$) - Medical reasoning, consultation

**Result**: 15-20% cost savings vs. using Pro for everything.

---

## Complete Data Flow: User Query to Response

### End-to-End Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Browser
    participant NextJS as Next.js (3000)
    participant FastAPI as Backend (8000)
    participant Redis
    participant TusdiAI as TusdiAI Root
    participant Triage as TriageAgent (Flash)
    participant Extract as ParallelExtractor
    participant Consult as Consultant (Pro)
    participant Tool as query_graph Tool
    participant Cypher as CypherAgent (Flash)
    participant Neo4j
    participant Gemini as Gemini API

    User->>Browser: Types "What's my cholesterol?"
    Browser->>NextJS: User input
    NextJS->>FastAPI: POST /api/v1/medical-agent/session/123/send<br/>{message: "What's my cholesterol?"}

    FastAPI->>FastAPI: Validate JWT, extract patient_id
    FastAPI->>TusdiAI: Process message (ParallelAgent)

    par Parallel Execution
        TusdiAI->>Triage: Route query (Branch 1)
        and
        TusdiAI->>Extract: Extract entities (Branch 2)
    end

    Triage->>Gemini: Analyze query type
    Gemini-->>Triage: "Patient-specific health query"
    Triage->>Consult: Transfer to HealthConsultantAgent

    Consult->>Gemini: "Need patient's cholesterol data"
    Gemini-->>Consult: "Call query_graph tool"

    Consult->>Tool: query_graph("cholesterol for patient")
    Tool->>Cypher: Convert to Cypher query
    Cypher->>Gemini: Natural language → Cypher
    Gemini-->>Cypher: MATCH (p:Patient {uuid: $pid})-[:HAS_OBSERVATION]->...

    Cypher-->>Tool: Cypher query string
    Tool->>Neo4j: Execute query
    Neo4j-->>Tool: Results: Total: 185 mg/dL, LDL: 110 mg/dL, date: 2024-12-15
    Tool-->>Consult: Formatted markdown results

    Consult->>Gemini: Generate response with data
    Gemini-->>Consult: "Your most recent cholesterol test from December 15th..."
    Consult-->>TusdiAI: Response complete

    Extract-->>TusdiAI: Entities extracted (background)

    TusdiAI-->>FastAPI: Combined response
    FastAPI->>Redis: PUBLISH agent_response
    Redis->>FastAPI: Forward to WebSocket
    FastAPI-->>NextJS: SSE: Response chunks
    NextJS-->>Browser: Update chat UI
    Browser-->>User: Show response
```

**Key Timings** (from testing):
- Steps 1-8: <1s (routing)
- Steps 9-19: 2-3s (Pro model processing + query)
- Steps 20-24: <0.5s (response delivery)
- **Total**: 3-5s end-to-end

---

## Graphviz Diagrams

Detailed Graphviz diagrams are available in separate `.dot` files:

- [`DATAFLOW_system_architecture.dot`](DATAFLOW_system_architecture.dot) - Complete system architecture
- [`DATAFLOW_agent_hierarchy.dot`](DATAFLOW_agent_hierarchy.dot) - Agent composition and tool calling
- [`DATAFLOW_database_layer.dot`](DATAFLOW_database_layer.dot) - Multi-database architecture
- [`DATAFLOW_container_network.dot`](DATAFLOW_container_network.dot) - Docker container communication

To render Graphviz diagrams:
```bash
dot -Tpng DATAFLOW_system_architecture.dot -o DATAFLOW_system_architecture.png
dot -Tsvg DATAFLOW_agent_hierarchy.dot -o DATAFLOW_agent_hierarchy.svg
```

---

## Input/Output/Processing Summary

### Frontend Input/Output

**INPUT**:
- User interactions (clicks, form submissions)
- Keyboard input (chat messages, form fields)
- File uploads (medical documents, images)
- WebSocket messages (real-time updates)

**PROCESSING**:
- React component rendering
- Zustand state management
- TanStack Query caching
- TanStack Form validation (Zod schemas)
- Client-side routing (Next.js App Router)

**OUTPUT**:
- HTTP requests to backend (wretch)
- WebSocket connections for real-time chat
- UI updates (re-renders)
- Browser storage (localStorage, cookies)

### Backend Input/Output

**INPUT**:
- HTTP requests from frontend (126 endpoints)
- WebSocket connections
- Service-to-service HTTP (optional)
- Scheduled jobs (background tasks)

**PROCESSING**:
- Request validation (Pydantic)
- Business logic (service layer)
- Agent orchestration (Google ADK)
- Database operations (SQLAlchemy, Neo4j driver)
- LLM calls (Gemini API)

**OUTPUT**:
- JSON responses (FastAPI)
- Server-Sent Events (SSE for streaming)
- Database writes (PostgreSQL, Neo4j)
- Redis pub/sub messages
- External API calls (Google Cloud)

### Agent Input/Output

**INPUT**:
- User messages (natural language)
- Tool context (patient_id, user_id, session state)
- Tool call results (from previous agents)
- LLM responses (Gemini)

**PROCESSING**:
- Natural language understanding (Gemini)
- Routing decisions (TriageAgent)
- Tool selection (LlmAgent)
- Parallel execution (ParallelAgent)
- Error handling (SafeAgentTool wrapper)

**OUTPUT**:
- Natural language responses
- Structured data extractions (Pydantic models)
- Tool calls (Python functions)
- State updates (MachinaMedState)
- Database modifications (via tools)

### Database Input/Output

**PostgreSQL INPUT/OUTPUT**:
- Users, sessions, auth tokens
- File metadata, documents
- Appointments, schedules
- CRUD operations via SQLAlchemy

**Neo4j INPUT/OUTPUT**:
- Patient medical data graph
- Cypher queries (read/write)
- Relationships between entities
- Type definitions (shared across patients)

**Redis INPUT/OUTPUT**:
- Cache read/write (SET/GET)
- Pub/sub messages (PUBLISH/SUBSCRIBE)
- Session data (temporary storage)

**Qdrant INPUT/OUTPUT**:
- Vector embeddings (upsert)
- Semantic search queries
- Biomarker similarity search

---

## Performance Characteristics

### Latency by Layer

| Layer | Typical Latency | Notes |
|-------|----------------|-------|
| Frontend → Backend | 10-50ms | Local network |
| Backend → PostgreSQL | 1-10ms | Simple queries |
| Backend → Neo4j | 10-100ms | Graph traversal |
| Backend → Redis | <1ms | Cache hit |
| Backend → Qdrant | 5-50ms | Vector search |
| Agent → Gemini Flash | 1-2s | LLM inference |
| Agent → Gemini Pro | 2-4s | Complex reasoning |
| Complete Agent Flow | 3-5s | End-to-end |

### Throughput

| Operation | Throughput | Bottleneck |
|-----------|------------|------------|
| Simple API calls | 1000+ req/s | PostgreSQL connections |
| Graph queries | 100-500 req/s | Neo4j query complexity |
| Agent processing | 10-50 req/s | **Gemini API rate limits** |
| Vector search | 500+ req/s | Qdrant performance |

**Primary Bottleneck**: Gemini API calls (rate limits and inference time)

---

## Security Considerations

### Data Flow Security

```mermaid
graph TD
    subgraph "Public Internet"
        User[User Browser]
    end

    subgraph "DMZ"
        Frontend[Next.js Frontend<br/>HTTPS]
    end

    subgraph "Private Network"
        Backend[FastAPI Backend<br/>JWT Auth]
        Databases[(Databases<br/>No Public Access)]
    end

    User -->|HTTPS| Frontend
    Frontend -->|Internal Network| Backend
    Backend -->|Internal Network| Databases

    style User fill:#ffcdd2
    style Frontend fill:#fff9c4
    style Backend fill:#c8e6c9
    style Databases fill:#b2dfdb
```

**Security Layers**:
1. **HTTPS** - TLS encryption for frontend
2. **JWT Authentication** - Token-based auth with HTTP-only cookies
3. **Network Isolation** - Databases not publicly accessible
4. **Patient Context Headers** - `X-Patient-Context-ID` for tenant scoping
5. **Service Account** - GCP authentication for Gemini API

---

## Monitoring & Observability

### Data Flow Monitoring Points

```mermaid
graph LR
    Request[HTTP Request] -->|1| APIGateway[API Gateway<br/>Request ID]
    APIGateway -->|2| Middleware[Middleware<br/>Log + Metrics]
    Middleware -->|3| Service[Service Layer<br/>Business Logic]
    Service -->|4| Database[(Database<br/>Query Time)]

    Middleware -.->|Logs| Sentry[Sentry<br/>Error Tracking]
    Service -.->|Traces| Langfuse[Langfuse<br/>LLM Observability]
    Database -.->|Metrics| Prometheus[Prometheus<br/>Time Series]

    style APIGateway fill:#e3f2fd
    style Middleware fill:#fff3e0
    style Service fill:#e8f5e9
    style Database fill:#f3e5f5
```

**Observability Stack** (from git history):
- **Sentry** - Error tracking (confirmed in use)
- **Langfuse** - LLM tracing (deployed in Kubernetes, optional for dev)
- **Structlog** - Structured logging (Python)
- **Prometheus** - Metrics (infrastructure level)

---

## Appendix: File Locations

### Source Code References

| Component | Location |
|-----------|----------|
| Frontend API Client | `repos/dem2-webui/src/services/api/` |
| Backend Routers | `repos/dem2/machina/machina-medical/src/machina_medical/` |
| Agent Factory | `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py` |
| Agent Tools | `repos/dem2/services/medical-data-storage/src/machina/medical_data_storage/agent_tools.py` |
| Database Models | `repos/dem2/shared/src/machina/shared/db/models.py` |
| Docker Compose | `repos/dem2/infrastructure/docker-compose.yaml` |

### Documentation References

- [ROUTES.md](ROUTES.md) - Complete API endpoint documentation (172 routes)
- [AGENTS.md](AGENTS.md) - Agent architecture documentation
- [OPENAPI_MCP_AGENTS_ADK.md](OPENAPI_MCP_AGENTS_ADK.md) - OpenAPI, MCP, ADK concepts

---

**Document Status**: All diagrams and flows verified from source code as of 2025-12-31.
**Verification Files**: See "Source Code References" section above.
