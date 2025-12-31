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
