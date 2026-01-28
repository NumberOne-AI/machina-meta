# Plan: Simplify IntervalCategory Enum

**Status**: COMPLETE
**Created**: 2026-01-28
**Last Updated**: 2026-01-28

## Objective

Revise the category system throughout the codebase, consolidating from 10 categories to 5 logical categories with 3 associated colors.

## New Category Schema

| Category   | Color   | Meaning                                            |
|------------|---------|----------------------------------------------------|
| Low        | Red     | Falls outside reference range (below lower limit)  |
| Diminished | Yellow  | Within reference range but near the lower boundary |
| Normal     | Green   | Healthy/optimal/target range                       |
| Elevated   | Yellow  | Within reference range but near the upper boundary |
| High       | Red     | Falls outside reference range (above upper limit)  |

## Example Mappings (Clinical Designation to Category)

| Logical Category   | Color   | Example Clinical Designation   | Example Biomarker                                    |
|--------------------|---------|--------------------------------|------------------------------------------------------|
| Low                | Red     | Anemia                         | Hemoglobin < 13.0 g/dL                               |
| Diminished         | Yellow  | Hypotension                    | SBP < 90 mm Hg                                       |
| Normal             | Green   | Normotension                   | SBP >= 90 && < 120 mm Hg                             |
| Elevated           | Yellow  | Borderline                     | Normalized Lathosterol within 85-125 umol/mmol of TC |
| High               | Red     | Jaundice                       | Bilirubin > 2 mg/dL                                  |

---

## Progress Tracking

### Completed

- [x] **Generic Parser Prompt** (`repos/dem2/services/docproc/.../generic.md`)
  - Added Category Classification section with conditionally required language
  - Updated all examples to include category field
  - Category is now CONDITIONALLY REQUIRED: if clinical_designation is extracted, category MUST be assigned

- [x] **IntervalCategory Enum** (`repos/dem2/packages/medical-types/.../observation.py`)
  - Reduced from 10 values to 5 (Low, Diminished, Normal, Elevated, High)
  - Updated docstring with color mapping and meanings
  - Updated `compute_color_from_category()` function
  - Removed `infer_category_from_label()` function entirely
  - Updated `_infer_synthetic_category()` for synthetic interval generation

- [x] **Extraction Schema** (`repos/dem2/packages/medical-types/.../extraction_schemas.py`)
  - Updated `ExtractRange.category` field description with new 5-category schema

- [x] **Frontend TypeScript Enum** (`repos/dem2-webui/src/types/fhir-storage.ts`)
  - Updated `IntervalCategory` enum to 5 values

- [x] **Frontend Color Mapping** (`repos/dem2-webui/src/lib/observation-range-helpers.ts`)
  - Updated `CATEGORY_COLORS` mapping
  - Updated `isNormal` check to only look for `IntervalCategory.Normal`

- [x] **Frontend Name Cell** (`repos/dem2-webui/src/components/fhir-storage/cells/name.tsx`)
  - Updated `formatReferenceRange()` to find Normal category only

- [x] **Utils** (`repos/dem2/services/medical-data-engine/.../utils.py`)
  - Removed import of `infer_category_from_label`
  - Removed fallback logic that called `infer_category_from_label`

- [x] **Observation Enrichment** (`repos/dem2/services/medical-data-storage/.../observation_enrichment.py`)
  - Removed import of `infer_category_from_label`
  - Set category to None for LabCorp data (non-LLM source)

- [x] **Vital Signs Reference Ranges** (`repos/dem2/shared/src/machina/shared/vital_signs/reference_ranges.py`)
  - Added explicit `category` field to all categories in `VITAL_SIGNS_REFERENCE_RANGES` dict

### Pending

- [x] **Fix Moderate Hypoxemia** - Change from `Diminished` to `Low` in reference_ranges.py
- [x] **Nomenclature Standardization** - Renamed fields in static reference range definitions to match RangeInterval model:
  - `"label"` → `"clinical_designation"`
  - `"low"` → `"lower_reference_limit"`
  - `"high"` → `"upper_reference_limit"`
- [x] **Update function** - Updated `get_vital_sign_reference_range()` to use standardized field names and explicit category from dict
- [x] **Fix Linting Errors** - Reformatted `reference_ranges.py` to fix 22 E501 line-too-long errors (all lines now ≤120 chars)
- [x] **Update Tests** - Updated tests to use new 5-category schema:
  - `packages/medical-types/tests/test_reference_range_intervals.py` - Updated LDL and BP test cases
  - `services/graph-memory/tests/test_observation_interval_matching.py` - Updated LDL and BP test cases
  - All 37 tests pass
- [x] **Update Router** - Fixed `graph-memory/.../observation/router.py` to check only `IntervalCategory.NORMAL` (removed OPTIMAL reference)
- [x] **Update Documentation** - Updated `REFERENCE_RANGE_EXTRACTION.md` to use new 5-category schema (NORMAL, ELEVATED, HIGH) and new field names (clinical_designation, interval_notation, lower_reference_limit, upper_reference_limit). Deleted outdated code examples and Future Enhancements section.

- [x] **Medical Catalog Models** (`repos/dem2/packages/external/src/machina/external/medcat/models.py`)
  - Found separate `IntervalCategory` enum with old 10-value schema
  - Updated to new 5-category schema (Low, Diminished, Normal, Elevated, High)
  - Updated docstring with color mapping and meanings

- [x] **Frontend Interval Status Badge** (`repos/dem2-webui/src/components/fhir-storage/interval-status-badge.tsx`)
  - Found switch statement still handling old categories (Ideal, Optimal, Borderline, Abnormal, Critical High, Critical Low)
  - Updated switch to handle only 5 new categories
  - Removed unused `darkRed` color style
  - Updated comment to document 5 categories with 3 colors

---

## Vital Signs Category Mapping Analysis

### Old vs New Category Assignment

The old `infer_category_from_label()` function used keyword matching which had several issues:
- Matched "Severe" to CRITICAL_HIGH even when clinically it means low (e.g., Severe Hypoxemia = low O2)
- Didn't handle medical terms like Bradycardia, Tachycardia, Fever, Hypothermia
- Inconsistent behavior across different vital signs

**Principle**: Any measurement falling outside normal reference ranges, sufficiently so as to warrant a clinical designation or diagnosis, should be categorized as Low or High (Red), not Diminished or Elevated (Yellow).

### Systolic Blood Pressure (8480-6)

| Clinical Designation   | Old infer_category_from_label   | New Explicit Category   | Notes                    |
|------------------------|---------------------------------|-------------------------|--------------------------|
| Normal                 | NORMAL                          | Normal                  | Correct                  |
| Elevated               | ELEVATED                        | Elevated                | Correct                  |
| Stage 1 Hypertension   | (not matched)                   | High                    | Clinical diagnosis = Red |
| Stage 2 Hypertension   | (not matched)                   | High                    | Clinical diagnosis = Red |
| Hypertensive Crisis    | (not matched)                   | High                    | Clinical diagnosis = Red |

### Diastolic Blood Pressure (8462-4)

| Clinical Designation   | Old infer_category_from_label   | New Explicit Category   | Notes                    |
|------------------------|---------------------------------|-------------------------|--------------------------|
| Normal                 | NORMAL                          | Normal                  | Correct                  |
| Stage 1 Hypertension   | (not matched)                   | High                    | Clinical diagnosis = Red |
| Stage 2 Hypertension   | (not matched)                   | High                    | Clinical diagnosis = Red |
| Hypertensive Crisis    | (not matched)                   | High                    | Clinical diagnosis = Red |

### Heart Rate (8867-4)

| Clinical Designation   | Old infer_category_from_label   | New Explicit Category   | Notes                    |
|------------------------|---------------------------------|-------------------------|--------------------------|
| Bradycardia            | (not matched)                   | Low                     | Clinical diagnosis = Red |
| Normal                 | NORMAL                          | Normal                  | Correct                  |
| Tachycardia            | (not matched)                   | High                    | Clinical diagnosis = Red |

### Body Temperature (8310-5)

| Clinical Designation   | Old infer_category_from_label   | New Explicit Category   | Notes                    |
|------------------------|---------------------------------|-------------------------|--------------------------|
| Hypothermia            | (not matched)                   | Low                     | Clinical diagnosis = Red |
| Normal                 | NORMAL                          | Normal                  | Correct                  |
| Fever                  | (not matched)                   | High                    | Clinical diagnosis = Red |

### Oxygen Saturation (2708-6)

| Clinical Designation   | Old infer_category_from_label   | New Explicit Category   | Notes                                      |
|------------------------|---------------------------------|-------------------------|--------------------------------------------|
| Severe Hypoxemia       | CRITICAL_HIGH (bug!)            | Low                     | Bug fix: "Severe" matched HIGH, but O2 LOW |
| Moderate Hypoxemia     | (not matched)                   | Low                     | Clinical diagnosis = Red (outside normal)  |
| Mild Hypoxemia         | (not matched)                   | Diminished              | Near boundary, within acceptable range     |
| Normal                 | NORMAL                          | Normal                  | Correct                                    |

### Respiratory Rate (9279-1)

| Clinical Designation   | Old infer_category_from_label   | New Explicit Category   | Notes                    |
|------------------------|---------------------------------|-------------------------|--------------------------|
| Bradypnea              | (not matched)                   | Low                     | Clinical diagnosis = Red |
| Normal                 | NORMAL                          | Normal                  | Correct                  |
| Tachypnea              | (not matched)                   | High                    | Clinical diagnosis = Red |

### Key Fixes

1. **Severe Hypoxemia**: Old system matched "Severe" keyword to CRITICAL_HIGH. This was a semantic bug - severe hypoxemia means critically LOW oxygen, not high.

2. **Moderate Hypoxemia**: Should be `Low` (Red), not `Diminished` (Yellow). It's a clinical designation indicating the patient has fallen outside normal ranges, warranting medical attention.

3. **Medical Terminology**: Clinical terms like Bradycardia, Tachycardia, Hypothermia, Fever, Hypertension, Bradypnea, Tachypnea now properly map to Low/High based on their clinical meaning rather than relying on keyword matching.

---

## Files Modified

| File                                                                                                             | Changes                                                                              |
|------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `repos/dem2/services/docproc/src/machina/docproc/extractor/agents/generic/prompts/generic.md`                    | Added Category Classification section, updated examples                              |
| `repos/dem2/packages/medical-types/src/machina/medical_types/observation.py`                                     | Updated IntervalCategory enum, color mapping, removed infer_category_from_label      |
| `repos/dem2/packages/medical-types/src/machina/medical_types/extraction_schemas.py`                              | Updated ExtractRange.category description                                            |
| `repos/dem2-webui/src/types/fhir-storage.ts`                                                                     | Updated TypeScript IntervalCategory enum                                             |
| `repos/dem2-webui/src/lib/observation-range-helpers.ts`                                                          | Updated CATEGORY_COLORS, isNormal check                                              |
| `repos/dem2-webui/src/components/fhir-storage/cells/name.tsx`                                                    | Updated formatReferenceRange                                                         |
| `repos/dem2/services/medical-data-engine/src/machina/medical_data_engine/enricher/observation_enricher/utils.py` | Removed infer_category_from_label usage                                              |
| `repos/dem2/services/medical-data-storage/src/machina/medical_data_storage/service/observation_enrichment.py`    | Removed infer_category_from_label, set category=None for LabCorp                     |
| `repos/dem2/shared/src/machina/shared/vital_signs/reference_ranges.py`                                           | Standardized field names, added explicit category, fixed Moderate Hypoxemia, linting |
| `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/observation/router.py`                  | Removed OPTIMAL from is_out_of_range check                                           |
| `repos/dem2/packages/medical-types/tests/test_reference_range_intervals.py`                                      | Updated tests to use new 5-category schema                                           |
| `repos/dem2/services/graph-memory/tests/test_observation_interval_matching.py`                                   | Updated tests to use new 5-category schema                                           |
| `repos/dem2/docs/REFERENCE_RANGE_EXTRACTION.md`                                                                  | Updated examples to new 5-category schema and field names, deleted Future Enhancements |
| `repos/dem2/packages/external/src/machina/external/medcat/models.py`                                             | Updated separate IntervalCategory enum to 5-category schema                            |
| `repos/dem2-webui/src/components/fhir-storage/interval-status-badge.tsx`                                         | Updated switch statement to 5 categories, removed darkRed color                        |
