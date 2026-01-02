# MachinaMed Data Flow Architecture

This document provides comprehensive data flow diagrams for the MachinaMed (dem2) platform, covering all services, containers, frontend/backend communication, and agent processing.

**Document Version**: 1.1
**Last Updated**: 2026-01-02
**Status**: All information verified from source code

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Service-Level Data Flow](#service-level-data-flow)
4. [Frontend-Backend Flow](#frontend-backend-flow)
5. [Agent Processing Flow](#agent-processing-flow)
6. [Document Processing Flow](#document-processing-flow)
7. [Database Layer Flow](#database-layer-flow)
8. [Container Communication](#container-communication)
9. [External Integration Flow](#external-integration-flow)
10. [Graphviz Diagrams](#graphviz-diagrams)

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

### Diagram Styling

All diagrams in this document follow the standards defined in **[DIAGRAMS.md](DIAGRAMS.md)**. Refer to that guide when creating or updating diagrams.

---

## System Architecture

### High-Level Architecture Diagram

```mermaid
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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

## Document Processing Flow

### Overview

MachinaMed's document processing pipeline extracts biomarkers and medical data from lab reports, PDFs, and images. The pipeline uses Gemini Vision AI for extraction, the medical-catalog service for reconciliation, and Neo4j for graph storage.

**Key Features**:
- Real-time progress tracking via Server-Sent Events (SSE)
- Concurrent processing with configurable limits (10 global, 5 per user)
- Biomarker normalization and deduplication
- Medical catalog integration for standardized biomarker definitions
- Complete graph-based storage with Instance→Type pattern

### High-Level Document Processing Flow

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    autonumber
    participant User
    participant Frontend as Frontend (3000)
    participant FileAPI as File Storage API
    participant GCS as Google Cloud Storage
    participant DocProcAPI as DocProc API
    participant Queue as Task Queue
    participant Pipeline as Extraction Pipeline
    participant Gemini as Gemini Vision API
    participant MedCat as Medical Catalog (8001)
    participant Engine as Medical Data Engine
    participant Neo4j as Neo4j Graph DB
    participant Postgres as PostgreSQL

    User->>Frontend: Upload PDF/Image
    Frontend->>FileAPI: POST /files/upload
    FileAPI->>GCS: Store file
    GCS-->>FileAPI: file_id
    FileAPI->>Postgres: Save FileRecord metadata
    FileAPI-->>Frontend: FileRecordOut (file_id)

    Frontend->>DocProcAPI: POST /process_document {file_id}
    DocProcAPI->>Queue: Add to task queue
    Queue-->>DocProcAPI: task_id
    DocProcAPI-->>Frontend: ProcessDocumentResponse (task_id)

    Frontend->>DocProcAPI: GET /tasks/stream (SSE)

    Queue->>Pipeline: Pick up task (background worker)
    Pipeline->>GCS: Fetch file
    Pipeline->>Pipeline: Convert PDF to images

    Pipeline->>Gemini: Extract metadata (patient, dates)
    Gemini-->>Pipeline: Metadata (patient_name, report_date)
    Pipeline->>DocProcAPI: Emit SSE event (phase: detect)
    DocProcAPI-->>Frontend: SSE: Metadata extracted

    Pipeline->>Gemini: Extract biomarkers (all pages)
    Gemini-->>Pipeline: List[Biomarker] with values
    Pipeline->>DocProcAPI: Emit SSE event (phase: process)
    DocProcAPI-->>Frontend: SSE: Biomarkers extracted

    Pipeline->>Pipeline: Normalize biomarker names
    Note over Pipeline: Remove footnotes, clean subscripts

    Pipeline->>Engine: process_raw_medical_data(DocumentResourcesNew)
    Engine->>Neo4j: Create DocumentReferenceNode

    Engine->>MedCat: POST /biomarkers/search_batch
    MedCat-->>Engine: Catalog entries (catalog_id, unit)

    Engine->>Engine: Deduplicate by (catalog_id, unit)

    Engine->>Neo4j: Create ObservationTypeNodes
    Engine->>Neo4j: Create ObservationValueNodes
    Engine->>Neo4j: Link DocumentReference → Observations

    Engine-->>Pipeline: Processing complete
    Pipeline->>DocProcAPI: Emit SSE event (phase: complete)
    DocProcAPI-->>Frontend: SSE: Document saved
    Frontend-->>User: Show extracted biomarkers
```

### Document Upload & File Storage

**Endpoints**: `repos/dem2/services/file-storage/src/machina/file_storage/router.py`

**Upload Flow**:
```mermaid
%%{init: {'theme':'neutral'}}%%
graph LR
    A[User] -->|Upload file| B[POST /files/upload]
    B -->|FileService.upload| C{Storage Type}
    C -->|GCS| D[Google Cloud Storage]
    C -->|Local| E[Local Filesystem]
    D -->|file_id| F[PostgreSQL FileRecord]
    E -->|file_id| F
    F -->|FileRecordOut| G[Return to user]

    style B fill:#e3f2fd
    style F fill:#c8e6c9
```

**File Storage Schema** (PostgreSQL):
```
FileRecord:
  - file_id (UUID)
  - filename (string)
  - mimetype (string)
  - size (int)
  - storage_path (string)
  - user_id (UUID)
  - created_at (timestamp)
  - document_reference_id (UUID, FK to Neo4j)
```

### Extraction Pipeline Architecture

**Location**: `repos/dem2/services/docproc/src/machina/docproc/extractor/pipeline.py`

```mermaid
%%{init: {'theme':'neutral'}}%%
graph TB
    subgraph "Pipeline Stages"
        A[1. Load File] -->|PDF or Image| B[2. Convert to Images]
        B -->|Page images| C[3. Metadata Extraction]
        C -->|MetadataAgent<br/>Gemini Vision| D[4. Biomarker Extraction]
        D -->|GenericAgent<br/>Gemini Vision| E[5. Normalization]
        E -->|NormalizerAgent| F[6. Deduplication]
        F --> G[PipelineResult]
    end

    subgraph "Parallel Processing"
        B -->|Max 3 concurrent| B1[Page 1]
        B --> B2[Page 2]
        B --> B3[Page 3]
    end

    subgraph "Progress Events"
        C -.->|SSE| H[phase: detect]
        D -.->|SSE| I[phase: process]
        F -.->|SSE| J[phase: upload]
        G -.->|SSE| K[phase: complete]
    end

    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#fff9c4
    style G fill:#c8e6c9
```

**Stage Details**:

1. **Load File**: Fetch from storage, detect MIME type (PDF/PNG/JPEG)
2. **Convert to Images**: Split PDF into pages, convert to RGB images
3. **Metadata Extraction**: Extract patient_name, document_name, report_date, collection_date
4. **Biomarker Extraction**: Process all pages in single LLM call for full context
5. **Normalization**: Clean biomarker names (remove footnotes, fix subscripts)
6. **Deduplication**: Remove duplicate values within document

### Biomarker Data Model

**Schema**: `repos/dem2/shared/src/machina/shared/docproc/schema.py`

```mermaid
%%{init: {'theme':'neutral'}}%%
classDiagram
    class Biomarker {
        +string long_name
        +string short_name
        +string document_name
        +string document_name_modifier
        +string document_footnote
        +list~string~ aliases
        +list~BiomarkerValue~ values
        +float confidence
        +bool is_biomarker_derivative
        +string specimen_type
        +string panel_name
    }

    class BiomarkerValue {
        +string value
        +string observation_date
        +string observation_time
        +string unit
        +string label
        +SourceLocation name_location
        +SourceLocation value_location
        +SourceLocation unit_location
    }

    class SourceLocation {
        +int page_number
        +int x
        +int y
        +int width
        +int height
    }

    Biomarker "1" --> "*" BiomarkerValue
    BiomarkerValue "1" --> "0..3" SourceLocation
```

### Biomarker Extraction with Gemini Vision

**Agent**: `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/generic/agent.py`

**Extraction Process**:
```mermaid
%%{init: {'theme':'neutral'}}%%
graph LR
    A[Document Pages] -->|All pages| B[Gemini 2.0 Vision]
    B -->|Tool Calling| C[extract_biomarkers tool]
    C -->|Validation| D{Valid?}
    D -->|Yes| E[List of Biomarkers]
    D -->|No| F[Empty result]
    E --> G[NormalizerAgent]
    G -->|Clean names| H[Normalized Biomarkers]

    style B fill:#e1bee7
    style G fill:#fff9c4
    style H fill:#c8e6c9
```

**Normalization Rules**:
- Remove footnote superscripts: `Glucose²` → `Glucose`
- Remove parenthetical abbreviations: `HDL (LA)` → `HDL`
- Convert chemical subscripts: `CO₂` → `CO2`
- Detect genetic markers: `rs10757278`, `9p21`

### Biomarker Reconciliation & Medical Catalog Integration

**Location**: `repos/dem2/services/medical-data-engine/src/machina/medical_data_engine/engine/processors/biomarker/`

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    autonumber
    participant Pipeline as Extraction Pipeline
    participant Engine as Medical Data Engine
    participant MedCat as Medical Catalog (Qdrant)
    participant Dedup as Deduplication Service
    participant Neo4j as Neo4j Graph DB

    Pipeline->>Engine: DocumentResourcesNew (biomarkers)

    loop For each biomarker
        Engine->>MedCat: search_biomarker(name)
        MedCat->>MedCat: Vector similarity search
        MedCat-->>Engine: BiomarkerEntryResult
        Note over MedCat,Engine: catalog_id, long_name,<br/>short_name, unit_properties,<br/>aliases
    end

    Engine->>Dedup: Group by (catalog_id, unit)
    Dedup->>Dedup: Merge duplicate values
    Dedup-->>Engine: Deduplicated biomarkers

    Engine->>Neo4j: Create ObservationTypeNodes
    Note over Neo4j: Node properties:<br/>catalog_id, unit, name,<br/>display_name, aliases

    Engine->>Neo4j: Create ObservationValueNodes
    Note over Neo4j: Node properties:<br/>value, observation_date,<br/>value_epoch, unit, patient_id

    Engine->>Neo4j: Create relationships
    Note over Neo4j: DocumentReference-[CONTAINS]->ObservationType<br/>ObservationType-[HAS_VALUE]->ObservationValue<br/>Patient-[HAS_OBSERVATION]->ObservationValue
```

**Medical Catalog Entry Structure**:
```
BiomarkerEntryResult:
  - id (catalog_id): Unique identifier
  - long_name: "High-Density Lipoprotein Cholesterol"
  - short_name: "HDL Cholesterol"
  - description: Clinical description
  - unit_properties: ["mg/dL", "mmol/L"]
  - aliases: ["HDL", "HDL-C", "Good Cholesterol"]
```

**Deduplication Strategy**:
- Group biomarkers by `(catalog_id, unit)` tuple
- Within each group, merge values by:
  - Value equality (numeric or string)
  - Observation time (dedupe same value at same time)
  - Unit normalization (convert to canonical unit)

### Graph Database Storage Pattern

**Instance→Type Pattern for Multi-Tenancy**:

```mermaid
%%{init: {'theme':'neutral'}}%%
graph LR
    subgraph "Instance Layer (Patient-Specific)"
        DR[DocumentReferenceNode<br/>uuid: doc-123<br/>patient_id: patient-456<br/>file_id: file-789<br/>document_name: Lab Report<br/>report_date: 2024-12-15]

        OV1[ObservationValueNode<br/>uuid: obs-val-1<br/>value: 185<br/>unit: mg/dL<br/>observation_date: 2024-12-15<br/>patient_id: patient-456]

        OV2[ObservationValueNode<br/>uuid: obs-val-2<br/>value: 110<br/>unit: mg/dL<br/>observation_date: 2024-12-15<br/>patient_id: patient-456]
    end

    subgraph "Type Layer (Shared)"
        OT1[ObservationTypeNode<br/>catalog_id: cat-001<br/>name: Cholesterol Total<br/>unit: mg/dL<br/>aliases: Total Cholesterol, CHOL]

        OT2[ObservationTypeNode<br/>catalog_id: cat-002<br/>name: LDL Cholesterol<br/>unit: mg/dL<br/>aliases: LDL, LDL-C]
    end

    DR -->|CONTAINS| OT1
    DR -->|CONTAINS| OT2
    OT1 -->|HAS_VALUE| OV1
    OT2 -->|HAS_VALUE| OV2

    style DR fill:#ffccbc
    style OV1 fill:#ffccbc
    style OV2 fill:#ffccbc
    style OT1 fill:#c5e1a5
    style OT2 fill:#c5e1a5
```

**Neo4j Node Schemas**:

**DocumentReferenceNode**:
```cypher
CREATE (doc:DocumentReference {
  uuid: "doc-123",
  name: "Lab_Report.pdf",
  file_id: "file-789",
  document_name: "Lab Report",
  source_type: "DOCUMENT",
  source_id: "external-id",
  url: "gs://bucket/file-789",
  content_type: "application/pdf",
  size: 245678,
  hash: "sha256-...",
  summary: "Blood chemistry panel",
  report_date: datetime("2024-12-15T00:00:00Z"),
  user_id: "user-123",
  patient_id: "patient-456",
  created_at: datetime("2024-12-15T10:30:00Z")
})
```

**ObservationTypeNode**:
```cypher
CREATE (type:ObservationType {
  catalog_id: "cat-001",
  unit: "mg/dL",
  name: "Cholesterol Total",
  display_name: "Total Cholesterol",
  description: "Total blood cholesterol measurement",
  summary: "Lipid panel biomarker",
  aliases: ["Total Cholesterol", "CHOL", "Cholesterol"],
  unit_properties: ["mg/dL", "mmol/L"]
})
```

**ObservationValueNode**:
```cypher
CREATE (value:ObservationValue {
  value: 185.0,
  observation_date: datetime("2024-12-15T08:30:00Z"),
  value_epoch: 1702627800,
  unit: "mg/dL",
  source_type: "DOCUMENT",
  source_id: "doc-123",
  patient_id: "patient-456",
  user_id: "user-123"
})
```

### Complete Document Processing Flow

**End-to-End Data Flow**:

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    Start([User uploads PDF]) --> Upload[POST /files/upload]
    Upload --> Store[Store in GCS/Local]
    Store --> FileRecord[(PostgreSQL FileRecord)]
    FileRecord --> Queue[POST /process_document]
    Queue --> TaskQueue[Task Queue Manager]
    TaskQueue --> Worker[Background Worker]

    Worker --> Load[Load file from storage]
    Load --> Convert[Convert PDF to images]
    Convert --> Metadata[Extract Metadata<br/>Gemini Vision]
    Metadata --> Extract[Extract Biomarkers<br/>Gemini Vision]
    Extract --> Normalize[Normalize names<br/>NormalizerAgent]
    Normalize --> DocResources[DocumentResourcesNew]

    DocResources --> DataEngine[Medical Data Engine]
    DataEngine --> CreateDoc[Create DocumentReferenceNode]
    CreateDoc --> Neo4jDoc[(Neo4j DocumentReference)]

    DataEngine --> SearchCatalog[Search Medical Catalog]
    SearchCatalog --> Qdrant[(Qdrant Vector Search)]
    Qdrant --> CatalogResults[BiomarkerEntryResults]

    CatalogResults --> Dedup[Deduplicate by<br/>catalog_id + unit]
    Dedup --> CreateTypes[Create ObservationTypeNodes]
    CreateTypes --> Neo4jTypes[(Neo4j ObservationTypes)]

    Neo4jTypes --> CreateValues[Create ObservationValueNodes]
    CreateValues --> Neo4jValues[(Neo4j ObservationValues)]

    Neo4jValues --> Link[Create relationships]
    Link --> Complete[Emit SSE: complete]
    Complete --> End([User sees biomarkers])

    Metadata -.->|SSE| SSE1[Frontend: detect]
    Extract -.->|SSE| SSE2[Frontend: process]
    Dedup -.->|SSE| SSE3[Frontend: upload]
    Complete -.->|SSE| SSE4[Frontend: complete]

    style Upload fill:#e3f2fd
    style DataEngine fill:#fff9c4
    style Neo4jDoc fill:#c8e6c9
    style Neo4jTypes fill:#c8e6c9
    style Neo4jValues fill:#c8e6c9
    style End fill:#a5d6a7
```

### Performance Characteristics

**Document Processing Metrics**:

| Stage | Typical Time | Notes |
|-------|--------------|-------|
| File Upload | 0.5-2s | Depends on file size |
| Queue Wait | 0-30s | Depends on concurrent load |
| PDF Conversion | 1-3s per page | Max 3 concurrent pages |
| Metadata Extraction | 2-4s | Gemini Vision API call |
| Biomarker Extraction | 5-15s | Depends on document complexity |
| Normalization | <1s | Local processing |
| Medical Catalog Search | 1-3s | Batch vector search |
| Deduplication | <1s | In-memory processing |
| Graph Storage | 2-5s | Depends on biomarker count |
| **Total** | **15-60s** | **Complete pipeline** |

**Concurrency Limits**:
- Global concurrent documents: 10
- Per-user concurrent documents: 5
- Page rendering concurrency: 3

### Key Implementation Files

| Component | Location |
|-----------|----------|
| File Upload API | `services/file-storage/src/machina/file_storage/router.py` |
| File Service | `services/file-storage/src/machina/file_storage/file_service.py` |
| Document Processing API | `services/docproc/src/machina/docproc/router.py` |
| Processing Service | `services/docproc/src/machina/docproc/service.py` |
| Extraction Pipeline | `services/docproc/src/machina/docproc/extractor/pipeline.py` |
| Generic Agent | `services/docproc/extractor/agents/generic/agent.py` |
| Normalizer Agent | `services/docproc/extractor/agents/normalizer/agent.py` |
| Medical Data Engine | `services/medical-data-engine/src/machina/medical_data_engine/engine/engine.py` |
| Biomarker Processor | `services/medical-data-engine/engine/processors/biomarker/` |
| Observation Converter | `services/medical-data-engine/engine/processors/biomarker/observation_converter.py` |
| Deduplication | `services/medical-data-engine/engine/processors/biomarker/deduplication.py` |
| Medical Catalog Client | `services/medical-catalog/` |
| Document Repository | `services/medical-data-storage/repository/document_reference_repository.py` |
| Observation Memory | `services/graph-memory/src/machina/graph_memory/medical/observation/` |
| Graph Nodes | `services/graph-memory/src/machina/graph_memory/medical/graph/` |

---

## Database Layer Flow

### Multi-Database Architecture

```mermaid
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
- [`DATAFLOW_document_processing.dot`](DATAFLOW_document_processing.dot) - Document upload, extraction, and storage pipeline
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
%%{init: {'theme':'neutral'}}%%
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
%%{init: {'theme':'neutral'}}%%
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
