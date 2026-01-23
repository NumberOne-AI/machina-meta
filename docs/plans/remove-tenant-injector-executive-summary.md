# Executive Summary: Remove TenantInjector and Add Neo4j RBAC

**Date**: 2026-01-23
**Revised**: 2026-01-23 (v3 - Two-stage approach)
**Status**: PROPOSED
**Full Plan**: [remove-tenant-injector.md](remove-tenant-injector.md)
**Overall Difficulty**: Low-Medium (Stage 1), Medium-High (Stage 2)

## The Problem

The `TenantInjector` system uses regex to inject `WHERE patient_id = $patient_id` into Cypher queries. This approach breaks when queries contain multi-word operators like `STARTS WITH`:

```
BEFORE: WHERE name STARTS WITH "T"
AFTER:  WHERE (name STARTS) AND patient_id = $patient_id WITH "T"  ← BROKEN SYNTAX
```

**Impact**: All graph queries using string matching patterns fail on tusdi-preview-92 and other environments.

## Solution: Two-Stage Approach

| Stage       | Scope              | Status   | Description                                                 |
|:------------|:-------------------|:---------|:------------------------------------------------------------|
| **Stage 1** | Immediate Fix      | READY    | Remove TenantInjector, rely on prompt engineering + logging |
| **Stage 2** | Future Enhancement | DEFERRED | Add Neo4j RBAC as database-enforced safety net              |

### Why Two Stages?

**Stage 1** fixes the immediate bug (broken queries) without requiring Enterprise Edition licensing.

**Stage 2** adds database-level security as a safety net, but requires Neo4j Enterprise Edition which has significant licensing costs.

## Stage 1: Immediate Fix

### Approach

|   Layer | Location           | Type        | Purpose                                              |
|--------:|:-------------------|:------------|:-----------------------------------------------------|
|       1 | Query Validation   | APPLICATION | Log queries, alert on missing patient_id filters     |
|       2 | Prompt Engineering | LLM         | Instruct agents to include patient_id in all queries |

### Risk Acknowledgment

Running without Neo4j RBAC means:
- Security relies on correct prompt engineering
- A malformed query could potentially access cross-patient data
- Logging provides audit trail but not prevention
- **Acceptable for current scale and controlled access environment**

### Implementation Phases

| Phase                    | Difficulty   | Description                                   |
|:-------------------------|:-------------|:----------------------------------------------|
| 1. Prompt Updates        | Low          | Add patient_id injection and rules to prompts |
| 2. Query Validation      | Low          | Create logging validator class                |
| 3. Remove TenantInjector | Low          | Delete ~918 lines of regex code               |
| 4. Testing               | Medium       | Regression and prompt effectiveness tests     |
| 5. Deployment            | Low          | Preview → Staging → Production                |

### Stage 1 Success Criteria

1. **Functionality**: All queries work (including STARTS WITH patterns)
2. **Audit**: All queries logged with patient context
3. **Maintainability**: ~918 lines of fragile regex code removed

## Stage 2: Future Enhancement (Neo4j RBAC)

### Prerequisites

Property-based access control requires **Neo4j Enterprise Edition**.

**Current Status**: Running Community Edition

### What is PBAC?

**PBAC (Property-Based Access Control)** allows security rules based on node property values, not just labels.

```cypher
-- PBAC example: User can only see nodes where patient_id matches their ID
DENY TRAVERSE ON GRAPH
  FOR (n:ObservationValueNode) WHERE n.patient_id <> 'patient_123'
  TO patient_123_role
```

Without PBAC (Community Edition), the database cannot enforce that Patient A only sees Patient A's data—it returns all matching nodes regardless of `patient_id`. This is why Stage 2 requires Enterprise licensing.

### Cost Analysis

| Option                       | Estimated Cost   | Notes                                            |
|:-----------------------------|:-----------------|:-------------------------------------------------|
| **Self-Hosted Enterprise**   | ~$36,000+/year   | Starting price; large deployments $100,000+/year |
| **AuraDB Professional**      | $65/month        | Cloud-managed, may lack PBAC                     |
| **AuraDB Business Critical** | $146/month       | Enhanced security, 99.95% SLA                    |
| **AuraDB Virtual Dedicated** | Contact sales    | Enterprise-grade                                 |

**Recommendation**: Contact Neo4j sales for accurate pricing before proceeding.

**Sources**: [Neo4j Pricing](https://neo4j.com/pricing/), [G2 Pricing](https://www.g2.com/products/neo4j-graph-database/pricing), [Vendr Analysis](https://www.vendr.com/marketplace/neo4j)

### Stage 2 Phases (Future)

| Phase                        | Difficulty   | Description                          |
|:-----------------------------|:-------------|:-------------------------------------|
| 6. Neo4j Enterprise Upgrade  | Medium-High  | Procurement, infrastructure update   |
| 7. Patient User Management   | Medium       | PatientUserManager, migration script |
| 8. Impersonation Integration | Medium       | Update GraphTraversalService         |
| 9. RBAC Testing/Deployment   | Medium       | Security tests, staged rollout       |

### Stage 2 Success Criteria

1. **Security**: Cross-patient data access physically impossible at database level
2. **Performance**: < 10% latency increase from RBAC
3. **Audit**: All queries logged with impersonated user identity

## Requirements

| Requirement              | Stage 1       | Stage 2         |
|:-------------------------|:--------------|:----------------|
| Neo4j Community Edition  | ✅ Sufficient | ❌ Insufficient |
| Neo4j Enterprise Edition | Not required  | **REQUIRED**    |
| Budget approval          | Not required  | ~$36,000+/year  |

## Risk Assessment

| Risk                               |   Stage | Likelihood   | Impact   | Mitigation                                |
|:-----------------------------------|--------:|:-------------|:---------|:------------------------------------------|
| Prompt fails to include patient_id |       1 | Low          | Medium   | Query validation logging, monitoring      |
| Cross-patient data access          |       1 | Low          | High     | Controlled access environment, audit logs |
| Neo4j Enterprise too expensive     |       2 | Medium       | Medium   | Evaluate cloud options, defer Stage 2     |
| RBAC performance impact            |       2 | Low          | Medium   | Target < 10%, monitor post-deployment     |

## Decision

**Proceed with Stage 1 immediately** to fix the broken query functionality.

**Defer Stage 2** pending:
1. Contact Neo4j sales for accurate Enterprise pricing
2. Cost/benefit analysis based on patient scale projections
3. Security audit requirements

## Next Steps

### Stage 1 (Immediate)
1. Update CypherAgent prompts with patient_id injection rules
2. Create QuerySecurityValidator for logging
3. Remove TenantInjector code (~918 lines)
4. Test and deploy to preview-92

### Stage 2 (Future)
1. Contact Neo4j sales for enterprise pricing quote
2. Evaluate AuraDB vs self-hosted options
3. Budget approval if proceeding
4. Implement RBAC infrastructure

## Summary

The revised plan prioritizes **fixing the immediate bug** (Stage 1) while deferring the **database-level security enhancement** (Stage 2) pending cost analysis. This approach:

- ✅ Fixes broken STARTS WITH queries immediately
- ✅ Removes fragile regex code (~918 lines)
- ✅ Adds audit logging for security monitoring
- ⚠️ Accepts temporary reliance on prompt engineering for security
- 📋 Plans for future Neo4j RBAC when budget allows
