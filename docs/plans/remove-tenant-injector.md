# Plan: Remove TenantInjector and Add Neo4j RBAC Security

**Status**: PROPOSED
**Created**: 2026-01-23
**Revised**: 2026-01-23 (v3 - Two-stage approach: immediate fix + future RBAC)
**Related Problem**: [PROBLEMS.md - Syntax errors caused by tenant patient_id query injection](../../PROBLEMS.md)
**Evidence Log**: [logs/tenant-injection-syntax-errors-2026-01-23.log](../../logs/tenant-injection-syntax-errors-2026-01-23.log)
**Executive Summary**: [remove-tenant-injector-executive-summary.md](remove-tenant-injector-executive-summary.md)

## Executive Summary

The current `TenantInjector` breaks Cypher queries containing `STARTS WITH`, `ENDS WITH`, etc. This plan implements a **two-stage approach**:

1. **Stage 1 (Immediate)**: Remove TenantInjector and rely on prompt engineering + query validation logging
2. **Stage 2 (Future)**: Add Neo4j RBAC as database-enforced security layer (requires Enterprise Edition)

**Current Status**: Running Neo4j Community Edition. Stage 1 proceeds immediately; Stage 2 deferred pending cost/benefit analysis of Enterprise upgrade.

## The Problem

`TenantInjector` uses regex to inject `WHERE patient_id = $patient_id` into Cypher queries. This breaks multi-word operators:

```
BEFORE: WHERE name STARTS WITH "T"
AFTER:  WHERE (name STARTS) AND patient_id = $patient_id WITH "T"  ← BROKEN
```

## Solution Architecture: Defense in Depth

|   Layer | Location           | Type        | Status   | Purpose                                                        |
|--------:|:-------------------|:------------|:---------|:---------------------------------------------------------------|
|       1 | Neo4j RBAC         | DATABASE    | Future   | Per-patient users, property-based access, impersonation        |
|       2 | Query Validation   | APPLICATION | Stage 1  | Pre-execution checks, logging, alerting on suspicious patterns |
|       3 | Prompt Engineering | LLM         | Stage 1  | Instruct agents to include patient_id in all queries           |

**Stage 1 (Immediate)**: Layers 2 and 3 only - application-level security with logging
**Stage 2 (Future)**: Layer 1 added - database-enforced security as safety net

### Risk Acknowledgment (Stage 1)

Running without Neo4j RBAC means:
- Security relies on correct prompt engineering and query validation
- A malformed or malicious query could potentially access cross-patient data
- Logging provides audit trail but not prevention
- Acceptable for current scale and controlled access environment

---

# STAGE 1: Immediate Fix (Prompt Engineering + Logging)

## Phase 1: Prompt Updates

**Technical difficulty**: Low (config updates and template changes)

1. **Update CypherAgent Instructions**
   - Add patient_id injection via `{patient_id}` template variable (from ADK state)
   - Add explicit rules: "ALWAYS include `WHERE patient_id = '{patient_id}'` for patient-scoped nodes"
   - List patient-scoped node types in prompt

2. **Patient-Scoped Nodes** (must always filter by patient_id):
   - `ObservationValueNode`
   - `ConditionCaseNode`
   - `SymptomEpisodeNode`
   - `EncounterNode`
   - `DocumentReferenceNode`
   - `IntakeEventNode`
   - `AllergyIntoleranceNode`
   - `PatientNode` (filter by `uuid`)

3. **Shared Nodes** (no patient filter needed):
   - `ObservationTypeNode`, `ConditionTypeNode`, `SymptomTypeNode`
   - `SubstanceNode`, `MedicationNode`, `SupplementNode`
   - `ReferenceRangeNode`, `BodySystemNode`

## Phase 2: Query Validation Layer

**Technical difficulty**: Low (straightforward logging class)

1. **Create Query Validator**
   ```python
   # repos/dem2/shared/src/machina/shared/graph_traversal/query_validator.py

   class QuerySecurityValidator:
       """Validates queries have appropriate patient_id constraints."""

       PATIENT_SCOPED_NODES = [
           "ObservationValueNode", "ConditionCaseNode", "SymptomEpisodeNode",
           "EncounterNode", "DocumentReferenceNode", "IntakeEventNode",
           "AllergyIntoleranceNode", "PatientNode",
       ]

       def validate_patient_scope(
           self,
           query: str,
           patient_id: str,
       ) -> ValidationResult:
           """
           Check if query references patient-scoped nodes with patient_id filter.

           Does NOT block execution - logs warnings for investigation.
           """
           # Check for patient-scoped node references
           # Log WARNING if node referenced without patient_id filter
           # Log INFO with query details for audit trail
           # Return validation result (always allows execution)
   ```

2. **Integrate into GraphTraversalService**
   - Call validator before executing query
   - Log validation results
   - Continue with execution regardless (logging only)

## Phase 3: Remove TenantInjector Code

**Technical difficulty**: Low (code deletion and import cleanup)

1. **Delete Files** (~918 lines removed):
   - `repos/dem2/shared/src/machina/shared/graph_traversal/tenant_injector.py` (531 lines)
   - `repos/dem2/shared/src/machina/shared/graph_traversal/where_clause_builder.py` (387 lines)
   - `repos/dem2/shared/tests/graph_traversal/test_tenant_injector.py` (~200 lines)

2. **Update GraphTraversalService**
   - Remove TenantInjector from constructor
   - Remove tenant injection call before query execution
   - Add QuerySecurityValidator integration

3. **Update Imports**
   - Remove TenantInjector imports from `__init__.py`
   - Update any files that imported these modules

## Phase 4: Testing and Validation

**Technical difficulty**: Medium (comprehensive test coverage)

1. **Regression Tests**
   - Verify `STARTS WITH` / `ENDS WITH` / `CONTAINS` patterns work
   - Verify all existing graph queries still function
   - Test complex multi-hop traversals

2. **Prompt Effectiveness Tests**
   - Verify CypherAgent generates queries with patient_id filters
   - Test various query patterns
   - Log and review any validation warnings

3. **Audit Log Verification**
   - Verify all queries are logged with patient context
   - Verify validation warnings are captured

## Phase 5: Deployment (Stage 1)

**Technical difficulty**: Low (standard deployment)

1. **Preview Environment** (tusdi-preview-92)
   - Deploy prompt updates and TenantInjector removal
   - Monitor for validation warnings
   - Manual testing of agent queries

2. **Staging** (tusdi-staging)
   - Extended monitoring
   - Review audit logs for anomalies

3. **Production** (tusdi-prod)
   - Deploy with enhanced monitoring
   - Set up alerts for validation warnings

## Stage 1 Files Changed

### New Files

| File                                            | Purpose                      |
|:------------------------------------------------|:-----------------------------|
| `shared/.../graph_traversal/query_validator.py` | Query validation and logging |

### Modified Files

| File                                    | Changes                              |
|:----------------------------------------|:-------------------------------------|
| `shared/.../graph_traversal/service.py` | Remove TenantInjector, add validator |
| `agents/CypherAgent/config.yml`         | Add patient_id injection and rules   |
| `agents/CypherAgent/factory.py`         | Add patient_id to prompt context     |

### Deleted Files

| File                      | Lines   | Reason                   |
|:--------------------------|:--------|:-------------------------|
| `tenant_injector.py`      | 531     | Replaced by prompt rules |
| `where_clause_builder.py` | 387     | Replaced by prompt rules |
| `test_tenant_injector.py` | ~200    | Tests for deleted code   |

## Stage 1 Phase Summary

| Phase                    | Difficulty   | Dependencies   |
|:-------------------------|:-------------|:---------------|
| 1. Prompt Updates        | Low          | None           |
| 2. Query Validation      | Low          | None           |
| 3. Remove TenantInjector | Low          | Phase 1, 2     |
| 4. Testing               | Medium       | Phase 3        |
| 5. Deployment            | Low          | Phase 4        |

---

# STAGE 2: Future Enhancement (Neo4j RBAC)

## Prerequisites

### Neo4j Enterprise Edition Required

Property-based access control and impersonation require **Neo4j Enterprise Edition**.

**Current Status**: Running Community Edition

**Verification Command**: `CALL dbms.components() YIELD edition`

### What is PBAC and Why It Matters

**PBAC = Property-Based Access Control**

PBAC is a Neo4j Enterprise feature that allows security rules based on node/relationship property values, not just labels.

**Standard RBAC (Community Edition):**
```cypher
-- Can only grant/deny access by label
GRANT READ ON GRAPH FOR (n:PatientData) TO some_role
-- Result: All users with this role see ALL PatientData nodes
```

**PBAC (Enterprise Edition):**
```cypher
-- Can grant/deny access based on property values
DENY TRAVERSE ON GRAPH
  FOR (n:ObservationValueNode) WHERE n.patient_id <> 'patient_123'
  TO patient_123_role
-- Result: User only sees nodes where patient_id matches their ID
```

**Why PBAC matters for patient isolation:**

Without PBAC, we cannot enforce at the database level that Patient A only sees Patient A's data. The database returns all matching nodes regardless of `patient_id` value.

| Feature                      | Community   | Enterprise   |
|:-----------------------------|:------------|:-------------|
| Label-based access control   | ✅          | ✅           |
| Property-based access (PBAC) | ❌          | ✅           |
| User impersonation           | ❌          | ✅           |

For Stage 2 to work, we need PBAC to create rules like "this user can only traverse nodes where `patient_id` equals their ID." This is the key feature that requires Enterprise licensing.

**Stage 1 workaround**: We rely on the LLM generating correct queries with `WHERE patient_id = 'X'` clauses, validated by logging. Less secure than database enforcement, but works without Enterprise licensing.

### Cost Analysis

Based on [Neo4j Pricing](https://neo4j.com/pricing/) research:

| Option                       | Estimated Cost           | Notes                                                                    |
|:-----------------------------|:-------------------------|:-------------------------------------------------------------------------|
| **Self-Hosted Enterprise**   | ~$36,000+/year           | Starting price; varies by scale. Large deployments can be $100,000+/year |
| **AuraDB Professional**      | $65/month ($780/year)    | Cloud-managed, may not include property-based access control             |
| **AuraDB Business Critical** | $146/month ($1,752/year) | Enhanced security features, 99.95% SLA                                   |
| **AuraDB Virtual Dedicated** | Contact sales            | Enterprise-grade, isolated environment                                   |
| **Developer License**        | Free                     | Single machine only (Neo4j Desktop)                                      |

**Key Considerations**:
- Self-hosted Enterprise requires annual subscription based on server count/size
- Property-based access control (PBAC) requires Enterprise tier
- Impersonation requires Enterprise tier
- Cloud options may have different feature availability per tier

**Recommendation**: Before proceeding with Stage 2, contact Neo4j sales for accurate pricing based on our deployment (GKE, expected patient count, performance requirements).

**Sources**:
- [Neo4j Pricing Page](https://neo4j.com/pricing/)
- [Neo4j G2 Pricing](https://www.g2.com/products/neo4j-graph-database/pricing)
- [Vendr Neo4j Analysis](https://www.vendr.com/marketplace/neo4j)

## Neo4j RBAC Architecture

### Overview

Neo4j Enterprise Edition provides fine-grained access control through:
- **Property-Based Access Control**: DENY/GRANT based on node property values
- **User Impersonation**: Execute queries in another user's security context
- **Role-Based Privileges**: Assign permissions to roles, roles to users

### Approach: User-per-Patient with Impersonation

```
                    ┌──────────────────┐
                    │   Application    │
                    │  (service user)  │
                    └────────┬─────────┘
                             │ impersonated_user=patient_<uuid>
                             ▼
                    ┌──────────────────┐
                    │     Neo4j        │
                    │  (RBAC enforced) │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │patient_│    │patient_│    │patient_│
         │  abc   │    │  def   │    │  xyz   │
         └────────┘    └────────┘    └────────┘
              │              │              │
              ▼              ▼              ▼
         Only sees      Only sees      Only sees
         patient_id=    patient_id=    patient_id=
         "abc" data     "def" data     "xyz" data
```

### RBAC Setup Commands

```cypher
// 1. Create base role for patient access
CREATE ROLE patient_base;
GRANT ACCESS ON DATABASE healthcare TO patient_base;
GRANT MATCH {*} ON GRAPH healthcare TO patient_base;

// 2. Create patient-specific user
CREATE USER patient_abc123 SET PASSWORD 'generated_secure_password' CHANGE NOT REQUIRED;

// 3. Create patient-specific role with property restrictions
CREATE ROLE patient_abc123_role;
GRANT ROLE patient_base TO patient_abc123_role;

// 4. DENY access to other patients' data
DENY TRAVERSE ON GRAPH healthcare
  FOR (n:ObservationValueNode) WHERE n.patient_id <> 'abc123'
  TO patient_abc123_role;

// ... repeat for all patient-scoped node types

// 5. Assign role to user
GRANT ROLE patient_abc123_role TO patient_abc123;

// 6. Grant service account impersonation privilege
GRANT IMPERSONATE (patient_abc123) ON DBMS TO service_account;
```

### Python Driver Integration

```python
async def execute_query(
    self,
    query: str,
    patient_id: str,
    parameters: dict | None = None,
) -> list[dict]:
    """Execute query with patient-scoped security context."""

    patient_user = f"patient_{patient_id}"

    async with self.driver.session(
        database="healthcare",
        impersonated_user=patient_user,  # <-- DATABASE-LEVEL SECURITY
    ) as session:
        result = await session.run(query, parameters or {})
        return [record.data() async for record in result]
```

## Stage 2 Implementation Phases

### Phase 6: Neo4j Enterprise Upgrade

**Technical difficulty**: Medium-High (infrastructure change + licensing)

1. **Procurement**
   - Contact Neo4j sales for enterprise pricing
   - Evaluate self-hosted vs AuraDB options
   - Budget approval

2. **Infrastructure Update**
   - Update Neo4j deployment to Enterprise Edition
   - Enable authentication in neo4j.conf
   - Update Kubernetes manifests

3. **Service Account Setup**
   ```cypher
   CREATE USER machina_service SET PASSWORD 'secure_password' CHANGE NOT REQUIRED;
   CREATE ROLE machina_service_role;
   GRANT ALL ON DATABASE healthcare TO machina_service_role;
   GRANT IMPERSONATE (*) ON DBMS TO machina_service_role;
   GRANT ROLE machina_service_role TO machina_service;
   ```

### Phase 7: Patient User Management

**Technical difficulty**: Medium (new service with workflow integration)

1. **Create PatientUserManager**
   ```python
   class PatientUserManager:
       """Manages Neo4j users for patient-level RBAC."""

       async def create_patient_user(self, patient_id: str) -> None:
           """Create Neo4j user and role for a patient."""

       async def delete_patient_user(self, patient_id: str) -> None:
           """Remove Neo4j user and role when patient deleted."""

       async def sync_all_patients(self) -> None:
           """Ensure all existing patients have Neo4j users."""
   ```

2. **Hook into Patient Creation Workflow**
3. **Migration Script for Existing Patients**

### Phase 8: Impersonation Integration

**Technical difficulty**: Medium (service refactoring)

1. **Update GraphTraversalService**
   - Add impersonation to query execution
   - Update driver configuration for service account

2. **Update QuerySecurityValidator**
   - Change from logging-only to logging + RBAC verification
   - Verify impersonation is active

### Phase 9: RBAC Testing and Deployment

**Technical difficulty**: Medium (security testing)

1. **Security Tests**
   - Verify cross-patient access denied at database level
   - Verify shared data still accessible
   - Verify impersonation audit trail

2. **Performance Tests**
   - Measure RBAC overhead (target: < 10% latency increase)

3. **Staged Deployment**
   - Preview → Staging → Production

## Stage 2 Files Changed

### New Files

| File                                                 | Purpose                   |
|:-----------------------------------------------------|:--------------------------|
| `shared/.../graph_traversal/patient_user_manager.py` | Neo4j user management     |
| `scripts/migrate_patient_users.py`                   | One-time migration script |

### Modified Files

| File                                            | Changes                     |
|:------------------------------------------------|:----------------------------|
| `shared/.../graph_traversal/service.py`         | Add impersonation           |
| `shared/.../graph_traversal/query_validator.py` | Add RBAC verification       |
| Kubernetes manifests                            | Add service account secrets |
| `neo4j.conf`                                    | Enable authentication       |

## Stage 2 Phase Summary

| Phase                        | Difficulty   | Dependencies              |
|:-----------------------------|:-------------|:--------------------------|
| 6. Neo4j Enterprise Upgrade  | Medium-High  | Budget approval, planning |
| 7. Patient User Management   | Medium       | Phase 6                   |
| 8. Impersonation Integration | Medium       | Phase 7                   |
| 9. RBAC Testing/Deployment   | Medium       | Phase 8                   |

---

## Overall Success Criteria

### Stage 1 Success
1. **Functionality**: All queries work (including STARTS WITH patterns)
2. **Audit**: All queries logged with patient context
3. **Maintainability**: ~918 lines of fragile regex code removed
4. **Monitoring**: Validation warnings alert on suspicious queries

### Stage 2 Success (Future)
1. **Security**: Cross-patient data access physically impossible at database level
2. **Performance**: < 10% latency increase from RBAC
3. **Audit**: All queries logged with impersonated user identity

## Rollback Plan

### Stage 1 Rollback
If prompt-based approach causes issues:
- Re-enable TenantInjector from git branch
- Investigate specific failing query patterns
- Adjust prompt engineering

### Stage 2 Rollback
If RBAC deployment fails:
- Disable impersonation
- Revert to Stage 1 (prompt-only) approach
- Investigate RBAC issues

## References

- [Neo4j Pricing](https://neo4j.com/pricing/)
- [Neo4j Role-Based Access Control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/)
- [Neo4j Property-Based Access Control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/property-based-access-control/)
- [Neo4j Impersonation](https://neo4j.com/docs/query-api/current/impersonation/)
- [Neo4j Fine-Grained Access Control Tutorial](https://neo4j.com/docs/operations-manual/current/tutorial/access-control/)
