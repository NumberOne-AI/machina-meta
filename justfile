# machina-meta unified operations

set dotenv-load := true

# Import gcloud-admin justfile as a module
mod gcloud-admin 'gcloud-admin/justfile'

# Import dem2 justfile as a module
mod dem2 'repos/dem2/justfile'

# Show available commands
default:
    @just --list

# Show detailed help for all commands
help:
    @cat HELP.md

# Bootstrap: clone and setup all repos
bootstrap:
    git submodule update --init --recursive
    @echo "Bootstrapping complete!"
    @echo "Next steps:"
    @echo "  1. Copy .env.example to .env in each service"
    @echo "  2. Run: just dev-setup"

# Initial development setup
dev-setup:
    @echo "Setting up dem2..."
    cd repos/dem2 && uv sync
    @echo "Setting up dem2-webui..."
    cd repos/dem2-webui && pnpm install
    @echo "Setting up medical-catalog..."
    cd repos/medical-catalog && uv sync
    @echo "Setup complete!"

# Sync all repos to latest
repo-sync:
    git submodule update --remote --merge

# Pull latest for all repos
repo-pull:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo "=== Pulling $dir ==="
        git -C "$dir" pull
    done

# Push all repos (submodules first, then parent)
repo-push:
    @./scripts/push-all.sh

# Show status across all repos
repo-status:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo ""
        echo "=== $(basename "$dir") ==="
        git -C "$dir" status -sb
    done

# Show git diff across all repos
repo-diff:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo ""
        echo "=== $(basename "$dir") ==="
        if git -C "$dir" diff --quiet; then
            echo "No changes"
        else
            git -C "$dir" diff --stat
            echo ""
            git -C "$dir" diff
        fi
    done

# Show current branches
repo-branches:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        printf "%-20s %s\n" "$(basename "$dir"):" "$(git -C "$dir" branch --show-current)"
    done

# Checkout branch across all repos (creates if doesn't exist)
repo-checkout branch:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        repo_name=$(basename "$dir")
        echo ""
        echo "=== $repo_name ==="

        # Check if branch exists locally
        if git -C "$dir" rev-parse --verify {{branch}} >/dev/null 2>&1; then
            echo "Checking out existing branch {{branch}}..."
            git -C "$dir" checkout {{branch}}
            echo "✅ Checked out {{branch}}"
        else
            echo "Branch {{branch}} doesn't exist locally, creating..."
            git -C "$dir" checkout -b {{branch}}
            echo "✅ Created new branch {{branch}}"
        fi
    done
    echo ""
    echo "All repos now on branch: {{branch}}"

# Checkout branch in a specific repo (e.g., just checkout-repo dem2 feature/my-branch)
checkout-repo repo branch:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ ! -d "repos/{{repo}}" ]; then
        echo "❌ ERROR: Repository 'repos/{{repo}}' not found"
        echo ""
        echo "Available repositories:"
        ls -1 repos/
        exit 1
    fi

    echo "Fetching latest changes for {{repo}}..."
    git -C "repos/{{repo}}" fetch

    echo "Checking out {{branch}} in {{repo}}..."
    if git -C "repos/{{repo}}" checkout {{branch}}; then
        echo "✅ Checked out existing branch {{branch}}"
        echo ""
        echo "Pulling latest changes..."
        git -C "repos/{{repo}}" pull || echo "⚠️  No remote tracking branch"
    else
        echo "Branch doesn't exist, creating new branch {{branch}}..."
        git -C "repos/{{repo}}" checkout -b {{branch}}
        echo "✅ Created new branch {{branch}}"
    fi

    echo ""
    echo "Current branch in {{repo}}: $(git -C repos/{{repo}} branch --show-current)"

# Start full stack in production mode (databases + frontend + backend containers)
dev-up:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Starting full stack in production mode..."
    echo "Building and starting all services (migrations run automatically)..."
    echo ""

    if ! docker compose --profile prod up -d --build; then
        echo ""
        echo "❌ ERROR: Failed to start services"
        echo ""
        echo "Showing service status:"
        docker compose ps
        echo ""
        echo "Showing recent logs:"
        docker compose logs --tail=50
        exit 1
    fi

    echo ""
    echo "Waiting for services to initialize..."
    sleep 5

    echo ""
    echo "Checking service status..."
    docker compose ps

    # Check for any services that failed
    if docker compose ps | grep -E "(Exit|unhealthy)" > /dev/null; then
        echo ""
        echo "⚠️  WARNING: Some services are not healthy"
        echo ""
        echo "Showing logs for failed services:"
        docker compose logs --tail=100
        echo ""
        echo "Run 'docker compose logs <service-name>' to see full logs"
    else
        echo ""
        echo "✅ All services started successfully!"
    fi

    echo ""
    echo "Services:"
    echo "  - Frontend:  http://localhost:3000"
    echo "  - Backend:   http://localhost:8000"
    echo "  - Neo4j:     http://localhost:7474"
    echo "  - Qdrant:    http://localhost:6333"
    echo ""
    echo "Run 'just dev-status' to check when all services are ready"

# Start databases only for hot-reload development
dev-up-hot:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Starting databases for hot-reload development..."
    echo ""

    if ! docker compose up -d postgres neo4j redis qdrant redisinsight; then
        echo ""
        echo "❌ ERROR: Failed to start database services"
        echo ""
        echo "Showing service status:"
        docker compose ps
        echo ""
        echo "Showing recent logs:"
        docker compose logs --tail=50
        exit 1
    fi

    echo "Waiting for databases to be ready..."
    sleep 10

    echo ""
    echo "Checking database status..."
    docker compose ps postgres neo4j redis qdrant redisinsight

    # Check for any databases that failed
    if docker compose ps postgres neo4j redis qdrant redisinsight | grep -E "(Exit|unhealthy)" > /dev/null; then
        echo ""
        echo "⚠️  WARNING: Some databases are not healthy"
        echo ""
        echo "Showing logs:"
        docker compose logs --tail=100 postgres neo4j redis qdrant redisinsight
        echo ""
        echo "Continuing with migrations anyway (may fail)..."
    fi

    echo ""
    echo "Applying migrations..."

    if ! (cd repos/dem2 && uv run alembic upgrade head); then
        echo ""
        echo "❌ ERROR: PostgreSQL migrations failed"
        echo ""
        echo "Possible causes:"
        echo "  - Database not ready (wait and try: cd repos/dem2 && uv run alembic upgrade head)"
        echo "  - Configuration issue in .env file"
        echo "  - Database connection error"
        echo ""
        echo "Check logs: docker compose logs postgres"
        exit 1
    fi

    if ! (cd repos/dem2 && just graph-upgrade-head); then
        echo ""
        echo "❌ ERROR: Neo4j graph migrations failed"
        echo ""
        echo "Possible causes:"
        echo "  - Neo4j not ready (wait and try: cd repos/dem2 && just graph-upgrade-head)"
        echo "  - Configuration issue"
        echo ""
        echo "Check logs: docker compose logs neo4j"
        exit 1
    fi

    echo ""
    echo "✅ Databases ready! Start application services:"
    echo "  Terminal 1: cd repos/dem2 && just run"
    echo "  Terminal 2: cd repos/dem2-webui && pnpm dev"
    echo ""
    echo "Run 'just dev-status' to check all services"

# Stop all development services
dev-down:
    @echo "Stopping all services..."
    docker compose --profile prod down
    @echo "Stopping any legacy services..."
    docker compose -p machina-med down 2>/dev/null || true

# Show status of all local dev servers and services
dev-status:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "# Development Stack Status"
    echo ""
    echo "| Category | Service | Type | Port(s) | Status | URL |"
    echo "|----------|---------|------|---------|--------|-----|"

    # Check Frontend
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -qE "^[23][0-9][0-9]$"; then
        echo "| Frontend | Frontend | Next.js | 3000 | ✅ Running | http://localhost:3000 |"
    else
        echo "| Frontend | Frontend | Next.js | 3000 | ❌ Stopped | - |"
    fi

    # Check Backend API
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null | grep -q "200"; then
        echo "| Backend | Backend API | FastAPI | 8000 | ✅ Running | http://localhost:8000 |"
    else
        echo "| Backend | Backend API | FastAPI | 8000 | ❌ Stopped | - |"
    fi

    # Check Medical Catalog
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null | grep -q "200"; then
        echo "| Backend | Medical Catalog | FastAPI | 8001 | ✅ Running | http://localhost:8001 |"
    else
        echo "| Backend | Medical Catalog | FastAPI | 8001 | ❌ Stopped | - |"
    fi

    # PostgreSQL
    if docker ps --format '{{{{.Names}}}}' | grep -q "postgres"; then
        echo "| Database | PostgreSQL | Relational | 5432 | ✅ Running | localhost:5432 |"
    else
        echo "| Database | PostgreSQL | Relational | 5432 | ❌ Stopped | - |"
    fi

    # Neo4j
    if docker ps --format '{{{{.Names}}}}' | grep -q "neo4j"; then
        echo "| Database | Neo4j | Graph | 7474, 7687 | ✅ Running | http://localhost:7474 |"
    else
        echo "| Database | Neo4j | Graph | 7474, 7687 | ❌ Stopped | - |"
    fi

    # Redis
    if docker ps --format '{{{{.Names}}}}' | grep -q "redis"; then
        echo "| Infrastructure | Redis | Cache/Pub-Sub | 6379 | ✅ Running | localhost:6379 |"
    else
        echo "| Infrastructure | Redis | Cache/Pub-Sub | 6379 | ❌ Stopped | - |"
    fi

    # Qdrant
    if docker ps --format '{{{{.Names}}}}' | grep -q "qdrant"; then
        echo "| Infrastructure | Qdrant | Vector Search | 6333 | ✅ Running | http://localhost:6333 |"
    else
        echo "| Infrastructure | Qdrant | Vector Search | 6333 | ❌ Stopped | - |"
    fi

    # RedisInsight (optional)
    if docker ps --format '{{{{.Names}}}}' | grep -q "redisinsight"; then
        echo "| Dev Tools | RedisInsight | Redis UI | 5540 | ✅ Running | http://localhost:5540 |"
    else
        echo "| Dev Tools | RedisInsight | Redis UI | 5540 | ⚪ Optional | - |"
    fi

# Run a Cypher query against Neo4j
neo4j-query query *args="":
    python3 scripts/neo4j-query.py "{{query}}" {{args}}

# Run checks across all repos
repo-check:
    @echo "=== dem2 ==="
    cd repos/dem2 && just check
    @echo ""
    @echo "=== dem2-webui ==="
    cd repos/dem2-webui && pnpm check
    @echo ""
    @echo "=== medical-catalog ==="
    cd repos/medical-catalog && just check

# Run tests across all repos
repo-test:
    @echo "=== dem2 ==="
    cd repos/dem2 && just test
    @echo ""
    @echo "=== dem2-webui ==="
    cd repos/dem2-webui && pnpm test

# Tag all repos with version
repo-tag version:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Tagging all repos with {{version}}..."
    for dir in repos/*/; do
        echo "Tagging $(basename "$dir")..."
        git -C "$dir" tag -a {{version}} -m "Release {{version}}"
        git -C "$dir" push origin {{version}}
    done
    echo "All repos tagged with {{version}}"

# Show git log summary for all repos
repo-log lines="10":
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo ""
        echo "=== $(basename "$dir") ==="
        git -C "$dir" log --oneline -n {{lines}}
    done

# Create preview environment (legacy - use preview-create instead)
preview name:
    cd repos/dem2 && git tag -f preview-{{name}} && git push origin preview-{{name}} --force
    cd repos/dem2-webui && git tag -f preview-{{name}} && git push origin preview-{{name}} --force
    cd repos/dem2-infra && git checkout -b preview/{{name}} || git checkout preview/{{name}}
    @echo "Preview environment '{{name}}' created"
    @echo "Push dem2-infra branch to trigger deployment"

# Create preview environment with helper script
preview-create id *args="":
    ./scripts/create-preview.sh {{id}} {{args}}

# Monitor preview deployment with ArgoCD CLI
preview-monitor id *args="":
    ./scripts/monitor-preview.sh {{id}} {{args}}

# Track preview deployment status (legacy - use preview-monitor)
preview-status id *args="":
    ./scripts/track-preview.sh {{id}} {{args}}

# Show detailed information about a preview environment
preview-info *args="":
    ./scripts/preview-tool.py info {{args}}

# Delete preview environment (remove tags and close PR to trigger ArgoCD cleanup)
preview-delete *args="":
    ./scripts/preview-tool.py delete {{args}}

# Check GitHub token permissions for preview workflows
check-token *args="":
    ./scripts/check-token-permissions.sh {{args}}

# Find all source code
find-src:
    find -type f | grep -Ev '(\.git|\.venv|\.mypy_cache|\.ruff_cache|\.pytest_cache|\.pyc)\b'
