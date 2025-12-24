# CLAUDE.md

This file provides guidance to Claude Code when working with the **machina-meta** workspace.

## ⚠️ CRITICAL: Git Push Policy

**NEVER push to git repositories unless explicitly requested or confirmed by the user.**

- Always commit changes locally
- **DO NOT** run `git push` automatically
- **DO NOT** push as part of workflows or multi-step operations
- Ask the user first: "Should I push these changes to the remote repository?"
- Only push if the user explicitly says "yes", "push", "push it", or gives clear confirmation

This applies to:
- machina-meta repository
- All submodule repositories (dem2, dem2-webui, dem2-infra, medical-catalog)

## Workspace Overview

**machina-meta** is the unified workspace for the MachinaMed (dem2) platform. It coordinates multiple git repositories using git submodules, providing integrated development and deployment workflows.

### Managed Repositories

| Repository | Description | Tech Stack |
|------------|-------------|------------|
| **dem2** | MachinaMed backend - medical AI platform | Python 3.13, FastAPI, uv, Neo4j, PostgreSQL |
| **dem2-webui** | MachinaMed frontend | Next.js 15, React 19, TypeScript, pnpm |
| **dem2-infra** | Infrastructure management | Kubernetes, ArgoCD, Helm |
| **medical-catalog** | Biomarker/medical catalog service | Python, FastAPI, Qdrant |

## Repository Structure

```
machina-meta/
├── repos/                    # Git submodules
│   ├── dem2/                # Backend API (port 8000)
│   ├── dem2-webui/          # Frontend (port 3000)
│   ├── dem2-infra/          # Infrastructure configs
│   └── medical-catalog/     # Catalog service
├── scripts/                 # Workspace automation
│   ├── bootstrap.sh
│   ├── status-all.sh
│   └── sync-all.sh
├── justfile                 # Unified operations
├── README.md                # User documentation
└── CLAUDE.md                # AI assistant guidance (this file)
```

## Quick Start

```bash
# Clone with submodules
git clone --recursive https://github.com/NumberOne-AI/machina-meta.git
cd machina-meta

# Bootstrap (first time)
just bootstrap

# Check status
just status
just branches
just dev-status

# Start development (choose one mode):

# Option 1: Production mode (full stack in containers)
just dev-up

# Option 2: Hot-reload mode (databases only, run apps manually)
just dev-up-hot
# Then in separate terminals:
cd repos/dem2 && just run
cd repos/dem2-webui && pnpm dev
```

## Working with the Workspace

### When to Use Workspace Commands

**Use workspace-level commands** (from machina-meta root) for:
- Multi-repo feature development
- Checking status across all services
- Coordinated releases and tagging
- Managing preview environments
- Cross-repo branch operations

**Use individual repo commands** (cd into repos/*) for:
- Service-specific development
- Running unit tests
- Service-specific debugging
- Committing changes

### Common Development Patterns

#### Multi-Repo Feature Development

```bash
# From machina-meta root
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

# Check status across all
cd ../..
just repo-status
just repo-branches
```

#### Checking Workspace State

```bash
just repo-status    # Git status across all repos
just repo-diff      # Show diffs across all repos
just repo-branches  # Show current branches
just repo-log 5     # Show last 5 commits from each repo
just dev-status     # Check all dev servers (API, frontend, databases)
```

#### Syncing Repositories

```bash
just repo-sync      # Update all submodules to latest
just repo-pull      # Pull latest in each repo
```

#### Development Stack

```bash
just dev-status   # Check what's running
just dev-up       # Start full stack (production mode - containers)
just dev-up-hot   # Start databases only (hot-reload mode)
just dev-down     # Stop all services
```

**Two Development Modes:**
- **Production Mode** (`just dev-up`): Full stack in Docker containers (frontend + backend + databases)
- **Hot-Reload Mode** (`just dev-up-hot`): Databases only, run apps with `just run` and `pnpm dev` for instant code changes

## Development Setup by Service

### dem2 (Backend)

```bash
cd repos/dem2

# Install dependencies
uv sync

# Start databases
just dev-env-up -d

# Run migrations
uv run alembic upgrade head
just graph-upgrade-head

# Load fixtures
just load-all-fixtures

# Start server
just run  # http://localhost:8000
```

**Key commands:**
- `just check` - Format + lint + typecheck
- `just test` - Run unit tests
- `uv run mypy` - Type checking
- `just graph-generate` - Regenerate graph models from schema.yml

### dem2-webui (Frontend)

```bash
cd repos/dem2-webui

# Install dependencies
pnpm install

# Generate API types (backend must be running)
pnpm generate

# Start dev server
pnpm dev  # http://localhost:3000

# Lint and format
pnpm check
```

### medical-catalog (Catalog Service)

```bash
cd repos/medical-catalog

# Install dependencies
uv sync

# Start service
just run
```

### dem2-infra (Infrastructure)

```bash
cd repos/dem2-infra

# Preview environments
git checkout -b preview/my-test
# Push to trigger deployment

# Check current deployments
kubectl get deployments -n tusdi-dev
```

## Architecture Overview

### Service Integration

```
┌─────────────────┐
│   dem2-webui    │  Port 3000 (Next.js)
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│      dem2       │  Port 8000 (FastAPI)
│   (Backend)     │
└────────┬────────┘
         │
         ├──► PostgreSQL (5432)  - User data, sessions
         ├──► Neo4j (7474,7687)  - Graph data
         ├──► Redis (6379)       - Pub/sub, cache
         ├──► Qdrant (6333)      - Vector embeddings
         └──► medical-catalog    - Biomarker data
```

### Frontend-Backend Integration

**API Contract:**
- OpenAPI spec: `http://localhost:8000/api/v1/openapi.json`
- Type generation: `cd repos/dem2-webui && pnpm generate`
- Manual types: `repos/dem2-webui/src/types/`

**Authentication:**
- Dual JWT token system (access + refresh)
- HTTP-only cookies
- Auto-refresh on 401
- Session polling every 60s

**Real-Time (WebSocket):**
- Endpoint: `ws://localhost:8000/api/v1/medical-data-engine/events`
- Redis pub/sub backend
- Auto-reconnection with exponential backoff

**Patient Context Headers:**
- `X-Patient-Context-ID` - Current patient
- `X-Patient-Latitude` / `X-Patient-Longitude` - Location
- `X-Client-Timezone` - Datetime handling

## Git Submodules

Each directory in `repos/` is an independent git repository tracked as a submodule.

### Submodule Workflow

```bash
# Make changes in a submodule
cd repos/dem2
git checkout dev
git pull
# ... make changes ...
git commit -am "changes"
git push

# Update parent workspace to track new commit
cd ../..
git add repos/dem2
git commit -m "Update dem2 to latest dev"
git push
```

### Submodule Tips

- Changes are tracked in the submodule's own repository
- The workspace tracks which commit each submodule points to
- Use `just sync-all` to update all submodules to latest
- Each submodule can be on different branches

## Preview Environments

Create preview environments for testing:

```bash
# From machina-meta root
just preview my-feature

# This will:
# 1. Tag dem2 and dem2-webui with preview-my-feature
# 2. Create/checkout preview/my-feature branch in dem2-infra
# 3. Push changes trigger ArgoCD deployment
```

## Development Services

The development stack is organized into 5 categories:

### Frontend
| Service | Port | Type | Health Check |
|---------|------|------|--------------|
| Frontend | 3000 | Next.js | http://localhost:3000 |

### Backend
| Service | Port | Type | Health Check |
|---------|------|------|--------------|
| Backend API | 8000 | FastAPI | http://localhost:8000/docs |

### Database
| Service | Port | Type | Health Check |
|---------|------|------|--------------|
| PostgreSQL | 5432 | Relational | `psql -h localhost -U postgres` |
| Neo4j | 7474, 7687 | Graph | http://localhost:7474 |

### Infrastructure
| Service | Port | Type | Health Check |
|---------|------|------|--------------|
| Redis | 6379 | Cache/Pub-Sub | `redis-cli ping` |
| Qdrant | 6333 | Vector Search | http://localhost:6333 |

### Dev Tools
| Service | Port | Type | Health Check |
|---------|------|------|--------------|
| RedisInsight | 5540 | Redis UI | http://localhost:5540 |

## Integration with External Tools

### gcloud-admin (DevOps Container)

The gcloud-admin container (located outside this workspace) can mount machina-meta:

```bash
# From gcloud-admin directory
just workspace-status    # Status from inside container
just workspace-branches  # Branches from inside container
just workspace-log       # Logs from inside container
```

The container mounts machina-meta at `/workspace/` for unified DevOps operations.

## Common Patterns

### Python Projects (dem2, medical-catalog)

- Package manager: `uv`
- Task runner: `just` (justfile)
- Linting: `ruff`
- Type checking: `mypy`
- Config: `dynaconf` with `config.toml`
- Testing: `pytest`

### TypeScript/JavaScript (dem2-webui)

- Package manager: `pnpm`
- Linting/formatting: `biome`
- Framework: Next.js 15 with App Router
- State: React Context + hooks
- API client: Wretch

### Infrastructure (dem2-infra)

- Orchestration: Kubernetes (GKE)
- CI/CD: GitHub Actions + ArgoCD
- Registry: Google Artifact Registry
- Manifests: Kustomize

## Environment Configuration

- **Secrets**: `.env` files (never commit)
- **Config**: `config.toml` files (can commit)
- **Template**: `.env.example` in each repo

Copy `.env.example` to `.env` and fill in values for each service.

## Git Workflow

- **Main branches**: `dev` (active development), `main` (production)
- **Feature branches**: `feature/description` or `TICKET-123-description`
- **Commits**: Conventional commits (`feat:`, `fix:`, `chore:`, etc.)
- **Preview envs**: `git tag -f preview-{id} && git push origin preview-{id} --force`

## Project-Specific Documentation

Refer to individual CLAUDE.md files for detailed service guidance:

- [repos/dem2/CLAUDE.md](repos/dem2/CLAUDE.md) - Backend development, architecture, testing
- [repos/dem2-webui/CLAUDE.md](repos/dem2-webui/CLAUDE.md) - Frontend patterns, components, API integration
- [repos/medical-catalog/CLAUDE.md](repos/medical-catalog/CLAUDE.md) - Catalog service specifics
- [repos/dem2-infra/](repos/dem2-infra/) - Infrastructure deployment, ArgoCD

## Workspace Principles

1. **Submodules maintain independence** - Each repo has its own git history
2. **Workspace provides coordination** - Unified commands for cross-repo operations
3. **Service isolation** - Services can be developed and tested independently
4. **Integrated deployment** - Preview environments coordinate across services

## Quick Reference

### Workspace Commands

| Command | Purpose |
|---------|---------|
| `just bootstrap` | Initial setup |
| `just repo-status` | Git status all repos |
| `just repo-diff` | Show diffs all repos |
| `just repo-branches` | Show current branches |
| `just repo-checkout <branch>` | Checkout across all repos |
| `just checkout-repo <repo> <branch>` | Checkout in specific repo |
| `just dev-status` | Check all services |
| `just dev-up` | Start full stack (production mode) |
| `just dev-up-hot` | Start databases only (hot-reload mode) |
| `just dev-down` | Stop all services |
| `just repo-check` | Lint/type check all |
| `just repo-test` | Test all repos |
| `just repo-log <n>` | Show commits |
| `just preview <name>` | Create preview env |

### Service Commands

| Action | dem2 | dem2-webui |
|--------|------|------------|
| Install | `uv sync` | `pnpm install` |
| Run | `just run` | `pnpm dev` |
| Check | `just check` | `pnpm check` |
| Test | `just test` | `pnpm test` |

## Troubleshooting

**Submodules out of sync:**
```bash
git submodule update --init --recursive
just repo-sync
```

**Databases not starting:**
```bash
cd repos/dem2
just dev-env-down
just dev-env-up -d
```

**Frontend types out of date:**
```bash
cd repos/dem2-webui
pnpm generate  # Backend must be running
```

**Port conflicts:**
```bash
just dev-status  # Check what's running
# Kill conflicting processes or change ports in configs
```

For more help, see [README.md](README.md) or individual repo documentation.
