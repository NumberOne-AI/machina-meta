# machina-meta Workspace Commands

## Getting Started

### Bootstrap workspace (first time setup)
```bash
just bootstrap
```
Initializes git submodules, checks for required tools (uv, pnpm, docker, just).

### Setup development environment
```bash
just dev-setup
```
Installs dependencies for all services (dem2, dem2-webui, medical-catalog).

## Development Stack

### Two Development Modes

#### Production Mode (Default) - Containerized Applications
```bash
just dev-up
```
Starts the **full stack in Docker containers** (production-like environment):
- **Frontend** (Next.js) - containerized on port 3000
- **Backend** (FastAPI) - containerized on port 8000
- **Databases**: PostgreSQL, Neo4j, Redis, Qdrant, RedisInsight
- **Migrations**: Applied automatically on backend startup
- **Startup time**: ~60 seconds total

This mode is ideal for:
- Testing the production build
- Consistent environment across team members
- End-to-end integration testing

#### Hot-Reload Mode - Local Development
```bash
just dev-up-hot
```
Starts **only the databases**, for local hot-reload development:
- **Databases**: PostgreSQL, Neo4j, Redis, Qdrant, RedisInsight
- **Migrations**: Applied automatically
- **Applications**: Run manually with hot-reload

After starting databases, run applications in separate terminals:
```bash
# Terminal 1: Backend API with hot-reload
cd repos/dem2 && just run         # http://localhost:8000

# Terminal 2: Frontend with hot-reload
cd repos/dem2-webui && pnpm dev   # http://localhost:3000
```

This mode is ideal for:
- Active feature development
- Instant code changes without rebuilds
- Debugging with direct console output

### Check status of all services
```bash
just dev-status
```
Shows markdown table with status of all 7 services across 5 categories:
- **Frontend**: Next.js application
- **Backend**: FastAPI application
- **Database**: PostgreSQL (relational), Neo4j (graph)
- **Infrastructure**: Redis (cache/pub-sub), Qdrant (vector search)
- **Dev Tools**: RedisInsight (Redis UI)

### Stop all development services
```bash
just dev-down
```
Stops all Docker containers (works for both modes).

## Git Operations (Cross-Repo)

### Show git status across all repos
```bash
just repo-status
```

### Show git diff across all repos
```bash
just repo-diff
```
Shows unstaged changes in all repositories with diff stats and full diffs.

### Show current branches in all repos
```bash
just repo-branches
```

### Checkout branch across all repos
```bash
just repo-checkout <branch-name>
```
Creates branch if it doesn't exist. Example: `just repo-checkout feature/my-feature`

### Checkout branch in a specific repo
```bash
just checkout-repo <repo-name> <branch-name>
```
Fetches latest, checks out branch (creates if needed), and pulls.

Examples:
- `just checkout-repo dem2 feature/docproc-extraction-pipeline`
- `just checkout-repo dem2-webui dev`
- `just checkout-repo medical-catalog main`

### Pull latest in all repos
```bash
just repo-pull
```

### Show recent commits
```bash
just repo-log           # Default: 10 commits per repo
just repo-log 5         # Show 5 commits per repo
```

### Sync all submodules to latest
```bash
just repo-sync
```
Updates all submodules to their remote tracking branches.

## Code Quality

### Run linting and type checks across all repos
```bash
just repo-check
```
Runs:
- dem2: `just check` (ruff format, ruff check, mypy)
- dem2-webui: `pnpm check` (biome)
- medical-catalog: `just check`

### Run tests across all repos
```bash
just repo-test
```
Runs unit tests in dem2 and dem2-webui.

## Release Management

### Tag all repos with a version
```bash
just repo-tag v2.5.0
```
Tags and pushes to all repos simultaneously.

### Create preview environment
```bash
just preview my-test
```
Creates preview tags (dem2, dem2-webui) and branch (dem2-infra).

## Service-Specific Commands

### dem2 (Backend)
```bash
cd repos/dem2
just run              # Start dev server
just check            # Lint + format + typecheck
just test             # Run tests
just graph-generate   # Regenerate graph models
```

### dem2-webui (Frontend)
```bash
cd repos/dem2-webui
pnpm dev              # Start dev server
pnpm check            # Lint + format + typecheck
pnpm test             # Run tests
pnpm generate         # Generate API types from OpenAPI
```

### medical-catalog (Catalog Service)
```bash
cd repos/medical-catalog
just run              # Start service
just check            # Lint + format + typecheck
```

## Common Workflows

### Working on a feature spanning multiple repos
```bash
# 1. Checkout feature branch everywhere
just repo-checkout feature/new-chat

# 2. Work in individual repos
cd repos/dem2
# ... make changes ...
git commit -m "feat: backend changes"
git push origin feature/new-chat

cd ../dem2-webui
# ... make changes ...
git commit -m "feat: frontend changes"
git push origin feature/new-chat

# 3. Check status
cd ../..
just repo-status
just repo-branches
```

### Daily development routine
```bash
# Morning: sync everything
just repo-pull
just dev-status

# Start databases if needed
just dev-up

# Start services in separate terminals
cd repos/dem2 && just run
cd repos/dem2-webui && pnpm dev

# Before committing
just repo-check
just repo-test

# End of day: stop services
just dev-down
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

## More Information

- Full documentation: `cat README.md`
- Architecture guide: `cat CLAUDE.md`
- Service docs: `cat repos/{service}/CLAUDE.md`
- Command list: `just --list`
