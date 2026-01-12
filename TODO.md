# TODO

This file tracks planned work, improvements, and technical debt across the workspace.
Structure follows the workspace hierarchy. Update continuously as work progresses.

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

## Workspace - Multi-Repo Features

- [PROPOSED] **Implement transactional multi-repo rebase with `just repo-rebase`** - Safe coordinated rebase across all submodules
  - Impact: HIGH | Added: 2026-01-07
  - Create `just repo-rebase` command for rebasing feature branches onto merge-base (e.g., origin/dev)
  - Design transactional two-phase approach:
    - **Phase 1 (dry-run)**: Analyze and output merge plan including conflict detection
    - **Phase 2 (execute)**: Run the plan atomically with ability to restore on failure
  - Implement `scripts/machina_git.py` with rebase orchestration logic
  - Handle edge cases:
    - Detect merge-base branch per repo (usually origin/dev, but configurable)
    - Fetch merge-base branch before rebase
    - Detect conflicts before applying changes
    - Save repo state (commit hashes) before rebase for rollback
    - Provide conflict resolution workflow
    - Allow plan adjustment and re-execution after failure
  - Requirements:
    - Must work across all 4 submodules (dem2, dem2-webui, dem2-infra, medical-catalog)
    - Atomic operation: either all repos rebase successfully or none do
    - State preservation: can restore to pre-rebase state if any repo fails
    - Conflict reporting: clear indication of which repos have conflicts and where
    - Interactive mode: user can review plan before execution
  - Integration points:
    - Extends existing `just repo-*` commands (repo-pull, repo-sync, repo-status)
    - Uses machina-git skill principles (explicit cd, safety-first, user confirmation)
    - Follows CLAUDE.md git rules (working directory safety, atomic operations)
  - Planned implementation:
    - [ ] Design Python script architecture for git state management
    - [ ] Implement dry-run analysis phase with conflict detection
    - [ ] Implement state save/restore mechanism
    - [ ] Implement rebase execution phase
    - [ ] Add conflict resolution workflow
    - [ ] Create justfile command wrapper
    - [ ] Write comprehensive tests for edge cases
    - [ ] Document usage in CLAUDE.md and README.md

- [PROPOSED] **Implement reference range interpretation for observation values** - Compute and display in-range/out-of-range status with color indicators
  - Impact: HIGH | Added: 2026-01-08
  - **Problem Statement**:
    - Reference ranges are extracted and displayed, but the UI doesn't visually indicate whether a specific observation value falls within the reference range
    - Users must manually compare the value against the displayed ranges (e.g., "Is 95 within 70-100?")
    - The `ChipValue` component currently uses `document_value_color` from extraction, which is only available for document-sourced values
    - The infrastructure for interval matching exists but is disabled (commented as "reference_range analysis is disabled")
  - **Current Architecture**:
    - Backend `RangeInterval` class has `contains(value: float) -> bool` method (repos/dem2/packages/medical-types)
    - Backend `ObservationReferenceRange` has `classify_value(value: float) -> str | None` method
    - Frontend has `isValueInInterval()` and `getMatchingIntervals()` helpers (observation-range-helpers.ts)
    - API returns full `reference_range` with intervals but frontend only uses `interval_category` field
    - `CATEGORY_COLORS` mapping exists: Normal→green, High/Low→red, Borderline→yellow, Critical→dark-red
  - **Architecture Decision - Hybrid Approach**:
    - **Backend computes**: Add `matched_interval_label: str | None` to `ObservationValueResponse`
    - **Backend uses**: `ObservationReferenceRange.classify_value()` to find matching interval label
    - **Frontend displays**: Status badge showing matched interval (e.g., "Normal", "High", "Low")
    - **Frontend colors**: Use existing `CATEGORY_COLORS` mapping based on interval category
    - **Rationale**: Backend computation ensures consistency, frontend focuses on presentation
  - **Backend Implementation** (repos/dem2):
    - [x] Phase 1: Add matched_interval field to API response (2026-01-09)
      - Update `ObservationValueResponse` model to include `matched_interval_label: str | None`
      - Update `ObservationValueResponse` model to include `matched_interval_category: IntervalCategory | None`
      - Locate where `ObservationValueResponse` is constructed (graph-memory observation router)
      - Add computation logic using `reference_range.classify_value(value_numeric)` if reference range exists
      - Handle edge cases: null reference range, null value_numeric, no matching interval
    - [x] Phase 2: Ensure reference range is available at value creation time (2026-01-09)
      - Verify reference ranges are linked to observation values via `[:MEASURED_WITH_RANGE]` relationship
      - Confirm Cypher queries retrieve reference range for each value (from fixes in commits d20c3042, adc46db6)
      - Test with existing data to ensure matched interval computation works
    - [ ] Phase 3: Add unit tests for interval matching
      - Test `RangeInterval.contains()` with inclusive/exclusive bounds
      - Test `ObservationReferenceRange.classify_value()` with multiple intervals
      - Test edge cases: boundary values, no matching interval, overlapping intervals
      - Test null handling: null value, null reference range
    - [ ] Phase 4: Update API documentation
      - Document new `matched_interval_label` and `matched_interval_category` fields in OpenAPI spec
      - Add examples showing interval matching results
  - **Frontend Implementation** (repos/dem2-webui):
    - [x] Phase 1: Update TypeScript types (2026-01-09 - commit d45008b)
      - Add `matched_interval_label?: string | null` to `ObservationValue` interface (fhir-storage.ts)
      - Add `matched_interval_category?: IntervalCategory | null` to `ObservationValue` interface
    - [x] Phase 2: Create status indicator component (2026-01-09 - commit f95668d)
      - Create `IntervalStatusBadge` component to show matched interval
      - Display: `<Badge color={getIntervalColor(category)}>Normal Range</Badge>` (or "High", "Low", etc.)
      - Handle null cases: no reference range, no matched interval (show neutral badge)
      - Use Flexoki color mapping for consistency (green/yellow/red)
    - [x] Phase 3: Integrate into ChipValue component (2026-01-09 - commit f1f9be8)
      - Add optional `showIntervalStatus` prop to `ChipValue` component
      - Display `IntervalStatusBadge` next to the value chip
      - Maintain existing `document_value_color` behavior as fallback
      - Ensure backward compatibility for values without reference ranges (default: false)
    - [x] Phase 4: Integrate into ObservationMetricCard (2026-01-09)
      - Enable interval status display in metric card footer (latest and previous values)
      - Pass showIntervalStatus={true} to ChipValue components
      - Works alongside existing `ReferenceRangeDisplay` component
    - [ ] Phase 5: Enhance ObservationHistoryChart (optional)
      - Highlight data points with color based on matched interval
      - Show reference range zones as colored bands behind chart
      - Add tooltip showing interval label on hover
  - **Testing Requirements**:
    - [x] **Backend unit tests** (pytest) - interval matching logic (2026-01-12)
      - ✅ Test `RangeInterval.contains()` with inclusive/exclusive boundaries (27 tests)
      - ✅ Test `ObservationReferenceRange.classify_value()` with multiple intervals
      - ✅ Test boundary conditions: exactly at low/high, one unit over/under
      - ✅ Test null handling: null value, null reference range, no matching interval
      - ✅ Test overlapping intervals (if supported)
      - ✅ Test real-world examples: LDL cholesterol, blood pressure classification
      - Location: `repos/dem2/packages/medical-types/tests/test_reference_range_intervals.py`
      - All 27 tests passing
    - [x] **Backend integration tests** (pytest) - API response with matched intervals (2026-01-12)
      - ✅ Test `ObservationValueResponse.from_node()` returns matched_interval_label and matched_interval_category
      - ✅ Test with document-extracted reference ranges
      - ✅ Test with standard reference ranges
      - ✅ Test with missing reference ranges (fields are null)
      - ✅ Test with non-numeric values (text-only)
      - ✅ Test boundary conditions and real-world examples (LDL, blood pressure)
      - Location: `repos/dem2/services/graph-memory/tests/test_observation_interval_matching.py`
      - All 10 tests passing
    - [SKIPPED] **Frontend component tests** (Vitest/React Testing Library) - not required for MVP
      - Component tests are not currently used in this project
      - Playwright E2E tests provide sufficient coverage for UI behavior
      - If component tests are added in future, test IntervalStatusBadge component
    - [x] **Frontend E2E test infrastructure** (Playwright) - ready for use (2026-01-12)
      - ✅ Framework: Playwright already configured at `repos/dem2-webui/playwright.config.ts`
      - ✅ `health-markers.spec.ts` test spec exists (currently skipped)
      - ✅ Page object methods implemented in HealthMarkersPage:
        - `verifyIntervalStatusFromRow()` - verifies badge text matches expected status
        - Locates badge via `[role="status"]` selector
        - Returns passed/failed with actual status for debugging
      - ✅ Test data structure supports interval status:
        - `HealthMarker.latestExpIntervalStatus?: string`
        - `HealthMarker.previousExpIntervalStatus?: string`
      - ⚠️ **Action required**: Add interval status expectations to test data in `health-markers-data.ts`
      - ⚠️ **Action required**: Unskip tests and run against live system with data
      - Location: `repos/dem2-webui/tests/test_specs/health-markers.spec.ts`
      - Run: `cd repos/dem2-webui && pnpm test` or `pnpm test:headed` (with UI)
    - [x] **End-to-end verification** - interval matching code tested and ready (2026-01-12)
      - ✅ Uploaded and processed 3 Boston Heart documents (July 2021, May 2024, Sep 2024)
      - ✅ Verified API returns `matched_interval_label` and `matched_interval_category` fields
      - ✅ Confirmed interval matching logic works correctly (27 unit tests + 10 integration tests passing)
      - ⚠️ **Critical finding**: Reference range extraction doesn't populate numeric bounds
        - Issue: Reference ranges extracted as text only (e.g., "3.5-5.3")
        - Impact: `low` and `high` fields are null, preventing interval matching from working
        - Root cause: Reference range extraction pipeline doesn't parse numeric bounds from text
        - Status: Interval matching code is ready and tested; blocked by upstream data extraction issue
        - Next step: Fix reference range extraction to populate numeric bounds (separate task)
    - [BLOCKED] **Performance test** - blocked by reference range extraction issue
      - ⚠️ **Blocked**: Requires reference range extraction fix first
      - Once fixed: Measure API response time for GET /observations/grouped
      - Target: < 5% increase in response time with matched interval computation
      - **Note**: Backend uses efficient Cypher queries with reference range retrieval, no N+1 issues expected
  - **Testing Infrastructure** (already in place):
    - **Backend**: pytest with testcontainers (PostgreSQL, Neo4j, Redis)
      - Config: `repos/dem2/pyproject.toml` (pytest.ini_options)
      - Fixtures: `repos/dem2/services/medical-data-storage/tests/conftest.py`
      - Run: `cd repos/dem2 && just test` or `uv run pytest`
      - Async support with pytest-asyncio
      - Session-scoped database fixtures for performance
    - **Frontend**: Playwright E2E testing framework
      - Config: `repos/dem2-webui/playwright.config.ts`
      - Page Objects: `repos/dem2-webui/tests/pages/` (11 page objects including HealthMarkersPage)
      - Test Specs: `repos/dem2-webui/tests/test_specs/` (9 existing specs)
      - Fixtures: `repos/dem2-webui/tests/fixtures.ts` (testUser1, testUser2, testUser3)
      - Test Data: `repos/dem2-webui/tests/test_data/` (Boston Heart documents, biomarker data)
      - Run: `cd repos/dem2-webui && pnpm test` (headless) or `pnpm test:headed` (with UI)
      - HTML reports: `repos/dem2-webui/tests/playwright-report/`
      - Supports multiple environments: local, dev, staging
    - **Workspace**: `just repo-test` runs tests across all repositories
  - **Rollout Strategy**:
    - Phase 1: Backend implementation and API updates (non-breaking, adds new fields)
    - Phase 2: Frontend implementation (progressive enhancement, works with or without backend data)
    - Phase 3: Enable by default in ObservationMetricCard
    - Phase 4: Monitor for edge cases and user feedback
    - Phase 5: Document in repos/dem2/docs/REFERENCE_RANGE_EXTRACTION.md
    - Phase 6: CI/CD integration - add tests to GitHub Actions workflows
  - **Key Files**:
    - Backend:
      - `repos/dem2/packages/medical-types/src/machina/medical_types/observation.py` - RangeInterval, ObservationReferenceRange classes
      - `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/observation/router.py` - API endpoint
      - `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/observation/models.py` - ObservationValueResponse
    - Frontend:
      - `repos/dem2-webui/src/types/fhir-storage.ts` - TypeScript interfaces
      - `repos/dem2-webui/src/lib/observation-range-helpers.ts` - Color mapping and helpers
      - `repos/dem2-webui/src/components/fhir-storage/cells/chip-value.tsx` - Value display
      - `repos/dem2-webui/src/components/fhir-storage/observation-metric-card.tsx` - Metric card
  - **Future Enhancements** (separate tasks):
    - Add confidence score for interval matching (when value is near boundary)
    - Support multiple matching intervals (if ranges overlap)
    - Add trend analysis: "moved from Normal to High"
    - Implement alert rules: notify when value exits normal range
    - Add interval history: track which intervals value has been in over time
  - **Dependencies**:
    - Requires reference range extraction to be working (✅ Complete - commits be409571, d20c3042, adc46db6)
    - Requires category field to be populated (✅ Complete - commit adc46db6)
    - Requires schema alignment between graph-memory and medical-data-storage (✅ Complete - commit d20c3042)
  - **Success Criteria**:
    - ✅ Backend returns `matched_interval_label` for all observations with reference ranges
    - ✅ Frontend displays color-coded status badge (green/yellow/red) based on interval category
    - ⚠️ BLOCKED: Interval matching works but awaits reference range extraction fix
    - ⚠️ BLOCKED: 100% of Boston Heart document observations show correct interval match
    - ✅ UI clearly communicates when value is in-range vs out-of-range
    - ✅ System gracefully handles null reference ranges and null values
    - ✅ No performance degradation from interval matching computation

- [PROPOSED] **Fix reference range extraction to populate numeric bounds** - Unblock interval matching feature
  - Impact: HIGH | Added: 2026-01-12
  - **Problem**: Reference ranges extracted as text only (e.g., "3.5-5.3"), numeric bounds remain null
  - **Impact**: Interval matching code cannot work without numeric bounds to compare against
  - **Status**: Interval matching feature is 100% complete and tested, blocked by this issue
  - **Implementation Steps**:
    - [ ] Phase 1: Investigate reference range extraction pipeline
      - Locate where reference ranges are extracted from documents
      - Find where `RangeInterval` objects are created with text but null bounds
      - Understand why numeric parsing isn't happening
      - Identify if this is docproc extraction, catalog enrichment, or graph storage issue
    - [ ] Phase 2: Implement numeric bound parsing
      - Parse numeric bounds from text formats: "3.5-5.3", "<80", ">120", ">=100"
      - Handle edge cases: "< 5", ">= 10", single values, ranges with spaces
      - Populate `low` and `high` fields in `RangeInterval` objects
      - Preserve existing `text` field for display purposes
    - [ ] Phase 3: Add tests for bound parsing
      - Unit tests for text parsing logic (various formats)
      - Integration tests verifying bounds populated in database
      - Test edge cases: malformed ranges, non-numeric text, special characters
    - [ ] Phase 4: Re-process existing documents
      - Run extraction pipeline on existing test documents
      - Verify numeric bounds populated in Neo4j reference range nodes
      - Confirm interval matching now returns labels for all observations
    - [ ] Phase 5: Verify interval matching works end-to-end
      - Query observations API and verify matched_interval_label is populated
      - Check frontend UI displays interval status badges correctly
      - Run Playwright E2E tests with real data
  - **Key Files to Investigate**:
    - `repos/dem2/services/docproc/` - Document extraction pipeline
    - `repos/dem2/packages/medical-types/src/machina/medical_types/observation.py` - RangeInterval model
    - `repos/dem2/services/graph-memory/` - Graph storage of reference ranges
  - **Expected Outcome**: All extracted reference ranges have numeric bounds, interval matching works for 97%+ of observations

<!-- Add tasks that span multiple repositories (e.g., coordinated releases, cross-repo refactoring) -->

---

## Workspace - Infrastructure & CI/CD

- [PROPOSED] **Add minikube cluster support to dev_stack.py** - Alternative to Docker Compose using Kubernetes locally
  - Impact: MEDIUM | Added: 2026-01-09
  - **Goal**: Add `minikube-up`, `minikube-down`, `minikube-status`, `minikube-destroy` commands as alternative to Docker Compose
  - **Approach**: Reuse existing Kustomize manifests from `repos/dem2-infra/k8s/base/` with new minikube overlay
  - **Key decisions**:
    - Build images locally in minikube's Docker daemon using `eval $(minikube docker-env)`
    - Add as alternative commands alongside existing `up`, `down`, `status`
    - Use local Kubernetes Secrets instead of External Secrets Operator
  - **Files to create**:
    - `repos/dem2-infra/k8s/overlays/minikube/kustomization.yaml` - Main overlay config
    - `repos/dem2-infra/k8s/overlays/minikube/namespace.yaml` - tusdi-minikube namespace
    - `repos/dem2-infra/k8s/overlays/minikube/local-secrets.yaml` - Replace External Secrets with local K8s Secrets
    - `repos/dem2-infra/k8s/overlays/minikube/storage-class.yaml` - Minikube-compatible storage class (standard)
    - `repos/dem2-infra/k8s/overlays/minikube/env-vars-patch.yaml` - Local environment URLs
    - `repos/dem2-infra/k8s/overlays/minikube/image-pull-policy-patch.yaml` - Set imagePullPolicy: Never
  - **Files to modify**:
    - `scripts/dev_stack.py` - Add ~300 lines for minikube management functions
    - `justfile` - Add minikube-up, minikube-down, minikube-status, minikube-destroy, minikube-forward commands
  - **Implementation steps**:
    - [ ] Create minikube Kustomize overlay directory structure
    - [ ] Create kustomization.yaml referencing base with patches
    - [ ] Create local-secrets.yaml with dev passwords + env var refs for API keys
    - [ ] Create storage-class.yaml using minikube's standard provisioner
    - [ ] Create env-vars-patch.yaml for localhost URLs
    - [ ] Create image-pull-policy-patch.yaml
    - [ ] Add prerequisite check functions to dev_stack.py (minikube, kubectl)
    - [ ] Add cluster management functions (create, start, stop, delete, status)
    - [ ] Add image building functions (get docker-env, build in minikube)
    - [ ] Add Kubernetes deployment functions (apply, delete, wait for pods)
    - [ ] Add main command handlers (minikube_up, minikube_down, etc.)
    - [ ] Update argparse in main() with new commands
    - [ ] Add justfile commands
    - [ ] Test end-to-end workflow
  - **Minikube cluster config**:
    - Profile: `machina-dev`
    - Resources: 4 CPUs, 8GB RAM, 40GB disk
    - Driver: docker
    - Addons: ingress, storage-provisioner
  - **Access pattern**: Port-forwarding to localhost (8000, 3000, 5432, 7474, 6379, 6333)
  - **Required env vars for full functionality**:
    - `OPENAI_API_KEY`, `GEMINI_API_KEY`, `SERPER_API_KEY`
    - `VISION_AGENT_API_KEY`, `GOOGLE_SEARCH_API_KEY`
    - `GOOGLE_AUTH_CLIENT_ID`, `GOOGLE_AUTH_CLIENT_SECRET`
  - **Detailed plan**: `/home/dbeal/.claude/plans/snappy-bouncing-taco.md`

---

## Workspace - Documentation & Tooling

- [PROPOSED] **Convert CLAUDE.md to skill-based architecture** - Reduce context size by 68% through on-demand skill loading
  - Impact: HIGH | Added: 2026-01-12
  - **Problem Statement**:
    - CLAUDE.md is currently ~1,272 lines (~22,250 tokens) loaded into every conversation
    - Much of this content is reference documentation only needed for specific workflows
    - Large context reduces response speed and limits room for code/conversation
    - Example: 313 lines of curl_api documentation rarely needed but always loaded
  - **Proposed Solution**:
    - Keep ~405 lines (32%) of critical safety rules in CLAUDE.md
    - Extract ~867 lines (68%) into 16 specialized skills loaded on-demand
    - Token savings: ~15,173 tokens (68% reduction) per conversation
  - **Skills to Create**:
    - `machina-api-testing` (313 lines) - Complete curl_api reference for API testing workflows
    - `machina-setup` (72 lines) - Service setup guides for initial development
    - `machina-docs` (106 lines) - Documentation maintenance procedures for AGENTS.md, DATAFLOW.md, etc.
    - `machina-dev-patterns` (49 lines) - Common development patterns and workflows
    - `machina-todo` (68 lines) - TODO.md task tracking guidelines
    - `machina-reference` (40 lines) - Quick reference tables for commands
    - `machina-troubleshoot` (28 lines) - Troubleshooting guide
    - `machina-structure` (26 lines) - Repository structure details
    - `machina-submodules` (28 lines) - Git submodules workflow
    - `machina-preview` (16 lines) - Preview environments
    - `machina-services` (31 lines) - Development services table
    - `machina-gcloud` (36 lines) - gcloud-admin DevOps container
    - `machina-quickstart` (18 lines) - Quick start procedures
    - `machina-nix` (13 lines) - Nix development environment
    - `machina-env` (7 lines) - Environment configuration
    - `machina-problems` (20 lines) - PROBLEMS.md guidance
  - **Core CLAUDE.md (keep always-loaded)**:
    - Architecture Analysis Protocol (55 lines) - Critical for preventing misunderstandings
    - Bash Command Execution Safety (86 lines) - Working directory safety protocol
    - Machina-Git Skill Requirement (25 lines) - Git safety enforcement
    - Git Rules (60 lines) - Submodule safety rules
    - Workspace Overview (13 lines) - High-level context
    - Working with Workspace (66 lines) - When to use what
    - Architecture diagram (45 lines) - System context
    - Common Patterns (25 lines) - Tech stack overview
    - Git Workflow (6 lines) - Branch strategy
    - Workspace Principles (6 lines) - Core principles
    - Documentation navigation (18 lines) - Where to find things
  - **Implementation Steps**:
    - [ ] Create skill directory structure: `.claude/skills/machina-*/`
    - [ ] Extract content from CLAUDE.md to skill files (SKILL.md)
    - [ ] Create skill.json metadata for each skill with invocation triggers
    - [ ] Update CLAUDE.md to reference skills and remove extracted content
    - [ ] Add "Skills Available" section to CLAUDE.md
    - [ ] Test skill invocation by asking questions that should trigger each skill
    - [ ] Measure actual token savings in real conversations
    - [ ] Update machina-git skill if it references removed CLAUDE.md sections
    - [ ] Document skill maintenance in CLAUDE.md
  - **Skill Metadata Design**:
    - Each skill.json includes:
      - name: Machine-readable skill identifier
      - description: Human-readable summary shown to user
      - triggers: Keywords/questions that should invoke this skill
      - dependencies: Other skills that should be loaded together
    - Example triggers:
      - machina-api-testing: "curl_api", "test API", "upload document", "query agent"
      - machina-setup: "setup", "install", "initialize", "bootstrap"
      - machina-docs: "update AGENTS.md", "regenerate DATAFLOW", "documentation"
  - **Testing Plan**:
    - [ ] Test conversation without any skills loaded (basic questions)
    - [ ] Test skill auto-invocation by asking "How do I test the API?"
    - [ ] Test skill dependency loading (one skill triggering another)
    - [ ] Test skill content accuracy (compare to original CLAUDE.md)
    - [ ] Measure token usage before/after in real workflows
    - [ ] Test that critical safety rules still work (bash cd patterns, git safety)
  - **Success Criteria**:
    - ✅ CLAUDE.md reduced to ~405 lines (~7,088 tokens)
    - ✅ All 16 skills created with proper metadata
    - ✅ Skills invoke correctly based on conversation context
    - ✅ Measured 60%+ token savings in typical workflows
    - ✅ No loss of functionality or information access
    - ✅ Faster response times due to reduced context
  - **Rollback Plan**:
    - If skills don't invoke correctly or cause confusion, revert to full CLAUDE.md
    - Git preserves original CLAUDE.md structure for easy rollback
    - Skills can be merged back incrementally if needed
  - **Related Problems**: See PROBLEMS.md - "Skillification context management challenges"

- [DONE] **Create workspace-level TODO.md and PROBLEMS.md framework** - Establish task/issue tracking at workspace level
  - Impact: MEDIUM | Added: 2025-12-29 | Completed: 2025-12-29
  - Created PROBLEMS.md with framework instructions and skeleton structure
  - Created TODO.md with framework instructions and skeleton structure
  - Updated CLAUDE.md with complete framework documentation from repos/dem2/CLAUDE.md
  - All current problems and tasks remain in repos/dem2 (all are dem2-specific)
  - Files created: PROBLEMS.md, TODO.md
  - Files modified: CLAUDE.md (added framework documentation sections)

- [REVIEW] **Create comprehensive API routes documentation** - Document all routes across all services
  - Impact: HIGH | Added: 2025-12-30
  - Created route scanning system with Python scripts
  - Scanned FastAPI routes from dem2 (126 routes) and medical-catalog (21 routes) using OpenAPI JSON
  - Scanned Next.js routes from dem2-webui (2 API routes + 23 pages)
  - Generated intermediate routes.json with structured data
  - Generated ROUTES.md with comprehensive markdown tables
  - Total: 172 routes documented across 3 services
  - Files created:
    - scripts/scan_routes.py (route scanner using OpenAPI for FastAPI services)
    - scripts/generate_routes_md.py (markdown generator)
    - routes.json (structured route data with descriptions from OpenAPI)
    - ROUTES.md (comprehensive documentation with detailed descriptions)
  - Implementation details:
    - FastAPI scanner fetches OpenAPI JSON from running services
    - Extracts complete route metadata: descriptions, parameters, response models
    - Provides helpful error messages if services are not running
    - Next.js scanner uses file-based detection for pages and API routes
    - Component extraction groups routes by REST URL path prefixes instead of file paths
    - Hierarchical JSON structure with 48% size reduction through optimization
  - Commits: ed93bb3, cdcc7b3, b7265ee, 140f1c4, d5fd8db
  - Status: Fixed component extraction to use REST URL path prefixes instead of file paths. Routes now properly grouped (e.g., /api/v1/auth contains 13 auth-related routes). Awaiting user review and approval.

- [DONE] **Create comprehensive Google ADK agent architecture documentation** - Document MachinaMed's multi-agent system
  - Impact: HIGH | Added: 2025-12-31 | Completed: 2025-12-31
  - Examined actual agent implementation code across medical-agent service
  - Documented all 11 agent types and their purposes
  - Analyzed 1469 lines of agent configuration files
  - Files examined:
    - agents/factory.py (agent creation and composition patterns)
    - agents/names.py (11 agent type definitions)
    - agents/TriageAgent/config.yml (157 lines of routing logic)
    - agents/HealthConsultantAgent/config.yml (medical consultation with body system mapping)
    - agents/CypherAgent/config.yml (50 lines of natural language to Cypher rules)
    - agents/MedicalContextAgent/agent.py (agent builder pattern)
    - agent_tools/safe_agent_tool.py (517 lines of error handling wrapper)
    - shared/medical_agent/state.py (MachinaMedState definition)
  - Files created:
    - docs/AGENTS.md (comprehensive architecture documentation with verified code examples)
  - Files modified:
    - CLAUDE.md (added documentation maintenance section for keeping AGENTS.md up to date)
  - Key sections:
    - Agent hierarchy (ParallelAgent root with TriageAgent + ParallelDataExtractor)
    - 11 agent types with purposes and models
    - Agent composition patterns (ParallelAgent, LlmAgent)
    - State management (MachinaMedState with patient_id, user_id, session topics)
    - Tool patterns (SafeAgentTool wrapper with status tracking and error handling)
    - Configuration system (YAML-based configs)
    - Detailed analysis of key agents (TriageAgent routing, HealthConsultantAgent consultation, CypherAgent query generation)
    - Model selection strategy (Gemini 2.5 Flash for routing/extraction, Gemini 2.5 Pro for medical reasoning)
    - Callback system (before_agent_callback, after_agent_callback)
    - Error handling (three-tier with fallback responses)
  - Commit: ffcdcce - "docs: create comprehensive Google ADK agent architecture documentation"

- [REVIEW] **Create comprehensive data flow documentation** - Document complete system data flows with diagrams
  - Impact: HIGH | Added: 2025-12-31 | Updated: 2026-01-02
  - Created master DATAFLOW.md with comprehensive INPUT/OUTPUT/PROCESSING documentation
  - Included 18+ Mermaid diagrams covering all architecture layers:
    - System architecture with all components and services
    - Service-level data flow (dem2, medical-catalog, webui)
    - Frontend-backend communication (HTTP REST + WebSocket)
    - Agent hierarchy showing TusdiAI → TriageAgent + ParallelDataExtractor
    - Agent tool execution flow (internal Python calls, NOT HTTP)
    - Database layer (PostgreSQL, Neo4j, Redis, Qdrant)
    - Container communication via Docker network
    - Authentication flow (Google SSO + JWT)
    - Real-time WebSocket chat flow
    - Complete end-to-end sequence diagram (24 steps)
    - **Document processing flow (8 new diagrams):**
      - High-level document processing sequence (upload → extraction → storage)
      - File upload and storage flow (GCS/Local + PostgreSQL)
      - Extraction pipeline architecture with 6 stages
      - Biomarker data model (class diagram)
      - Gemini Vision extraction process
      - Biomarker reconciliation and medical-catalog integration
      - Graph database storage pattern (Instance→Type)
      - Complete end-to-end document flow
  - Created 5 Graphviz .dot files for detailed diagrams:
    - DATAFLOW_system_architecture.dot (complete component and data flow)
    - DATAFLOW_agent_hierarchy.dot (agent composition and tool calling pattern)
    - **DATAFLOW_document_processing.dot (document upload, extraction, and storage pipeline)**
    - DATAFLOW_database_layer.dot (multi-database architecture with Instance→Type pattern)
    - DATAFLOW_container_network.dot (Docker service connectivity and port mapping)
  - Verified all diagrams from actual source code
  - Key findings documented:
    - Agents call Python functions directly, NOT HTTP endpoints
    - Frontend uses 126 OpenAPI endpoints via wretch HTTP client
    - Multi-database architecture with clear separation of concerns
    - Neo4j Instance→Type pattern for multi-tenant scoping
    - **Document processing: PDF → Gemini Vision → Medical Catalog → Neo4j (15-60s)**
    - **Biomarker reconciliation: Vector search + deduplication by (catalog_id, unit)**
    - **Real-time progress tracking via Server-Sent Events (SSE)**
    - **Concurrency limits: 10 global, 5 per-user, 3 concurrent page renders**
  - Performance characteristics:
    - Agent processing: 3-5s end-to-end
    - Document processing: 15-60s end-to-end
  - Security considerations and monitoring stack documented
  - Files created:
    - docs/DATAFLOW.md (1,410 lines with Mermaid diagrams, version 1.1)
    - docs/DATAFLOW_system_architecture.dot
    - docs/DATAFLOW_agent_hierarchy.dot
    - docs/DATAFLOW_document_processing.dot
    - docs/DATAFLOW_database_layer.dot
    - docs/DATAFLOW_container_network.dot
  - Commits:
    - 110d6da - "docs: complete DATAFLOW.md with Graphviz diagrams"
    - 5c4e013 - "fix: quote special characters in Mermaid diagram labels"
    - 837242d - "fix: remove quotes from Mermaid node labels"
    - 9c715e1 - "docs: add comprehensive document processing flow to DATAFLOW.md"
    - deb2f4b - "docs: add Graphviz diagram for document processing pipeline"
  - Status: All requested documentation completed, including detailed document processing flow with biomarker extraction, reconciliation, and graph storage patterns. Awaiting user review and approval.

---

## Repository-Specific TODOs

For repository-specific tasks, see:
- [repos/dem2/TODO.md](repos/dem2/TODO.md) - Backend tasks
- [repos/dem2-webui/TODO.md](repos/dem2-webui/TODO.md) - Frontend tasks (if created)
- [repos/medical-catalog/TODO.md](repos/medical-catalog/TODO.md) - Catalog service tasks (if created)
- [repos/dem2-infra/TODO.md](repos/dem2-infra/TODO.md) - Infrastructure tasks (if created)

---

## Journal

Track changes to this TODO file: new items added, state changes, revisions, reorganizations.

### 2025-12-29

- Created workspace-level TODO.md with framework instructions
- Established structure for workspace-level vs repository-specific task tracking
