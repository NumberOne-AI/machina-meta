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
just dev-up           # Start full stack in Docker containers
just dev-down         # Stop all services
```

The `dev-up` command starts:
- **Frontend** (Next.js) on port 3000
- **Backend** (FastAPI) on port 8000
- **Medical Catalog** (FastAPI) on port 8001
- **Databases**: PostgreSQL (5432), Neo4j (7474/7687), Redis (6379), Qdrant (6333)
- **Dev Tools**: RedisInsight (5540)
- Migrations are applied automatically on backend startup
- Total startup time: ~90 seconds

### Cross-Repo Operations
```bash
just repo-status               # Git status across all repos
just repo-branches             # Show current branch in each repo
just repo-checkout <branch>    # Checkout branch across all repos (creates if needed)
just checkout-repo <repo> <branch>  # Checkout in specific repo
just repo-pull                 # Pull latest for all repos
just repo-sync                 # Update all submodules to latest
just repo-diff                 # Show diffs across all repos
just repo-log [n]              # Show last n commits (default: 10)
just repo-check                # Run linting/type checks
just repo-test                 # Run tests across repos
just repo-tag <version>        # Tag all repos with version
```

## Development Workflow

### Working on a Feature

```bash
# Create feature branch in relevant repos
just repo-checkout feature/my-feature

# Work in individual repos
cd repos/dem2
# ... make changes ...
git commit -m "feat: backend changes"
git push origin feature/my-feature

cd ../dem2-webui
# ... make changes ...
git commit -m "feat: frontend changes"
git push origin feature/my-feature

# Check status across all repos
cd ../..
just repo-status
just repo-branches
```

### Creating Preview Environment

```bash
just preview my-test
# Creates preview tags and branches

# Monitor deployment
./scripts/monitor-preview.sh my-test
```

### Service-Specific Development

**dem2 (Backend)**
```bash
cd repos/dem2
just run              # Start dev server (http://localhost:8000)
just check            # Lint + format + typecheck
just test             # Run tests
just graph-generate   # Regenerate graph models
```

**dem2-webui (Frontend)**
```bash
cd repos/dem2-webui
pnpm dev              # Start dev server (http://localhost:3000)
pnpm check            # Lint + format + typecheck
pnpm test             # Run tests
pnpm generate         # Generate API types from OpenAPI (backend must be running)
```

**medical-catalog (Catalog Service)**
```bash
cd repos/medical-catalog
just run              # Start service (http://localhost:8001)
just check            # Lint + format + typecheck
```

## Updating Submodules

```bash
# Update all to latest
just repo-sync

# Update specific submodule
cd repos/dem2
git pull origin dev
cd ../..
git add repos/dem2
git commit -m "Update dem2 to latest"
```

## Troubleshooting

### Submodules out of sync
```bash
git submodule update --init --recursive
just repo-sync
```

### Database connection issues
```bash
cd repos/dem2
just dev-env-down
just dev-env-up -d
# Wait 10 seconds, then:
uv run alembic upgrade head
```

### Port conflicts
```bash
just dev-status    # Check what's running
just dev-down      # Stop everything
# Kill any lingering processes on ports 3000, 8000, 5432, etc.
```

### Frontend types out of date
```bash
cd repos/dem2-webui
pnpm generate  # Backend must be running
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
