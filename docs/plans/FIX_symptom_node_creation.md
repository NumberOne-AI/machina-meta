# Plan: Fix SymptomNode Creation Issues

**Created:** 2026-01-28
**Status:** PROPOSED
**Related Problem:** PROBLEMS.md "SymptomNode not created properly from conversational symptom queries"
**Related TODO:** TODO.md "Fix symptom episode merge prompt to include modifiers"

## Executive Summary

SymptomNode creation from conversational queries exhibits different failure modes across environments. This plan addresses three distinct bugs affecting symptom persistence and data integrity.

## Problem Statement

When a user describes symptoms with modifiers (aggravating/relieving factors) in natural language:
- **Expected**: SymptomEpisodeNode created with proper arrays for `aggravating_factors`, `relieving_factors`
- **Actual**: Variable behavior across environments - some fail to create, some lose modifiers

### Test Query
```
"I have a headache that gets worse when I'm stressed or in bright light,
and gets better when I rest in a dark room."
```

### Expected Result
```
SymptomEpisodeNode:
  name: "headache"
  aggravating_factors: ["stress", "bright light"]
  relieving_factors: ["rest", "dark room"]
```

## Identified Bugs

| Bug | Environment | Root Cause | Severity |
|-----|-------------|------------|----------|
| BUG #1 | local-dev | `list[string]` generator bug - arrays stringified | HIGH |
| BUG #2 | ALL | Merge prompt missing modifier fields | HIGH |
| BUG #3 | K8s (preview-92, dev) | Unknown - symptoms not persisted | HIGH |

---

## Phase 1: Fix Merge Prompt (BUG #2)

**Priority:** HIGHEST - Affects all environments
**Estimated Effort:** Small
**Risk:** Low

### Problem

`_build_episode_merge_prompt()` in `symptom_enricher.py` does NOT include modifier fields:
- `aggravating_factors` ❌
- `relieving_factors` ❌
- `associated_signs` ❌

When merging existing episodes, the LLM has no modifier data and returns NULL.

### Solution

Add modifier fields to both EXISTING EPISODE and NEW INPUT sections of the merge prompt.

### Files to Modify

```
repos/dem2/services/medical-data-engine/src/machina/medical_data_engine/enricher/symptom_enricher.py
  - Lines 753-803: _build_episode_merge_prompt()
```

### Implementation Steps

1. [ ] Read current `_build_episode_merge_prompt()` implementation
2. [ ] Add `aggravating_factors` to EXISTING EPISODE section (from `existing_episode`)
3. [ ] Add `relieving_factors` to EXISTING EPISODE section (from `existing_episode`)
4. [ ] Add `associated_signs` to EXISTING EPISODE section (from `existing_episode`)
5. [ ] Add `aggravating_factors` to NEW INPUT section (from `resource`)
6. [ ] Add `relieving_factors` to NEW INPUT section (from `resource`)
7. [ ] Add `associated_signs` to NEW INPUT section (from `resource`)
8. [ ] Run linting and type checks: `(cd repos/dem2 && just check)`
9. [ ] Test on local-dev: Create symptom, then update it - verify modifiers preserved

### Test Plan

```bash
# 1. Start local dev stack
just dev-up

# 2. Create a fresh symptom
# Query: "I have a headache that gets worse when I'm stressed"

# 3. Update the symptom (triggers merge path)
# Query: "The headache also gets worse in bright light"

# 4. Verify modifiers preserved
just neo4j-query "MATCH (s:SymptomEpisodeNode {name: 'headache'}) RETURN s.aggravating_factors"
# Expected: ["stress", "bright light"]
```

### Rollback Plan

Revert the single file change if issues arise.

---

## Phase 2: Fix list[string] Generator Bug (BUG #1)

**Priority:** HIGH - Affects local-dev
**Estimated Effort:** Small
**Risk:** Medium (requires graph regeneration)

### Problem

`generator.py` type_map handles `list[float]` but NOT `list[string]`:

```python
type_map = {
    "string": ("StringProperty", "StringProperty"),
    "list[float]": ("ArrayProperty", "ArrayProperty"),
    # list[string] MISSING!
}
```

Result: `StringProperty()` instead of `ArrayProperty(StringProperty())` for list[string] fields.

### Solution

Add `list[string]` mapping to the type_map.

### Files to Modify

```
repos/dem2/services/graph-memory/src/machina/graph_memory/generator.py
  - Lines 64-71: type_map dictionary
```

### Implementation Steps

1. [ ] Read current `generator.py` type_map
2. [ ] Add `"list[string]": ("ArrayProperty", "ArrayProperty")` entry
3. [ ] Verify ArrayProperty import exists
4. [ ] Regenerate graph nodes: `(cd repos/dem2 && just graph-generate)`
5. [ ] Verify `nodes.py` now has `ArrayProperty(StringProperty())` for modifier fields
6. [ ] Run linting and type checks: `(cd repos/dem2 && just check)`
7. [ ] Test on local-dev: Create symptom with modifiers, verify stored as arrays not strings

### Test Plan

```bash
# 1. After regeneration, check nodes.py
grep -A2 "aggravating_factors" repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/condition/nodes.py
# Expected: ArrayProperty(StringProperty())

# 2. Test data storage
just dev-up
# Create symptom with modifiers
just neo4j-query "MATCH (s:SymptomEpisodeNode) RETURN s.aggravating_factors LIMIT 1"
# Expected: ["stress", "bright light"] (array, not stringified)
```

### Rollback Plan

1. Revert generator.py change
2. Regenerate graph nodes
3. Commit revert

---

## Phase 3: Investigate K8s Persistence Failure (BUG #3)

**Priority:** HIGH - Affects preview-92 and dev
**Estimated Effort:** Medium (investigation)
**Risk:** Low (investigation only)

### Problem

On K8s environments (tusdi-preview-92, tusdi-dev), symptoms are extracted but NOT persisted to Neo4j.

### Investigation Steps

1. [ ] **Check K8s logs for symptom processing errors**
   ```bash
   # In gcloud-admin shell
   kubectl logs -n tusdi-preview-92 -l app=tusdi-api --tail=500 | grep -E "symptom_processing_failed|task_processing_completed"
   ```

2. [ ] **Verify DataExtractorAgent extracts symptoms**
   - Check session state after query
   - Look for `ExtractUserQueryResources.symptoms` in response

3. [ ] **Check patient_id validation**
   ```bash
   kubectl logs -n tusdi-preview-92 -l app=tusdi-api --tail=500 | grep "process_raw_medical_data_missing_patient_id"
   ```

4. [ ] **Compare configurations**
   - Check for environment-specific settings
   - Compare Gemini model versions
   - Check Neo4j connection settings

5. [ ] **Enable debug logging** (if needed)
   - Set log level to DEBUG for `machina.medical_data_engine.engine.processors.symptom`

### Potential Causes

| Cause | Likelihood | How to Verify |
|-------|------------|---------------|
| LLM doesn't extract symptoms | Medium | Check session state for `symptoms` array |
| Neo4j connection failure | Medium | Check for connection errors in logs |
| Patient ID missing | Low | Check for validation error logs |
| Permission/RBAC issue | Low | Check Neo4j auth errors |

### Resolution (TBD after investigation)

Will be determined based on investigation findings.

---

## Phase 4: Verification and Documentation

**Priority:** Required after fixes
**Estimated Effort:** Small

### Steps

1. [ ] Test all fixes on local-dev
2. [ ] Deploy to tusdi-staging and verify
3. [ ] Deploy to tusdi-preview-92 and verify
4. [ ] Deploy to tusdi-dev and verify
5. [ ] Update PROBLEMS.md to [SOLVED]
6. [ ] Update TODO.md tasks to [DONE]
7. [ ] Update evidence report with final results

### Success Criteria

| Environment | Expected Result |
|-------------|-----------------|
| local-dev | Symptoms created with proper arrays (not stringified) |
| tusdi-staging | Symptoms created with modifiers preserved during updates |
| tusdi-preview-92 | Symptoms persisted to Neo4j |
| tusdi-dev | Symptoms persisted to Neo4j |

---

## Dependencies

- Phase 2 requires Phase 1 to be completed first (easier to test)
- Phase 3 investigation can proceed in parallel
- Phase 4 requires all other phases complete

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Graph regeneration breaks other fields | HIGH | Test all node types after regeneration |
| Merge prompt change affects other LLM behavior | MEDIUM | Review prompt carefully, test edge cases |
| K8s investigation inconclusive | MEDIUM | Add more detailed logging if needed |

## Timeline

| Phase | Target |
|-------|--------|
| Phase 1 | Immediate - fix is straightforward |
| Phase 2 | After Phase 1 verified |
| Phase 3 | Parallel with Phase 1-2 |
| Phase 4 | After all phases complete |

## Appendix: Key Files

```
repos/dem2/services/medical-data-engine/src/machina/medical_data_engine/
├── enricher/
│   └── symptom_enricher.py        # BUG #2 - merge prompt
├── engine/
│   ├── engine.py                  # Resource preparation
│   └── processors/
│       └── symptom.py             # Symptom processing
├── service.py                     # Task queuing
└── worker.py                      # Task execution

repos/dem2/services/graph-memory/src/machina/graph_memory/
├── generator.py                   # BUG #1 - type mapping
└── medical/graph/condition/
    └── nodes.py                   # Generated node definitions

repos/dem2/services/medical-agent/src/machina/medical_agent/agents/
└── DataExtractorAgent/
    ├── agent.py                   # LLM extraction
    └── config.yml                 # Agent configuration
```
