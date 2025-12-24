# machina-meta unified operations

set dotenv-load := true

# Show available commands
default:
    @just --list

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
    echo "=== Development Stack Status ==="
    echo ""

    # Check Backend API
    echo "Backend API (port 8000):"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null | grep -q "200"; then
        echo "  ✓ Running - http://localhost:8000"
    else
        echo "  ✗ Not responding"
    fi
    echo ""

    # Check Frontend
    echo "Frontend (port 3000):"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200"; then
        echo "  ✓ Running - http://localhost:3000"
    else
        echo "  ✗ Not responding"
    fi
    echo ""

    # Check Database Containers
    echo "Database Services:"

    # PostgreSQL
    if docker ps --format '{{{{.Names}}}}' | grep -q "postgres"; then
        echo "  ✓ PostgreSQL - Running (port 5432)"
    else
        echo "  ✗ PostgreSQL - Not running"
    fi

    # Neo4j
    if docker ps --format '{{{{.Names}}}}' | grep -q "neo4j"; then
        echo "  ✓ Neo4j - Running (ports 7474, 7687)"
    else
        echo "  ✗ Neo4j - Not running"
    fi

    # Redis
    if docker ps --format '{{{{.Names}}}}' | grep -q "redis"; then
        echo "  ✓ Redis - Running (port 6379)"
    else
        echo "  ✗ Redis - Not running"
    fi

    # Qdrant
    if docker ps --format '{{{{.Names}}}}' | grep -q "qdrant"; then
        echo "  ✓ Qdrant - Running (port 6333)"
    else
        echo "  ✗ Qdrant - Not running"
    fi

    # RedisInsight (optional)
    if docker ps --format '{{{{.Names}}}}' | grep -q "redisinsight"; then
        echo "  ✓ RedisInsight - Running (port 5540)"
    else
        echo "  · RedisInsight - Not running (optional)"
    fi

    echo ""
    echo "Quick Actions:"
    echo "  Start databases: just dev-up"
    echo "  Start backend:   cd repos/dem2 && just run"
    echo "  Start frontend:  cd repos/dem2-webui && pnpm dev"
    echo "  Stop all:        just dev-down"

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
