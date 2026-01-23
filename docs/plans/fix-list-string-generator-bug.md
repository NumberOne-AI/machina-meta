# Plan: Fix Neo4j Node Generator list[string] Type Mapping Bug

**Created**: 2026-01-23
**Status**: PROPOSED
**Evidence**: [docs/evidence/EVIDENCE_list_string_generator_bug_20260123.md](../evidence/EVIDENCE_list_string_generator_bug_20260123.md)
**Related Problem**: PROBLEMS.md - "Neo4j generator list[string] type mapping bug"
**Related TODO**: TODO.md - "Fix Neo4j node generator list[string] type mapping"

---

## Executive Summary

The Neo4j node generator does not map `list[string]` schema types to `ArrayProperty(StringProperty())`, causing data corruption and Pydantic validation errors. This plan outlines a 4-phase approach to fix the generator, regenerate node classes, migrate corrupted data, and verify the fix.

---

## Phase 1: Fix Generator Type Mapping

**Objective**: Add `list[string]` support to the generator's type mapping.

### 1.1 Modify generator.py

**File**: `repos/dem2/services/graph-memory/src/machina/graph_memory/generator.py`

**Current code (lines 64-71):**
```python
type_map = {
    "string": ("StringProperty", "StringProperty"),
    "datetime": ("DateTimeProperty", "DateTimeProperty"),
    "float": ("FloatProperty", "FloatProperty"),
    "integer": ("IntegerProperty", "IntegerProperty"),
    "boolean": ("BooleanProperty", "BooleanProperty"),
    "list[float]": ("ArrayProperty", "ArrayProperty"),
}
```

**Fixed code:**
```python
type_map = {
    "string": ("StringProperty", "StringProperty"),
    "datetime": ("DateTimeProperty", "DateTimeProperty"),
    "float": ("FloatProperty", "FloatProperty"),
    "integer": ("IntegerProperty", "IntegerProperty"),
    "boolean": ("BooleanProperty", "BooleanProperty"),
    "list[float]": ("ArrayProperty", "ArrayProperty"),
    "list[string]": ("ArrayProperty(StringProperty())", "ArrayProperty, StringProperty"),
}
```

### 1.2 Update import handling

The generator also needs to handle the import for `ArrayProperty` and `StringProperty` when `list[string]` is used. Verify that `_collect_imports()` method handles composite imports correctly.

**Current behavior** (line 224-228):
```python
_, import_name = self.type_mapper.map_type(prop.type, prop.name)
if ", " in import_name:
    for imp in import_name.replace("from neomodel import ", "").split(", "):
        imports.add(imp)
```

This already handles comma-separated imports, so `"ArrayProperty, StringProperty"` will be split correctly.

### 1.3 Verification

After modification, verify:
```bash
# Check that list[string] maps correctly
(cd repos/dem2 && uv run python -c "
from machina.graph_memory.generator import TypeMapper
tm = TypeMapper()
print(tm.map_type('list[string]', 'test'))
# Expected: ('ArrayProperty(StringProperty())', 'ArrayProperty, StringProperty')
")
```

---

## Phase 2: Regenerate Node Classes

**Objective**: Regenerate all `nodes.py` files with corrected type mappings.

### 2.1 Run generator

```bash
(cd repos/dem2 && just graph-generate)
```

### 2.2 Verify generated output

Check that the affected fields are now `ArrayProperty(StringProperty())`:

```bash
grep -n "aggravating_factors\|relieving_factors\|associated_signs\|synonyms\|tags\|risk_factors\|complications\|related_symptoms\|unit_properties\|aliases" \
  repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/condition/nodes.py
```

**Expected output:**
```
97:    aggravating_factors = ArrayProperty(StringProperty())
98:    relieving_factors = ArrayProperty(StringProperty())
99:    associated_signs = ArrayProperty(StringProperty())
...
```

### 2.3 Run type checker

```bash
(cd repos/dem2 && uv run mypy)
```

Ensure no new type errors are introduced.

---

## Phase 3: Neo4j Data Migration

**Objective**: Convert existing corrupted string data to proper list format.

### 3.1 Create migration script

**File**: `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/migrations/migration_YYYYMMDD_fix_list_string_fields.py`

```python
"""
Migration: Fix list[string] fields stored as stringified lists.

This migration converts fields that were incorrectly stored as string
representations of Python lists (e.g., "['a', 'b']") to proper Neo4j arrays.

Affected fields:
- SymptomTypeNode: synonyms, tags, aggravating_factors, relieving_factors, associated_signs
- SymptomEpisodeNode: aggravating_factors, relieving_factors, associated_signs
- ConditionTypeNode: synonyms, tags, risk_factors, complications, related_symptoms
- ObservationTypeNode: unit_properties, aliases
"""

import ast
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Fields to migrate per node label
FIELDS_TO_MIGRATE = {
    "SymptomTypeNode": [
        "synonyms", "tags", "aggravating_factors",
        "relieving_factors", "associated_signs"
    ],
    "SymptomEpisodeNode": [
        "aggravating_factors", "relieving_factors", "associated_signs"
    ],
    "ConditionTypeNode": [
        "synonyms", "tags", "risk_factors",
        "complications", "related_symptoms"
    ],
    "ObservationTypeNode": [
        "unit_properties", "aliases"
    ],
}


def parse_stringified_list(value: str | list | None) -> list[str] | None:
    """Convert stringified list to actual list.

    Handles:
    - None -> None
    - Already a list -> return as-is
    - "['a', 'b']" -> ['a', 'b']
    - Empty string -> None
    """
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if not value or value.strip() == "":
        return None

    # Try to parse as Python literal
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass

    # If not parseable, treat as single-item list
    return [value]


async def migrate_node_fields(
    tx: Any,
    label: str,
    fields: list[str],
    dry_run: bool = False
) -> int:
    """Migrate fields for a specific node label."""

    # Build SET clause for all fields
    set_clauses = []
    for field in fields:
        set_clauses.append(f"n.{field} = $migrated_{field}")

    # Query to find nodes with stringified list values
    # Check if field is a string starting with '['
    where_conditions = " OR ".join([
        f"(n.{field} IS NOT NULL AND n.{field} STARTS WITH '[')"
        for field in fields
    ])

    query = f"""
    MATCH (n:{label})
    WHERE {where_conditions}
    RETURN n, id(n) as node_id
    """

    result = await tx.run(query)
    records = await result.data()

    migrated_count = 0
    for record in records:
        node = record["n"]
        node_id = record["node_id"]

        # Prepare migrated values
        params = {"node_id": node_id}
        needs_update = False

        for field in fields:
            value = node.get(field)
            migrated = parse_stringified_list(value)
            params[f"migrated_{field}"] = migrated

            if value != migrated:
                needs_update = True
                logger.debug(
                    f"Node {node_id}: {field} '{value}' -> {migrated}"
                )

        if needs_update and not dry_run:
            update_query = f"""
            MATCH (n:{label})
            WHERE id(n) = $node_id
            SET {', '.join(set_clauses)}
            """
            await tx.run(update_query, params)
            migrated_count += 1
        elif needs_update:
            migrated_count += 1

    return migrated_count


async def run_migration(session: Any, dry_run: bool = False) -> dict[str, int]:
    """Run the full migration."""

    results = {}

    async with session.begin_transaction() as tx:
        for label, fields in FIELDS_TO_MIGRATE.items():
            count = await migrate_node_fields(tx, label, fields, dry_run)
            results[label] = count
            logger.info(
                f"{'[DRY RUN] ' if dry_run else ''}"
                f"Migrated {count} {label} nodes"
            )

        if not dry_run:
            await tx.commit()

    return results
```

### 3.2 Add migration to migrations registry

Register the migration in the migrations index so it runs during startup or via CLI.

### 3.3 Test migration locally

```bash
# Dry run first
(cd repos/dem2 && uv run python -c "
import asyncio
from machina.graph_memory.medical.graph.migrations.migration_YYYYMMDD_fix_list_string_fields import run_migration
# ... setup session ...
results = asyncio.run(run_migration(session, dry_run=True))
print(results)
")

# Then actual run
(cd repos/dem2 && uv run python -c "
# ... same but with dry_run=False ...
")
```

---

## Phase 4: Verification and Testing

### 4.1 Unit tests for generator

Add test case for `list[string]` mapping:

**File**: `repos/dem2/services/graph-memory/tests/test_generator.py`

```python
def test_list_string_type_mapping():
    """Verify list[string] maps to ArrayProperty(StringProperty())."""
    from machina.graph_memory.generator import TypeMapper

    tm = TypeMapper()
    prop_class, import_name = tm.map_type("list[string]", "test_field")

    assert prop_class == "ArrayProperty(StringProperty())"
    assert "ArrayProperty" in import_name
    assert "StringProperty" in import_name
```

### 4.2 Integration test for symptom processing

Verify symptom processing works end-to-end after fix:

```bash
# Start dev stack
just dev-up

# Create test symptom with list fields
(cd repos/dem2 && just curl_api '{"function": "query_agent", "query": "I have a headache that gets worse with bright lights and loud noises, and gets better with rest and dark rooms."}')

# Check logs for validation errors
grep "validation errors for SymptomType" repos/dem2/logs/app.log | tail -5
# Should show no new errors
```

### 4.3 Verify data in Neo4j

```bash
# Query symptom nodes to verify list format
just neo4j-query "
MATCH (st:SymptomTypeNode)
WHERE st.aggravating_factors IS NOT NULL
RETURN st.name, st.aggravating_factors,
       apoc.meta.type(st.aggravating_factors) as type
LIMIT 5
"
# type should be 'LIST OF STRING', not 'STRING'
```

---

## Rollback Plan

If issues are discovered after deployment:

### Generator rollback
```bash
git revert <commit-hash-of-generator-fix>
(cd repos/dem2 && just graph-generate)
```

### Migration rollback
Create reverse migration that converts arrays back to strings (not recommended, but possible):
```cypher
MATCH (n:SymptomTypeNode)
WHERE apoc.meta.type(n.aggravating_factors) = 'LIST OF STRING'
SET n.aggravating_factors = toString(n.aggravating_factors)
```

---

## Deployment Checklist

- [ ] **Phase 1**: Fix generator.py
  - [ ] Add `list[string]` to type_map
  - [ ] Verify import handling works
  - [ ] Run local type mapping test

- [ ] **Phase 2**: Regenerate nodes
  - [ ] Run `just graph-generate`
  - [ ] Verify all 15 fields are now ArrayProperty
  - [ ] Run `uv run mypy` - no new errors
  - [ ] Commit generator fix + regenerated nodes

- [ ] **Phase 3**: Data migration
  - [ ] Create migration script
  - [ ] Test with dry_run=True locally
  - [ ] Test with dry_run=False locally
  - [ ] Commit migration script

- [ ] **Phase 4**: Verification
  - [ ] Add generator unit test
  - [ ] Run integration test for symptom processing
  - [ ] Verify Neo4j data types are correct
  - [ ] Monitor logs for validation errors

- [ ] **Deployment**
  - [ ] Deploy to preview environment
  - [ ] Run migration on preview Neo4j
  - [ ] Verify symptom processing works
  - [ ] Deploy to production
  - [ ] Run migration on production Neo4j
  - [ ] Monitor for errors

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Migration corrupts data | Low | High | Dry-run first, backup Neo4j before migration |
| Type change breaks existing code | Medium | Medium | Run full test suite before deployment |
| Migration takes too long | Low | Low | Run during maintenance window |
| Some fields have invalid stringified data | Medium | Low | `parse_stringified_list()` handles edge cases |

---

## Time Estimate

| Phase | Estimated Time |
|-------|---------------|
| Phase 1: Fix generator | 15 minutes |
| Phase 2: Regenerate nodes | 5 minutes |
| Phase 3: Data migration | 30 minutes (including testing) |
| Phase 4: Verification | 30 minutes |
| **Total** | ~1.5 hours |

---

## Dependencies

- Neo4j database access (local dev and target environments)
- APOC plugin for Neo4j (for `apoc.meta.type()` verification)
- `just` command runner configured
- `uv` package manager configured
