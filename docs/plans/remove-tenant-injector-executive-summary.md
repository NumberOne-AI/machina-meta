# Executive Summary: Replace TenantInjector with Neo4j RBAC

**Date**: 2026-01-23
**Revised**: 2026-01-23 (v2 - Neo4j RBAC Security Layer)
**Status**: PROPOSED
**Full Plan**: [remove-tenant-injector.md](remove-tenant-injector.md)
**Timeline**: ~10-12 days across 7 phases

## The Problem

The `TenantInjector` system uses regex to inject `WHERE patient_id = $patient_id` into Cypher queries. This approach breaks when queries contain multi-word operators like `STARTS WITH`:

```
BEFORE: WHERE name STARTS WITH "T"
AFTER:  WHERE (name STARTS) AND patient_id = $patient_id WITH "T"  ← BROKEN SYNTAX
```

**Impact**: All graph queries using string matching patterns fail on tusdi-preview-92 and other environments.

## Revised Solution: Defense in Depth

The v2 plan addresses security concerns by implementing **database-enforced** patient isolation rather than relying on application-level query manipulation or prompt engineering.

|   Layer | Location           | Purpose                                                                                                                                                                         |
|--------:|:-------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|       1 | Neo4j RBAC         | **PRIMARY SECURITY** - Per-patient users with property-based access control, impersonation for per-request security context, queries physically cannot return unauthorized data |
|       2 | Query Validation   | APPLICATION - Pre-execution check for patient_id, logging/alerting on suspicious patterns, does NOT block (RBAC handles security)                                               |
|       3 | Prompt Engineering | LLM - Instruct agents to include patient_id in queries, provides correct queries but NOT relied upon for security                                                               |

## Key Design: Neo4j RBAC with Impersonation

**How It Works**:

1. **Patient User Creation**: When patient created, create corresponding Neo4j user
2. **Property-Based DENY Rules**: User can only access nodes where `patient_id` matches
3. **Impersonation**: Application executes queries as patient-specific user
4. **Database Enforcement**: Neo4j filters results—cross-patient access is physically impossible

```python
# Query execution with impersonation
async with self.driver.session(
    database="healthcare",
    impersonated_user=f"patient_{patient_id}",  # ← DATABASE-LEVEL SECURITY
) as session:
    result = await session.run(query, parameters)
```

## Comparison: v1 vs v2

| Aspect              | v1 (Prompt-Only)   | v2 (Neo4j RBAC)                |
|:--------------------|:-------------------|:-------------------------------|
| **Security Layer**  | Application (LLM)  | Database (Neo4j)               |
| **Failure Mode**    | Silent data leak   | Query returns empty (secure)   |
| **LLM Reliability** | 100% dependence    | 0% dependence for security     |
| **Audit Trail**     | Application logs   | Database audit + impersonation |
| **Risk Level**      | **HIGH**           | **LOW**                        |

## Requirements

| Requirement              | Status     | Notes                                      |
|:-------------------------|:-----------|:-------------------------------------------|
| Neo4j Enterprise Edition | **VERIFY** | Required for property-based access control |
| Service account          | To create  | Needs IMPERSONATE privilege                |
| Per-patient users        | To create  | ~1 user per patient                        |

## Implementation Timeline

| Phase                        | Duration        | Description                              |
|:-----------------------------|:----------------|:-----------------------------------------|
| 1. RBAC Infrastructure       | 2-3 days        | Service account, base roles, auth config |
| 2. Patient User Management   | 2-3 days        | PatientUserManager, migration script     |
| 3. Impersonation Integration | 1-2 days        | Update GraphTraversalService             |
| 4. Query Validation          | 1 day           | Logging layer (secondary safety)         |
| 5. Prompt Updates + Cleanup  | 0.5 days        | Remove TenantInjector (~918 lines)       |
| 6. Testing                   | 2 days          | Security, regression, performance tests  |
| 7. Deployment                | 1 day           | Preview → Staging → Production           |
| **Total**                    | **~10-12 days** |                                          |

## Risk Assessment (v2)

| Risk                         | Likelihood   | Impact   | Mitigation                                     |
|:-----------------------------|:-------------|:---------|:-----------------------------------------------|
| Neo4j not Enterprise Edition | Medium       | High     | Verify before starting; plan upgrade if needed |
| Performance impact from RBAC | Low          | Medium   | < 10% target; monitor post-deployment          |
| User management complexity   | Low          | Low      | Automated via PatientUserManager               |
| Rollback needed              | Low          | Medium   | Keep TenantInjector in branch temporarily      |

## Success Criteria

1. **Security**: Cross-patient data access **physically impossible** at database level
2. **Functionality**: All queries work, including `STARTS WITH` patterns
3. **Performance**: < 10% latency increase
4. **Audit**: All queries logged with impersonated user identity
5. **Maintainability**: ~918 lines of fragile regex code removed

## Decision

The v2 plan addresses all critical concerns from the v1 review:

- ✅ **Security**: Database-enforced, not LLM-dependent
- ✅ **Validation Layer**: Added as secondary safety (logging/alerting)
- ✅ **Testing**: Explicit security tests for cross-patient isolation
- ✅ **Failure Mode**: Returns empty (safe), not data leak (catastrophic)

**Recommendation**: Proceed with v2 implementation pending Neo4j Enterprise Edition verification.

## Next Steps

1. **Verify Neo4j Edition**: `CALL dbms.components() YIELD edition`
2. If Enterprise: Begin Phase 1 (RBAC Infrastructure)
3. If Community: Plan upgrade path before proceeding

## Summary

The revised plan transforms patient isolation from a fragile regex-based application layer to a robust database-enforced security layer. Neo4j RBAC with impersonation ensures that even if an LLM generates a query without patient_id filters, the database will only return data the impersonated user is authorized to see.

**The key insight**: Move security enforcement from "fixing queries" to "restricting what queries can return."
