# MALFORMED_FUNCTION_CALL Error Analysis Report

**Date:** 2026-01-19
**Environment:** MachinaMed (dem2) - tusdi-dev (GKE)
**Affected Component:** TriageAgent via Google ADK
**Reporter:** Stuart McClure
**Investigator:** David Beal + Claude Code

---

## Executive Summary

The `MALFORMED_FUNCTION_CALL` error is a **Gemini API-level issue** that occurs during LLM response parsing, before any tool code executes. This causes users to receive empty responses when the TriageAgent fails to generate valid function calls.

**Key Finding:** This is a known issue in the Google ADK ecosystem with no permanent fix. The error occurs at the LLM response generation level, meaning solutions like `VALIDATED` mode or the Reflect and Retry plugin have limited effectiveness.

---

## Incident Details

### Observed Behavior

| Metric | Value |
|--------|-------|
| Total errors found | 2 (in tusdi-dev logs) |
| Error type | `MALFORMED_FUNCTION_CALL` |
| Affected agent | TriageAgent |
| Date range | 2026-01-16 to 2026-01-19 |
| User impact | Empty response (content_length=0) |

### Error Timeline

**Error #1:** 2026-01-16T22:11:55Z
- Invocation: `e-7e37bfa7-1fe4-413c-a1f1-18cccc6fe6ce`
- Query: Unknown
- Result: Empty response to user

**Error #2:** 2026-01-19T01:08:58Z
- Invocation: `e-20e9bc1d-4d7c-4b0f-a501-2ae0f909785d`
- Query: "tell me the details of this document"
- Result: Empty response to user

### Log Evidence

```
2026-01-19T01:08:58.869203Z [ERROR] LLM error response
  event_type="llm_response"
  agent="TriageAgent"
  error_code="MALFORMED_FUNCTION_CALL"
  error_message=""

2026-01-19T01:08:58.881632Z [INFO] event_yielded
  author="TriageAgent"
  content_summary="None"
  content_length=0
  is_final_response=True
```

---

## Root Cause Analysis

### What is MALFORMED_FUNCTION_CALL?

`MALFORMED_FUNCTION_CALL` is a `FinishReason` enum value returned by the Gemini API when:
1. The model attempts to generate a function call
2. The generated output is syntactically invalid or unparseable
3. The Gemini API cannot parse the model's own output

**Critical Insight:** This error occurs at the **LLM response level**, before any tool code executes.

### Why Does It Happen?

Based on research of Google ADK GitHub issues:

| Cause | Description | Source |
|-------|-------------|--------|
| **Hyphenated parameter names** | Parameters like `X-Rundeck-Auth-Token` cause ~95% failure rate | [Issue #1192](https://github.com/google/adk-python/issues/1192) |
| **Invalid syntax generation** | Model generates code like `_auth_prefix_vaf_X-Rundeck-Auth-Token = "token"` | [Issue #1192](https://github.com/google/adk-python/issues/1192) |
| **Transient model issues** | Backend model changes can cause/resolve the issue | [Issue #9](https://github.com/google/adk-python/issues/9) |
| **Complex tool schemas** | Tools with complex parameter structures may confuse the model | ADK Docs |

### Error Flow

```
User Query
    ↓
TriageAgent receives query
    ↓
LLM (Gemini) generates response
    ↓
❌ MALFORMED_FUNCTION_CALL (parsing fails)
    ↓
Empty response returned to user
    ↓
HealthConsultantAgent NEVER called
```

---

## Investigation: Attempted Fixes

### Fix #1: VALIDATED Function Calling Mode

**Hypothesis:** Adding `FunctionCallingConfigMode.VALIDATED` would enable constrained decoding and prevent malformed outputs.

**Implementation:**
- Added `inject_validated_tool_config` model validator to `AgentConfig`
- Applied VALIDATED mode to all 14 agents via centralized configuration
- Updated UrlHandlerInnerAgent from AUTO to VALIDATED

**Commit:** `9428e31e` (2026-01-19)

**Result:** ❌ **Did not fix the issue**

The error still occurred after deploying with VALIDATED mode:
```
2026-01-20T00:41:13.138050Z [ERROR] LLM error response
  agent="TriageAgent"
  error_code="MALFORMED_FUNCTION_CALL"
```

**Why It Didn't Work:**
- VALIDATED mode is marked as **(Preview)** in Google documentation
- The error occurs during JSON parsing, before schema validation
- The simple tool schema (`request: STRING`) provides minimal constraints

### Fix #2: Reflect and Retry Plugin

**Hypothesis:** The ADK Reflect and Retry plugin could intercept and retry failed function calls.

**Research Finding:** ❌ **Won't help**

The plugin handles **tool execution errors** (after parsing), but `MALFORMED_FUNCTION_CALL` occurs **during LLM response parsing** (before tool execution). No tool is invoked when this error occurs.

---

## Google ADK Issue Tracker Research

### Issue #1192: MALFORMED_FUNCTION_CALL with OpenAPIToolSet

**URL:** https://github.com/google/adk-python/issues/1192

**Summary:**
- ~95% failure rate when using hyphenated header parameters
- Workaround: Avoid hyphens in parameter names
- Status: Closed (no permanent fix)

**Key Quote:**
> "This only fails when the header is 'X-Rundeck-Auth-Token'... if I change this to just 'AuthToken' it does not fail."

### Issue #9: Malformed Function Call

**URL:** https://github.com/google/adk-python/issues/9

**Summary:**
- User reported MALFORMED_FUNCTION_CALL with valid SQL queries
- Issue resolved itself after model backend changes
- Status: Closed (attributed to transient model issues)

**Key Quote:**
> "I am monitoring this issue, today it went smooth. Maybe it was something with yesterday model's shifting behind aliases."

---

## Function Calling Modes Comparison

| Mode | Behavior | Prevents MALFORMED_FUNCTION_CALL? |
|------|----------|----------------------------------|
| **AUTO** (default) | Model decides between text or function call | No |
| **ANY** | Model MUST call a function; guarantees schema adherence | Potentially (forces function output) |
| **VALIDATED** (Preview) | Constrains to valid function calls or text; ensures schema adherence | Partially (still in Preview) |
| **NONE** | No function calls allowed | N/A |

**Documentation Source:** https://ai.google.dev/gemini-api/docs/function-calling

---

## Current Tool Schema Analysis

The TriageAgent uses tools wrapped by `SafeAgentTool` and `AgentTool`:

```
Functions available to TriageAgent:
- UrlHandlerAgent: {'request': {'type': STRING}}
- HealthConsultantAgent: {'request': {'type': STRING}}
```

The schema is **minimal** - just a single string parameter. This provides limited constraints for the model to validate against.

---

## Recommended Solutions

### Immediate (High Priority)

1. **Add Graceful Error Handling**
   - Detect MALFORMED_FUNCTION_CALL in response
   - Return user-friendly message instead of empty response
   - Example: "I encountered an issue processing your request. Please try rephrasing your question."

2. **Add LLM-Level Retry Logic**
   - Retry the LLM call when MALFORMED_FUNCTION_CALL occurs
   - Configure max retries (e.g., 2-3 attempts)
   - Use exponential backoff

### Short-Term (Medium Priority)

3. **Improve Tool Schemas**
   - Add more descriptive parameter definitions
   - Include enum constraints where applicable
   - Avoid special characters in parameter names

4. **Add Detailed Logging**
   - Log the raw LLM response when MALFORMED_FUNCTION_CALL occurs
   - Track patterns to identify problematic queries

### Long-Term (Low Priority)

5. **Monitor Google ADK Updates**
   - VALIDATED mode is in Preview - may improve
   - Watch for fixes to known issues

6. **Consider Fallback Models**
   - Test with different Gemini model versions
   - Evaluate if certain models are more stable

---

## Implementation Locations

| Solution | File(s) to Modify |
|----------|-------------------|
| Error handling | `services/medical-agent/src/machina/medical_agent/agents/factory.py` |
| Retry logic | `services/medical-agent/src/machina/medical_agent/common/` (new module) |
| Tool schemas | `services/medical-agent/src/machina/medical_agent/agent_tools/` |
| Logging | `services/medical-agent/src/machina/medical_agent/callbacks/` |

---

## Related Files

- **PROBLEMS.md:** `repos/dem2/PROBLEMS.md` - "TriageAgent MALFORMED_FUNCTION_CALL" [OPEN]
- **TODO.md:** `repos/dem2/TODO.md` - "Fix TriageAgent MALFORMED_FUNCTION_CALL errors" [PROPOSED]
- **Agent Trace Log:** `AGENT_TRACE_ERRORS_20260119.md` (workspace root)
- **Configurator:** `services/medical-agent/src/machina/medical_agent/common/configurator.py`
- **Factory:** `services/medical-agent/src/machina/medical_agent/agents/factory.py`

---

## References

### Official Documentation
- [Function calling with the Gemini API](https://ai.google.dev/gemini-api/docs/function-calling)
- [ADK Reflect and Retry Plugin](https://google.github.io/adk-docs/plugins/reflect-and-retry/)
- [ADK Callbacks Documentation](https://google.github.io/adk-docs/callbacks/)
- [ADK Custom Tools](https://google.github.io/adk-docs/tools-custom/)

### GitHub Issues
- [#1192 - MALFORMED_FUNCTION_CALL with OpenAPIToolSet](https://github.com/google/adk-python/issues/1192)
- [#9 - Malformed function call](https://github.com/google/adk-python/issues/9)
- [#53 - Tool use with function calling is unsupported](https://github.com/google/adk-python/issues/53)

### Community Discussions
- [MALFORMED_FUNCTION_CALL with large text content - Google AI Forum](https://discuss.ai.google.dev/t/getting-finishreason-malformed-function-call-when-function-calling-arugments-contain-large-amount-of-text-content/69488)
- [Gemini models return MALFORMED_FUNCTION_CALL with Deep Agents](https://github.com/langchain-ai/deepagents/issues/417)

---

## Appendix: Commit History

| Commit | Date | Description | Result |
|--------|------|-------------|--------|
| `9428e31e` | 2026-01-19 | Add VALIDATED mode to all agents | Did not fix issue |

---

**Report Generated:** 2026-01-19T17:45:00-07:00
**Last Updated:** 2026-01-19T17:45:00-07:00
