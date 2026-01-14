# Conflict Resolution Log

- **Source Branch**: feature/docproc-extraction-pipeline
- **Target Branch**: origin/dev
- **New Branch**: dbeal-docproc-dev
- **Date**: 2026-01-14
- **Status**: IN_PROGRESS

## Summary Statistics

| Repository   | Conflicts Encountered | Resolved | Ours | Theirs | Manual |
|--------------|----------------------:|:--------:|:----:|:------:|:------:|
| dem2         |                     0 |        0 |    0 |      0 |      0 |
| dem2-webui   |                     0 |        0 |    0 |      0 |      0 |

## Conflict Resolution Strategy

### Prefer "Ours" (Feature Branch)
1. Deleted custom parser files (boston_heart_v4, dutch_plus, nutr_eval, supervisor)
2. Deleted strategy.py routing layer
3. Reference range parsing architecture changes
4. Changes to extractor pipeline.py, models.py

### Prefer "Theirs" (origin/dev)
1. Bug fixes unrelated to document processing
2. Non-conflicting feature additions

### Manual Review Required
1. Changes to shared types/interfaces
2. Test file conflicts
3. Configuration changes

## Detailed Conflict Log

### dem2

(Conflicts will be logged here during rebase)

### dem2-webui

(Conflicts will be logged here during rebase)

#### Conflict #1: Commit 5/250 - 9c192c73 "Distinguish report and collection dates"

**Files:**
- `services/docproc/src/machina/docproc/extractor/agents/supervisor/agent.py` - Rule A (deleted supervisor)
- `services/docproc/src/machina/docproc/extractor/agents/supervisor/models.py` - Rule A (deleted supervisor)
- `services/docproc/src/machina/docproc/extractor/agents/supervisor/prompts/detect_format.md` - Rule A (deleted supervisor)
- `services/docproc/src/machina/docproc/extractor/agents/base.py` - Kept David's approach (report_date/collection_date)
- `services/docproc/src/machina/docproc/extractor/pipeline.py` - Kept David's approach (simple dates)
- `services/docproc/src/machina/docproc/extractor/processors/generic.py` - Kept David's GenericPipeline architecture

**Resolution:**
- Deleted supervisor agent files per Rule A
- Chose David's simpler date fields over Maxim's subreport approach from origin/dev (commit 37e3910b)
- Kept David's GenericPipeline architecture

**Rationale:** Feature branch architectural decisions take precedence over origin/dev changes


#### Conflict #2: Commit 8/250 - 3dec63f4 "Upgrade document recognizer to Claude Opus"

**Files:**
- `services/docproc/config.toml` - Model name: CLAUDE_SONNET (Maxim/origin/dev) vs CLAUDE_OPUS (David)

**Resolution:** Kept David's CLAUDE_OPUS per commit message intent


#### Conflict #3: Commit 17/250 - deae162a "Add biomarker canonical mapping"

**Files:**
- `services/docproc/src/machina/docproc/extractor/agents/generic/models.py` - Modify/delete: kept David's file (exists in final feature branch)
- `services/docproc/src/machina/docproc/extractor/agents/generic/prompts/generic.md` - Modify/delete: kept David's file
- `services/docproc/src/machina/docproc/extractor/converters/generic.py` - Content: kept David's canonical mapper approach

**Resolution:** Kept David's generic agent files and converter approach per feature branch architecture


#### Conflict #4: Commit 21/250 - 18b4085a "Disable historical data point collection"

**Files:**
- `services/docproc/src/machina/docproc/extractor/agents/generic/__init__.py` - Modify/delete: kept David's file

**Resolution:** Kept generic agent __init__.py per feature branch architecture


#### Conflict #5: Commit 28/250 - 942ff90c "refactor: Remove reference range (rr) parsing from document processing"

**Files:**
- `services/docproc/src/machina/docproc/extractor/converters/reference_parser.py` - David's commit deletes this (completed deletion)
- `services/medical-data-engine/src/machina/medical_data_engine/engine/processors/biomarker/reference_range_converter.py` - David's commit deletes this (completed deletion)
- `services/medical-data-engine/src/machina/medical_data_engine/engine/processors/biomarker/biomarker_processor.py` - Removed ReferenceRangeConverter code per David's refactoring

**Resolution:** Completed David's refactoring to remove reference range parsing from document processing


#### Conflict #9: Commit 96/250 - f7b39665 "refactor: Remove format-specific extractors, use generic pipeline only"

**Files:**
- `services/docproc/src/machina/docproc/extractor/converters/__init__.py` - Content conflict
- `services/docproc/src/machina/docproc/extractor/agents/dutch_plus/*` - Deleted (David)
- `services/docproc/src/machina/docproc/extractor/agents/nutr_eval/*` - Deleted (David)
- `services/docproc/src/machina/docproc/extractor/processors/dutch_plus.py` - Deleted (David)
- `services/docproc/src/machina/docproc/extractor/processors/nutr_eval.py` - Deleted (David)
- `services/docproc/src/machina/docproc/extractor/strategy.py` - Deleted (David)

**Conflict Details:**
Maxim's origin/dev added "DutchPlusConverter" to __all__ exports.
David's feature branch removes all format-specific converters (dutch_plus, nutr_eval).

**Resolution:** Kept David's version (removed DutchPlusConverter from exports)

**Rationale:** KEY architectural commit - David's decision to use only generic pipeline


#### Conflict #10: Commit 204/250 - 9ca1beca "fix: update DerivativeEntryResult schema to match medical-catalog"

**Files:**
- `services/medical-data-engine/src/machina/medical_data_engine/engine/processors/biomarker/observation_converter.py` - Content conflict

**Conflict Details:**
Maxim's origin/dev uses: display_name, display_name_search, short_name
David's feature branch uses: long_name, document_name (removed display_name_search)

**Resolution:** Kept David's schema fix to align with medical-catalog service

**Rationale:** David's commit fixes schema alignment with medical-catalog


#### Conflict #11: Commit 239/250 - 1ec90cdd "refactor: deprecate unused observation processors and remove from engine"

**Files:**
- `services/medical-data-engine/src/machina/medical_data_engine/engine/processors/observations2.py` - Content conflict

**Conflict Details:**
Maxim's origin/dev uses: display_name, display_name_search, simple biomarker handling
David's feature branch adds: catalog_validated, verbatim_name fields, unvalidated biomarker handling

**Resolution:** Kept David's refactored version with validated/unvalidated distinction

**Rationale:** David's refactoring to handle both validated and unvalidated biomarkers


#### Conflict #12: Commit 245/250 - d0ecdb8c "feat(graph): add RangeIntervalNode for biomarker color highlighting"

**Files:**
- `services/graph-memory/src/machina/graph_memory/medical/graph/condition/nodes.py` - Content conflict
- `services/medical-agent/src/machina/medical_agent/session_context/observation_context.py` - Content conflict

**Conflict Details:**
Maxim's origin/dev: synonyms/tags as ArrayProperty, uses document_value_color, _format_date
David's feature branch: synonyms/tags as StringProperty, uses matched_interval_color, _format_datetime

**Resolution:** Kept David's RangeIntervalNode implementation

**Rationale:** David's feature for biomarker color highlighting with interval matching


---

## Phase 2 Complete: dem2 Rebase

**Status**: ✅ COMPLETED
**Final Commit (dem2)**: 9eca12af test(batch): update extraction test outputs
**Branch**: dbeal-docproc-dev
**Original Feature Branch**: Preserved at backup/docproc-pre-rebase-20260114

### Summary Statistics (dem2)

| Repository   | Conflicts Encountered | Resolved | David's | Maxim's | Mixed |
|--------------|----------------------:|:--------:|:-------:|:-------:|:-----:|
| dem2         |                    12 |       12 |      12 |       0 |     0 |

**Conflict Details:**
- All 12 conflicts resolved by preferring David's feature branch changes
- Conflicts primarily involved: custom parser removal, reference range refactoring, schema updates, interval matching
- No breaking issues encountered
- 250 commits successfully rebased onto origin/dev

**Branch Correction:**
- Rebase initially updated feature/docproc-extraction-pipeline instead of dbeal-docproc-dev
- Fixed by: force-updating dbeal-docproc-dev to rebased HEAD, restoring feature/docproc-extraction-pipeline from backup tag
- Both branches now in correct state


---

## Phase 3 Complete: dem2-webui Rebase

**Status**: ✅ COMPLETED
**Final Commit (dem2-webui)**: a8877d5 test: update health markers page tests with interval color assertions
**Branch**: dbeal-docproc-dev
**Original Feature Branch**: Preserved at backup/docproc-pre-rebase-20260114

### Summary Statistics (dem2-webui)

| Repository   | Conflicts Encountered | Resolved | QA Team | Maxim's | Mixed |
|--------------|----------------------:|:--------:|:-------:|:-------:|:-----:|
| dem2-webui   |                     2 |        2 |       2 |       0 |     0 |

**Conflict Details:**
- Conflict #1 (commit 1/15): Test file (allergies.spec.ts) - mikemorioka-qa's test improvements
- Conflict #2 (commit 3/15): Multiple test data files - mikemorioka-qa's automated document processing test data
- All conflicts resolved by preferring incoming QA team's test data and improvements
- 1 commit dropped automatically (ddd9c054 - patch contents already upstream)
- 14 commits successfully rebased onto origin/dev (15 attempted, 1 dropped)

**Branch Correction:**
- Same issue as dem2: rebase updated feature/docproc-extraction-pipeline instead of dbeal-docproc-dev
- Fixed by: force-updating dbeal-docproc-dev to rebased HEAD, restoring feature/docproc-extraction-pipeline from backup tag
- Both branches now in correct state

---

## Final Rebase Summary

**Both repositories successfully rebased!**

| Repository   | Commits Rebased | Conflicts | Commits Dropped | Branch        |
|--------------|----------------:|----------:|----------------:|---------------|
| dem2         |             250 |        12 |               0 | dbeal-docproc-dev |
| dem2-webui   |              14 |         2 |               1 | dbeal-docproc-dev |
| **TOTAL**    |         **264** |    **14** |           **1** | **Both repos** |

**Status**: ✅ READY FOR PHASE 4 VERIFICATION

