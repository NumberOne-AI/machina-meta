# PROBLEMS

This file tracks known problems, issues, and challenges that may or may not have solutions yet.
Problems are observations that need investigation before becoming actionable TODO items.

## ⚠️ CRITICAL: Immediate Commit Requirement

**Changes to this file (and TODO.md) MUST be committed to git immediately after modification.**

Do not batch changes to PROBLEMS.md or TODO.md with other work. These files track project state and must be version-controlled as soon as they are updated.

## Relationship to TODO.md

```
PROBLEMS.md                          TODO.md
┌─────────────────┐                 ┌─────────────────┐
│ [OPEN] Problem  │ ──investigate──▶│ [PROPOSED] Task │
│                 │                 │                 │
│ [INVESTIGATING] │ ──solution────▶ │ [STARTED] Task  │
│                 │                 │                 │
│ [SOLVED]        │ ◀──completed─── │ [DONE] Task     │
└─────────────────┘                 └─────────────────┘
```

- **OPEN** problems need investigation to understand root cause
- **INVESTIGATING** problems have active analysis or proposed solutions
- **SOLVED** problems have completed TODO items addressing them
- **WONT_FIX** problems are acknowledged but intentionally not addressed

## Problem Format

Each problem includes:
- State: `[OPEN]`, `[INVESTIGATING]`, `[SOLVED]`, or `[WONT_FIX]`
- Severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- Added: Date problem was identified
- Related TODOs: Links to TODO.md items addressing this problem
- Observations: Evidence or symptoms of the problem

**Severity Levels**:
- `CRITICAL` - Blocking production or core functionality
- `HIGH` - Significant impact on users or development
- `MEDIUM` - Notable issue worth tracking
- `LOW` - Minor annoyance or edge case

---

## Workspace - Multi-Repo Coordination

<!-- Add workspace-level problems that affect multiple repositories -->

---

## Workspace - Infrastructure

- [OPEN] **502 Bad Gateway on preview-92 bulk file upload** - QA intermittently sees 502 errors on file uploads
  - Severity: MEDIUM | Added: 2026-01-15
  - Related TODOs: None yet
  - **Environment**: preview-92.n1-machina.dev
  - **Endpoint**: `POST /api/v1/file-storage/files/upload/bulk`
  - **Symptoms**:
    - QA reports 502 Bad Gateway when uploading multiple files via browser
    - Upload uses `XMLHttpRequest` with `multipart/form-data`
    - Chrome 143 on Windows, 12 PDF files (~20MB total)
  - **Attempted Fix: Traefik Buffering Middleware** (REVERTED):
    - **Commit**: `487ff43` (dem2-infra PR #93) - Added `upload-buffering-middleware.yaml`
    - **Revert**: `37b2d43` (dem2-infra PR #94) - Reverted due to i/o timeout errors
    - **Config tried**:
      ```yaml
      apiVersion: traefik.io/v1alpha1
      kind: Middleware
      metadata:
        name: upload-buffering
        namespace: gateway
      spec:
        buffering:
          maxRequestBodyBytes: 524288000  # 500MB
          maxResponseBodyBytes: 104857600  # 100MB
          retryExpression: "IsNetworkError() && Attempts() < 2"
      ```
    - **Result: Made things WORSE** - Traefik logged errors:
      ```
      ERR vulcand/oxy/buffer: error when reading request body, err: i/o timeout
        middlewareName=gateway-upload-buffering@kubernetescrd
        routerName=tusdi-dev-tusdi-ingress-dev-n1-machina-dev-api@kubernetes
      ```
    - **Root cause of failure**: Buffering middleware reads entire request body into memory before forwarding; this triggers Traefik's default read timeout for large uploads
  - **Investigation Findings** (2026-01-15):
    - **Pod Status**: tusdi-api running 27h, 1 restart (27h ago) - stable
    - **Traefik Logs**: No recent "no endpoints found" errors; old errors from Jan 14
    - **Endpoints**: Kubernetes endpoints healthy, traffic routing correctly
    - **Curl Testing**: Could NOT reproduce with QA's exact headers
      - 9 files (15.3 MB): HTTP 200 in 2.67s
      - 11 files (19.3 MB): HTTP 200 in 3.5s
      - HTTP/2 tested: HTTP 200
    - **401 Test**: Expired token correctly returns 401 (reaches backend, not 502)
  - **Architecture Context**:
    - Traffic flow: Browser → GKE L4 Load Balancer → Traefik Ingress → tusdi-api
    - Frontend uses `XMLHttpRequest` in `dem2-webui/src/lib/upload-file.ts`
    - Traefik v3.5.3 with default timeout configuration
  - **Potential Causes Still Under Investigation**:
    1. **Transient network issue**: Load balancer or Traefik momentary hiccup
    2. **QA-specific environment**: Browser extensions, corporate proxy, VPN
    3. **Timing-sensitive race condition**: Specific file sizes or upload timing
    4. **HTTP/2 multiplexing edge case**: Browser HTTP/2 vs curl HTTP/1.1 behavior
    5. **Traefik static timeout config**: May need to modify Traefik deployment ConfigMap
  - **Status**: Cannot reproduce via curl; buffering middleware approach failed and was reverted; marked OPEN pending more QA reports with timestamps
  - **Next Steps**:
    - [ ] Request exact timestamp from QA when 502 occurs
    - [ ] Cross-reference with Traefik logs at that timestamp
    - [ ] Check GKE load balancer logs for connection resets
    - [ ] Test with browser automation (Playwright) to match exact browser behavior
    - [ ] Investigate Traefik static timeout configuration (ConfigMap changes)

- [OPEN] **Document processing task silently dropped during bulk upload** - 1 of 12 files failed to process with no error logged
  - Severity: HIGH | Added: 2026-01-16
  - Related TODOs: None yet
  - **Environment**: preview-92 (tusdi-preview-92 namespace)
  - **Affected File**: `Boston Heart - May 2024.pdf` (file_id: `42b5036a-29bd-43e7-abf9-21e44b1ef712`)
  - **Symptoms**:
    - 12 files uploaded via bulk upload at 09:50:36 UTC
    - 11 files processed successfully and saved to Neo4j with `processing_status: completed`
    - 1 file (Boston Heart - May 2024) has no corresponding `DocumentReferenceNode` in Neo4j
    - **No logs containing the file ID** - task was never started or silently failed to enqueue
    - File exists in PostgreSQL `filerecord` table but `document_reference_id` is NULL
  - **Investigation Findings** (2026-01-16):
    - **Database Connection Contention**: Multiple `session_held_too_long` warnings during bulk upload
      - Sessions held for 22s to 200+ seconds
      - Stack trace shows contention in `task_processor.py` → `docproc/service.py` → `file_storage/repository.py`
    - **Auth Errors**: "Unexpected error during token validation" and "Future exception was never retrieved" around 09:54:40
    - **Task Queue**: In-memory task queue - no persistence across pod restarts
    - **Pod Restart**: Pod was replaced at 20:17 (10+ hours after upload) - NOT the cause
    - **Successful Files**: All other Boston Heart files (July 2021, June 2025, Sep 2024) processed correctly
  - **Root Cause Analysis**:
    - When 12 files uploaded simultaneously, the task queue tried to process all concurrently
    - Database connection pool was exhausted, causing some operations to timeout or fail silently
    - This specific file's task either:
      1. Failed to enqueue due to connection timeout
      2. Was enqueued but the enqueue confirmation was lost
      3. Started processing but failed before any log entry was written
    - No error handling or retry mechanism caught this silent failure
  - **Code Locations**:
    - Task processor: `repos/dem2/shared/src/machina/shared/tasks/task_processor.py:67`
    - Document processing: `repos/dem2/services/docproc/src/machina/docproc/service.py:465`
    - File storage: `repos/dem2/services/file-storage/src/machina/file_storage/repository.py:33`
  - **Potential Fixes**:
    1. **Rate limiting**: Limit concurrent document processing tasks to prevent pool exhaustion
    2. **Persistent task queue**: Use Redis or PostgreSQL for task state instead of in-memory
    3. **Better error handling**: Log file ID at task enqueue time, not just at processing start
    4. **Health check**: Periodic reconciliation between `filerecord` and Neo4j to detect orphaned files
    5. **Retry mechanism**: Automatic retry for tasks that fail to start
  - **Workaround**: Manually re-trigger processing for the affected file via UI or API
  - **Next Steps**:
    - [ ] Re-process Boston Heart - May 2024.pdf manually
    - [ ] Investigate adding rate limiting to bulk upload processing
    - [ ] Consider persistent task queue (Redis-backed)
    - [ ] Add logging at task enqueue time with file ID
    - [ ] Create reconciliation script to detect orphaned files

- [INVESTIGATING] **Gemini 3 Max Tokens Error (2026-01-24)**
  - Severity: MEDIUM | Added: 2026-01-24
  - Status: [INVESTIGATING]
  - Evidence Report: [docs/evidence/gemini-3-max-tokens-error-2026-01-24.md](docs/evidence/gemini-3-max-tokens-error-2026-01-24.md)
  - Description: `FinishReason.MAX_TOKENS` observed in `tusdi-preview-92` logs for Gemini 3 Pro.
  - Evidence: `finish_reason=FinishReason.MAX_TOKENS model=gemini-3-pro-preview`
  - Impact: Document extraction fails for large documents or complex reasoning paths.
  - Related TODO: "Enhance docproc generic parser with Gemini 3 controls"

---

## Workspace - Documentation & Tooling

- [OPEN] **Skillification context management challenges** - Risk of skills not loading when needed or loading unnecessarily
  - Severity: MEDIUM | Added: 2026-01-12
  - Related TODOs: "Convert CLAUDE.md to skill-based architecture" (TODO.md)
  - **Observations**:
    - Converting CLAUDE.md (1,272 lines) into 16 skills promises 68% token savings (~15,173 tokens)
    - But this assumes skills load correctly and only when needed
    - Risk of skills not invoking when context requires them (missing critical information)
    - Risk of skills loading unnecessarily (defeating the purpose)
    - Risk of circular dependencies between skills
    - Risk of skills becoming out of sync with each other
  - **Specific Concerns**:
    1. **Invocation Accuracy**: Will Claude Code correctly detect when a skill is needed?
       - Example: User asks about "document processing" - should load machina-api-testing?
       - Example: User asks "How do I setup?" - clear trigger for machina-setup
       - Example: User asks general question - might need machina-structure for context
    2. **Critical Context Loss**: Are the 405 lines kept in core CLAUDE.md sufficient?
       - What if a workflow needs information from multiple skills?
       - What if critical safety rules reference content moved to skills?
       - Will Architecture Analysis Protocol still work without full workspace context?
    3. **Skill Dependencies**: Some skills naturally reference others
       - machina-api-testing references machina-setup (need backend running first)
       - machina-docs references machina-todo (task tracking for doc updates)
       - machina-preview references machina-submodules (git workflow)
       - How to handle cascading skill loads without loading everything?
    4. **Maintenance Burden**: Keeping 16+ skills synchronized
       - When CLAUDE.md core changes, which skills need updates?
       - When a skill changes, how to identify dependent skills?
       - Risk of information drift between skills over time
    5. **Token Savings Reality**: Will we actually save tokens?
       - If many workflows require 3-4 skills, might load 300+ lines anyway
       - Initial skill invocation adds metadata overhead
       - Might actually increase tokens if skills invoke incorrectly
  - **Evidence Needed**:
    - [ ] Measure actual skill invocation patterns in real conversations
    - [ ] Track how many skills get loaded per typical workflow
    - [ ] Identify which skills are frequently loaded together (dependency patterns)
    - [ ] Measure real token savings after implementation vs theoretical 68%
    - [ ] Count false negatives (skill should load but doesn't)
    - [ ] Count false positives (skill loads unnecessarily)
  - **Potential Solutions Under Consideration**:
    - **Option 1: Hierarchical Skills** - Group related skills into parent skills
      - machina-dev (includes: setup, dev-patterns, services, troubleshoot)
      - machina-git-workflows (includes: submodules, preview)
      - machina-testing (includes: api-testing, reference)
      - Reduces skill count but increases average skill size
    - **Option 2: Lazy Loading with Cache** - Load skills once per session, keep in context
      - First invocation loads skill, subsequent references use cached version
      - Reduces repeated skill loading overhead
      - But defeats token savings if skills stay loaded
    - **Option 3: Hybrid Approach** - Keep frequently-used content in core, only extract rarely-used
      - Keep: api-testing basics, common setup, troubleshooting (top 20% by usage)
      - Extract: Advanced api-testing, nix, gcloud, env (bottom 80% by usage)
      - Requires usage data to identify the 80/20 split
    - **Option 4: Context-Aware Loading** - Skills know their dependencies and load together
      - machina-api-testing auto-loads machina-setup if not loaded
      - machina-preview auto-loads machina-submodules if not loaded
      - Requires sophisticated skill metadata
  - **Decision Criteria**:
    - Measured token savings > 50% of theoretical (i.e., >7,500 tokens saved in practice)
    - Skill invocation accuracy > 90% (correct skill loaded when needed)
    - False negatives < 5% (rarely miss loading a needed skill)
    - Maintenance time < 10 min/month to keep skills synchronized
    - User experience: No noticeable degradation in response quality/relevance
  - **Next Steps**:
    1. Implement minimal prototype with 3 skills (api-testing, setup, troubleshoot)
    2. Measure real-world invocation patterns over 10 conversations
    3. Calculate actual token savings vs theoretical
    4. Decide: full rollout, adjust approach, or abandon based on data
  - **Status**: Needs investigation and prototyping before full implementation

---

## Workspace - Agent System

- [SOLVED] **Syntax errors caused by tenant patient_id query injection in CypherAgent** - TenantInjector breaks multi-word Cypher operators
  - Severity: HIGH | Added: 2026-01-23 | Solved: 2026-01-23
  - Related TODOs: "Replace TenantInjector with Neo4j RBAC security" (TODO.md - Workspace - Agent System)
  - Related Plan: [docs/plans/remove-tenant-injector.md](docs/plans/remove-tenant-injector.md)
  - Executive Summary: [docs/plans/remove-tenant-injector-executive-summary.md](docs/plans/remove-tenant-injector-executive-summary.md)
  - Evidence Log: [logs/tenant-injection-syntax-errors-2026-01-23.log](logs/tenant-injection-syntax-errors-2026-01-23.log)
  - **Environment**: tusdi-preview-92 (and all environments using TenantInjector)
  - **Symptoms**:
    - Queries with `STARTS WITH`, `ENDS WITH`, or similar patterns fail with `Neo.ClientError.Statement.SyntaxError`
    - Error: `Invalid input ')': expected 'WITH'`
    - Agent sees repeated failures and cannot recover
  - **Root Cause Analysis**:
    - `WhereClauseBuilder._find_where_clause_end()` in `where_clause_builder.py` (lines 149-190) searched for clause boundaries
    - When CypherAgent generated `STARTS WITH "value"`, the injector found `WITH` keyword
    - It incorrectly interpreted this as a new WITH clause, not part of `STARTS WITH`
    - Injected `AND ov.patient_id = $patient_id` between `STARTS` and `WITH "value"`
    - **Result**: `WHERE (toLower(ot.summary) STARTS) AND ov.patient_id = $patient_id WITH "t"` - BROKEN SYNTAX
  - **Solution Implemented (Stage 1)**:
    - Removed TenantInjector (~918 lines of fragile regex code deleted)
    - Updated CypherAgent prompts with explicit patient_id injection rules
    - Created QuerySecurityValidator for logging (audit trail, not blocking)
    - Queries now generated with `WHERE ov.patient_id = $patient_id` by LLM prompt engineering
  - **Files Changed**:
    - `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/config.yml` - Added patient_id filtering rules
    - `repos/dem2/shared/src/machina/shared/graph_traversal/service.py` - Removed TenantInjector
    - `repos/dem2/shared/src/machina/shared/graph_traversal/query_validator.py` - NEW: QuerySecurityValidator
  - **Files Deleted**:
    - `repos/dem2/shared/src/machina/shared/graph_traversal/tenant_injector.py` (531 lines)
    - `repos/dem2/shared/src/machina/shared/graph_traversal/where_clause_builder.py` (387 lines)
    - `repos/dem2/shared/tests/graph_traversal/test_tenant_injector.py`
    - `repos/dem2/shared/tests/graph_traversal/test_where_clause_builder.py`
  - **Stage 2 (Future - Deferred)**: Add Neo4j RBAC as database-enforced safety net
    - Requires Neo4j Enterprise Edition (~$36,000+/year)
    - Per-patient users with property-based access control
    - Use impersonation to execute queries in patient's security context
    - Deferred pending cost/benefit analysis

- [SOLVED] **CypherValidator false failures when only parameter errors exist** - is_valid calculated before filtering
  - Severity: MEDIUM | Added: 2026-01-24 | Solved: 2026-01-24
  - Related TODOs: "Fix CypherValidator false validation failures" (TODO.md - Workspace - Agent System)
  - **Environment**: All environments using CypherValidator (graph query validation)
  - **Symptoms**:
    - Backend logs show `Query validation failed` with empty errors array
    - Valid queries incorrectly flagged as invalid
    - Log entry: `{'event': 'Query validation failed', 'errors': []}`
    - CypherValidationError raised but no actual errors to report
  - **Root Cause Analysis**:
    - `CypherValidator.validate()` in `validator.py` (lines 126-127) had logic bug:
      ```python
      is_valid = len(errors) == 0  # Calculated BEFORE filtering
      return is_valid, self._filter_parameter_errors(errors)  # Returns FILTERED list
      ```
    - When SyntaxValidator reports `parameternotprovided` for `patient_id`/`user_id`:
      - Raw `errors` list has 1 entry → `is_valid = False`
      - `_filter_parameter_errors()` removes patient_id/user_id warnings
      - Returns `(False, [])` - invalid status with empty errors
    - This causes `CypherValidationError` to be raised with no explanation
  - **Solution Implemented**:
    - Calculate `is_valid` AFTER filtering:
      ```python
      filtered_errors = self._filter_parameter_errors(errors)
      is_valid = len(filtered_errors) == 0
      return is_valid, filtered_errors
      ```
  - **File Modified**:
    - `repos/dem2/shared/src/machina/shared/graph_traversal/validator.py` (lines 126-128)
  - **Verification**:
    - Rebuilt backend with `just dev-restart`
    - Ran test query: "Show me all my test results where the biomarker name starts with the letter T"
    - 0 "Query validation failed" messages in logs after fix

---

## Repository-Specific Problems

For repository-specific problems, see:
- [repos/dem2/PROBLEMS.md](repos/dem2/PROBLEMS.md) - Backend issues
- [repos/dem2-webui/PROBLEMS.md](repos/dem2-webui/PROBLEMS.md) - Frontend issues (if created)
- [repos/medical-catalog/PROBLEMS.md](repos/medical-catalog/PROBLEMS.md) - Catalog service issues (if created)
- [repos/dem2-infra/PROBLEMS.md](repos/dem2-infra/PROBLEMS.md) - Infrastructure issues (if created)
