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

---

## Workspace - Infrastructure & CI/CD

- [STARTED] **Research Argo Workflows and install on GKE** - Evaluate workflow orchestration capabilities
  - Impact: MEDIUM | Added: 2026-01-21
  - **Documentation**: [docs/ARGO_WORKFLOWS.md](docs/ARGO_WORKFLOWS.md)
  - **Goal**: Understand Argo Workflows capabilities and install on GKE cluster for document processing
  - **Research Areas**:
    - [ ] Core concepts: Workflows, WorkflowTemplates, DAGs, Steps
    - [ ] Artifact handling: S3/GCS artifact repository setup
    - [ ] Event triggers: Argo Events for webhook/message triggers
    - [ ] Resource management: Pod resource limits, parallelism control
    - [ ] Monitoring: Argo UI, metrics, logging integration
    - [ ] Security: RBAC, service accounts, secrets handling
  - **Installation Tasks**:
    - [ ] Add Argo Workflows Helm chart to dem2-infra
    - [ ] Configure artifact repository (GCS bucket)
    - [ ] Set up Argo UI ingress with auth
    - [ ] Create namespace and RBAC for workflows
    - [ ] Test basic workflow execution
  - **Evaluation Criteria**:
    - Integration with existing Kubernetes setup
    - Learning curve for team
    - Comparison with Celery (current task queue)
    - Cost implications (controller resources)
  - **Documentation**: Create docs/ARGO_WORKFLOWS.md with findings

- [PROPOSED] **Use Argo Workflows for parallel document processing pipeline** - Orchestrate docproc stages as DAG workflow
  - Impact: HIGH | Added: 2026-01-21
  - **Documentation**: [docs/ARGO_WORKFLOWS.md](docs/ARGO_WORKFLOWS.md)
  - **Depends On**: Research Argo Workflows and install on GKE (above)
  - **Problem**: Current document processing runs sequentially, limiting throughput for batch uploads
  - **Proposed Solution**: Use Argo Workflows to orchestrate extraction pipeline stages as parallel DAG
  - **Benefits**:
    - Parallel processing of multiple documents simultaneously
    - Retry logic and fault tolerance at workflow level
    - Visual monitoring of pipeline progress in Argo UI
    - Resource-efficient: spin up workers on-demand via Kubernetes
    - Decoupled stages: easier to debug, test, and scale independently
  - **Pipeline Stages to Orchestrate**:
    - Document upload/validation
    - Page rendering (parallel per page)
    - Gemini Vision extraction (parallel per page)
    - Result aggregation
    - Medical catalog enrichment
    - Neo4j graph storage
  - **Implementation Tasks**:
    - [ ] Define WorkflowTemplate for docproc pipeline
    - [ ] Create Argo Events integration for upload triggers
    - [ ] Set up artifact passing between stages (GCS)
    - [ ] Configure resource limits per stage
    - [ ] Add workflow definitions to dem2-infra
    - [ ] Integrate with existing task tracking
    - [ ] Migrate from Celery or run hybrid
  - **Related**: docs/DATAFLOW.md (document processing flow)

- [PROPOSED] **Add GKE service port-forwarding via gcloud-admin** - Enable querying remote Neo4j/services from host
  - Impact: MEDIUM | Added: 2026-01-21
  - **Problem**: Current gcloud-admin kubectl port-forward only works inside the container, not accessible from host
  - **Use Case**: Need to query Neo4j on preview/dev environments for debugging (e.g., duplicate biomarker investigation)
  - **Current Workaround**: Run kubectl directly on host (requires local kubectl+gcloud setup)
  - **Proposed Solution**:
    - Add port mapping to docker-compose when running port-forward commands
    - Example: `docker compose run --rm -p 17474:17474 gcloud-admin kubectl port-forward ...`
    - Or create a dedicated justfile recipe that handles the double port-forward
  - **Implementation Options**:
    1. Add `just gcloud-admin::forward-neo4j <namespace>` recipe that handles port mapping
    2. Add generic `just gcloud-admin::forward <namespace> <service> <local-port> <remote-port>` recipe
    3. Document the manual docker-compose run command with port mapping
  - **Required for**: Remote Neo4j querying, debugging production/preview data issues
  - **Files to modify**:
    - `gcloud-admin/justfile` - Add port-forward recipes
    - `gcloud-admin/CLAUDE.md` - Document usage
    - `CLAUDE.md` - Reference in debugging section

- [PROPOSED] **Research Neo4j indexes to optimize query_graph performance** - Investigate index strategies for medical agent queries
  - Impact: HIGH | Added: 2026-01-21
  - **Problem**: Analysis of tusdi-preview-92 LLM traces shows `query_graph` tool (Neo4j) is primary bottleneck
    - 16.7% of requests exceed 60 seconds
    - Max response time: 710.65s (11.8 minutes)
    - Tool execution consumes 87-100% of time in slow queries
    - See: `docs/ANALYSIS_OF_MEDICAL_AGENT_QUERIES_tusdi-preview-92_20260121.md`
  - **Research Areas**:
    - [ ] Neo4j index types: B-tree, full-text, range, point, token lookup
    - [ ] Composite indexes for common query patterns
    - [ ] Index usage analysis with `EXPLAIN` and `PROFILE` on slow queries
    - [ ] Current index state: `SHOW INDEXES` on production Neo4j
    - [ ] Query patterns from HealthConsultantAgent's Cypher generation
    - [ ] Index memory implications and trade-offs
  - **Investigation Steps**:
    - [ ] Extract common Cypher query patterns from LLM traces
    - [ ] Profile slow queries with `PROFILE` to identify full scans
    - [ ] Identify missing indexes on frequently filtered properties
    - [ ] Research Neo4j best practices for medical/graph data models
    - [ ] Document index recommendations with expected impact
  - **Key Questions**:
    - Which node labels are most frequently queried? (Observation, Biomarker, Patient?)
    - Which properties are used in WHERE clauses?
    - Are there relationship traversals that could benefit from indexes?
    - What's the current index coverage on the graph schema?
  - **Related**:
    - P0 Action: Add 30s timeout to query_graph tool (separate task)
    - Analysis: `docs/MEDICAL_AGENT_QUERIES_tusdi-preview-92_20260121.md`
    - Script: `scripts/analyze_llm_traces.py`
  - **Output**: Create `docs/NEO4J_INDEX_RECOMMENDATIONS.md` with findings

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
  - **Detailed plan**: [docs/plans/minikube-dev-stack-support.md](docs/plans/minikube-dev-stack-support.md)

---

## Workspace - Agent System

- [PROPOSED] **Migrate Text-to-Cypher to `neo4j-graphrag`** - Standardize GraphRAG implementation with security best practices
  - Impact: HIGH | Added: 2026-01-27
  - **Proposal**: [docs/proposals/GRAPH_RAG_MIGRATION.md](docs/proposals/GRAPH_RAG_MIGRATION.md)
  - **Goal**: Replace custom, fragile Text-to-Cypher implementation in `CypherAgent` with official `neo4j-graphrag` library
  - **Benefits**:
    - **Security**: Moves from regex-based validation to Neo4j PBAC + Impersonation (enforced by DB kernel)
    - **Reliability**: Uses standard, battle-tested schema introspection via APOC
    - **Maintenance**: Offloads prompt engineering and parsing logic to official library
  - **Migration Phases**:
    1.  Integration & Proof of Concept (Done)
    2.  Implementation of Safe Components (`PBACText2CypherRetriever`)
    3.  Agent Migration (Update `CypherAgent`)
    4.  Cleanup (Remove legacy schema formatter and regex parsers)
  - **Related**:
    - PROBLEMS.md "Fragile Text-to-Cypher implementation in CypherAgent" [OPEN]
    - TODO.md "Remove TenantInjector and add Neo4j RBAC security" [DONE]

- [STARTED] **DOCX to image conversion for Gemini Vision processing** - High-quality document rendering for LLM extraction
  - Impact: MEDIUM | Added: 2026-01-22
  - **Problem**: Need to convert DOCX files to images for Gemini Vision API processing
  - **Current State**:
    - ✅ Spire.Doc: Works but only outputs ~96 DPI (unreadable for OCR)
    - ✅ LibreOffice + poppler: Works at 300 DPI (industry standard)
    - ✅ Docker container: Fixed for non-root users
  - **Completed**:
    - [x] Add extraction-only modes (extract-text, extract-images, extract-all)
    - [x] Increase default DPI from 200 to 300
    - [x] Add `media_resolution="high"` for Gemini API
    - [x] Skip Spire.Doc when DPI > 150 (doesn't support custom resolution)
    - [x] Fix Docker container permissions (uv, cache, HOME)
    - [x] Commit: a8763c7 "feat(scripts): add extraction-only modes and 300 DPI support"
  - **Research**:
    - [ ] Evaluate Syncfusion's DocIO as alternative to Spire.Doc
      - .NET library (like Spire.Doc) for DOCX processing
      - May support custom DPI for image rendering
      - Check licensing and Python integration options
  - **Files**:
    - `scripts/gemini_docx_poc.py` - Main conversion script
    - `scripts/spire-doc-poc/` - Docker container for DOCX processing

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