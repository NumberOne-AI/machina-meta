# Evidence: Neo4j Node Generator list[string] Type Mapping Bug

**Date**: 2026-01-23
**Severity**: HIGH
**Status**: INVESTIGATING
**Reporter**: Claude Code analysis of app.log errors

---

## Summary

The Neo4j node generator (`generator.py`) does not correctly map `list[string]` schema types to Neo4j `ArrayProperty(StringProperty())`. Instead, it falls back to `StringProperty()`, causing list data to be stored as stringified Python list representations (e.g., `"['a', 'b']"`) instead of proper Neo4j arrays.

When reading data back, Pydantic models expect `list[str]` but receive strings, causing validation errors.

---

## Error Evidence

### Log Entries (repos/dem2/logs/app.log)

**Error 1** - Line 14402 (2026-01-23 02:37:48):
```
machina.medical_data_engine.engine.processors.symptom - ERROR - {
  'name': 'bad breath',
  'error': '3 validation errors for SymptomType
    aggravating_factors
      Input should be a valid list [type=list_type, input_value="[\'nerve compression\', \'cold\']", input_type=str]
    relieving_factors
      Input should be a valid list [type=list_type, input_value="[\'changing position\', \'warming\']", input_type=str]
    associated_signs
      Input should be a valid list [type=list_type, input_value="[\'tingling\', \'numbness\', \'burning sensation\']", input_type=str]',
  'event': 'symptom_processing_failed'
}
```

**Error 2** - Line 15892 (2026-01-23 03:15:46):
```
machina.medical_data_engine.engine.processors.symptom - ERROR - {
  'name': 'tingling sensation in spleen',
  'error': '3 validation errors for SymptomType...'
}
```

**Error 3** - Line 19612 (2026-01-23 18:05:59):
```
machina.medical_data_engine.engine.processors.symptom - ERROR - {
  'name': 'Migraine',
  'error': '3 validation errors for SymptomType...'
}
```

**Total occurrences**: 128 `SymptomType` validation errors in current log file.

### Stack Trace

```
File "services/medical-data-engine/src/machina/medical_data_engine/engine/processors/symptom.py", line 90, in _process_single_resource
    existing_episode, merged_data, type_node = await self.find_in_storage(...)
File "services/medical-data-engine/src/machina/medical_data_engine/engine/processors/symptom.py", line 430, in find_in_storage
    (self.service.node_to_symptom_type(node), score, node.uuid)
File "services/graph-memory/src/machina/graph_memory/medical/graph/condition/symptom.py", line 610, in node_to_symptom_type
    return SymptomType(
        name=node.name,
        ...
        aggravating_factors=node.aggravating_factors,
        relieving_factors=node.relieving_factors,
        associated_signs=node.associated_signs,
    )
pydantic_core._pydantic_core.ValidationError: 3 validation errors for SymptomType
```

---

## Root Cause Analysis

### 1. Schema Definition (Correct)

**File**: `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/schema.yml`

```yaml
# Lines 188-190 (SymptomTypeNode)
aggravating_factors: {type: "list[string]", required: false}
relieving_factors: {type: "list[string]", required: false}
associated_signs: {type: "list[string]", required: false}

# Lines 222-224 (SymptomEpisodeNode)
aggravating_factors: { type: "list[string]", required: false }
relieving_factors:   { type: "list[string]", required: false }
associated_signs:    { type: "list[string]", required: false }
```

The schema correctly defines these as `list[string]`.

### 2. Generated Node Definition (Incorrect)

**File**: `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/condition/nodes.py`

```python
# Lines 97-99 (SymptomTypeNode)
aggravating_factors = StringProperty()  # WRONG: Should be ArrayProperty(StringProperty())
relieving_factors = StringProperty()    # WRONG: Should be ArrayProperty(StringProperty())
associated_signs = StringProperty()     # WRONG: Should be ArrayProperty(StringProperty())

# Lines 133-135 (SymptomEpisodeNode)
aggravating_factors = StringProperty()  # WRONG
relieving_factors = StringProperty()    # WRONG
associated_signs = StringProperty()     # WRONG
```

### 3. Generator Type Mapping (Bug Location)

**File**: `repos/dem2/services/graph-memory/src/machina/graph_memory/generator.py`

```python
# Lines 64-75
type_map = {
    "string": ("StringProperty", "StringProperty"),
    "datetime": ("DateTimeProperty", "DateTimeProperty"),
    "float": ("FloatProperty", "FloatProperty"),
    "integer": ("IntegerProperty", "IntegerProperty"),
    "boolean": ("BooleanProperty", "BooleanProperty"),
    "list[float]": ("ArrayProperty", "ArrayProperty"),  # Only list[float] handled!
    # MISSING: "list[string]" mapping
}

prop_class, import_name = type_map.get(
    prop_type, ("StringProperty", "StringProperty")  # Falls back to StringProperty!
)
```

The `type_map` handles `list[float]` → `ArrayProperty` but does NOT handle `list[string]`.
Unknown types fall back to `StringProperty`, causing the bug.

### 4. Pydantic Model (Correct)

**File**: `repos/dem2/packages/medical-types/src/machina/medical_types/symptom.py`

```python
# Lines 296-320 (SymptomType)
class SymptomType(BaseModel):
    aggravating_factors: list[str] | None = Field(...)  # Expects list[str]
    relieving_factors: list[str] | None = Field(...)    # Expects list[str]
    associated_signs: list[str] | None = Field(...)     # Expects list[str]
```

---

## Full Scope of Affected Fields

**15 fields across 5 node types** are affected by this bug:

| Node Type | Field Name | Schema Type | Generated As | Should Be |
|-----------|------------|-------------|--------------|-----------|
| ConditionTypeNode | `synonyms` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| ConditionTypeNode | `tags` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| ConditionTypeNode | `risk_factors` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| ConditionTypeNode | `complications` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| ConditionTypeNode | `related_symptoms` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomTypeNode | `synonyms` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomTypeNode | `tags` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomTypeNode | `aggravating_factors` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomTypeNode | `relieving_factors` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomTypeNode | `associated_signs` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomEpisodeNode | `aggravating_factors` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomEpisodeNode | `relieving_factors` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| SymptomEpisodeNode | `associated_signs` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| ObservationTypeNode | `unit_properties` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |
| ObservationTypeNode | `aliases` | `list[string]` | `StringProperty()` | `ArrayProperty(StringProperty())` |

---

## Data Corruption Pattern

When Python lists are assigned to `StringProperty` fields:

**Input (Python):**
```python
node.aggravating_factors = ['nerve compression', 'cold']
```

**Stored in Neo4j (String):**
```
"['nerve compression', 'cold']"
```

**Read back (String, not list):**
```python
node.aggravating_factors  # Returns: "['nerve compression', 'cold']" (str)
```

**Pydantic validation fails:**
```
Input should be a valid list [type=list_type, input_value="['nerve compression', 'cold']", input_type=str]
```

---

## Commands to Reproduce

### 1. Search for errors in app.log
```bash
grep -n "validation errors for SymptomType" repos/dem2/logs/app.log | head -5
```

### 2. Verify schema defines list[string]
```bash
grep -n "list\[string\]" repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/schema.yml
```

### 3. Verify nodes.py has StringProperty (bug)
```bash
grep -n "aggravating_factors\|relieving_factors\|associated_signs" \
  repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/condition/nodes.py
```

### 4. Verify generator.py missing list[string] mapping
```bash
grep -A 10 "type_map = {" repos/dem2/services/graph-memory/src/machina/graph_memory/generator.py
```

---

## Impact Assessment

### User Impact
- **Symptom processing failures**: Users cannot track symptoms with aggravating/relieving factors
- **Silent data loss**: List data is stored but cannot be retrieved correctly
- **Agent tool failures**: Medical agent queries involving symptoms fail silently

### Data Impact
- **Existing data corrupted**: All stored `list[string]` fields contain stringified lists
- **New data will be corrupted**: Until generator is fixed and nodes regenerated
- **Migration required**: Existing data needs conversion from string→list format

### Affected Functionality
- Symptom tracking and search
- Condition tracking (synonyms, tags, risk factors, complications)
- Observation type metadata (aliases, unit properties)

---

## Related Files

| File | Purpose |
|------|---------|
| `repos/dem2/services/graph-memory/src/machina/graph_memory/generator.py` | Node generator (bug location) |
| `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/schema.yml` | Schema definition |
| `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/condition/nodes.py` | Generated node classes |
| `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/condition/symptom.py` | `node_to_symptom_type()` converter |
| `repos/dem2/packages/medical-types/src/machina/medical_types/symptom.py` | `SymptomType` Pydantic model |
| `repos/dem2/services/medical-data-engine/src/machina/medical_data_engine/engine/processors/symptom.py` | Symptom processor (error location) |

---

## Next Steps

1. **Fix generator.py**: Add `list[string]` type mapping
2. **Regenerate nodes.py**: Run `just graph-generate`
3. **Create Neo4j migration**: Convert corrupted string→list data
4. **Test end-to-end**: Verify symptom processing works

See: [docs/plans/fix-list-string-generator-bug.md](../plans/fix-list-string-generator-bug.md)
