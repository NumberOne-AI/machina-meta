# TODO

This file tracks planned work, improvements, and technical debt for the gcloud-admin container.
Update continuously as work progresses.

## Task States
- **PROPOSED** - Under consideration, not yet approved
- **STARTED** - Approved and in progress
- **DONE** - Completed
- **REVERTED** - Was DONE but later rolled back
- **CANCELLED** - Removed from scope with documented reason

## Task Format
Each task includes:
- State: `[PROPOSED]`, `[STARTED]`, `[DONE]`, `[REVERTED]`, or `[CANCELLED]`
- Impact: `HIGH`, `MEDIUM`, or `LOW`
- Added: Date task was created
- Completed: Date task was finished (for DONE items)

## Task Journal Requirements

**All changes to a task MUST be journaled within the task entry.**

When modifying an existing task:
- Adding steps: Add with `- [ ]` checkbox
- Completing steps: Change `- [ ]` to `- [x]` with completion note
- Removing steps: Do NOT delete. Mark as: `- [CANCELLED] Step - Reason (date)`
- Changing scope: Add a note explaining the change

## Impact Levels
- **HIGH** - Critical for operations, blocking deployments, or security
- **MEDIUM** - Important improvement, enhances reliability or usability
- **LOW** - Nice to have, minor improvement

## ⚠️ CRITICAL: Immediate Commit Requirement

**Changes to this file (and PROBLEMS.md) MUST be committed to git immediately after modification.**

Do not batch changes to TODO.md or PROBLEMS.md with other work.

---

## Container Image

### Tool Updates

- [PROPOSED] **Automate tool version updates**
  - Impact: MEDIUM | Added: 2025-12-18
  - Create script to check for newer versions of installed tools
  - Consider Renovate or Dependabot for Dockerfile

- [PROPOSED] **Add Terraform CLI**
  - Impact: LOW | Added: 2025-12-18
  - For infrastructure changes managed outside Kubernetes
  - Version: latest stable

### Image Optimization

- [PROPOSED] **Multi-stage build for smaller image**
  - Impact: LOW | Added: 2025-12-18
  - Current image is large due to dev dependencies
  - Separate build stage from runtime stage

---

## Cluster Operations

### Authentication

- [DONE] **Initial container setup with GKE auth**
  - Impact: HIGH | Added: 2025-12-18 | Completed: 2025-12-18
  - [x] Dockerfile with gke-gcloud-auth-plugin
  - [x] docker-compose.yaml with volume mounts
  - [x] justfile with common operations
  - [x] Tested GKE cluster access

### Monitoring

- [PROPOSED] **Add Prometheus/Grafana CLI tools**
  - Impact: LOW | Added: 2025-12-18
  - `promtool` for PromQL validation
  - CLI access to Grafana dashboards

---

## Deployment Automation

### Preview Environments

- [PROPOSED] **Add preview environment management commands**
  - Impact: MEDIUM | Added: 2025-12-18
  - `just preview-create <id>` - Create preview namespace
  - `just preview-delete <id>` - Clean up preview
  - `just preview-list` - List active previews

### Rollback Procedures

- [PROPOSED] **Document rollback procedures**
  - Impact: HIGH | Added: 2025-12-18
  - ArgoCD rollback commands
  - Database migration rollback
  - Kubernetes deployment rollback

---

## Documentation

- [DONE] **Initial documentation**
  - Impact: MEDIUM | Added: 2025-12-18 | Completed: 2025-12-18
  - [x] README.md with usage instructions
  - [x] CLAUDE.md for AI assistance
  - [x] TODO.md framework
  - [x] PROBLEMS.md framework

---

## Historical / Completed

(Move completed items here to keep active section clean)
