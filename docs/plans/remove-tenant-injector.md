# Plan: Replace TenantInjector with Neo4j RBAC Security

**Status**: PROPOSED
**Created**: 2026-01-23
**Revised**: 2026-01-23 (v2 - Added Neo4j RBAC security layer)
**Related Problem**: [PROBLEMS.md - Syntax errors caused by tenant patient_id query injection](../../PROBLEMS.md)
**Evidence Log**: [logs/tenant-injection-syntax-errors-2026-01-23.log](../../logs/tenant-injection-syntax-errors-2026-01-23.log)
**Executive Summary**: [remove-tenant-injector-executive-summary.md](remove-tenant-injector-executive-summary.md)

## Executive Summary

The current `TenantInjector` breaks Cypher queries containing `STARTS WITH`, `ENDS WITH`, etc. Rather than simply removing it and relying on prompt engineering (high risk), this revised plan implements **Neo4j Role-Based Access Control (RBAC)** as a database-enforced security layer.

**Key Change from v1**: Security is enforced at the database level, not the application level.

## The Problem (Unchanged)

`TenantInjector` uses regex to inject `WHERE patient_id = $patient_id` into Cypher queries. This breaks multi-word operators:

```
BEFORE: WHERE name STARTS WITH "T"
AFTER:  WHERE (name STARTS) AND patient_id = $patient_id WITH "T"  ← BROKEN
```

## Revised Solution: Defense in Depth

|   Layer | Location           | Type              | Purpose                                                            |
|--------:|:-------------------|:------------------|:-------------------------------------------------------------------|
|       1 | Neo4j RBAC         | DATABASE-ENFORCED | Per-patient users, property-based access, impersonation            |
|       2 | Query Validation   | APPLICATION       | Pre-execution checks, logging, alerting on suspicious patterns     |
|       3 | Prompt Engineering | LLM               | Instruct agents to include patient_id (not relied on for security) |

**Layer 1 Details** (Primary Security):
- Patient-specific users with property-based access control
- Impersonation for per-request security context
- Queries physically cannot return unauthorized data

**Layer 2 Details** (Secondary Safety):
- Pre-execution check for patient_id in queries
- Reject queries that could bypass security
- Logging and alerting on suspicious patterns

**Layer 3 Details** (Tertiary - Correctness):
- Instruct agents to include patient_id in generated queries
- Provides correct queries, but NOT relied upon for security

## Neo4j RBAC Architecture

### Overview

Neo4j Enterprise Edition provides fine-grained access control through:
- **Property-Based Access Control**: DENY/GRANT based on node property values
- **User Impersonation**: Execute queries in another user's security context
- **Role-Based Privileges**: Assign permissions to roles, roles to users

**References**:
- [Neo4j Role-Based Access Control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/)
- [Neo4j Property-Based Access Control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/property-based-access-control/)
- [Neo4j Impersonation](https://neo4j.com/docs/query-api/current/impersonation/)
- [Fine-Grained Access Control Tutorial](https://neo4j.com/docs/operations-manual/current/tutorial/access-control/)

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

### How It Works

1. **Patient User Creation**: When a patient is created in the system, create a corresponding Neo4j user
2. **Role Assignment**: Assign patient-specific role with property-based restrictions
3. **Query Execution**: Backend uses impersonation to execute queries as the patient user
4. **Database Enforcement**: Neo4j filters results based on the impersonated user's permissions

### RBAC Setup Commands

```cypher
// 1. Create base role for patient access
CREATE ROLE patient_base;

// 2. Grant read access to the healthcare graph
GRANT ACCESS ON DATABASE healthcare TO patient_base;
GRANT MATCH {*} ON GRAPH healthcare TO patient_base;

// 3. Create patient-specific user (done per-patient)
CREATE USER patient_abc123 SET PASSWORD 'generated_secure_password' CHANGE NOT REQUIRED;

// 4. Create patient-specific role with property restrictions
CREATE ROLE patient_abc123_role;
GRANT ROLE patient_base TO patient_abc123_role;

// 5. DENY access to other patients' data via property-based rules
DENY TRAVERSE ON GRAPH healthcare
  FOR (n:ObservationValueNode) WHERE n.patient_id <> 'abc123'
  TO patient_abc123_role;

DENY TRAVERSE ON GRAPH healthcare
  FOR (n:ConditionCaseNode) WHERE n.patient_id <> 'abc123'
  TO patient_abc123_role;

DENY TRAVERSE ON GRAPH healthcare
  FOR (n:SymptomEpisodeNode) WHERE n.patient_id <> 'abc123'
  TO patient_abc123_role;

// ... repeat for all patient-scoped node types

// 6. Assign role to user
GRANT ROLE patient_abc123_role TO patient_abc123;

// 7. Grant service account impersonation privilege
GRANT IMPERSONATE (patient_abc123) ON DBMS TO service_account;
```

### Python Driver Integration

```python
# In GraphTraversalService

async def execute_query(
    self,
    query: str,
    patient_id: str,
    parameters: dict | None = None,
) -> list[dict]:
    """Execute query with patient-scoped security context."""

    # Impersonate the patient-specific user
    patient_user = f"patient_{patient_id}"

    async with self.driver.session(
        database="healthcare",
        impersonated_user=patient_user,  # <-- KEY: Database-level security
    ) as session:
        result = await session.run(query, parameters or {})
        return [record.data() async for record in result]
```

### Patient-Scoped Node Types

Based on the graph schema, these nodes have `patient_id` property and need RBAC rules:

| Node Type                | Property              | DENY Rule Needed    |
|:-------------------------|:----------------------|:--------------------|
| `ObservationValueNode`   | `patient_id`          | Yes                 |
| `ConditionCaseNode`      | `patient_id`          | Yes                 |
| `SymptomEpisodeNode`     | `patient_id`          | Yes                 |
| `EncounterNode`          | `patient_id`          | Yes                 |
| `DocumentReferenceNode`  | `patient_id`          | Yes                 |
| `IntakeEventNode`        | `patient_id`          | Yes                 |
| `AllergyIntoleranceNode` | `patient_id`          | Yes                 |
| `PatientNode`            | `uuid` (special case) | Yes (match on uuid) |

### Shared/Type Nodes (No Restrictions)

These nodes are shared across patients (ontology/reference data):

| Node Type             | Reason                       |
|:----------------------|:-----------------------------|
| `ObservationTypeNode` | Shared biomarker definitions |
| `ConditionTypeNode`   | Shared condition definitions |
| `SymptomTypeNode`     | Shared symptom definitions   |
| `SubstanceNode`       | Shared substance catalog     |
| `MedicationNode`      | Shared medication catalog    |
| `SupplementNode`      | Shared supplement catalog    |
| `ReferenceRangeNode`  | Shared reference ranges      |
| `BodySystemNode`      | Shared body system ontology  |

## Implementation Plan

### Phase 1: Neo4j RBAC Infrastructure (Prerequisite)

**Estimated effort**: 2-3 days

1. **Verify Neo4j Enterprise Edition**
   - Check current deployment: `CALL dbms.components() YIELD edition`
   - Enterprise Edition required for property-based access control
   - If Community Edition, plan upgrade path

2. **Enable Authentication**
   ```
   # neo4j.conf
   dbms.security.auth_enabled=true
   dbms.security.procedures.unrestricted=apoc.*
   ```

3. **Create Service Account**
   ```cypher
   CREATE USER machina_service SET PASSWORD 'secure_password' CHANGE NOT REQUIRED;
   CREATE ROLE machina_service_role;
   GRANT ALL ON DATABASE healthcare TO machina_service_role;
   GRANT IMPERSONATE (*) ON DBMS TO machina_service_role;
   GRANT ROLE machina_service_role TO machina_service;
   ```

4. **Create Base Patient Role**
   ```cypher
   CREATE ROLE patient_base;
   GRANT ACCESS ON DATABASE healthcare TO patient_base;
   GRANT MATCH {*} ON GRAPH healthcare TO patient_base;
   ```

5. **Update Kubernetes Secrets**
   - Add `NEO4J_SERVICE_USER` and `NEO4J_SERVICE_PASSWORD`
   - Update deployment manifests

### Phase 2: Patient User Management

**Estimated effort**: 2-3 days

1. **Create Patient User Service**
   ```python
   # repos/dem2/shared/src/machina/shared/graph_traversal/patient_user_manager.py

   class PatientUserManager:
       """Manages Neo4j users for patient-level RBAC."""

       async def create_patient_user(self, patient_id: str) -> None:
           """Create Neo4j user and role for a patient."""

       async def delete_patient_user(self, patient_id: str) -> None:
           """Remove Neo4j user and role when patient deleted."""

       async def sync_all_patients(self) -> None:
           """Ensure all existing patients have Neo4j users."""
   ```

2. **Hook into Patient Creation**
   - Modify patient creation workflow to call `create_patient_user()`
   - Add migration script to create users for existing patients

3. **Generate DENY Rules per Patient**
   ```python
   def generate_patient_deny_rules(patient_id: str) -> list[str]:
       """Generate Cypher DENY statements for patient-scoped nodes."""
       patient_scoped_nodes = [
           "ObservationValueNode",
           "ConditionCaseNode",
           "SymptomEpisodeNode",
           "EncounterNode",
           "DocumentReferenceNode",
           "IntakeEventNode",
           "AllergyIntoleranceNode",
       ]

       rules = []
       for node_type in patient_scoped_nodes:
           rules.append(f"""
               DENY TRAVERSE ON GRAPH healthcare
               FOR (n:{node_type}) WHERE n.patient_id <> '{patient_id}'
               TO patient_{patient_id}_role
           """)

       # Special case for PatientNode (uses uuid, not patient_id)
       rules.append(f"""
           DENY TRAVERSE ON GRAPH healthcare
           FOR (n:PatientNode) WHERE n.uuid <> '{patient_id}'
           TO patient_{patient_id}_role
       """)

       return rules
   ```

### Phase 3: Impersonation Integration

**Estimated effort**: 1-2 days

1. **Update GraphTraversalService**
   ```python
   # repos/dem2/shared/src/machina/shared/graph_traversal/service.py

   class GraphTraversalService:
       def __init__(
           self,
           neo4j_driver: Any,
           validator: CypherValidator,
           formatter: GraphResultFormatter,
           # Remove: tenant_injector: TenantInjector,
       ):
           self.driver = neo4j_driver
           self.validator = validator
           self.formatter = formatter

       async def execute_query(
           self,
           query: str,
           patient_id: str,
           user_id: str,
           parameters: dict | None = None,
       ) -> list[dict]:
           """Execute query with patient-scoped security context."""

           # Validate query syntax
           validated_query = self.validator.validate(query)

           # Execute with impersonation (DATABASE-LEVEL SECURITY)
           patient_user = f"patient_{patient_id}"

           async with self.driver.session(
               database=self.database_name,
               impersonated_user=patient_user,
           ) as session:
               result = await session.run(validated_query, parameters or {})
               records = [record.data() async for record in result]

           return self.formatter.format(records)
   ```

2. **Update Driver Configuration**
   ```python
   # Update Neo4j driver to use service account
   driver = AsyncGraphDatabase.driver(
       uri=config.neo4j.uri,
       auth=(config.neo4j.service_user, config.neo4j.service_password),
   )
   ```

### Phase 4: Query Validation Layer (Secondary Safety)

**Estimated effort**: 1 day

1. **Add Query Validator**
   ```python
   # repos/dem2/shared/src/machina/shared/graph_traversal/query_validator.py

   class QuerySecurityValidator:
       """Validates queries have appropriate security constraints."""

       def validate_patient_scope(
           self,
           query: str,
           patient_id: str,
       ) -> ValidationResult:
           """
           Check if query references patient-scoped nodes appropriately.

           This is a SECONDARY safety check. Primary security is via RBAC.
           Logs warnings for queries that might indicate prompt issues.
           """
           # Parse query for patient-scoped node references
           # Log warning if no patient_id constraint found
           # Does NOT block execution (RBAC handles security)
   ```

### Phase 5: Prompt Updates (Tertiary Layer)

**Estimated effort**: 0.5 days

1. **Update CypherAgent Instructions**
   - Add patient_id injection via `{patient_id}` template
   - Simplify tenant scoping rules (no longer critical for security)
   - Focus on query correctness, not security

2. **Remove TenantInjector Code**
   - Delete `tenant_injector.py` (531 lines)
   - Delete `where_clause_builder.py` (387 lines)
   - Delete `test_tenant_injector.py`
   - Update imports in `service.py`

### Phase 6: Testing and Validation

**Estimated effort**: 2 days

1. **Security Tests**
   ```python
   async def test_cross_patient_access_denied():
       """Verify patient A cannot access patient B's data."""
       # Create two patients with observations
       # Query as patient A
       # Verify only patient A's data returned
       # Query for patient B's data explicitly
       # Verify empty result (not error - data appears non-existent)

   async def test_shared_data_accessible():
       """Verify type nodes are accessible to all patients."""
       # Query ObservationTypeNode as patient A
       # Verify results returned

   async def test_impersonation_context():
       """Verify impersonation sets correct security context."""
       # Execute query with impersonation
       # Verify audit log shows correct user
   ```

2. **Regression Tests**
   - All existing graph query tests
   - STARTS WITH / ENDS WITH / CONTAINS patterns
   - Complex multi-hop traversals

3. **Performance Tests**
   - Measure query latency with RBAC enabled
   - Compare to baseline without RBAC
   - Target: < 10% performance impact

### Phase 7: Deployment

**Estimated effort**: 1 day

1. **Preview Environment**
   - Deploy to tusdi-preview-92
   - Run security test suite
   - Manual verification

2. **Staging**
   - Deploy to tusdi-staging
   - Extended soak test (24-48 hours)
   - Performance monitoring

3. **Production**
   - Deploy to tusdi-prod
   - Gradual rollout if possible
   - Monitoring and alerting

## Requirements

### Neo4j Enterprise Edition

Property-based access control and impersonation require **Neo4j Enterprise Edition**.

**Current Status**: Verify with `CALL dbms.components() YIELD edition`

If Community Edition:
- Upgrade to Enterprise (licensing cost)
- Or use AuraDB Business Critical / Virtual Dedicated Cloud

### Configuration Changes

```
# neo4j.conf additions
dbms.security.auth_enabled=true
dbms.security.procedures.unrestricted=apoc.*
```

## Performance Considerations

From [Neo4j Documentation](https://neo4j.com/docs/operations-manual/current/authentication-authorization/property-based-access-control/):

> Performance impact depends on:
> - Number of properties on nodes/relationships (more = greater impact)
> - Number of property-based privileges (more = greater impact)
> - Type of privilege (TRAVERSE has greater impact than READ)

**Mitigations**:
- Use block storage format
- Minimize number of DENY rules per patient (use role inheritance)
- Monitor query performance after deployment
- Consider caching for frequently accessed shared data

## Scalability Considerations

### User Management at Scale

| Patients   | Neo4j Users   | Roles    | Consideration                   |
|:-----------|:--------------|:---------|:--------------------------------|
| 100        | 100           | 100      | No issues                       |
| 1,000      | 1,000         | 1,000    | Monitor memory                  |
| 10,000     | 10,000        | 10,000   | May need optimization           |
| 100,000+   | 100,000+      | 100,000+ | Consider alternative approaches |

**Alternatives for Very Large Scale**:
- Database-per-tenant (expensive, complex)
- Parameterized security rules (not supported in current Neo4j)
- Application-level security with audit logging (less secure)

## Rollback Plan

If RBAC deployment fails:

1. **Immediate**: Disable impersonation, revert to direct service account queries
2. **Short-term**: Re-enable TenantInjector (keep code in branch)
3. **Long-term**: Fix underlying issues and redeploy

## Files Changed

### New Files

| File                                                 | Purpose                   |
|:-----------------------------------------------------|:--------------------------|
| `shared/.../graph_traversal/patient_user_manager.py` | Neo4j user management     |
| `shared/.../graph_traversal/query_validator.py`      | Query security validation |
| `scripts/migrate_patient_users.py`                   | One-time migration script |

### Modified Files

| File                                    | Changes                                  |
|:----------------------------------------|:-----------------------------------------|
| `shared/.../graph_traversal/service.py` | Add impersonation, remove TenantInjector |
| `agents/CypherAgent/config.yml`         | Simplify tenant rules                    |
| `agents/CypherAgent/factory.py`         | Add patient_id to prompts                |
| `agents/CypherAgent/query_runner.py`    | Remove tenant preview logging            |
| Kubernetes manifests                    | Add service account secrets              |
| `neo4j.conf`                            | Enable authentication                    |

### Deleted Files

| File                      | Lines   | Reason                 |
|:--------------------------|:--------|:-----------------------|
| `tenant_injector.py`      | 531     | Replaced by RBAC       |
| `where_clause_builder.py` | 387     | Replaced by RBAC       |
| `test_tenant_injector.py` | ~200    | Tests for deleted code |

## Success Criteria

1. **Security**: Cross-patient data access physically impossible at database level
2. **Functionality**: All existing queries work (including STARTS WITH patterns)
3. **Performance**: < 10% latency increase
4. **Audit**: All queries logged with impersonated user identity
5. **Maintainability**: Simpler codebase without regex manipulation

## Timeline Summary

| Phase                        | Duration        | Dependencies     |
|:-----------------------------|:----------------|:-----------------|
| 1. RBAC Infrastructure       | 2-3 days        | Neo4j Enterprise |
| 2. Patient User Management   | 2-3 days        | Phase 1          |
| 3. Impersonation Integration | 1-2 days        | Phase 2          |
| 4. Query Validation          | 1 day           | Phase 3          |
| 5. Prompt Updates            | 0.5 days        | Phase 3          |
| 6. Testing                   | 2 days          | Phase 4, 5       |
| 7. Deployment                | 1 day           | Phase 6          |
| **Total**                    | **~10-12 days** |                  |

## References

- [Neo4j Role-Based Access Control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/)
- [Neo4j Property-Based Access Control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/property-based-access-control/)
- [Neo4j Fine-Grained Access Control Tutorial](https://neo4j.com/docs/operations-manual/current/tutorial/access-control/)
- [Neo4j Impersonation - Query API](https://neo4j.com/docs/query-api/current/impersonation/)
- [Neo4j Python Driver - Impersonation](https://neo4j.com/docs/python-manual/current/transactions/)
- [Neo4j Security Best Practices](https://neo4j.com/product/neo4j-graph-database/security/)
