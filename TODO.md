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

- [PROPOSED] **Migrate Text-to-Cypher to `neo4j-graphrag`** - Standardize GraphRAG implementation
  - Impact: HIGH | Added: 2026-01-27
  - **Proposal**: [docs/proposals/GRAPH_RAG_MIGRATION.md](docs/proposals/GRAPH_RAG_MIGRATION.md)
  - **Goal**: Replace custom Text-to-Cypher implementation in `CypherAgent` with official library.

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

### 2026-01-27
- Moved completed tasks to DONE.md.
- Reverted DOCX to image conversion to [STARTED].
