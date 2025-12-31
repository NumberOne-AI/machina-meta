# OpenAPI, MCP, Agents, and ADK: Understanding the Relationships

> **Purpose**: This document explains how OpenAPI, MCP (Model Context Protocol), AI agents, and Google ADK interrelate, with conceptual guidance for potential MachinaMed architecture decisions.

**Status**: Conceptual Reference (Unverified Integration Patterns)
**Last Updated**: 2025-12-31
**Audience**: Developers, architects, AI engineers

## ⚠️ IMPORTANT: Verification Status

**What is VERIFIED:**
- ✅ OpenAPI, MCP, ADK concepts and definitions
- ✅ MachinaMed's current architecture (Google ADK with 126 OpenAPI endpoints)
- ✅ MCP protocol specifications (from official documentation)

**What is UNVERIFIED:**
- ❌ Integration patterns (code examples are hypothetical, not tested)
- ❌ MCP SDK compatibility with Google ADK (not verified in practice)
- ❌ MCP ecosystem value for medical domain (requires survey)
- ❌ Performance characteristics of proposed integrations

**Before implementing any pattern in this document:**
1. Verify the code examples actually work
2. Test compatibility between MCP SDK and Google ADK
3. Survey MCP ecosystem for valuable medical tools
4. Prototype and measure performance

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Core Concepts](#core-concepts)
3. [Detailed Comparisons](#detailed-comparisons)
4. [Integration Patterns](#integration-patterns)
5. [MachinaMed Recommendations](#machinamed-recommendations)
6. [FAQ](#faq)

---

## Quick Reference

| Technology | Type | Purpose | MachinaMed Usage |
|------------|------|---------|------------------|
| **OpenAPI** | REST API Specification | Define HTTP endpoints | ✅ Current backend (126 routes) |
| **MCP** | Tool Protocol | Standardize tool access | ⭐ Potential for external tools |
| **Agents** | AI Systems | Reasoning + tool use | ✅ Google ADK agents (23 agents) |
| **Google ADK** | Agent Framework | Multi-agent orchestration | ✅ Core architecture |

---

## Core Concepts

### 1. OpenAPI (REST API Specification)

**What it is:**
- Industry standard for describing HTTP REST APIs
- JSON/YAML format defining endpoints, parameters, responses
- Used by FastAPI to auto-generate documentation

**Example:**
```yaml
# OpenAPI spec excerpt
/api/v1/patients:
  get:
    summary: List patients
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
    responses:
      200:
        description: List of patients
        content:
          application/json:
            schema:
              type: array
```

**MachinaMed Usage:**
- Backend: `http://localhost:8000/api/v1/*` (126 endpoints)
- Auto-generated docs: `http://localhost:8000/docs`
- Frontend calls these HTTP endpoints

**Key Characteristics:**
- ✅ HTTP-based (standard web protocol)
- ✅ Language-agnostic (any HTTP client)
- ✅ Well-established ecosystem
- ✅ Works with API gateways, load balancers
- ❌ Not specifically designed for AI tools

---

### 2. MCP (Model Context Protocol)

**What it is:**
- Open standard created by Anthropic (2024)
- Protocol for AI assistants to access tools and data
- Defines how to expose and call tools

**Architecture:**
```
┌─────────────┐
│  MCP Client │  (Any LLM: Claude, GPT, Gemini)
└──────┬──────┘
       │ MCP Protocol
       │ (stdio/SSE/HTTP)
       ▼
┌─────────────┐
│ MCP Server  │  (Tool Provider)
│  - Tools    │  (Functions to call)
│  - Resources│  (Data to access)
│  - Prompts  │  (Templates to use)
└─────────────┘
```

**Tool Definition Example:**
```json
{
  "name": "query_patient_graph",
  "description": "Query patient medical data using natural language",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language query"
      },
      "patient_id": {
        "type": "string",
        "description": "Patient identifier"
      }
    },
    "required": ["query", "patient_id"]
  }
}
```

**Transport Options:**
- **stdio**: Standard input/output (local processes)
- **SSE**: Server-Sent Events (HTTP streaming)
- **HTTP**: Streamable HTTP

**MachinaMed Potential:**
- ⭐ Integrate external MCP tools (medical calculators, drug databases)
- ⭐ Expose MachinaMed to Claude Desktop users

**Key Characteristics:**
- ✅ Designed for AI tool calling
- ✅ Open standard (vendor-neutral)
- ✅ Growing ecosystem (50+ community tools)
- ✅ Works with any LLM
- ❌ New (launched Q4 2024)
- ❌ Smaller ecosystem than HTTP/REST

---

### 3. AI Agents

**What they are:**
- AI systems that reason, plan, and use tools to accomplish tasks
- Combine LLM reasoning with ability to take actions
- Can be simple (single-purpose) or complex (multi-agent systems)

**Conceptual Model:**
```
User Request
    ↓
┌──────────────────────────┐
│      AI Agent            │
│                          │
│  1. Understand request   │
│  2. Plan approach        │
│  3. Use tools            │ ──→ Tools (MCP, HTTP, native)
│  4. Synthesize result    │
│  5. Respond to user      │
└──────────────────────────┘
```

**Agent Capabilities:**
- **Reasoning**: Understand complex queries
- **Planning**: Break tasks into steps
- **Tool Use**: Call functions to get data or perform actions
- **Learning**: Improve from feedback (in some systems)

**MachinaMed Agents:**
```
TriageAgent (router)
    ↓
HealthConsultantAgent (medical reasoning)
    ↓ Uses tools:
    ├─ query_graph (graph queries)
    ├─ CypherAgent (NL → Cypher)
    ├─ GoogleSearchAgent (research)
    └─ save_resources (data persistence)
```

**Key Characteristics:**
- ✅ High-level reasoning capabilities
- ✅ Can orchestrate multiple tools
- ✅ Natural language understanding
- ✅ Context-aware decisions
- ❌ Requires tool infrastructure
- ❌ More complex than simple API calls

---

### 4. Google ADK (Agent Development Kit)

**What it is:**
- Python framework for building production-grade agent systems
- Developed by Google, optimized for Gemini models
- Provides orchestration, state management, tool execution

**Architecture:**
```
┌─────────────────────────────────────────────┐
│         Google ADK Application              │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │     Agent Orchestration               │  │
│  │  - Multi-agent coordination           │  │
│  │  - Routing (TriageAgent pattern)      │  │
│  │  - Sub-agent composition              │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│  ┌───────────────▼───────────────────────┐  │
│  │      State Management                 │  │
│  │  - Session persistence                │  │
│  │  - Conversation history               │  │
│  │  - User/patient context               │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│  ┌───────────────▼───────────────────────┐  │
│  │        Tool Execution                 │  │
│  │  - Tool calling                       │  │
│  │  - Context injection                  │  │
│  │  - Error handling & retries           │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│  ┌───────────────▼───────────────────────┐  │
│  │      LLM Integration                  │  │
│  │  - Gemini API                         │  │
│  │  - Prompt management                  │  │
│  │  - Response streaming                 │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Agent Definition Example:**
```yaml
# HealthConsultantAgent config
name: HealthConsultantAgent
model: gemini-2.5-pro
description: Provides personalized health consultations

tools:
  - name: query_graph
    description: Query patient medical data
  - agent: CypherAgent
  - agent: GoogleSearchAgent

state:
  - user_id
  - patient_id
  - conversation_history
```

**MachinaMed Usage:**
- ✅ Core architecture (23 agents)
- ✅ Production-ready orchestration
- ✅ Complex multi-agent workflows
- ✅ FHIR-compliant medical reasoning

**Key Characteristics:**
- ✅ Full framework (batteries included)
- ✅ Production-ready (error handling, monitoring)
- ✅ Multi-agent support (agent composition)
- ✅ State management (sessions, history)
- ✅ Gemini-optimized
- ❌ Python-only
- ❌ Google Cloud dependency
- ❌ Proprietary (not open standard)

---

## Detailed Comparisons

### OpenAPI vs MCP

| Aspect | OpenAPI | MCP |
|--------|---------|-----|
| **Purpose** | Define REST APIs | Define AI tool interfaces |
| **Protocol** | HTTP REST | stdio/SSE/HTTP |
| **Audience** | Web developers | AI developers |
| **Ecosystem** | Massive (20+ years) | Growing (1 year) |
| **Use Case** | General APIs | AI tool calling |
| **Interoperability** | High (HTTP standard) | Medium (newer standard) |
| **AI Integration** | Manual | Native |

**Can they work together?** ✅ Yes!

**Pattern 1: MCP Server wraps OpenAPI**
```python
# Expose OpenAPI endpoints as MCP tools
from mcp.server import Server
import httpx

server = Server("machina-medical")

@server.call_tool()
async def call_tool(name, arguments):
    # Call MachinaMed OpenAPI endpoint
    response = await httpx.post(
        f"http://localhost:8000/api/v1/{name}",
        json=arguments
    )
    return response.json()
```

**Result:** Claude Desktop can now call MachinaMed's OpenAPI endpoints!

---

### Agents vs Tools

| Aspect | Agents | Tools |
|--------|--------|-------|
| **Role** | Decision maker | Action executor |
| **Intelligence** | High (LLM-powered) | None (deterministic) |
| **Autonomy** | Plans multi-step tasks | Executes single action |
| **Example** | HealthConsultantAgent | query_graph function |

**Relationship:**
```
Agent (Brain)
  ↓ decides to use
Tool (Hands)
  ↓ performs
Action (Result)
```

**Analogy:**
- **Agent** = Doctor (diagnoses, plans treatment)
- **Tools** = Medical instruments (stethoscope, X-ray machine)
- **MCP** = Standard interface for instruments

---

### Google ADK vs MCP

| Aspect | Google ADK | MCP |
|--------|-----------|-----|
| **Type** | Agent framework | Tool protocol |
| **Scope** | Full system | Tool layer only |
| **Orchestration** | ✅ Multi-agent | ❌ Client handles |
| **State** | ✅ Sessions, history | ❌ Stateless |
| **Language** | Python only | Any |
| **Vendor** | Google | Anthropic (open) |
| **Maturity** | Production | Early adoption |

**Are they competitive?** ❌ No - different layers!

**Complementary relationship:**
```
┌──────────────────────────────────┐
│       Google ADK (Layer 1)       │  ← Agent orchestration
│  - Multi-agent coordination      │
│  - State management              │
│  - Session persistence           │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│        Tools (Layer 2)           │  ← Tool execution
│  - Native ADK tools              │
│  - MCP tools (via SDK)           │ ← MCP integration here!
│  - HTTP APIs                     │
└──────────────────────────────────┘
```

**Key Insight:** ADK handles ORCHESTRATION, MCP handles TOOL INTERFACES.

You can use both together!

---

## Integration Patterns

⚠️ **WARNING: All patterns below are HYPOTHETICAL and UNTESTED.**

These examples demonstrate potential integration approaches but have NOT been verified to work in practice. Before implementing:
1. Test MCP SDK compatibility with Google ADK's async patterns
2. Verify subprocess management works with ADK agent lifecycle
3. Measure performance impact
4. Test error handling and edge cases

### Pattern 1: ADK Agents Use MCP Tools (HYPOTHETICAL)

**Use Case:** Integrate external MCP ecosystem tools into MachinaMed agents

**Status:** ❌ Unverified - Code example not tested

**Assumptions:**
- MCP SDK works with Google ADK's async/await patterns
- stdio subprocess management compatible with ADK agent lifecycle
- Performance overhead is acceptable
- Error handling integrates with ADK's SafeAgentTool pattern

```python
# repos/dem2/services/medical-agent/mcp_tools.py

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from google.adk.tools import ToolContext

class MCPToolWrapper:
    """Wraps external MCP tools for Google ADK agents."""

    def __init__(self, command: str, args: list[str]):
        self.command = command
        self.args = args

    async def call_tool(self, tool_name: str, arguments: dict):
        """Call MCP tool via stdio."""
        async with stdio_client(StdioServerParameters(
            command=self.command,
            args=self.args
        )) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.call_tool(tool_name, arguments)
                return result

# Define ADK tool that uses MCP
@agent_tool(name="medical_calculator")
async def medical_calculator(
    operation: str,
    tool_context: ToolContext,
    **params
) -> dict:
    """Medical calculator using external MCP tool.

    Args:
        operation: Calculation type (bmi, egfr, ascvd_risk, etc.)
        **params: Parameters for the calculation

    Returns:
        Calculation result
    """
    mcp_calc = MCPToolWrapper(
        command="uvx",
        args=["mcp-server-medical-calc"]
    )
    return await mcp_calc.call_tool(operation, params)

# Add to HealthConsultantAgent
tools = [
    query_graph,          # Native ADK tool
    medical_calculator,   # External MCP tool
    GoogleSearchAgent(),  # ADK sub-agent
]
```

**Benefits:**
- ✅ Access MCP ecosystem tools
- ✅ Keep ADK orchestration
- ✅ No HTTP overhead (direct stdio)
- ✅ Simple integration

---

### Pattern 2: Expose ADK Agents via MCP (HYPOTHETICAL)

**Use Case:** Make MachinaMed accessible to Claude Desktop, Claude Code, and other MCP clients

**Status:** ❌ Unverified - Code example not tested

**Assumptions:**
- MCP Server can handle async HTTP calls to MachinaMed API
- Authentication/authorization can be properly forwarded
- Latency overhead is acceptable for user experience
- MachinaMed API responses can be converted to MCP tool responses

```python
# repos/dem2/services/mcp-server/machina_mcp_server.py

from mcp.server import Server
import httpx

server = Server("machina-medical")

@server.list_tools()
async def list_tools():
    """Expose MachinaMed capabilities as MCP tools."""
    return [
        {
            "name": "ask_medical_question",
            "description": "Ask a medical question about patient data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "patient_id": {"type": "string"}
                },
                "required": ["question", "patient_id"]
            }
        },
        {
            "name": "analyze_lab_results",
            "description": "Analyze patient lab results",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "loinc_codes": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["patient_id"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name, arguments):
    """Call MachinaMed agents via HTTP API."""

    if name == "ask_medical_question":
        # Call MachinaMed agent endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/med-agent/run_sse",
                json={
                    "message": arguments["question"],
                    "session_id": f"mcp-{arguments['patient_id']}",
                    "app_name": "main_chat"
                },
                headers={
                    "X-Patient-Context-ID": arguments["patient_id"]
                }
            )
            return response.json()

    # ... other tools
```

**Usage in Claude Desktop:**
```json
// ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "machina-medical": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "machina.mcp_server.machina_mcp_server"
      ]
    }
  }
}
```

**Benefits:**
- ✅ Claude Desktop users can access MachinaMed
- ✅ Claude Code integration for developers
- ✅ Standard MCP interface
- ✅ No changes to core ADK architecture

---

### Pattern 3: Hybrid Architecture (HYPOTHETICAL - Conceptual Only)

**Use Case:** Production MachinaMed with both MCP integration and exposure

**Status:** ❌ Unverified - Architectural concept not validated

**Assumptions:**
- Patterns 1 and 2 are both technically feasible (not yet verified)
- Performance overhead of dual integration is acceptable
- Maintenance complexity is manageable
- Security implications are addressed

```
┌──────────────────────────────────────────────────┐
│           MachinaMed (Google ADK)                │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │      HealthConsultantAgent                 │  │
│  │      (Orchestration via ADK)               │  │
│  └────────┬───────────────────────────────────┘  │
│           │                                      │
│  ┌────────▼─────────────────────────────────┐   │
│  │             Tools                        │   │
│  │                                          │   │
│  │  Native ADK:          External MCP:     │   │
│  │  - query_graph        - medical_calc    │   │
│  │  - save_resources     - drug_checker    │   │
│  │  - CypherAgent        - guidelines      │   │
│  │  - GoogleSearchAgent                    │   │
│  └──────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────┘
                   │
                   │ Also exposed via MCP
                   ▼
            ┌──────────────┐
            │   MCP Server │
            └──────┬───────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
  ┌──────────┐        ┌──────────────┐
  │  Claude  │        │  Claude Code │
  │ Desktop  │        │  (Devtools)  │
  └──────────┘        └──────────────┘
```

**Implementation:**
- Core: Google ADK with 23 agents
- Tools: Mix of native ADK + external MCP
- Exposure: Optional MCP server for external access

**Benefits:**
- ✅ Best of all worlds
- ✅ ADK production reliability
- ✅ MCP ecosystem access
- ✅ External accessibility
- ✅ Flexibility to expand

---

## MachinaMed Recommendations

### Current State (VERIFIED)
- ✅ Google ADK with 23 agents (production-ready)
- ✅ 126 OpenAPI endpoints
- ✅ Complex multi-agent orchestration
- ❌ No MCP integration

### ⚠️ BEFORE ANY MCP INTEGRATION: Verification Required

**Critical validation steps (MUST complete before proceeding):**

1. **Verify Technical Feasibility** (4-8 hours)
   - [ ] Test MCP SDK installation and basic usage
   - [ ] Verify MCP SDK async patterns work with Google ADK
   - [ ] Test subprocess lifecycle management
   - [ ] Prototype minimal integration (hello-world level)
   - [ ] Document any compatibility issues discovered

2. **Survey MCP Ecosystem** (4-8 hours)
   - [ ] List all available MCP medical/health tools
   - [ ] Assess quality, maintenance status, documentation
   - [ ] Test 2-3 promising tools locally
   - [ ] Evaluate if ANY provide value over building ourselves
   - [ ] Document findings with specific tool names/repos

3. **Measure Performance** (2-4 hours)
   - [ ] Benchmark MCP tool call overhead
   - [ ] Compare to direct HTTP API calls
   - [ ] Test under realistic load
   - [ ] Verify acceptable latency for consultations

**Decision Point:** Only proceed if ALL three validations show positive results.

---

### IF Validation Passes: Phased Integration Approach

**Only implement these phases AFTER completing validation above!**

#### Phase 1: Minimal Viable Integration
**Goal:** Integrate 1 external MCP tool as proof of concept

**Prerequisites:**
- ✅ Technical feasibility verified
- ✅ At least 1 valuable MCP tool identified
- ✅ Performance acceptable

**Implementation:**
```python
# HYPOTHETICAL - requires verification first!
# Add single MCP tool to HealthConsultantAgent
tools = [
    query_graph,
    save_resources,
    mcp_calculator,  # Single external tool for testing
    CypherAgent(),
]
```

**Success Criteria:**
- Tool works reliably in consultations
- Performance overhead < 100ms per call
- Provides measurable value over alternatives
- No breaking changes to existing workflows

**Effort:** 1-2 weeks (after validation)

---

#### Phase 2: Expand Integration (Optional)
**Goal:** Add 2-3 more valuable tools

**Only proceed if Phase 1 succeeds!**

**Effort:** 1-2 weeks per tool

---

#### Phase 3: Expose via MCP (Optional)
**Goal:** Make MachinaMed accessible to Claude Desktop

**Only proceed if there's demonstrated demand!**

**Effort:** 1-2 weeks

---

### What NOT to Do

❌ **Don't use mcpo** - MachinaMed can use MCP SDK directly (simpler, faster)

❌ **Don't replace Google ADK** - ADK provides critical orchestration and state management

❌ **Don't integrate without verification** - Must complete validation steps first

❌ **Don't assume patterns work** - All integration examples in this doc are unverified

❌ **Don't commit to MCP without evidence** - Verify ecosystem value before investing

---

## FAQ

### Q: Can I use OpenAPI and MCP together?
**A:** Yes! Create MCP server that calls OpenAPI endpoints, or vice versa.

### Q: Should MachinaMed use MCP or OpenAPI?
**A:** Both! OpenAPI for HTTP endpoints (current), MCP for AI tool integration (future).

### Q: Is Google ADK compatible with MCP?
**A:** Yes! ADK agents can call MCP tools, and ADK agents can be exposed via MCP.

### Q: What's the difference between agents and tools?
**A:** Agents make decisions and orchestrate tasks. Tools perform specific actions. Agents use tools.

### Q: Do I need mcpo to integrate MCP?
**A:** No! MachinaMed can use the MCP Python SDK directly for better performance.

### Q: Can Claude Desktop call MachinaMed?
**A:** Yes! Create MCP server that wraps MachinaMed's HTTP API.

### Q: Should I migrate from Google ADK to MCP?
**A:** No! They're complementary. Keep ADK for orchestration, use MCP for tool interfaces.

---

## References

### Documentation
- **MCP Official Docs**: https://modelcontextprotocol.io/
- **OpenAPI Specification**: https://spec.openapis.org/oas/latest.html
- **Google ADK**: (Internal Google documentation)
- **MachinaMed Architecture**: `repos/dem2/CLAUDE.md`

### Related Files
- **MachinaMed Agents**: `repos/dem2/services/medical-agent/`
- **Agent Tools**: `repos/dem2/services/medical-data-storage/src/machina/medical_data_storage/agent_tools.py`
- **API Routes**: `ROUTES.md`

### Code Examples
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP Servers**: https://github.com/modelcontextprotocol/servers

---

## Glossary

- **Agent**: AI system that reasons, plans, and uses tools
- **ADK**: Agent Development Kit (Google's agent framework)
- **MCP**: Model Context Protocol (tool calling standard)
- **OpenAPI**: REST API specification format
- **Tool**: Function an agent can call to perform actions
- **stdio**: Standard input/output (process communication)
- **SSE**: Server-Sent Events (HTTP streaming)

---

**Questions or feedback?** Contact the MachinaMed team or open an issue.
