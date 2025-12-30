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
  - Commits: ed93bb3, (pending: OpenAPI integration)
  - Status: Updated to use OpenAPI JSON, awaiting user review and approval

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
