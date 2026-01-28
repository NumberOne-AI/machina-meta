# TODO

This file tracks planned work, improvements, and technical debt across the workspace.
Structure follows the workspace hierarchy. Update continuously as work progresses.

For completed tasks, see [DONE.md](DONE.md).

## Task States
- **PROPOSED** - Under consideration, not yet approved
- **STARTED** - Approved and in progress
- **REVIEW** - Work completed, awaiting user review and approval before marking DONE
- **DONE** - Completed and approved by user
- **REVERTED** - Was DONE but later rolled back (e.g., git revert)
- **CANCELLED** - Removed from scope with documented reason

## Task Format
Each task includes:
- State: `[PROPOSED]`, `[STARTED]`, `[DONE]`, `[REVERTED]`, or `[CANCELLED]`
- Impact: `HIGH`, `MEDIUM`, or `LOW` (required for all tasks)
- Added: Date task was created
- Completed: Date task was finished (for DONE items)

## Task Journal Requirements

**All changes to a task MUST be journaled within the task entry.**

When modifying an existing task:
- Adding implementation steps: Add with `- [ ]` checkbox
- Completing steps: Change `- [ ]` to `- [x]` with completion note
- Removing steps: Do NOT delete silently. Mark as cancelled with reason:
  - `- [CANCELLED] Step description - Reason for cancellation (YYYY-MM-DD)`
- Changing scope: Add a note explaining the change

This ensures the full history of task evolution is preserved in the task itself.

## Impact Levels
- **HIGH** - Critical for core functionality, blocking other work, or significant user value
- **MEDIUM** - Important improvement, enhances quality or developer experience
- **LOW** - Nice to have, minor improvement, or future consideration

## ⚠️ IMPORTANT: Commit Requirements

**Every git commit MUST have an associated TODO.md item.**

This is a mandatory workflow requirement:
1. Before making a commit, ensure there is a corresponding task entry in this file
2. If no task exists, create one (even retroactively) before or with the commit
3. Mark the task as DONE with completion date when the work is finished
4. Trivial fixes (typos, formatting) may share a parent task or use a catch-all maintenance task

This ensures all work is tracked, provides context for code changes, and maintains a complete project history.

## ⚠️ CRITICAL: Immediate Commit Requirement

**Changes to this file (and PROBLEMS.md) MUST be committed to git immediately after modification.**

Do not batch changes to TODO.md or PROBLEMS.md with other work. These files track project state and must be version-controlled as soon as they are updated.

---

## Workspace - Documentation & Tooling

- [PROPOSED] **Convert CLAUDE.md to skill-based architecture** - Reduce context size by 68% through on-demand skill loading
  - Impact: HIGH | Added: 2026-01-12
  - **Proposed Solution**: Keep critical safety rules in CLAUDE.md, extract reference docs into specialized skills.

---

## Workspace - DevOps & Environment Tooling

- [STARTED] **Standardize K8s environment import and local development tooling** - Consistent env vars and localhost rewriting
  - Impact: MEDIUM | Added: 2026-01-27
  - Related Problem: "Inconsistent local/preview/dev/staging environment tooling" (PROBLEMS.md)
  - **Completed**:
    - [x] Add comparison mode to `import_k8s_environment.py` (`ad2c403`)
    - [x] Add markdown table output for env comparison (`7522acb`, `9352343`)
    - [x] Add automatic localhost rewriting for K8s hostnames (`12250a9`)
    - [x] Add regex support for `port_forward_service.py` service matching (`12250a9`)
    - [x] Standardize `user_manager.py` to use `DYNACONF_PG_DB__*` variables (`b387221e`)
    - [x] Add `DYNACONF_BACKEND_API__HOST/PORT` env vars to K8s deployments (`60052ed`)
    - [x] Add `[default.backend_api]` config section to dynaconf (`e9c0334b`)
    - [x] Add `DYNACONF_BACKEND_API__HOST` to localhost rewrite vars (`bb87318`)
  - **Remaining**:
    - [ ] Update `curl_api.sh` to use `DYNACONF_BACKEND_API__*` variables
    - [ ] Document standard workflow for local K8s environment access
    - [ ] Add port rewriting to import script (not just hostnames)
  - **Files Modified**:
    - `scripts/import_k8s_environment.py` - K8s env import with localhost rewriting
    - `scripts/port_forward_service.py` - Regex service matching
    - `repos/dem2/scripts/user_manager.py` - Dynaconf variable standardization
    - `repos/dem2-infra/k8s/base/app.yaml` - Backend API env vars
    - `repos/dem2/machina/machina-medical/config.toml` - backend_api config section

---

## Workspace - Multi-Repo Features

- [PROPOSED] **Implement transactional multi-repo rebase with `just repo-rebase`** - Safe coordinated rebase across all submodules
  - Impact: HIGH | Added: 2026-01-07
  - Create `just repo-rebase` command for rebasing feature branches onto merge-base.
  - Implement `scripts/machina_git.py` with rebase orchestration logic.

- [STARTED] **DOCX to image conversion for Gemini Vision processing** - High-quality document rendering for LLM extraction
  - Impact: MEDIUM | Added: 2026-01-22
  - **Problem**: Need to convert DOCX files to images for Gemini Vision API processing
  - **Current State**:
    - ✅ LibreOffice + poppler: Works at 300 DPI (industry standard)
    - ✅ Docker container: Fixed for non-root users
  - **Completed**:
    - [x] Add extraction-only modes (extract-text, extract-images, extract-all)
    - [x] Increase default DPI from 200 to 300
    - [x] Add `media_resolution="high"` for Gemini API
    - [x] Commit: a8763c7 "feat(scripts): add extraction-only modes and 300 DPI support"

---

## Workspace - Infrastructure & CI/CD

- [STARTED] **Research Argo Workflows and install on GKE** - Evaluate workflow orchestration capabilities
  - Impact: MEDIUM | Added: 2026-01-21
  - **Goal**: Understand Argo Workflows capabilities and install on GKE cluster for document processing.

- [PROPOSED] **Use Argo Workflows for parallel document processing pipeline** - Orchestrate docproc stages as DAG workflow
  - Impact: HIGH | Added: 2026-01-21
  - **Proposed Solution**: Use Argo Workflows to orchestrate extraction pipeline stages as parallel DAG.

- [PROPOSED] **Add GKE service port-forwarding via gcloud-admin** - Enable querying remote Neo4j/services from host
  - Impact: MEDIUM | Added: 2026-01-21
  - **Problem**: Current gcloud-admin kubectl port-forward only works inside the container.

- [PROPOSED] **Research Neo4j indexes to optimize query_graph performance** - Investigate index strategies
  - Impact: HIGH | Added: 2026-01-21
  - **Problem**: Analysis of slow queries shows `query_graph` tool (Neo4j) is primary bottleneck.

- [PROPOSED] **Add minikube cluster support to dev_stack.py** - Alternative to Docker Compose
  - Impact: MEDIUM | Added: 2026-01-09
  - **Goal**: Add `minikube-up`, `minikube-down`, etc. commands to `scripts/dev_stack.py`.

---

## Workspace - Agent System

- [DONE] **Support multi-interval reference range extraction in generic parser** - Extract all range classifications (Normal, Borderline, Increased Risk, etc.)
  - Impact: HIGH | Added: 2026-01-27 | Completed: 2026-01-28
  - Related Problem: "Reference range extraction incomplete - only extracts single interval" (PROBLEMS.md)
  - **Problem**: Current generic parser extracts only ONE reference range per biomarker, losing clinical context
  - **Goal**: Extract ALL reference range intervals with their clinical designations
  - **Data to Extract Per Interval**:
    1. `interval_notation`: Numeric bounds (e.g., `<1.0`, `1.0-3.0`, `>3.0`)
    2. `clinical_designation`: Clinical label (e.g., `Normal`, `Increased Risk`)
  - **Implementation Plan**:
    - [x] **Phase 1: Analysis** - Catalog multi-interval patterns from sample lab reports (2026-01-27)
    - [x] **Phase 2: Schema Design** - Update LLM output schema (2026-01-27)
      - Updated `DocumentBiomarkerEntry` and `BiomarkerValue`
      - Defined `ExtractionReferenceRangeInterval` matching `RangeInterval`
      - Removed legacy `reference_range: str` from all models
    - [x] **Phase 3: Prompt Engineering** - Update generic parser prompts (2026-01-27)
      - Modified `generic.md` to request array of intervals with examples
      - Removed all references to legacy string `reference_range`
    - [x] **Phase 4: Data Models** - Update backend data structures (2026-01-27)
      - Updated `DocExtractObservation` and `ExtractReferenceRange` in `medical-types`
    - [x] **Phase 5: Graph Storage** - Update Neo4j storage (2026-01-27)
      - Verified `ObservationNode` JSON serialization is compatible
      - Updated `convert_extract_ranges` utility to handle structured intervals
    - [x] **Phase 6: Frontend Display** - Update UI components (2026-01-27)
      - Refactored `RangeInterval` to CLSI/IFCC terminology (`clinical_designation`, etc.)
      - Updated `ReferenceRangeDisplay`, `ObservationHistoryChart`, and `ObservationValueForm`
    - [x] **Phase 7: Testing** - End-to-end validation (2026-01-27)
      - Verified successful extraction from `Boston Heart July 2021.pdf`
    - [x] **Phase 8: Type Error Fixes** - Fix remaining mypy errors (2026-01-28)
      - Fixed `observation_converter.py`: Added `_create_reference_range_from_intervals()` method
      - Fixed `code_resolver.py`: Use `document_reference_range.stringify()` instead of missing `reference_range_str`
      - Fixed `metadata_enricher.py`: Same fix for LLM prompt context
      - Fixed `observation-history-chart.tsx`: Corrected variable name `reference_range` (was `referenceRange`)
      - Updated `REFERENCE_RANGE_EXTRACTION.md` documentation
      - All 27 reference range tests pass, all 10 observation interval tests pass
      - Commit: `f9484ace` (dem2), `fe4cc00` (dem2-webui)

- [DONE] **Simplify IntervalCategory enum from 10 to 5 categories** - Consolidate category schema with 3 colors
  - Impact: HIGH | Added: 2026-01-28 | Completed: 2026-01-28
  - **Plan:** [docs/plans/simplify-categories.md](docs/plans/simplify-categories.md)
  - **Problem**: Original 10-category schema (Ideal, Optimal, Normal, Borderline, Elevated, Abnormal, Low, High, Critical Low, Critical High) was overly complex and inconsistent
  - **Solution**: Consolidated to 5 logical categories with 3 colors:
    - Low (Red): Falls outside reference range (below lower limit)
    - Diminished (Yellow): Within reference range but near lower boundary
    - Normal (Green): Healthy/optimal/target range
    - Elevated (Yellow): Within reference range but near upper boundary
    - High (Red): Falls outside reference range (above upper limit)
  - **Implementation**:
    - [x] Updated `IntervalCategory` enum in `observation.py` and `medcat/models.py`
    - [x] Updated frontend TypeScript enum in `fhir-storage.ts`
    - [x] Updated color mappings in `observation-range-helpers.ts` and `interval-status-badge.tsx`
    - [x] Updated `formatReferenceRange()` in `name.tsx`
    - [x] Standardized field names: `label`→`clinical_designation`, `low`→`lower_reference_limit`, `high`→`upper_reference_limit`
    - [x] Updated vital signs reference ranges with explicit categories
    - [x] Removed deprecated `infer_category_from_label()` function
    - [x] Updated generic parser prompt with Category Classification section
    - [x] Updated tests (37 tests pass)
    - [x] Updated documentation (`REFERENCE_RANGE_EXTRACTION.md`)
  - **Files Modified**: 14 files across dem2 and dem2-webui (see plan file for full list)
  - **Commits**: Multiple commits on `dbeal-docproc-dev` branches

- [PROPOSED] **Migrate Text-to-Cypher to `neo4j-graphrag`** - Standardize GraphRAG implementation
  - Impact: HIGH | Added: 2026-01-27
  - **Proposal**: [docs/proposals/GRAPH_RAG_MIGRATION.md](docs/proposals/GRAPH_RAG_MIGRATION.md)
  - **Goal**: Replace custom Text-to-Cypher implementation in `CypherAgent` with official library.

- [REVIEW] **Fix symptom episode merge prompt to include modifiers**
  - Impact: HIGH | Added: 2026-01-28 | Implemented: 2026-01-28
  - Related Problem: "SymptomNode not created properly from conversational symptom queries" (PROBLEMS.md)
  - **Plan:** [docs/plans/FIX_symptom_node_creation.md](docs/plans/FIX_symptom_node_creation.md)
  - Evidence: [docs/evidence/REPORT_symptom_staging_test_20260128.md](docs/evidence/REPORT_symptom_staging_test_20260128.md)
  - **Implementation** (2026-01-28):
    - [x] Phase 1: Added `aggravating_factors`, `relieving_factors`, `associated_signs` to merge prompt (BUG #2)
    - [x] Phase 2: Added `list[string]` type mapping to generator.py, regenerated nodes (BUG #1)
    - [x] Phase 2.5: Fixed SymptomType pydantic model type mismatch (BUG #4) - Changed `synonyms`/`tags` from `str | None` to `list[str] | None` across backend and frontend
    - [ ] Phase 3: K8s persistence investigation (BUG #3) - pending
    - [ ] Phase 4: Verification on staging/preview environments
  - **Commits:**
    - `1f69c15c` (dem2, dbeal-docproc-dev branch) - BUG #1 and #2
    - BUG #4 pending commit across dem2 and dem2-webui
  - **Awaiting:** Verification on staging before marking DONE
  - **Files Modified (BUG #4)**:
    - `packages/medical-types/src/machina/medical_types/symptom.py` - Changed synonyms/tags to `list[str] | None`
    - `services/graph-memory/.../symptom_schema.py` - Updated 4 schema models
    - `services/medical-data-engine/.../symptom_enricher.py` - Fixed `_create_type_from_catalog()` to pass arrays
    - `src/types/symptoms.ts` (frontend) - Changed to `string[] | null`
    - `src/components/symptoms/sections/symptom-about-section.tsx` (frontend) - Iterate arrays directly
  - **Static Analysis:** All passed (mypy, ruff, biome, tsc)

---

## Repository-Specific TODOs

For repository-specific tasks, see:
- [repos/dem2/TODO.md](repos/dem2/TODO.md) - Backend tasks
- [repos/dem2-webui/TODO.md](repos/dem2-webui/TODO.md) - Frontend tasks
- [repos/medical-catalog/TODO.md](repos/medical-catalog/TODO.md) - Catalog service tasks
- [repos/dem2-infra/TODO.md](repos/dem2-infra/TODO.md) - Infrastructure tasks

---

## Journal

Track changes to this TODO file: new items added, state changes, revisions, reorganizations.

### 2025-12-29
- Created workspace-level TODO.md with framework instructions
- Established structure for workspace-level vs repository-specific task tracking

### 2026-01-28
- Updated symptom fix task with BUG #4 (SymptomType pydantic model type mismatch) fix details.
- Fixed `synonyms`/`tags` type alignment across backend (medical-types, graph-memory, medical-data-engine) and frontend (symptoms.ts, symptom-about-section.tsx).
- All static analysis passed (mypy, ruff, biome, tsc).

### 2026-01-27
- Moved completed tasks to DONE.md.
- Reverted DOCX to image conversion to [STARTED].
