# DEVOPS.md - DevOps and Infrastructure Guide

**Version:** 1.0
**Last Updated:** 2026-01-06

This document provides comprehensive guidance for DevOps operations in the MachinaMed workspace, including preview environments, CI/CD pipelines, ArgoCD deployment workflows, and monitoring procedures.

## Table of Contents

- [Overview](#overview)
- [Preview Environments](#preview-environments)
- [CI/CD Pipelines](#cicd-pipelines)
- [ArgoCD Deployment](#argocd-deployment)
- [Monitoring and Observability](#monitoring-and-observability)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)

## Overview

The MachinaMed platform uses a multi-repository architecture with coordinated deployments across:

- **dem2**: Backend API service
- **dem2-webui**: Frontend web application
- **medical-catalog**: Biomarker catalog service
- **dem2-infra**: Kubernetes manifests and ArgoCD configuration

### Infrastructure Stack

- **Orchestration**: Kubernetes (GKE)
- **GitOps**: ArgoCD for continuous deployment
- **CI**: GitHub Actions for build and test
- **Registry**: Google Artifact Registry
- **Environments**: dev, staging, preview-*, production

## Preview Environments

Preview environments provide isolated deployments for feature branches, enabling testing before merging to main branches.

### How Preview Environments Work

1. **Feature Branch**: Developer pushes commits to a feature branch (e.g., `feature/docproc-extraction-pipeline`)
2. **Pull Request**: PR is created in dem2 repository (e.g., PR #421)
3. **Preview Branch**: Corresponding preview branch created in dem2-infra (e.g., `preview/docproc-extraction-pipeline`)
4. **Image Build**: GitHub Actions builds and pushes Docker images with preview tags
5. **Infrastructure Update**: dem2-infra preview branch references the preview image tags
6. **ArgoCD Sync**: ArgoCD ApplicationSet detects the preview branch and creates/syncs the application
7. **Deployment**: Application deploys to isolated namespace (e.g., `tusdi-preview-421`)

### Preview Environment Naming

| Component | Pattern | Example |
|-----------|---------|---------|
| Feature branch | `feature/<name>` | `feature/docproc-extraction-pipeline` |
| Pull request | PR #N | PR #421 |
| Preview branch (infra) | `preview/<name>` | `preview/docproc-extraction-pipeline` |
| ArgoCD application | `preview-pr-<N>` | `preview-pr-421` |
| Kubernetes namespace | `tusdi-preview-<N>` | `tusdi-preview-421` |
| Preview URL | `https://<name>.preview.n1-machina.dev` | `https://docproc-extraction-pipeline.preview.n1-machina.dev` |

### Creating a Preview Environment

**From machina-meta workspace:**

```bash
# Create/update preview environment
just preview <preview-id>

# Example
just preview docproc-extraction-pipeline
```

This command:
1. Tags dem2 and dem2-webui with `preview-<preview-id>-<commit-hash>`
2. Pushes tags to trigger Docker image builds
3. Creates/updates `preview/<preview-id>` branch in dem2-infra
4. Pushes infra changes to trigger ArgoCD sync

### Monitoring Preview Deployments

**Using the monitor script:**

```bash
# From machina-meta root
./scripts/monitor-preview.sh <preview-id> [options]

# Options
--timeout <secs>    # Max wait time (default: 600s)
--pr <number>       # PR number (auto-detected if not provided)
--poll-only         # Use polling instead of argocd app wait

# Examples
./scripts/monitor-preview.sh docproc-extraction-pipeline
./scripts/monitor-preview.sh docproc-extraction-pipeline --timeout 300
./scripts/monitor-preview.sh docproc-extraction-pipeline --pr 421
```

**Using kubectl directly:**

```bash
# Via gcloud-admin container
cd gcloud-admin
docker compose run --rm gcloud-admin kubectl get applications -n argocd | grep preview

# Check specific preview
docker compose run --rm gcloud-admin kubectl get application preview-pr-421 -n argocd -o yaml

# Check pods in preview namespace
docker compose run --rm gcloud-admin kubectl get pods -n tusdi-preview-421

# Watch deployment progress
docker compose run --rm gcloud-admin kubectl get pods -n tusdi-preview-421 -w
```

**Using ArgoCD CLI:**

```bash
# Login to ArgoCD
argocd login argo.n1-machina.dev --grpc-web --sso

# List preview applications
argocd app list --server argo.n1-machina.dev --grpc-web | grep preview

# Get application status
argocd app get preview-pr-421 --server argo.n1-machina.dev --grpc-web

# Wait for deployment
argocd app wait preview-pr-421 --server argo.n1-machina.dev --grpc-web --health --timeout 600

# Sync application manually
argocd app sync preview-pr-421 --server argo.n1-machina.dev --grpc-web
```

### Preview Environment Lifecycle

1. **Creation**: ArgoCD ApplicationSet auto-creates application when preview branch appears
2. **Updates**: Push to feature branch → New image build → Update infra branch → ArgoCD syncs
3. **Monitoring**: Use `monitor-preview.sh` or ArgoCD UI to track deployment status
4. **Testing**: Access via preview URL once healthy
5. **Cleanup**: Delete preview branch in dem2-infra to remove application

### Preview URLs and Access

Preview environments are accessible at:
```
https://<preview-id>.preview.n1-machina.dev
```

**ArgoCD UI for preview:**
```
https://argo.n1-machina.dev/applications/preview-pr-<N>
```

**GitHub PR (dem2-infra):**
```
https://github.com/NumberOne-AI/dem2-infra/pull/<N>
```

## CI/CD Pipelines

### GitHub Actions Workflows

#### dem2 Repository

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **PR Quality Checks** | Pull request | Lint, format, type check, tests |
| **Build Preview Docker Image** | Pull request | Build and push preview images |
| **Deploy to Dev Environment** | Push to `dev` | Deploy to dev environment |
| **Deploy to Staging Environment** | Push to `staging` | Deploy to staging environment |
| **Nightly Extraction Tests** | Schedule (3:30 AM) | Validate document extraction |
| **Nightly Answering Tests** | Schedule (5:00 AM) | Validate agent responses |

#### Workflow Status Monitoring

```bash
# List recent workflow runs
gh run list --limit 10

# Check runs for specific branch
gh run list --branch feature/docproc-extraction-pipeline --limit 5

# Watch active workflow
gh run watch <run-id>

# View workflow logs
gh run view <run-id> --log
```

### Docker Image Tags

| Environment | Tag Pattern | Example |
|-------------|-------------|---------|
| Development | `dev-<commit-hash>` | `dev-17e47eea` |
| Staging | `staging-<commit-hash>` | `staging-17e47eea` |
| Preview | `preview-<name>-<commit-hash>` | `preview-docproc-extraction-pipeline-17e47eea` |
| Production | `<version>` | `v1.2.3` |

### Image Registry

**Registry:** `us-central1-docker.pkg.dev/n1-machina1/tusdi/`

**Images:**
- `tusdi-api`: Backend API service
- `tusdi-webui`: Frontend web application

## ArgoCD Deployment

### Application Types

| Type | Purpose | Managed By |
|------|---------|------------|
| **dev** | Development environment | ArgoCD Application |
| **staging** | Staging environment | ArgoCD Application |
| **preview-pr-\*** | Preview environments | ArgoCD ApplicationSet |
| **gateway** | API Gateway | ArgoCD Application |
| **medical-catalog** | Catalog service | ArgoCD Application |
| **langfuse** | Observability platform | ArgoCD Application |

### ApplicationSet for Previews

ArgoCD ApplicationSet automatically creates preview applications based on branches in dem2-infra:

- **Source**: dem2-infra repository
- **Branch pattern**: `preview/*`
- **Application naming**: `preview-pr-<PR-number>`
- **Namespace**: `tusdi-preview-<PR-number>`
- **Polling**: Every 30 seconds

### Sync Status

| Status | Meaning |
|--------|---------|
| **Synced** | Deployed manifest matches desired state |
| **OutOfSync** | Changes in git not yet deployed |
| **Unknown** | Unable to determine status |

### Health Status

| Status | Meaning |
|--------|---------|
| **Healthy** | All resources running correctly |
| **Progressing** | Deployment in progress |
| **Degraded** | Some resources failing |
| **Missing** | Resources not found |

### Manual Operations

```bash
# Sync application
argocd app sync <app-name> --server argo.n1-machina.dev --grpc-web

# Hard refresh (bypass cache)
argocd app get <app-name> --hard-refresh --server argo.n1-machina.dev --grpc-web

# Rollback to previous revision
argocd app rollback <app-name> <revision> --server argo.n1-machina.dev --grpc-web

# Delete application
argocd app delete <app-name> --server argo.n1-machina.dev --grpc-web
```

## Monitoring and Observability

### Checking Application Status

**All applications:**
```bash
cd gcloud-admin
docker compose run --rm gcloud-admin kubectl get applications -n argocd
```

**Specific application:**
```bash
docker compose run --rm gcloud-admin kubectl get application <app-name> -n argocd -o yaml
```

### Pod Status

```bash
# List pods in namespace
docker compose run --rm gcloud-admin kubectl get pods -n <namespace>

# Describe pod
docker compose run --rm gcloud-admin kubectl describe pod <pod-name> -n <namespace>

# View logs
docker compose run --rm gcloud-admin kubectl logs <pod-name> -n <namespace> --tail=100

# Follow logs
docker compose run --rm gcloud-admin kubectl logs <pod-name> -n <namespace> -f
```

### Common Namespaces

| Namespace | Purpose |
|-----------|---------|
| `argocd` | ArgoCD control plane |
| `tusdi-dev` | Development environment |
| `tusdi-staging` | Staging environment |
| `tusdi-preview-*` | Preview environments |
| `gateway` | API Gateway |
| `medical-catalog` | Catalog service |

### Logs and Debugging

```bash
# Get events in namespace
docker compose run --rm gcloud-admin kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Check resource usage
docker compose run --rm gcloud-admin kubectl top pods -n <namespace>

# Interactive shell in pod
docker compose run --rm gcloud-admin kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Port forward to local machine
docker compose run --rm -p 8080:8080 gcloud-admin kubectl port-forward -n <namespace> svc/<service-name> 8080:80
```

## Common Operations

### Updating a Preview Environment

**Scenario**: You've pushed new commits to a feature branch and want to deploy to preview.

```bash
# 1. Push commits to feature branch (already done)
cd repos/dem2
git push origin feature/docproc-extraction-pipeline

# 2. Update preview environment from workspace root
cd /path/to/machina-meta
just preview docproc-extraction-pipeline

# 3. Monitor deployment
./scripts/monitor-preview.sh docproc-extraction-pipeline
```

### Checking Preview Status

```bash
# Quick status check
cd gcloud-admin
docker compose run --rm gcloud-admin kubectl get applications -n argocd | grep preview

# Detailed status
argocd app get preview-pr-421 --server argo.n1-machina.dev --grpc-web

# Check pods
docker compose run --rm gcloud-admin kubectl get pods -n tusdi-preview-421
```

### Triggering Manual Sync

```bash
# If ArgoCD hasn't picked up changes
argocd app sync preview-pr-421 --server argo.n1-machina.dev --grpc-web

# With prune (remove deleted resources)
argocd app sync preview-pr-421 --prune --server argo.n1-machina.dev --grpc-web
```

### Deleting a Preview Environment

```bash
# 1. Delete preview branch in dem2-infra
cd repos/dem2-infra
git push origin --delete preview/docproc-extraction-pipeline

# 2. ArgoCD will automatically clean up the application
# Or manually delete
argocd app delete preview-pr-421 --server argo.n1-machina.dev --grpc-web
```

## Troubleshooting

### Preview Application Not Created

**Symptoms**: Preview branch exists but ArgoCD application not showing up.

**Checks**:
1. Verify preview branch exists in dem2-infra: `git branch -r | grep preview`
2. Check dem2-infra PR has 'preview' label
3. Wait 30 seconds for ApplicationSet to poll
4. Check ApplicationSet logs:
   ```bash
   docker compose run --rm gcloud-admin kubectl logs -n argocd \
     -l app.kubernetes.io/name=argocd-applicationset-controller --tail=100
   ```

### Application Stuck in Progressing

**Symptoms**: Application shows "Progressing" for extended time.

**Checks**:
1. Check pod status: `kubectl get pods -n <namespace>`
2. Check pod events: `kubectl describe pod <pod-name> -n <namespace>`
3. Check image pull status: Look for `ImagePullBackOff` or `ErrImagePull`
4. Verify image exists in registry:
   ```bash
   gcloud artifacts docker images list us-central1-docker.pkg.dev/n1-machina1/tusdi/tusdi-api \
     --filter="tags:preview-*"
   ```

### Application Showing as Degraded

**Symptoms**: Health status is "Degraded".

**Checks**:
1. Check failing resources: `argocd app get <app-name> --server argo.n1-machina.dev --grpc-web`
2. Check pod logs: `kubectl logs <pod-name> -n <namespace> --tail=100`
3. Check events: `kubectl get events -n <namespace> --sort-by='.lastTimestamp'`
4. Common causes:
   - Startup probes failing
   - Database connection issues
   - Missing secrets/config
   - Resource limits exceeded

### Image Not Found

**Symptoms**: Pod shows `ImagePullBackOff` or `ErrImagePull`.

**Checks**:
1. Verify workflow ran successfully: `gh run list --branch <branch> --limit 5`
2. Check if image was pushed:
   ```bash
   gcloud artifacts docker images list us-central1-docker.pkg.dev/n1-machina1/tusdi/tusdi-api \
     --filter="tags:<preview-tag>"
   ```
3. Verify tag in dem2-infra preview branch matches built image
4. Check GitHub Actions build logs for push errors

### ArgoCD Sync Fails

**Symptoms**: Application shows "OutOfSync" and sync operation fails.

**Checks**:
1. View sync error: `argocd app get <app-name> --server argo.n1-machina.dev --grpc-web`
2. Check Kustomize/Helm rendering: Local test with `kustomize build` or `helm template`
3. Verify YAML syntax in dem2-infra
4. Check resource quotas: `kubectl describe resourcequota -n <namespace>`

### Cannot Access Preview URL

**Symptoms**: Preview URL returns 404 or connection error.

**Checks**:
1. Verify application is Healthy: `argocd app get <app-name>`
2. Check ingress: `kubectl get ingress -n <namespace>`
3. Verify DNS: `nslookup <preview-id>.preview.n1-machina.dev`
4. Check service: `kubectl get svc -n <namespace>`
5. Test with port-forward: `kubectl port-forward -n <namespace> svc/tusdi-webui 3000:80`

## Related Documentation

- [../CLAUDE.md](../CLAUDE.md) - Workspace overview and git policies
- [../gcloud-admin/CLAUDE.md](../gcloud-admin/CLAUDE.md) - GKE cluster access and operations
- [../README.md](../README.md) - Getting started with machina-meta workspace
- [../repos/dem2-infra/](../repos/dem2-infra/) - Infrastructure repository

## Quick Reference

### Essential Commands

```bash
# Preview Management
just preview <name>                           # Create/update preview
./scripts/monitor-preview.sh <name>          # Monitor preview deployment

# ArgoCD
argocd app list                              # List all applications
argocd app get <app-name>                    # Get application details
argocd app sync <app-name>                   # Sync application
argocd app wait <app-name> --health          # Wait for healthy state

# Kubernetes (via gcloud-admin)
kubectl get applications -n argocd           # List ArgoCD apps
kubectl get pods -n <namespace>              # List pods
kubectl logs <pod-name> -n <namespace>       # View logs
kubectl describe pod <pod-name> -n <ns>      # Describe pod

# GitHub Actions
gh run list --limit 10                       # List recent runs
gh run watch <run-id>                        # Watch workflow
gh workflow list                             # List workflows
```

### Environment URLs

| Environment | URL |
|-------------|-----|
| Development | https://dev.n1-machina.dev |
| Staging | https://staging.n1-machina.dev |
| Preview | https://\<preview-id\>.preview.n1-machina.dev |
| ArgoCD | https://argo.n1-machina.dev |

---

**For questions or issues with DevOps workflows, consult this document or ask in #engineering.**
