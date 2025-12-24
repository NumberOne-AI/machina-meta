# machina-meta unified operations

set dotenv-load := true

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
sync-all:
    git submodule update --remote --merge

# Pull latest for all repos
pull-all:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo "=== Pulling $dir ==="
        git -C "$dir" pull
    done

# Show status across all repos
status:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo ""
        echo "=== $(basename "$dir") ==="
        git -C "$dir" status -sb
    done

# Show current branches
branches:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        printf "%-20s %s\n" "$(basename "$dir"):" "$(git -C "$dir" branch --show-current)"
    done

# Checkout branch across all repos (creates if doesn't exist)
checkout branch:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo "Checking out {{branch}} in $(basename "$dir")..."
        git -C "$dir" checkout {{branch}} 2>/dev/null || git -C "$dir" checkout -b {{branch}}
    done

# Start full development stack
dev-up:
    @echo "Starting databases..."
    cd repos/dem2 && just dev-env-up -d
    @echo "Waiting for databases to be ready..."
    sleep 5
    @echo ""
    @echo "Apply migrations..."
    cd repos/dem2 && uv run alembic upgrade head
    cd repos/dem2 && just graph-upgrade-head
    @echo ""
    @echo "Stack ready! Start services:"
    @echo "  Terminal 1: cd repos/dem2 && just run"
    @echo "  Terminal 2: cd repos/dem2-webui && pnpm dev"

# Stop all development services
dev-down:
    cd repos/dem2 && just dev-env-down

# Show status of all local dev servers and services
dev-status:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "# Development Stack Status"
    echo ""
    echo "| Layer | Service | Type | Port(s) | Status | URL |"
    echo "|-------|---------|------|---------|--------|-----|"

    # Check Backend API
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null | grep -q "200"; then
        echo "| Application | Backend API | FastAPI | 8000 | ✅ Running | http://localhost:8000 |"
    else
        echo "| Application | Backend API | FastAPI | 8000 | ❌ Stopped | - |"
    fi

    # Check Frontend
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200"; then
        echo "| Application | Frontend | Next.js | 3000 | ✅ Running | http://localhost:3000 |"
    else
        echo "| Application | Frontend | Next.js | 3000 | ❌ Stopped | - |"
    fi

    # PostgreSQL
    if docker ps --format '{{{{.Names}}}}' | grep -q "postgres"; then
        echo "| Data | PostgreSQL | Database | 5432 | ✅ Running | localhost:5432 |"
    else
        echo "| Data | PostgreSQL | Database | 5432 | ❌ Stopped | - |"
    fi

    # Neo4j
    if docker ps --format '{{{{.Names}}}}' | grep -q "neo4j"; then
        echo "| Data | Neo4j | Graph Database | 7474, 7687 | ✅ Running | http://localhost:7474 |"
    else
        echo "| Data | Neo4j | Graph Database | 7474, 7687 | ❌ Stopped | - |"
    fi

    # Redis
    if docker ps --format '{{{{.Names}}}}' | grep -q "redis"; then
        echo "| Data | Redis | Cache/Pub-Sub | 6379 | ✅ Running | localhost:6379 |"
    else
        echo "| Data | Redis | Cache/Pub-Sub | 6379 | ❌ Stopped | - |"
    fi

    # Qdrant
    if docker ps --format '{{{{.Names}}}}' | grep -q "qdrant"; then
        echo "| Data | Qdrant | Vector DB | 6333 | ✅ Running | http://localhost:6333 |"
    else
        echo "| Data | Qdrant | Vector DB | 6333 | ❌ Stopped | - |"
    fi

    # RedisInsight (optional)
    if docker ps --format '{{{{.Names}}}}' | grep -q "redisinsight"; then
        echo "| Tools | RedisInsight | Dev Tool | 5540 | ✅ Running | http://localhost:5540 |"
    else
        echo "| Tools | RedisInsight | Dev Tool | 5540 | ⚪ Optional | - |"
    fi

# Run checks across all repos
check-all:
    @echo "=== dem2 ==="
    cd repos/dem2 && just check
    @echo ""
    @echo "=== dem2-webui ==="
    cd repos/dem2-webui && pnpm check
    @echo ""
    @echo "=== medical-catalog ==="
    cd repos/medical-catalog && just check

# Run tests across all repos
test-all:
    @echo "=== dem2 ==="
    cd repos/dem2 && just test
    @echo ""
    @echo "=== dem2-webui ==="
    cd repos/dem2-webui && pnpm test

# Tag all repos with version
tag-release version:
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
log lines="10":
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in repos/*/; do
        echo ""
        echo "=== $(basename "$dir") ==="
        git -C "$dir" log --oneline -n {{lines}}
    done

# Create preview environment
preview name:
    cd repos/dem2 && git tag -f preview-{{name}} && git push origin preview-{{name}} --force
    cd repos/dem2-webui && git tag -f preview-{{name}} && git push origin preview-{{name}} --force
    cd repos/dem2-infra && git checkout -b preview/{{name}} || git checkout preview/{{name}}
    @echo "Preview environment '{{name}}' created"
    @echo "Push dem2-infra branch to trigger deployment"
