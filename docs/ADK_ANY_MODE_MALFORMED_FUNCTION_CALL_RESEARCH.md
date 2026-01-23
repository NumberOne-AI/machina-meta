# ADK ANY Mode Research: Fixing MALFORMED_FUNCTION_CALL

**Date:** 2026-01-19
**Purpose:** Research for implementing ANY mode + respond_to_user tool pattern
**Related:** `docs/ADK_MALFORMED_FUNCTION_CALL_REPORT_20260119.md`

---

## Executive Summary

Research indicates that using `FunctionCallingConfigMode.ANY` combined with a "respond to user" tool is a viable approach to fix `MALFORMED_FUNCTION_CALL` errors. ANY mode enables true constrained decoding (unlike VALIDATED which is in Preview), and a respond tool allows agents to still produce natural language responses.

---

## 1. FunctionCallingConfigMode Comparison

| Mode | Constrained Decoding | Forces Function Call | Status | MALFORMED Risk |
|------|---------------------|---------------------|--------|----------------|
| `AUTO` | No | No | Stable | Higher |
| `VALIDATED` | Partial | No | **Preview** | Medium (didn't fix our issue) |
| `ANY` | **Yes** | **Yes** | Stable | Lower |
| `NONE` | N/A | Disabled | Stable | N/A |

**Key Insight:** ANY mode is the only stable mode with true constrained decoding.

---

## 2. How Tool Responses Flow to Users

**YES - Tool results DO become user responses.** The flow:

```
User Query
    ↓
LlmAgent processes via AutoFlow/SingleFlow
    ↓
Gemini generates function call (constrained by ANY mode)
    ↓
Tool executes via functions.py
    ├─ Tool.run_async() returns Event.content
    ├─ Framework adds tool response to conversation
    └─ Model satisfied → Return to user
    ↓
User receives final content
```

**For nested agents (AgentTool pattern):**
1. Child agent's final `Event.content` becomes the tool's return value
2. Parent agent receives this as `function_response`
3. Parent yields to user OR uses as context

This means a `respond_to_user` tool's message will naturally flow back to the user.

---

## 3. Proposed "Respond to User" Tool

### Design

```python
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

class RespondToUserInput(BaseModel):
    """Input schema for respond_to_user tool."""
    message: str = Field(description="The natural language message to send to the user")

def respond_to_user(message: str) -> str:
    """Send a natural language response to the user.

    Use this tool when you want to communicate directly with the user
    without calling any other tools. This is for conversational responses,
    clarifying questions, acknowledgments, etc.
    """
    return message

respond_tool = FunctionTool(func=respond_to_user)
```

### Why This Works

1. **Simple schema** - Just `message: str`, no hyphenated params
2. **Passthrough** - Returns message directly, becomes Event.content
3. **Natural flow** - ADK framework handles propagation to user
4. **No special handling** - Works like any other tool

---

## 4. MALFORMED_FUNCTION_CALL Triggers

Based on Google ADK GitHub issues (#1192, #9):

| Trigger | Failure Rate | Mechanism |
|---------|--------------|-----------|
| **Hyphenated parameter names** | ~95% | Model generates invalid Python: `_X-Auth-Token = "..."` |
| **Complex nested schemas** | Variable | JSON parsing fails on special chars |
| **Large text in arguments** | Variable | Truncation or malformed JSON |
| **Transient model issues** | Intermittent | Gemini backend changes |

### Reproduction Strategy

Use hyphenated parameter names to reliably trigger the error:

```python
class ProblematicToolInput(BaseModel):
    """Tool with hyphenated param names - causes MALFORMED_FUNCTION_CALL."""
    X_Auth_Token: str = Field(alias="X-Auth-Token")  # Hyphenated alias
    Content_Type: str = Field(alias="Content-Type")  # Hyphenated alias

def problematic_tool(**kwargs) -> str:
    return "success"
```

---

## 5. ADK Patterns for Responses

### Pattern 1: Callbacks (ADK Recommended)

```python
def response_callback(ctx: CallbackContext) -> types.Content | None:
    if should_respond:
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text="Response")]
        )
    return None

agent = LlmAgent(
    ...,
    after_model_callback=[response_callback]
)
```

### Pattern 2: SetModelResponseTool (Structured Output)

When agent has `output_schema`, ADK auto-creates `set_model_response` tool:
- Model calls tool with structured data
- Tool validates and returns
- Parent receives structured response

### Pattern 3: AgentTool Propagation (MachinaMed Current)

- Nested agent's final response → tool return value
- Parent receives as `function_response`
- Parent yields to user

### Pattern 4: respond_to_user Tool (Proposed)

- Explicit tool for text responses
- Works with ANY mode
- Simple, predictable behavior

---

## 6. Implementation Plan

### Phase 1: Minimal Reproduction (bugs/adk/)

Create test scripts to:
1. **reproduce_malformed.py** - Trigger MALFORMED_FUNCTION_CALL using hyphenated params
2. **test_any_mode_fix.py** - Prove ANY mode + respond tool fixes it

### Phase 2: MachinaMed Implementation

1. **Create RespondToUserTool**
   - Location: `services/medical-agent/src/machina/medical_agent/agent_tools/respond_to_user.py`
   - Simple passthrough tool

2. **Update AgentConfigurator**
   - Change VALIDATED → ANY in `configurator.py`
   - Ensure all agents get ANY mode

3. **Register Tool with All Agents**
   - Add to agents that interact with users
   - Update agent instructions to use it

4. **Update Agent Prompts**
   - Instruct agents to use `respond_to_user` for conversational responses
   - Examples in config.yml files

### Phase 3: Testing

1. Unit tests for respond_to_user tool
2. Integration tests with ANY mode
3. Verify no MALFORMED_FUNCTION_CALL in logs
4. Test conversational scenarios still work

---

## 7. Key Files to Modify

### New Files
- `bugs/adk/reproduce_malformed.py` - Reproduction script
- `bugs/adk/test_any_mode_fix.py` - Fix verification script
- `services/medical-agent/src/machina/medical_agent/agent_tools/respond_to_user.py` - New tool

### Modified Files
- `services/medical-agent/src/machina/medical_agent/common/configurator.py` - VALIDATED → ANY
- `services/medical-agent/src/machina/medical_agent/agents/factory.py` - Register respond tool
- `services/medical-agent/src/machina/medical_agent/agents/*/config.yml` - Update prompts

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| ANY mode breaks text responses | respond_to_user tool handles this |
| Agent doesn't know to use respond tool | Update prompts with clear instructions |
| Performance overhead | Minimal - simple passthrough |
| Schema validation issues | Simple `message: str` schema, no complex types |

---

## 9. ADK Source References

**Core ADK Files (in .venv):**
- `google/adk/agents/llm_agent.py` - Main agent with callbacks
- `google/adk/tools/agent_tool.py` - Nested agent output → tool result
- `google/adk/tools/set_model_response_tool.py` - Structured response pattern
- `google/adk/flows/llm_flows/functions.py` - Tool execution and result handling

**MachinaMed Files:**
- `repos/dem2/services/medical-agent/src/machina/medical_agent/common/configurator.py` - Mode injection
- `repos/dem2/services/medical-agent/src/machina/medical_agent/agent_tools/safe_agent_tool.py` - Tool wrapper
- `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py` - Agent construction

---

## 10. Next Steps

1. [ ] Create `bugs/adk/` directory with reproduction scripts
2. [ ] Verify MALFORMED_FUNCTION_CALL can be reproduced
3. [ ] Verify ANY mode + respond tool fixes it
4. [ ] Plan implementation for MachinaMed
5. [ ] Update TODO.md with implementation tasks

---

**Research Status:** Complete
**Ready for:** Minimal reproduction case development
