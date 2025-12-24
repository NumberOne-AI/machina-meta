# CLAUDE.md

This file provides guidance to Claude Code when working with the machina-meta workspace.

## Workspace Overview

**machina-meta** is the unified workspace for the MachinaMed (dem2) platform. It uses git submodules to coordinate multiple related repositories in an integrated manner.

## Repository Structure

```
machina-meta/
├── repos/                    # Git submodules
│   ├── dem2/                # Backend API
│   ├── dem2-webui/          # Frontend
│   ├── dem2-infra/          # Infrastructure
│   └── medical-catalog/     # Catalog service
├── scripts/                 # Workspace automation
├── justfile                 # Unified operations
└── README.md               # Workspace documentation
```

## Working with the Workspace

### When to Use Workspace Commands

Use workspace-level commands (in machina-meta root) when:
- Working on features spanning multiple repos
- Checking status across the platform
- Creating coordinated releases
- Managing preview environments

Use individual repo commands (cd into repos/*) when:
- Working on a single service
- Running service-specific tests
- Service-specific debugging

### Common Patterns

**Multi-repo feature development:**
```bash
# From machina-meta root
just checkout feature/my-feature

# Work in repos
cd repos/dem2 && git commit -m "feat: backend changes"
cd repos/dem2-webui && git commit -m "feat: frontend changes"

# Push from each repo
cd repos/dem2 && git push origin feature/my-feature
cd repos/dem2-webui && git push origin feature/my-feature
```

**Checking workspace state:**
```bash
just status      # See all repo states
just branches    # See current branches
just log         # See recent commits
just dev-status  # Check all dev servers (API, frontend, databases)
```

**Syncing repos:**
```bash
just sync-all    # Update all submodules to latest
just pull-all    # Pull latest in each repo
```

## Git Submodules

Each directory in `repos/` is a git submodule pointing to an independent repository. Changes to submodules:

1. Are tracked in the submodule's own repository
2. Require updating the parent repo to point to new commits
3. Can be worked on independently

### Updating a Submodule

```bash
# Make changes in a submodule
cd repos/dem2
git checkout dev
git pull
git commit -am "changes"
git push

# Update parent to track new commit
cd ../..
git add repos/dem2
git commit -m "Update dem2 to latest"
```

## Integration with gcloud-admin

The gcloud-admin DevOps container has workspace-aware commands:

```bash
cd ../NumberOne-AI/gcloud-admin
just workspace-status    # Status from inside container
just workspace-branches  # Branches from inside container
just workspace-log       # Logs from inside container
```

The container mounts the entire machina-meta workspace at `/workspace/`.

## Project-Specific Documentation

Refer to individual repo CLAUDE.md files for service-specific guidance:

- [dem2/CLAUDE.md](repos/dem2/CLAUDE.md) - Backend development
- [dem2-webui/CLAUDE.md](repos/dem2-webui/CLAUDE.md) - Frontend development
- [dem2-infra/](repos/dem2-infra/) - Infrastructure management
- [medical-catalog/CLAUDE.md](repos/medical-catalog/CLAUDE.md) - Catalog service

## Key Principles

1. **Submodules maintain independence** - Each repo has its own git history and can be worked on independently
2. **Workspace provides coordination** - Top-level justfile and scripts coordinate operations
3. **gcloud-admin as operational hub** - DevOps container provides unified view of workspace
4. **dem2-infra as infrastructure source of truth** - Tracks deployed versions across environments

## Development Workflow

See [README.md](README.md) for:
- Quick start guide
- Common commands
- Development workflows
- Updating submodules
