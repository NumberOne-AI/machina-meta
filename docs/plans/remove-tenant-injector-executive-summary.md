# Executive Summary: TenantInjector Removal Plan

**Date**: 2026-01-23
**Status**: PROPOSED - Requires Critical Review
**Full Plan**: [remove-tenant-injector.md](remove-tenant-injector.md)

## The Problem

The `TenantInjector` system uses regex to inject `WHERE patient_id = $patient_id` into Cypher queries. This approach breaks when queries contain multi-word operators like `STARTS WITH`:

```
BEFORE: WHERE name STARTS WITH "T"
AFTER:  WHERE (name STARTS) AND patient_id = $patient_id WITH "T"  ← BROKEN
```

**Impact**: All graph queries using string matching patterns fail on tusdi-preview-92 and other environments.

## Proposed Solution

Remove TenantInjector (~918 lines) and instruct agents to include patient_id filters directly in generated Cypher via prompt engineering.

## Critical Concerns

### 1. Security: LLM Reliability Risk (HIGH)

| Current State | Proposed State |
|--------------|----------------|
| TenantInjector adds filters automatically (defense-in-depth) | 100% reliant on LLM following instructions |
| Bugs cause syntax errors (visible failures) | LLM omission causes data leakage (silent failures) |

**The failure mode changes from "query fails" to "returns wrong patient's data."**

### 2. Missing: Query Validation Safety Net

The plan removes TenantInjector without adding a replacement safety check.

**Recommendation**: Add a pre-execution validator that:
- Parses generated Cypher
- Verifies patient-scoped nodes have `patient_id` filter
- Rejects queries that could leak cross-patient data

### 3. Alternative Solutions Not Evaluated

| Alternative | Effort | Risk | Considered? |
|-------------|--------|------|-------------|
| Fix WhereClauseBuilder regex | Medium | Low | No |
| Use proper Cypher parser (libcypher-parser) | High | Low | No |
| Add validation layer + keep TenantInjector | Medium | Low | No |
| Prompt-only (proposed) | Medium | **High** | Yes |

### 4. Testing Gap

Plan lacks specifics on verifying no cross-patient data leakage:
- How to test Patient A cannot see Patient B's data?
- What's the test matrix for all query patterns?
- How to regression test after deployment?

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation in Plan? |
|------|------------|--------|---------------------|
| LLM forgets patient_id filter | Medium | **Critical** (data leak) | No |
| Prompt injection via patient_id | Low | High | No |
| Regression in production | Medium | High | Partial |
| Rollback complexity | - | Medium | No |

## Recommendations

### Before Proceeding

1. **Add Query Validation Layer** (non-negotiable for security)
   - Validate all Cypher queries contain patient_id filters before execution
   - Reject queries that could return cross-patient data
   - Log/alert on validation failures

2. **Evaluate Fixing WhereClauseBuilder**
   - The bug is specific to `STARTS WITH` / `ENDS WITH` detection
   - A targeted fix may be lower risk than full removal

3. **Define Security Test Plan**
   - Create test cases with multiple patients
   - Verify query isolation before and after changes
   - Automate as regression tests

### If Proceeding with Removal

1. **Phase the rollout**:
   - Phase 1: Add validation layer (safety net)
   - Phase 2: Update prompts with patient_id instructions
   - Phase 3: Remove TenantInjector (only after Phase 1-2 proven)

2. **Use parameterized patient_id** (`$patient_id`) not literal strings in prompts

3. **Add monitoring/alerting** for queries without patient_id filters

## Decision Required

| Option | Description | Risk Level |
|--------|-------------|------------|
| A | Proceed as planned (prompt-only) | **High** |
| B | Add validation layer first, then remove TenantInjector | Medium |
| C | Fix WhereClauseBuilder bug instead of removal | Low |
| D | Hybrid: Fix bug + add validation + improve prompts | **Lowest** |

**Recommendation**: Option D - Fix the immediate bug, add validation layer, improve prompts. Defer full TenantInjector removal until validation layer proves effective.

## Summary

The plan correctly identifies the problem but proposes a high-risk solution. Removing the safety net (TenantInjector) without adding a replacement validation layer changes failure modes from visible errors to silent data leakage.

**Key question**: Is a syntax error bug worse than potential cross-patient data exposure?

The syntax error is frustrating but safe. Data leakage is catastrophic.
