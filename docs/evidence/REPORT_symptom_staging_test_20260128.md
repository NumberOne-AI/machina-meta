# SymptomNode Staging Test Report

**Date:** 2026-01-28
**Environment:** tusdi-staging
**Test Query:** "I have a headache that gets worse when I am stressed or in bright light, and gets better when I rest in a dark room."

## Test Results

### Before Deletion (existing symptoms)

| Symptom UUID | Session Date | aggravating_factors | relieving_factors | snomed_ct_code |
|--------------|--------------|---------------------|-------------------|----------------|
| `3b8eda9b-3931-4c7d-b09f-6b32eaaaccb2` | 2026-01-26 | `["stress", "bright light"]` | `["rest", "dark room"]` | `25064002` |
| `f6978d10-e5b4-437f-9a5b-0f5fa30b93ea` | 2026-01-28 | `null` | `null` | `null` |

### After Deletion (fresh creation)

Deleted both SymptomEpisodeNodes and ran the test again:

| Field | Value |
|-------|-------|
| name | `headache` |
| aggravating_factors | `["stress", "bright light"]` ✅ |
| relieving_factors | `["rest", "dark room"]` ✅ |
| snomed_ct_code | `null` |

**Key Finding:** Arrays stored as proper Neo4j arrays, not stringified like local-dev.

## Root Cause Analysis

### Two Separate Bugs Identified

#### BUG #1: `list[string]` Generator Bug (local-dev only)

- **Location:** `repos/dem2/services/graph-memory/src/machina/graph_memory/generator.py`
- **Issue:** `type_map` handles `list[float]` but NOT `list[string]`, so fields are generated as `StringProperty()` instead of `ArrayProperty(StringProperty())`
- **Effect:** Arrays are stringified on write: `["stress", "bright light"]` → `"['stress', 'bright light']"`
- **Evidence:** [docs/evidence/EVIDENCE_list_string_generator_bug_20260123.md](EVIDENCE_list_string_generator_bug_20260123.md)
- **Status:** Known issue, fix planned

#### BUG #2: Merge Prompt Missing Modifiers (ALL environments)

- **Location:** `repos/dem2/services/medical-data-engine/src/machina/medical_data_engine/enricher/symptom_enricher.py` lines 753-803
- **Issue:** `_build_episode_merge_prompt()` does NOT include `aggravating_factors`, `relieving_factors`, or `associated_signs` in the LLM prompt
- **Effect:** When merging/updating existing episodes, LLM has no modifier data → returns NULL
- **Evidence:** Fresh creation works (arrays stored correctly), UPDATE path loses modifiers

### Code Analysis

The `_build_episode_merge_prompt()` method builds the prompt for the LLM merge operation:

```python
# EXISTING EPISODE section includes:
- name ✓
- summary ✓
- severity ✓
- status ✓
- laterality ✓
- frequency_pattern ✓
- course ✓
- occurrence_date ✓
- snomed_ct_code ✓
- aggravating_factors ❌ NOT INCLUDED
- relieving_factors ❌ NOT INCLUDED
- associated_signs ❌ NOT INCLUDED

# NEW INPUT section includes:
- name ✓
- summary ✓
- severity ✓
- laterality ✓
- occurrence_date ✓
- aggravating_factors ❌ NOT INCLUDED
- relieving_factors ❌ NOT INCLUDED
```

The system prompt says "**aggravating_factors, relieving_factors, associated_signs**: Merge lists (combine unique values)" but these fields are never passed to the LLM, so it returns NULL.

## Observations

1. **Fresh symptom creation WORKS** - modifiers correctly extracted and stored as arrays
2. **Symptom updates FAIL** - when a similar symptom exists, updates lose the modifiers
3. **MAX_TOKENS observed** - `"finishReason":"MAX_TOKENS"` in agent response (Gemini 3 issue)
4. **SNOMED enrichment not triggered** - `snomed_ct_code` is null on fresh creation
5. **Staging uses proper arrays** - confirms BUG #1 is local-dev specific

## Conclusion

The symptom extraction pipeline works correctly for **new symptom creation**. The problem is in the **symptom enricher's merge path** - the `_build_episode_merge_prompt()` method does not include modifier fields in the prompt.

**Fix Required:** Add `aggravating_factors`, `relieving_factors`, and `associated_signs` to both EXISTING EPISODE and NEW INPUT sections of the merge prompt.

**TODO Added:** See TODO.md "Fix symptom episode merge prompt to include modifiers"

**Status:** ROOT CAUSE IDENTIFIED - Merge prompt missing modifier fields
