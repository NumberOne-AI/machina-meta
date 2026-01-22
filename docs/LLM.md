# LLM Integration and Prompt Engineering

**Version:** 1.0
**Last Updated:** 2026-01-06
**Scope:** LLM provider integrations, prompt engineering patterns, and instruction design across machina-meta workspace

---

## Table of Contents

1. [Overview](#overview)
2. [LLM Provider Integrations](#llm-provider-integrations)
3. [Prompt Engineering Fundamentals](#prompt-engineering-fundamentals)
4. [System Prompt Architecture](#system-prompt-architecture)
5. [Prompt Template System](#prompt-template-system)
6. [Domain-Specific Prompts](#domain-specific-prompts)
7. [Structured Output Prompting](#structured-output-prompting)
8. [Context Injection Patterns](#context-injection-patterns)
9. [Multi-Agent Prompt Coordination](#multi-agent-prompt-coordination)
10. [Model Configuration](#model-configuration)
11. [Cost Management](#cost-management)
12. [Prompt Versioning and Testing](#prompt-versioning-and-testing)
13. [Citations](#citations)

---

## Overview

MachinaMed's LLM integration architecture supports multiple providers with a focus on **prompt engineering excellence**. The system employs sophisticated prompt composition, dynamic context injection, and multi-agent coordination patterns to deliver reliable medical AI interactions.

**Related Documentation**:
- [MULTI_AGENT_ARCHITECTURE.md](docs/MULTI_AGENT_ARCHITECTURE.md) - Complete agent architecture and tool use patterns
- [DATAFLOW.md](docs/DATAFLOW.md) - System-wide data flow including LLM interactions

### Architectural Principles

1. **Provider Abstraction**: Unified interface across Google, Anthropic, and OpenAI[^1]
2. **Prompt Composability**: Templates with runtime context injection[^2]
3. **Version Control**: Prompt versioning for different model generations[^3]
4. **Cost Awareness**: Rate limiting and token tracking[^4]
5. **Structured Outputs**: Pydantic schemas for reliable extraction[^5]

---

## LLM Provider Integrations

### Primary Provider: Google Gemini (via Google ADK)

**Framework**: Google Agent Development Kit (ADK)[^6]

**Models in Use**:
```python
# Fast routing and low-latency responses
GEMINI_2_5_FLASH = "gemini-2.5-flash"      # TriageAgent[^7]

# Primary medical reasoning
GEMINI_2_5_PRO = "gemini-2.5-pro"          # Most agents[^8]

# Future features
GEMINI_3_0_PRO_PREVIEW = "gemini-3.0-pro-preview"[^9]
```

**Configuration**:
```python
from google.adk.models import Gemini
from google import genai
from google.genai import types

gemini = Gemini(
    model_name="gemini-2.5-pro",
    retry=types.HttpRetryOptions(attempts=3)[^10]
)
```

**Context Windows**:
- Gemini 2.5 Flash: 1M tokens
- Gemini 2.5 Pro: 2M tokens

### Secondary Provider: Anthropic Claude (via Vertex AI)

**Models Available**[^11]:

| Model | Input | Output | Cache Support | Use Case |
|-------|-------|--------|---------------|----------|
| Claude 4.5 Haiku | $1.00/M | $5.00/M | Yes | Fast document processing |
| Claude 4.5 Sonnet | $3.00/M | $15.00/M | Yes | Balanced performance |
| Claude 4.5 Opus | $15.00/M | $75.00/M | Yes | Complex reasoning |

**Implementation Locations**:
- Document Processing: `repos/dem2/services/docproc/src/machina/docproc/llm/`[^12]
- Medical Catalog: `repos/medical-catalog/src/llm/providers/anthropic.py`[^13]

**Prompt Caching**: Ephemeral cache control for session-level efficiency
- Cache Read: 10% of input price
- Cache Write: 125% of input price

### LLM Proxy Architecture

**Central Proxy**: Unified interface with rate limiting and cost tracking[^14]

**Features**:
- **Rate Limiting**: 60 requests/minute (configurable)
- **Concurrency Control**: 10 max concurrent requests
- **Auto-Streaming**: Enabled for outputs > 16,000 tokens[^15]
- **Provider Routing**: Intelligent selection based on task
- **Cost Tracking**: Real-time token and cost calculation

**Implementation**:
- Dem2: `repos/dem2/services/docproc/src/machina/docproc/llm/proxy.py`[^16]
- Medical Catalog: `repos/medical-catalog/src/llm/proxy.py`[^17]

---

## Prompt Engineering Fundamentals

### Core Principles

**1. Medical Accuracy First**
- Prioritize precision over creativity
- Use low temperature (0.0-0.1)[^18]
- Require evidence-based reasoning
- Discourage speculation

**2. Structured Thinking**
- Step-by-step reasoning frameworks
- Explicit decomposition of complex queries
- Clear decision trees

**3. Context Awareness**
- Inject temporal context (current_time)[^19]
- Include patient/user profiles when relevant
- Provide graph schema for query generation

**4. Tool Use Guidance**
- Explicit tool descriptions
- When to use each tool
- Expected input/output formats

**5. Output Format Control**
- Pydantic schemas for structured outputs
- Natural language for consultations
- Markdown formatting for readability

### Prompt Design Guidelines

**Length**: No strict limits, optimize for clarity
- TriageAgent: ~157 lines[^20]
- HealthConsultantAgent: ~184 lines (comprehensive)[^21]
- DataExtractorAgent: ~120 lines (granularity rules)

**Structure**: Standard format across all agents
```yaml
name: AgentName
model: gemini-2.5-pro
description: |
  Brief agent description (1-2 sentences)
instruction: |
  # Role and Context
  You are a [role] specialized in [task].

  # Capabilities
  - Capability 1
  - Capability 2

  # Instructions
  1. Step 1
  2. Step 2

  # Examples (optional)

  # Constraints
  - Constraint 1
  - Constraint 2
generate_config:
  temperature: 0.1
  max_output_tokens: 512
```

---

## System Prompt Architecture

### Storage Pattern

All agent prompts stored in YAML configuration files[^22]:

**Directory Structure**:
```
repos/dem2/services/medical-agent/src/machina/medical_agent/agents/
├── global_config.yml[^23]             # Shared settings
├── TriageAgent/
│   └── config.yml[^24]                # Routing logic
├── HealthConsultantAgent/
│   ├── config.yml[^25]                # Current version
│   ├── config_3.yml                   # Gemini 3.0 version
│   └── config_4.yml                   # Future version
├── DataExtractorAgent/
│   └── config.yml[^26]                # Extraction rules
├── AskTusdiAIHandlerAgent/
│   └── config.yml                     # AI query handler
├── CypherAgent/
│   └── config.yml                     # Graph query agent
├── DataEntryAgent/
│   └── config.yml                     # Data entry agent
├── GoogleSearchAgent/
│   └── config.yml                     # Web search agent
├── HealthConsultantLiteAgent/
│   └── config.yml                     # Lightweight consultant
├── MedicalContextAgent/
│   └── config.yml                     # Medical context agent
├── MedicalMeasurementsAgent/
│   └── config.yml                     # Measurements agent
└── UrlHandlerAgent/
    └── config.yml                     # URL processing agent
```

### Key System Prompts

#### 1. TriageAgent: Request Classification and Routing

**Purpose**: Initial contact point, analyzes user intent and routes to specialist agents

**Key Sections**:

**A. Persona and Context**:
```yaml
instruction: |
  # Role
  You are TriageAgent, the first point of contact for all user requests.

  # Context Variables
  - {user_profile?}: Person speaking to you
  - {patient_profile?}: Person being discussed
  - {user_is_patient?}: Boolean if same person
  - {current_time}: Current timestamp with timezone
```

**B. Routing Rules**:
```yaml
  # Rule 0: URL Handling (ALWAYS FIRST)
  If user provides URL → URLHandlerAgent

  # Rule 1: Non-Health Requests
  If request is not health-related → Politely refuse

  # Rule 2: Full Data Lists
  If asking for all symptoms/allergies/medications → Redirect to UI

  # Rule 3A: Modification Requests
  If delete/update/correct → DataEntryAgent

  # Rule 3B: New Information Sharing
  If sharing new health info → DataExtractorAgent → Acknowledge

  # Rule 4: Consultations
  If health question/consultation → HealthConsultantAgent
```

**C. Tools Available**:
- URLHandlerAgent (nested agent)
- HealthConsultantAgent (nested agent)

**Full Prompt**: 157 lines[^27]

#### 2. HealthConsultantAgent: Medical Reasoning and Consultation

**Purpose**: Main health consultation with graph querying and web research

**Key Sections**:

**A. Comprehensive Health Check Detection**:
```yaml
instruction: |
  # Decision: Holistic vs. Specific Query

  HOLISTIC QUERIES (comprehensive health check):
  - "How am I doing?"
  - "What's my health status?"
  - "Give me a health overview"

  SPECIFIC QUERIES (targeted lookup):
  - "What's my blood pressure?"
  - "Do I have any allergies to peanuts?"
  - "When is my next appointment?"
```

**B. Step-by-Step Reasoning Framework**:
```yaml
  # Reasoning Process

  Step 1: Understand Core Question
  - What is the user really asking?
  - What entities are mentioned? (conditions, medications, labs)

  Step 2: Formulate Retrieval Plan
  - What data do I need from the graph?
  - Do I need external research?

  Step 3: Execute Plan
  - Run graph queries (query_graph tool)
  - Perform web searches if needed (GoogleSearchAgent)
  - Process URLs if provided (URLHandlerAgent)

  Step 4: Synthesize Response
  - Combine all gathered information
  - Provide clear, actionable answer

  Step 5: Next Steps
  - Suggest follow-up actions
  - Recommend consultations if needed
```

**C. Body System Mapping**:
```yaml
  # Map Organs to Systems
  liver → hepatic
  heart → cardiovascular
  kidney → renal
  lung → respiratory
  brain → neurological
  stomach → gastrointestinal
  [comprehensive mapping provided]
```

**D. Temporal Filtering Logic**:
```yaml
  # Encounter Queries with Time

  "upcoming appointments":
    encounters WHERE start_time > {current_time}

  "past appointments":
    encounters WHERE start_time < {current_time}

  "today's appointments":
    encounters WHERE DATE(start_time) = DATE({current_time})
```

**E. Observation Handling**:
```yaml
  # ALWAYS Include for Observations
  - value_numeric / value_text
  - unit
  - observed_at (from ObservationValueNode, NOT metadata)
  - reference_range
  - interpretation (normal, high, low, critical)

  # Map to Body Systems
  Glucose → Endocrine
  Hemoglobin → Hematologic
  ALT/AST → Hepatic
```

**F. Intake Regimen Logic**:
```yaml
  # Critical Distinction

  IntakeRegimenNode:
    - What patient is PRESCRIBED
    - Frequency (daily, twice daily, etc.)
    - Route, dosage_value, dosage_unit

  IntakeEventNode:
    - ACTUAL intake records
    - taken_at timestamp
    - status (taken, missed, skipped)

  # NEVER assume medication taken based solely on frequency
  "Did I take my medication today?"
    → Query IntakeEventNode for today's date
    → Do NOT assume from IntakeRegimenNode frequency
```

**G. Fast Graph Summary**:
```yaml
  # Optimization for Simple Queries

  If query is simple (is_complex: false):
    - Single entity lookup
    - Total paths ≤ 5
    - Total nodes ≤ 60
    → FastGraphSummaryAgent (gemini-2.5-flash)[^28]
    → Sub-second response

  If query is complex:
    → Full reasoning with current agent
```

**H. Tone Guidelines**:
```yaml
  # Communication Style
  - Trustworthy and supportive
  - Concise and action-oriented
  - Medical accuracy paramount
  - Empathetic without being patronizing
  - Use patient's preferred language/terminology
```

**Full Prompt**: 184 lines[^29]

#### 3. DataExtractorAgent: Granular Health Information Extraction

**Purpose**: Extract health information from user input for storage in long-term memory

**Key Sections**:

**A. Extraction Granularity Rules**:

**Symptoms**:
```yaml
  # Extract EACH distinct symptom separately

  Input: "chest tightness, rapid heartbeat, and sweating"

  CORRECT:
  - Symptom 1: "chest tightness"
  - Symptom 2: "rapid heartbeat"
  - Symptom 3: "sweating"

  INCORRECT:
  - "panic attack" (that's an interpretation, not reported symptom)
```

**Observations**:
```yaml
  # Extract EACH measurement from panels separately

  Input: "My BMP showed sodium 140, potassium 4.0, chloride 100, CO2 22, BUN 15, creatinine 1.0, glucose 95"

  EXTRACT: 7 separate observations
  - Sodium: 140 mEq/L
  - Potassium: 4.0 mEq/L
  - Chloride: 100 mEq/L
  - Carbon Dioxide: 22 mEq/L
  - Blood Urea Nitrogen: 15 mg/dL
  - Creatinine: 1.0 mg/dL
  - Glucose: 95 mg/dL

  DO NOT EXTRACT: "BMP panel" (extract measurements instead)
```

**Blood Pressure**:
```yaml
  # TWO separate observations

  Input: "Blood pressure was 120/80"

  EXTRACT:
  - Systolic Blood Pressure: 120 mmHg
  - Diastolic Blood Pressure: 80 mmHg
```

**Conditions**:
```yaml
  # Extract ALL mentioned conditions

  Input: "I have diabetes with neuropathy"

  EXTRACT: 2 separate conditions
  - Diabetes
  - Neuropathy
```

**Allergies**:
```yaml
  # Context-dependent granularity

  Pattern A: "CATEGORY (examples)"
    Input: "Nuts (peanuts, almonds)"
    EXTRACT: "Nuts" (category level)

  Pattern B: "specific1, specific2, specific3"
    Input: "peanuts, almonds, walnuts"
    EXTRACT: 3 separate allergies
```

**B. What NOT to Extract**:
```yaml
  # Exclusions
  - Resolved/historical symptoms ("had headaches last year")
  - Medical interpretations ("looks like infection")
  - Panel names ("CMP panel" → extract individual measurements)
  - Speculative conditions ("might be diabetes")
```

**Full Prompt**: ~120 lines[^30]

#### 4. GoogleSearchAgent: Medical Research

**Purpose**: Search authoritative medical web resources

**Search Strategy**:
```yaml
instruction: |
  # Target Authoritative Sources

  PREFERRED SITES:
  - site:healthline.com
  - site:webmd.com
  - site:medlineplus.gov
  - site:mayoclinic.org
  - site:clevelandclinic.org
  - site:nih.gov

  # Output Format
  Return 5-6 most relevant URLs with:
  - header: Page title
  - link: Full URL
  - explanation: Why this is relevant (1-2 sentences)
```

**Full Prompt**: ~80 lines[^31]

---

## Prompt Template System

### Template Rendering Engine

**Pattern**: Jinja2-like template rendering with context injection

**Implementation**:
```python
from machina.medical_agent.common.configurator import render_template

prompt_text = render_template(
    config.instruction,
    context={
        "AgentName": {entry.name: entry for entry in AgentName},
        "graph_nodes": graph_nodes_text,
        "current_time": callback_context.state["current_time"],
    }
)
```

### Context Variables

**Standard Variables**:
```yaml
{user_profile?}        # Optional: User profile JSON
{patient_profile?}     # Optional: Patient profile JSON
{user_is_patient?}     # Optional: Boolean flag
{current_time}         # Required: Formatted timestamp with timezone
{current_time_iso}     # Required: ISO 8601 format
{user_timezone}        # Required: Timezone name (e.g., "America/New_York")
{graph_nodes}          # Required: Available Neo4j node types
{recent_observations?} # Optional: Recent health metrics
{active_allergies?}    # Optional: Current allergies
```

**Optional Variables**: Suffix `?` indicates optional (empty string if not available)

### Dynamic Schema Injection

**Graph Schema Nodes**:
```python
# Load Neo4j schema
graph_nodes = load_graph_schema()

# Format for prompt
graph_nodes_text = "\n".join([
    f"- {node.label}: {node.properties}"
    for node in graph_nodes
])

# Inject into prompt
prompt = config.instruction.format(graph_nodes=graph_nodes_text)
```

**Operations Schema (DataExtractor)**:
```python
# Load operations schema at runtime
operations_schema = ExtractUserQueryResources.model_json_schema()

# Inject into prompt
prompt = config.instruction.format(
    operations_schema=json.dumps(operations_schema, indent=2)
)
```

### Temporal Context Injection

**Before Agent Callback**[^32]:
```python
def _update_time(
    callback_context: CallbackContext,
    agent_request: Request,
) -> None:
    """Inject current time with timezone into agent state."""
    user_timezone = extract_timezone_from_headers(agent_request)
    tz = pytz.timezone(user_timezone)
    now = datetime.now(tz)

    callback_context.state["current_time_iso"] = now.isoformat()
    callback_context.state["current_time"] = now.strftime("%Y-%m-%d %I:%M %p %Z")
    callback_context.state["user_timezone"] = user_timezone
```

**Usage in Prompt**:
```yaml
instruction: |
  Current time: {current_time}
  User timezone: {user_timezone}

  When querying encounters:
  - "upcoming" means start_time > {current_time_iso}
  - "past" means start_time < {current_time_iso}
```

---

## Domain-Specific Prompts

### Frontend Prompt Utilities

**Location**: `repos/dem2-webui/src/lib/`[^33]

**Available Utilities**:
```typescript
// Domain-specific prompt generators
export const createAllergyPrompt = (allergyName: string) =>
  `I would like to learn more about ${allergyName}`;

export const createSymptomPrompt = (symptomName: string) =>
  `Tell me about ${symptomName} and what might cause it`;

export const createMedicationPrompt = (medicationName: string) =>
  `I want to learn more about ${medicationName}`;
```

**Pattern**: Small, composable functions for UI-triggered prompts

**Files**[^34]:
- `repos/dem2-webui/src/lib/allergy-prompt.ts`
- `repos/dem2-webui/src/lib/symptom-prompt.ts`
- `repos/dem2-webui/src/lib/condition-prompt.ts`
- `repos/dem2-webui/src/lib/medication-prompt.ts`
- `repos/dem2-webui/src/lib/supplement-prompt.ts`
- `repos/dem2-webui/src/lib/health-indicator-prompt.ts`
- `repos/dem2-webui/src/lib/hello-prompt.ts`
- `repos/dem2-webui/src/lib/document-reference-prompt.ts`
- `repos/dem2-webui/src/lib/intake-regimen-prompt.ts`

### Document Processing Prompts

**Location**: `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/`[^35]

**Agent Prompt Files**:
- `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/metadata/prompts/extract_metadata.md`
- `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/generic/prompts/generic.md`
- `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/normalizer/prompts/normalizer.md`
- `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/reference_range/prompts/enrich.md`

**Agent Prompts**:

**1. Metadata Agent**: Extract document metadata
```yaml
# Extract:
- document_date
- author
- facility
- document_type
```

**2. Generic Agent**: Unstructured content extraction

**3. Normalizer Agent**: Standardize extracted values
```yaml
# Normalization rules:
- Unit conversion (mg/dL, mmol/L)
- Date format standardization
- Name canonicalization
```

**4. Reference Range Agent**: Match lab values to ranges
```yaml
# Output:
- reference_range: "70-100 mg/dL"
- interpretation: "normal" | "high" | "low" | "critical"
```

### Medical Catalog Prompts

**Location**: `repos/medical-catalog/src/biomarkers/llm_agents/`[^36]

**Phase 1: Categorization**[^37]
```markdown
# Prompt: repos/medical-catalog/src/biomarkers/llm_agents/phase1_categorizer/prompt.md

Determine if entry is a biomarker and categorize it.

Output:
- is_biomarker: boolean
- canonical_name: string
- categories: list[str]
- primary_category: str
- is_derivative: boolean
- confidence: float (0.0-1.0)
```

**Phase 2: Enrichment**[^38]
```markdown
# Prompt: repos/medical-catalog/src/biomarkers/llm_agents/phase2_enricher/prompt.md

Enrich biomarker with detailed information:
- Medical context and significance
- Related conditions
- Testing methodology
- Reference ranges
- Clinical interpretation
```

**Phase 3: Description Generation**[^39]
```markdown
# Prompt: repos/medical-catalog/src/biomarkers/llm_agents/phase3_describer/prompt.md

Generate patient-friendly descriptions:
- Plain language explanation
- Why this biomarker matters
- What abnormal values might indicate
```

---

## Structured Output Prompting

### Pydantic Schema Integration

**Pattern**: Define output structure with Pydantic, inject into prompt

**Example: DataExtractor**:
```python
from pydantic import BaseModel

class ExtractUserQueryResources(BaseModel):
    operations: list[Operation]
    resources: list[Resource]

# In agent config:
generate_config:
  response_schema: ExtractUserQueryResources
```

**Prompt Guidance**:
```yaml
instruction: |
  Output format:
  {
    "operations": [
      {
        "operation_type": "create",
        "resource_type": "observation",
        "attributes": {
          "name": "Blood Glucose",
          "value_numeric": 95.0,
          "unit": "mg/dL"
        }
      }
    ]
  }
```

### Output Schema Examples

**GoogleSearchResult**[^40]:
```python
class SearchResult(BaseModel):
    header: str              # Page title
    link: str                # Full URL
    explanation: str         # Relevance (1-2 sentences)

class GoogleSearchResult(BaseModel):
    urls: list[SearchResult]
```

**VideoInsightsResult**[^41]:
```python
class VideoInsight(BaseModel):
    timestamp: str           # "HH:MM:SS"
    headline: str            # Brief headline
    detail: str              # Detailed explanation
    body_systems: list[str]  # Related systems

class VideoInsightsResult(BaseModel):
    metadata: VideoMetadata
    summaries: list[str]
    insights: list[VideoInsight]
    follow_up_questions: list[str]
```

**DataEntryResult**[^42]:
```python
class DataEntryResult(BaseModel):
    status: str                      # 'success' | 'failure'
    saved_resources: list[str]       # FHIR resource types
    extracted_symptoms: list[str]
    extracted_allergies: list[str]
```

---

## Context Injection Patterns

### User/Patient Profile Context

**Conditional Injection**:
```python
context = {}

# Only inject if profile exists
if user_profile:
    context["user_profile"] = json.dumps(user_profile, indent=2)

if patient_profile:
    context["patient_profile"] = json.dumps(patient_profile, indent=2)

# Boolean flag
context["user_is_patient"] = str(user_id == patient_id).lower()

prompt = render_template(config.instruction, context=context)
```

**Prompt Usage**:
```yaml
instruction: |
  # Context
  {user_profile?}
  {patient_profile?}

  # Relationship
  User is patient: {user_is_patient?}

  # Adapt language based on relationship
  If user_is_patient == true:
    Use "you" and "your"
  If user_is_patient == false:
    Use patient's name and "their"
```

### Recent Health Data Context

**Dynamic Data Injection**:
```python
# Query recent observations
recent_obs = query_recent_observations(patient_id, days=30)

# Format for prompt
obs_text = "\n".join([
    f"- {obs.name}: {obs.value} {obs.unit} ({obs.observed_at})"
    for obs in recent_obs
])

context["recent_observations"] = obs_text
```

**Prompt Usage**:
```yaml
instruction: |
  # Recent Observations (last 30 days)
  {recent_observations?}

  Use this context to answer questions about recent trends.
```

### Graph Schema Context

**Schema Loading**:
```python
# Load available node types from Neo4j
graph_nodes = [
    "PatientNode",
    "ObservationValueNode",
    "ConditionCaseNode",
    "MedicationNode",
    "SymptomNode",
    "AllergyNode",
    "EncounterNode",
    # ... more types
]

graph_nodes_text = "\n".join(f"- {node}" for node in graph_nodes)
context["graph_nodes"] = graph_nodes_text
```

**Prompt Usage**:
```yaml
instruction: |
  # Available Graph Nodes
  {graph_nodes}

  When generating Cypher queries, use these node types.
```

---

## Multi-Agent Prompt Coordination

### Agent-as-Tool Pattern

**Nested Agent Instructions**:
```yaml
# TriageAgent prompt
instruction: |
  You have access to these specialized agents:

  1. URLHandlerAgent
     - Use for: Any URL (web pages, YouTube videos)
     - Input: URL string
     - Output: Extracted content and insights

  2. HealthConsultantAgent
     - Use for: Health questions and consultations
     - Input: User question
     - Output: Comprehensive medical response

  ALWAYS call the appropriate agent, don't try to answer directly.
```

**Tool Use Guidance**:
```yaml
  # When to Use Each Agent

  URL in message:
    → URLHandlerAgent FIRST
    → Then process results

  Health question:
    → HealthConsultantAgent
    → Return their response

  New health information:
    → DataExtractorAgent
    → Acknowledge saved data
```

### State Preservation Across Agents

**SafeAgentTool Pattern**[^43]:
```python
consultant_tool = SafeAgentTool(
    agent=health_consultant_agent,
    result_state_key="consultant_result",
    status_state_key="consultant_status",
    error_state_key="consultant_error",
)

# State available to parent agent
if callback_context.state.get("consultant_status") == "success":
    result = callback_context.state["consultant_result"]
```

**Prompt Access to State**:
```yaml
instruction: |
  # Previous Agent Results
  {consultant_result?}

  If consultant result is available, use it in your response.
```

### Parallel Agent Coordination

**DataExtractor Parallel Pattern**:
```yaml
# Two agents run in parallel:

MedicalMeasurementsAgent:
  - Extract: observations, symptoms, conditions, allergies
  - Focus: Clinical measurements

MedicalContextAgent:
  - Extract: practitioners, organizations, encounters, regimens
  - Focus: Context and relationships

# Results merged by parent ParallelDataExtractor
```

**Prompt Design for Parallel Agents**:
```yaml
# Each agent has focused, non-overlapping instructions
MedicalMeasurementsAgent instruction: |
  Extract ONLY clinical measurements. DO NOT extract:
  - Practitioner names
  - Organization names
  - Encounter details

MedicalContextAgent instruction: |
  Extract ONLY contextual information. DO NOT extract:
  - Symptoms
  - Observations
  - Conditions
```

---

## Model Configuration

### Model Selection Matrix

| Agent | Model | Rationale |
|-------|-------|-----------|
| TriageAgent | gemini-2.5-flash[^44] | Fast routing, low latency |
| HealthConsultantAgent | gemini-2.5-pro[^45] | Complex reasoning, large context |
| DataExtractorAgent | gemini-2.5-pro[^46] | Accurate structured extraction |
| GoogleSearchAgent | gemini-2.5-pro[^47] | Relevance assessment |
| FastGraphSummaryAgent | gemini-2.5-flash[^48] | Sub-second simple queries |
| All Other Agents | gemini-2.5-pro[^49] | Default for reliability |

### Generate Content Configuration

**Standard Config**[^50]:
```yaml
generate_config:
  temperature: 0.1                    # Low for deterministic outputs
  max_output_tokens: 512              # Varies by agent (512-2000)
  tool_config:
    function_calling_config:
      mode: AUTO                      # Auto-detect tool use
```

**Temperature Guidelines**:
```yaml
0.0:    # Deterministic (data extraction, structured outputs)
0.1:    # Slightly variable (consultations, natural responses)
0.7+:   # Creative (NOT used for medical applications)
```

**Token Limits by Agent**:
```yaml
TriageAgent: 512 tokens              # Short routing decisions
DataExtractorAgent: 1000 tokens      # Structured JSON output
HealthConsultantAgent: 2000 tokens   # Comprehensive responses
GoogleSearchAgent: 512 tokens        # URL list with descriptions
```

---

## Cost Management

### Rate Limiting

**Configuration**[^51]:
```python
# LLM Proxy settings
rate_limit_per_minute = 60           # Default
max_concurrent_requests = 10
```

**Per-Service Overrides**:
```yaml
# Service-specific config
llm_proxy:
  rate_limit_per_minute: 120         # Higher for critical services
  max_concurrent_requests: 20
```

### Token Tracking

**Cost Calculation**[^52]:
```python
def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> float:
    input_cost = input_tokens * model.input_price_per_token
    output_cost = output_tokens * model.output_price_per_token

    # Anthropic caching costs
    cache_read_cost = cache_read_tokens * (model.input_price_per_token * 0.10)
    cache_write_cost = cache_creation_tokens * (model.input_price_per_token * 1.25)

    return input_cost + output_cost + cache_read_cost + cache_write_cost
```

### Streaming Optimization

**Auto-Streaming**[^53]:
```python
# Enable streaming for large outputs
if expected_output_tokens > 16000:
    enable_streaming = True
```

**Benefits**:
- Reduced latency for first token
- Better user experience for long responses
- Lower memory usage

### Model Cost Comparison

**Per Million Tokens** (as of 2026-01-06)[^54]:

| Model | Input | Output | Cache Read | Cache Write |
|-------|-------|--------|------------|-------------|
| Gemini 2.5 Flash | $0.15 | $0.60 | N/A | N/A |
| Gemini 2.5 Pro | $1.25 | $10.00 | N/A | N/A |
| Claude 4.5 Haiku | $1.00 | $5.00 | $0.10 | $1.25 |
| Claude 4.5 Sonnet | $3.00 | $15.00 | $0.30 | $3.75 |
| Claude 4.5 Opus | $15.00 | $75.00 | $1.50 | $18.75 |

---

## Prompt Versioning and Testing

### Version Control Strategy

**Multiple Versions per Agent**[^55]:
```
HealthConsultantAgent/
├── config.yml        # Current production (Gemini 2.5)
├── config_3.yml      # Gemini 3.0 preview
└── config_4.yml      # Future Gemini 4.0
```

**Version Selection**:
```python
def load_agent_config(agent_name: str, version: str = "default") -> AgentConfig:
    if version == "default":
        config_path = f"{agent_name}/config.yml"
    else:
        config_path = f"{agent_name}/config_{version}.yml"

    return load_yaml(config_path)
```

### Prompt Testing

**Unit Testing Pattern**:
```python
import pytest
from machina.medical_agent.agents import TriageAgent

def test_triage_url_handling():
    """Test TriageAgent routes URLs to URLHandlerAgent."""
    agent = TriageAgent()

    request = "Check out this video: https://youtube.com/watch?v=abc123"
    response = agent.run(request)

    # Assert URLHandlerAgent was called
    assert "url_handler_tool" in response.tool_calls
    assert response.tool_calls["url_handler_tool"].status == "success"

def test_triage_consultation_routing():
    """Test TriageAgent routes consultations to HealthConsultantAgent."""
    agent = TriageAgent()

    request = "What's my blood pressure?"
    response = agent.run(request)

    # Assert HealthConsultantAgent was called
    assert "consultant_full_tool" in response.tool_calls
```

**Integration Testing**:
```python
def test_end_to_end_consultation():
    """Test full consultation flow."""
    triage = TriageAgent()

    request = "I have a headache and fever. What should I do?"
    response = triage.run(request)

    # Verify response quality
    assert "headache" in response.text.lower()
    assert "fever" in response.text.lower()
    assert len(response.text) > 100  # Comprehensive response
```

### A/B Testing Prompts

**Pattern**:
```python
# Version A: Current prompt
agent_a = HealthConsultantAgent(config="config.yml")

# Version B: Experimental prompt
agent_b = HealthConsultantAgent(config="config_experimental.yml")

# Random assignment
if random.random() < 0.5:
    agent = agent_a
    version = "A"
else:
    agent = agent_b
    version = "B"

# Track metrics
track_prompt_version(
    agent_name="HealthConsultantAgent",
    version=version,
    response_time=response.duration,
    token_count=response.usage.total_tokens,
    user_satisfaction=get_user_feedback(),
)
```

### Prompt Quality Metrics

**Automated Evaluation**:
```python
def evaluate_prompt_quality(agent: LlmAgent, test_cases: list[TestCase]):
    metrics = {
        "accuracy": 0.0,
        "token_efficiency": 0.0,
        "response_time": 0.0,
        "tool_use_correctness": 0.0,
    }

    for test_case in test_cases:
        response = agent.run(test_case.input)

        # Evaluate
        metrics["accuracy"] += calculate_accuracy(response, test_case.expected)
        metrics["token_efficiency"] += response.usage.total_tokens / test_case.optimal_tokens
        metrics["response_time"] += response.duration
        metrics["tool_use_correctness"] += evaluate_tool_calls(response, test_case.expected_tools)

    # Average across test cases
    for key in metrics:
        metrics[key] /= len(test_cases)

    return metrics
```

---

## Citations

[^1]: **Multi-Provider Support** - Three provider implementations; Verify: `ls repos/medical-catalog/src/llm/providers/*.py | wc -l`

[^2]: **Template Rendering** - Render template function for context injection; Verify: `grep 'def render_template' repos/dem2/services/medical-agent/src/machina/medical_agent/common/configurator.py`

[^3]: **Config Versions** - Multiple config versions per agent; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config*.yml | wc -l`

[^4]: **Rate Limiting** - 60 requests per minute default; Verify: `grep 'rate_limit_per_minute.*60' repos/medical-catalog/src/llm/proxy.py`

[^5]: **Pydantic Schemas** - ExtractUserQueryResources schema; Verify: `grep 'class ExtractUserQueryResources' repos/dem2/services/medical-agent/src/machina/medical_agent/schemas.py`

[^6]: **Google ADK Import** - Google ADK agents module; Verify: `grep 'from google.adk.agents import' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`

[^7]: **TriageAgent Model** - Uses gemini-2.5-flash; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml`

[^8]: **Primary Model** - gemini-2.5-pro for most agents; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml`

[^9]: **Preview Model** - gemini-3.0-pro-preview; Verify: `grep 'gemini-3.0-pro-preview' repos/medical-catalog/src/llm/models.py`

[^10]: **Retry Policy** - 3 attempts; Verify: `grep 'HttpRetryOptions(attempts=3)' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`

[^11]: **Claude Models** - Claude pricing in models.py; Verify: `grep 'claude-4-5' repos/medical-catalog/src/llm/models.py`

[^12]: **DocProc LLM** - Document processing LLM integration; Verify: `ls -d repos/dem2/services/docproc/src/machina/docproc/llm/`

[^13]: **Anthropic Provider** - Anthropic in medical-catalog; Verify: `ls repos/medical-catalog/src/llm/providers/anthropic.py`

[^14]: **LLM Proxy** - Unified proxy class; Verify: `grep 'class LLMProxy' repos/medical-catalog/src/llm/proxy.py`

[^15]: **Streaming Threshold** - 16,000 tokens; Verify: `grep '16000' repos/medical-catalog/src/llm/proxy.py`

[^16]: **Dem2 Proxy** - Proxy in docproc; Verify: `ls repos/dem2/services/docproc/src/machina/docproc/llm/proxy.py`

[^17]: **Catalog Proxy** - Proxy in medical-catalog; Verify: `ls repos/medical-catalog/src/llm/proxy.py`

[^18]: **Temperature Config** - Low temperature in generate_config; Verify: `yq -r '.generate_config.temperature' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/DataExtractorAgent/config.yml`

[^19]: **Current Time** - Time injection callback; Verify: `grep '_update_time' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`

[^20]: **TriageAgent Lines** - Config line count; Verify: `wc -l repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml`

[^21]: **HealthConsultant Lines** - Config line count; Verify: `wc -l repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml`

[^22]: **YAML Configs** - Agent configs in YAML; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml | wc -l`

[^23]: **Global Config** - Global configuration file; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/global_config.yml`

[^24]: **TriageAgent Config** - Config exists; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml`

[^25]: **HealthConsultant Config** - Config exists; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml`

[^26]: **DataExtractor Config** - Config exists; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/DataExtractorAgent/config.yml`

[^27]: **TriageAgent Prompt Length** - 157 lines; Verify: `wc -l repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml`

[^28]: **Fast Summary** - Fast summary callback; Verify: `grep '_fast_summary_after_agent_callback' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`

[^29]: **HealthConsultant Prompt Length** - 184 lines; Verify: `wc -l repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml`

[^30]: **DataExtractor Prompt** - Instruction section; Verify: `yq -r '.instruction' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/DataExtractorAgent/config.yml | head -1`

[^31]: **GoogleSearch Prompt** - Instruction section; Verify: `yq -r '.instruction' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/GoogleSearchAgent/config.yml | head -1`

[^32]: **Update Time Callback** - Time injection function; Verify: `grep 'def _update_time' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`

[^33]: **Frontend Prompts** - Prompt utility files; Verify: `ls repos/dem2-webui/src/lib/*-prompt.ts | head -1`

[^34]: **Prompt Files** - Multiple prompt utilities; Verify: `ls repos/dem2-webui/src/lib/*-prompt.ts | wc -l`

[^35]: **DocProc Prompts** - Agent prompts directory; Verify: `ls -d repos/dem2/services/docproc/src/machina/docproc/extractor/agents/`

[^36]: **Catalog Agents** - LLM agents directory; Verify: `ls -d repos/medical-catalog/src/biomarkers/llm_agents/`

[^37]: **Phase1 Categorizer** - Categorization agent; Verify: `ls -d repos/medical-catalog/src/biomarkers/llm_agents/phase1_categorizer/`

[^38]: **Phase2 Enricher** - Enrichment agent; Verify: `ls -d repos/medical-catalog/src/biomarkers/llm_agents/phase2_enricher/`

[^39]: **Phase3 Describer** - Description agent; Verify: `ls -d repos/medical-catalog/src/biomarkers/llm_agents/phase3_describer/`

[^40]: **GoogleSearchResult** - Search result schema; Verify: `grep 'class GoogleSearchResult' repos/dem2/services/medical-agent/src/machina/medical_agent/schemas.py`

[^41]: **VideoInsightsResult** - Video insights schema; Verify: `grep 'class VideoInsightsResult' repos/dem2/services/medical-agent/src/machina/medical_agent/agent_tools/video_insights_tool.py`

[^42]: **DataEntryResult** - Data entry result schema; Verify: `grep 'class DataEntryResult' repos/dem2/services/medical-agent/src/machina/medical_agent/schemas.py`

[^43]: **SafeAgentTool** - Safe tool wrapper; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agent_tools/safe_agent_tool.py`

[^44]: **Triage Flash** - TriageAgent uses flash; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml`

[^45]: **Consultant Pro** - HealthConsultant uses pro; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml`

[^46]: **Extractor Pro** - DataExtractor uses pro; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/DataExtractorAgent/config.yml`

[^47]: **Search Pro** - GoogleSearch uses pro; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/GoogleSearchAgent/config.yml`

[^48]: **Fast Summary Flash** - Fast summary uses flash; Verify: `grep 'gemini-2.5-flash' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`

[^49]: **Default Pro** - Default model is pro; Verify: `yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/DataEntryAgent/config.yml`

[^50]: **Generate Config** - Standard generation config; Verify: `yq -r '.generate_config' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config.yml`

[^51]: **Rate Limit Config** - Default rate limit; Verify: `grep 'rate_limit_per_minute' repos/medical-catalog/src/llm/proxy.py`

[^52]: **Cost Calculation** - Calculate cost method; Verify: `grep 'def calculate_cost' repos/medical-catalog/src/llm/models.py`

[^53]: **Streaming Threshold** - 16000 token threshold; Verify: `grep '16000' repos/medical-catalog/src/llm/proxy.py`

[^54]: **Model Pricing** - Pricing in models.py; Verify: `grep 'input_price\|output_price' repos/medical-catalog/src/llm/models.py | head -1`

[^55]: **Config Versions** - Multiple versions exist; Verify: `ls repos/dem2/services/medical-agent/src/machina/medical_agent/agents/HealthConsultantAgent/config*.yml`
