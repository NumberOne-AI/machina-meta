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

<!-- Add tasks that span multiple repositories (e.g., coordinated releases, cross-repo refactoring) -->

---

## Workspace - Infrastructure & CI/CD

<!-- Add workspace-level infrastructure tasks (e.g., unified testing, deployment coordination) -->

---

## Workspace - Documentation & Tooling

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
