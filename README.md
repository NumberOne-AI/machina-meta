# machina-meta

Unified workspace for the MachinaMed (dem2) platform.

## Quick Start

```bash
# Clone with submodules
git clone --recursive git@github.com:NumberOne-AI/machina-meta.git

# Or if already cloned without --recursive
git submodule update --init --recursive

# Bootstrap workspace
just bootstrap

# Setup development environment
just dev-setup

# Start development stack
just dev-up
```

## Repository Structure

- `repos/dem2/` - Backend API (Python, FastAPI)
- `repos/dem2-webui/` - Frontend (Next.js, React)
- `repos/dem2-infra/` - Infrastructure (Kubernetes, ArgoCD)
- `repos/medical-catalog/` - Medical catalog service

**Note**: gcloud-admin is not yet included as a submodule. It's located in the original NumberOne-AI directory.

## Common Commands

### Development Stack
```bash
just dev-status       # Check status of all dev servers
just dev-up           # Start development stack
just dev-down         # Stop all services
```

### Cross-Repo Operations
```bash
just status           # Git status across all repos
just branches         # Show current branch in each repo
just checkout <name>  # Checkout branch across all repos
just pull-all         # Pull latest for all repos
just check-all        # Run linting/type checks
just test-all         # Run tests across repos
```

## Development Workflow

### Working on a Feature

```bash
# Create feature branch in relevant repos
just checkout feature/my-feature

# Work in individual repos
cd repos/dem2
# ... make changes ...
git commit -m "feat: backend changes"

cd ../dem2-webui
# ... make changes ...
git commit -m "feat: frontend changes"

# Push branches
cd ../dem2
git push origin feature/my-feature
cd ../dem2-webui
git push origin feature/my-feature
```

### Creating Preview Environment

```bash
just preview my-test
# Creates preview tags and branches
```

## Updating Submodules

```bash
# Update all to latest
just sync-all

# Update specific submodule
cd repos/dem2
git pull origin dev
cd ../..
git add repos/dem2
git commit -m "Update dem2 to latest"
```

## Documentation

### Workspace Documentation
- [docs/LLM.md](docs/LLM.md) - LLM integration and prompt engineering reference
- [docs/AGENTS.md](docs/AGENTS.md) - Google ADK agent architecture
- [docs/DATAFLOW.md](docs/DATAFLOW.md) - System data flow architecture

### Individual Repository Documentation
- [dem2/CLAUDE.md](repos/dem2/CLAUDE.md) - Backend development guide
- [dem2-webui/CLAUDE.md](repos/dem2-webui/CLAUDE.md) - Frontend development guide
- [dem2-infra/README.md](repos/dem2-infra/README.md) - Infrastructure documentation
- [medical-catalog/CLAUDE.md](repos/medical-catalog/CLAUDE.md) - Catalog service guide

## Architecture

The workspace follows a multi-repo pattern with git submodules:

```
Frontend (Next.js) ──────► Backend (FastAPI) ──────► Medical Catalog
     │                           │
     │                           ├──► PostgreSQL
     │                           ├──► Neo4j
     │                           └──► Redis
     │
     └──────────────────────────────► Infrastructure (K8s)
```

All services are deployed to GKE via ArgoCD, with configurations managed in `dem2-infra`.

## Getting Help

- Check individual repo CLAUDE.md files for service-specific guidance
- See `/help` in Claude Code for tool assistance
- Report issues: https://github.com/anthropics/claude-code/issues
