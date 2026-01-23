# Plan: Remove TenantInjector and Implement Prompt-Based Patient ID Restrictions

**Status**: PROPOSED
**Created**: 2026-01-23
**Related Problem**: [PROBLEMS.md - Syntax errors caused by tenant patient_id query injection](../../PROBLEMS.md)
**Evidence Log**: [logs/tenant-injection-syntax-errors-2026-01-23.log](../../logs/tenant-injection-syntax-errors-2026-01-23.log)

## Executive Summary

The current `TenantInjector` system uses regex-based manipulation to inject `WHERE patient_id = $patient_id` clauses into Cypher queries. This approach is fundamentally fragile and breaks when Cypher queries contain multi-word operators like `STARTS WITH`, `ENDS WITH`, or `CONTAINS`.

**This plan proposes:**
1. Remove the `TenantInjector` and `WhereClauseBuilder` entirely
2. Update CypherAgent instructions to include patient_id filtering in generated queries
3. Use ADK's `MachinaMedState` to inject patient_id dynamically into agent prompts
4. Apply the same pattern to all agents that need patient-scoped data access

## Problem Statement

### Current Architecture

```
User Query
    ↓
CypherAgent generates Cypher (no patient_id filter)
    ↓
TenantInjector.inject_tenant_filters() -- REGEX MANIPULATION
    ↓
Broken Cypher (syntax errors with STARTS WITH, etc.)
    ↓
Neo4j rejects query
```

### Root Cause

The `WhereClauseBuilder._find_where_clause_end()` method searches for `WITH` keyword to determine WHERE clause boundaries. When a query contains `STARTS WITH "value"`, the regex finds `WITH` at the wrong position and injects the patient_id filter mid-expression:

**Before injection:**
```cypher
WHERE toLower(ot.summary) STARTS WITH "t"
```

**After injection (BROKEN):**
```cypher
WHERE (toLower(ot.summary) STARTS) AND ov.patient_id = $patient_id WITH "t"
```

### Evidence

From `tusdi-preview-92` logs on 2026-01-23:
```
Neo.ClientError.Statement.SyntaxError
Invalid input ')': expected 'WITH' (line 1, column 107)
```

See [evidence log](../../logs/tenant-injection-syntax-errors-2026-01-23.log) for full details.

## Proposed Solution

### Target Architecture

```
User Query
    ↓
CypherAgent receives patient_id via MachinaMedState
    ↓
Agent instructions include patient_id filtering rules
    ↓
CypherAgent generates Cypher WITH patient_id filter built-in
    ↓
Valid Cypher executes against Neo4j
```

### Key Changes

1. **Remove TenantInjector entirely** - No more regex-based query manipulation
2. **Instruct agents to include patient_id** - Prompt engineering instead of post-processing
3. **Pass patient_id via ADK state** - Use existing `MachinaMedState` infrastructure
4. **Agents responsible for scoping** - Shift responsibility to the LLM that generates queries

## Implementation Plan

### Phase 1: CypherAgent Config Changes

**File**: `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/config.yml`

#### Remove These Sections (currently lines 28-60)

Delete all mentions of:
- "CRITICAL: VARIABLE SCOPE FOR TENANT FILTERING"
- "CRITICAL TENANT SCOPING RULES"
- "Correct query examples for tenant scoping"
- TypeNode vs Instance node distinction for multi-tenancy

#### Add New Patient ID Filtering Instructions

Replace with clear, positive instructions:

```yaml
instruction: |
  Generate Cypher queries for the medical knowledge graph from natural language.

  # PATIENT SCOPING (REQUIRED)

  The current patient ID is: {patient_id}

  **All queries MUST filter by patient_id:**
  - For nodes with `patient_id` property: Add `WHERE node.patient_id = "{patient_id}"`
  - For PatientNode: Add `WHERE p.uuid = "{patient_id}"`

  **Patient-scoped nodes** (have patient_id property):
  - ObservationValueNode
  - ConditionCaseNode
  - SymptomEpisodeNode
  - EncounterNode
  - DocumentReferenceNode
  - IntakeEventNode
  - AllergyIntoleranceNode

  **Type nodes** (NO patient_id, shared across patients):
  - ObservationTypeNode, ConditionTypeNode, SymptomTypeNode
  - SubstanceNode, MedicationNode, SupplementNode
  - BodySystemNode, IngredientNode

  **Query Pattern:**
  ```cypher
  MATCH (ov:ObservationValueNode)-[:INSTANCE_OF]->(ot:ObservationTypeNode)
  WHERE ov.patient_id = "{patient_id}"
    AND toLower(ot.summary) CONTAINS "cholesterol"
  RETURN ov, ot
  ```

  **Medication/Regimen Pattern** (IntakeRegimenNode has no patient_id):
  ```cypher
  MATCH (p:PatientNode)-[:HAS_REGIMEN]->(regimen:IntakeRegimenNode)
  WHERE p.uuid = "{patient_id}"
  RETURN regimen
  ```

  # ... rest of existing instructions ...
```

### Phase 2: Dynamic Patient ID Injection

**File**: `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/factory.py`

#### Current State Access Pattern

The codebase already has `MachinaMedState` infrastructure:

```python
# Already exists in factory.py
async def test_cypher_wrapper(tool_context: ToolContext, cypher_query: str, dry_run: bool = True):
    state = MachinaMedState.from_tool_context(tool_context)
    return await test_cypher(
        self.graph_traversal_service,
        cypher_query=cypher_query,
        patient_id=state.patient_id,  # <-- Already extracted
        user_id=tool_context._invocation_context.user_id,
        # ...
    )
```

#### Add Instruction Rendering with Patient ID

Modify agent creation to inject patient_id into instructions:

```python
def create_agent(self, config: AgentConfig | None = None) -> LlmAgent:
    """Create agent using provided config or load from config.yml."""
    if config is None:
        config = self._load_config()

    # Render instruction with dynamic patient_id
    # Note: patient_id will be injected via before_agent_callback at runtime

    return LlmAgent(
        name=config.name,
        model=self._model,
        instruction=config.instruction,  # Contains {patient_id} placeholder
        tools=[self._build_test_cypher_tool()],
        before_agent_callback=[self._inject_patient_context],
        # ...
    )

async def _inject_patient_context(self, callback_context: CallbackContext):
    """Inject patient_id into agent instruction at runtime."""
    from machina.shared.utils.render import render_template

    state = MachinaMedState.from_callback_context(callback_context)

    # Store patient_id in state for use in prompt rendering
    callback_context.state["patient_id"] = state.patient_id

    # The instruction template contains {patient_id} which gets
    # substituted when the agent processes its instruction
```

#### Alternative: Use State Variables in Prompts

ADK supports `{state_variable}` syntax in instructions. If the agent instruction contains `{patient_id}`, and `callback_context.state["patient_id"]` is set, ADK will substitute it.

```python
# In before_agent_callback
callback_context.state["patient_id"] = state.patient_id
```

Then in config.yml:
```yaml
instruction: |
  The current patient ID is: {patient_id}

  All queries MUST filter by this patient_id...
```

### Phase 3: Remove TenantInjector from GraphTraversalService

**File**: `repos/dem2/shared/src/machina/shared/graph_traversal/service.py`

#### Before (Current)

```python
from machina.shared.graph_traversal.tenant_injector import TenantInjector

class GraphTraversalService:
    def __init__(
        self,
        neo4j_driver: Any,
        validator: CypherValidator,
        tenant_injector: TenantInjector,  # <-- Remove
        formatter: GraphResultFormatter,
    ):
        self.tenant_injector = tenant_injector  # <-- Remove

    def _prepare_query(self, query: str, patient_id: str, user_id: str) -> str:
        # ... validation ...
        query_with_limit = self.validator.enforce_limit(query)
        query_with_filters = self.tenant_injector.inject_tenant_filters(  # <-- Remove
            query_with_limit, patient_id, user_id
        )
        return query_with_filters
```

#### After (Proposed)

```python
# Remove TenantInjector import entirely

class GraphTraversalService:
    def __init__(
        self,
        neo4j_driver: Any,
        validator: CypherValidator,
        formatter: GraphResultFormatter,
        # tenant_injector removed
    ):
        # self.tenant_injector removed

    def _prepare_query(self, query: str, patient_id: str, user_id: str) -> str:
        # ... validation ...
        query_with_limit = self.validator.enforce_limit(query)
        # No tenant injection - agent is responsible for patient_id filtering
        return query_with_limit
```

### Phase 4: Remove Files

Delete these files entirely:

| File | Lines | Purpose |
|------|-------|---------|
| `repos/dem2/shared/src/machina/shared/graph_traversal/tenant_injector.py` | 531 | Main injector class |
| `repos/dem2/shared/src/machina/shared/graph_traversal/where_clause_builder.py` | 387 | WHERE clause manipulation |
| `repos/dem2/shared/tests/graph_traversal/test_tenant_injector.py` | ~200 | Tests for deleted code |

### Phase 5: Update Other Agents

Based on research, these agents need patient_id context in their instructions:

| Agent | Needs patient_id | Action |
|-------|------------------|--------|
| **CypherAgent** | YES | Update config.yml with patient_id injection |
| **HealthConsultantAgent** | YES (via query_graph) | No change needed - uses CypherAgent |
| **HealthConsultantLiteAgent** | YES (via query_graph) | No change needed - uses CypherAgent |
| **DataExtractorAgent** | YES | Already uses MachinaMedState |
| **DataEntryAgent** | YES | Already uses MachinaMedState |
| **MedicalMeasurementsAgent** | YES | Already uses MachinaMedState |
| **MedicalContextAgent** | YES | Already uses MachinaMedState |
| **TriageAgent** | NO | Routes to other agents |
| **GoogleSearchAgent** | NO | External search only |
| **UrlHandlerAgent** | NO | External URLs only |
| **FastGraphSummaryAgent** | NO | Receives pre-filtered data |

### Phase 6: Query Runner Cleanup

**File**: `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/query_runner.py`

Remove tenant injection preview logging (lines 1087-1091):

```python
# DELETE this preview code
augmented_query_preview = (
    traversal_service.tenant_injector.inject_tenant_filters(
        preview_source, patient_id, user_id
    )
)
```

Replace with:
```python
# No tenant injection - query is used as-is
augmented_query_preview = preview_source
```

## Risk Assessment

### Risks

1. **LLM may forget to include patient_id filter**
   - Mitigation: Strong prompt engineering with examples
   - Mitigation: Add validation in `test_cypher()` to check for patient_id
   - Mitigation: Unit tests for generated queries

2. **Cross-patient data leakage if filter omitted**
   - Mitigation: Add safety check in `GraphTraversalService.execute_query()` that validates patient-scoped nodes have filters
   - Mitigation: Log warnings for queries without patient_id filters

3. **Migration complexity**
   - Mitigation: Phase implementation, test in preview environment first
   - Mitigation: Keep TenantInjector code in separate branch for rollback

### Benefits

1. **No more syntax errors** - LLM generates complete, valid Cypher
2. **Simpler architecture** - Remove ~918 lines of fragile regex code
3. **Better query quality** - LLM can optimize entire query including filters
4. **Maintainability** - Prompt changes easier than regex debugging

## Testing Strategy

### Unit Tests

1. **CypherAgent output validation**
   - Test that generated queries include patient_id filter
   - Test with STARTS WITH, ENDS WITH, CONTAINS patterns
   - Test medication queries include PatientNode filter

2. **GraphTraversalService**
   - Test query execution without tenant injection
   - Test that patient_id parameter is passed correctly

### Integration Tests

1. **End-to-end query flow**
   - Natural language query → Cypher → Neo4j
   - Verify results are patient-scoped

2. **Security validation**
   - Verify no cross-patient data leakage
   - Test with multiple patients in database

### Preview Environment Testing

1. Deploy to tusdi-preview-92
2. Run same queries that previously failed (STARTS WITH patterns)
3. Verify queries succeed with correct patient scoping

## Rollout Plan

### Phase 1: Development (1-2 days)
- [ ] Update CypherAgent config.yml with new instructions
- [ ] Add patient_id injection to CypherAgent factory
- [ ] Remove TenantInjector from GraphTraversalService
- [ ] Update query_runner.py to remove tenant preview logging

### Phase 2: Testing (1 day)
- [ ] Run existing unit tests (expect some failures for deleted code)
- [ ] Update/remove tests for deleted TenantInjector
- [ ] Add new tests for patient_id in generated queries
- [ ] Manual testing with STARTS WITH queries

### Phase 3: Preview Deployment (1 day)
- [ ] Deploy to tusdi-preview-92
- [ ] Test previously failing queries
- [ ] Verify patient scoping with multiple test patients
- [ ] Monitor for any errors

### Phase 4: Production Deployment
- [ ] Merge to dev branch
- [ ] Deploy to tusdi-dev
- [ ] Monitor for 24-48 hours
- [ ] Deploy to production

### Phase 5: Cleanup
- [ ] Delete tenant_injector.py
- [ ] Delete where_clause_builder.py
- [ ] Delete test_tenant_injector.py
- [ ] Update CLAUDE.md documentation

## Open Questions

1. **Should we add a validation layer that checks queries have patient_id filters?**
   - Pro: Safety net against LLM mistakes
   - Con: Adds complexity, may have false positives

2. **Should patient_id be a Cypher parameter ($patient_id) or literal value?**
   - Parameter: More secure (prevents injection), standard Neo4j practice
   - Literal: Simpler prompt, but potential security concern
   - **Recommendation**: Use parameter `$patient_id` with explicit instruction

3. **How to handle queries that intentionally span all patients (admin use cases)?**
   - Option A: Special admin flag that bypasses patient scoping
   - Option B: Separate admin agent without patient_id injection
   - **Recommendation**: Not needed for current use cases; add later if required

## Appendix: Affected Files Summary

| File | Action | Lines Changed |
|------|--------|---------------|
| `agents/CypherAgent/config.yml` | Modify | ~60 lines |
| `agents/CypherAgent/factory.py` | Modify | ~20 lines |
| `graph_traversal/service.py` | Modify | ~15 lines |
| `agents/CypherAgent/query_runner.py` | Modify | ~10 lines |
| `graph_traversal/tenant_injector.py` | DELETE | -531 lines |
| `graph_traversal/where_clause_builder.py` | DELETE | -387 lines |
| `tests/graph_traversal/test_tenant_injector.py` | DELETE | ~-200 lines |

**Net change**: ~-1,000 lines of code removed, ~100 lines modified

## References

- [MachinaMedState implementation](../../repos/dem2/shared/src/machina/shared/medical_agent/state.py)
- [ADK state access patterns](../../repos/dem2/services/medical-agent/src/machina/medical_agent/agents/DataExtractorAgent/agent.py)
- [Template rendering](../../repos/dem2/shared/src/machina/shared/utils/render.py)
- [Evidence log](../../logs/tenant-injection-syntax-errors-2026-01-23.log)
