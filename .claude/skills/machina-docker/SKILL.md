---
name: machina-docker
description: Docker development environment for machina-meta workspace. Use for container management, development stacks, database services, health checks, volume management, and infrastructure. The single authoritative source for all Docker operations.
---

# Docker Skill

Comprehensive Docker environment management for the machina-meta workspace. This is the **single authoritative source** for all Docker operations.

## When to Use This Skill

### Development Environment Management
- Starting/stopping the development stack
- Checking service status and health
- Managing database containers (PostgreSQL, Neo4j, Redis, Qdrant)
- Running full-stack development (frontend + backend + databases)

### Service Operations
- Building Docker images
- Running specific service containers
- Debugging container issues
- Log extraction and analysis

### Database Operations
- Managing development databases
- Snapshot/restore operations (Qdrant)
- Volume management and data persistence
- Database migrations in containers

### Specialized Stacks
- Langfuse observability (local and production)
- Local LLM inference (Ollama, vLLM with GPU)
- Remote debugging tools (pgAdmin, Neo4j Browser)
- gcloud-admin DevOps container

### Infrastructure & Deployment
- Gateway infrastructure (ngrok, nginx)
- Monitoring stacks (Langfuse + OTEL)
- LLM experiment environments

---

## Quick Reference

### Primary Development Commands

All Docker commands should be run from the **machina-meta workspace root**.

> **Note:** Justfile rules in `repos/dem2`, `repos/dem2-webui`, and `repos/medical-catalog` are **deprecated**. Use workspace-level commands instead.

**Workspace Level (machina-meta root):**

| Command | Purpose | Underlying Operation |
|---------|---------|---------------------|
| `just dev-up` | Start full stack (all services) | `./scripts/dev_stack.py up` |
| `just dev-down` | Stop all services | `./scripts/dev_stack.py down` |
| `just dev-status` | Check all service health | `./scripts/dev_stack.py status` |
| `just dev-restart` | Rebuild and restart | `docker compose --profile dev up -d --build` |
| `just dev-check` | Run sanity check tests | Non-destructive verification suite |

**gcloud-admin DevOps:**

| Command | Purpose | Underlying Operation |
|---------|---------|---------------------|
| `just gcloud-admin::shell` | Interactive DevOps shell | `docker compose run --rm gcloud-admin` |
| `just gcloud-admin::kubectl <args>` | Run kubectl | `docker compose run --rm gcloud-admin kubectl <args>` |
| `just gcloud-admin::helm <args>` | Run helm | `docker compose run --rm gcloud-admin helm <args>` |
| `just gcloud-admin::k9s` | Cluster TUI | `docker compose run --rm gcloud-admin k9s` |
| `just gcloud-admin::argocd <args>` | Run ArgoCD CLI | `docker compose run --rm gcloud-admin argocd <args>` |
| `just gcloud-admin::preview-info <identifier>` | Get preview deployment info | Shows tags, commits, PR status, ArgoCD health |

**Preview Environment Info:**

Check the current state of a preview deployment using any identifier:

```bash
# By GKE namespace
just gcloud-admin::preview-info --gke-namespace tusdi-preview-92

# By git tag
just gcloud-admin::preview-info --git-tag preview-dbeal-docproc-dev

# By ArgoCD app name
just gcloud-admin::preview-info --argocd-app preview-pr-92

# By infra branch
just gcloud-admin::preview-info --infra-branch preview/dbeal-docproc-dev

# By infra PR number
just gcloud-admin::preview-info --pr 92

# By git branch
just gcloud-admin::preview-info --git-branch feature/dbeal-docproc-dev

# Output formats: terminal, json, markdown (default: markdown)
just gcloud-admin::preview-info --gke-namespace tusdi-preview-92 --format json
```

**Output includes:**
- Preview ID resolved from identifier
- Backend/Frontend tag commits and dates
- Infrastructure branch and PR status
- ArgoCD sync and health status
- GitHub workflow status for all repos

**Updating Preview Deployments:**

To deploy new changes to a preview environment:

```bash
# Step 1: Check current preview state and get the Preview Tag name
just gcloud-admin::preview-info --gke-namespace tusdi-preview-92
# Look for: | **dem2 (Backend)** | Preview Tag | ✅ preview-dbeal-docproc-dev |

# Step 2: Tag the desired commit with the EXACT preview tag name
cd repos/dem2 && git tag -f preview-dbeal-docproc-dev HEAD

# Step 3: Push and overwrite the tag to remote (triggers CI/CD)
cd repos/dem2 && git push origin preview-dbeal-docproc-dev --force

# Step 4: Monitor for deployment progress
just gcloud-admin::preview-info --gke-namespace tusdi-preview-92
# Watch for: Workflows status → ArgoCD sync → Health status
```

**Note:** The preview tag name comes from `preview-info` output (e.g., `preview-dbeal-docproc-dev`).
Frontend (dem2-webui) follows the same pattern if frontend changes need deployment.

### Deprecated Commands (in child repos)

The following patterns are **deprecated** and should be migrated to workspace-level commands:

| Deprecated Command | Replacement |
|-------------------|-------------|
| `(cd repos/dem2 && just dev-env-up)` | `just dev-up` (starts full stack) |
| `(cd repos/dem2 && just dev-env-down)` | `just dev-down` |
| `(cd repos/dem2 && just med-api-up)` | `just dev-up` |
| `(cd repos/medical-catalog && just dev-env-up)` | `just dev-up` |
| `(cd repos/medical-catalog && just docker-build)` | (pending migration) |

---

## Docker Compose Files Map

| File | Location | Purpose | Profile |
|------|----------|---------|---------|
| `docker-compose.yaml` | Root | **Main workspace stack (primary)** | `dev` |
| `docker-compose.yaml` | `repos/dem2/infrastructure/` | Backend dev environment | `dev`, `test` |
| `docker-compose.langfuse.local.yaml` | `repos/dem2/infrastructure/` | Local Langfuse observability | - |
| `docker-compose.yml` | `repos/dem2/infrastructure/remote-debug/` | pgAdmin, Neo4j debug | - |
| `docker-compose.qdrant.yaml` | `repos/dem2/services/indicators-catalog/` | Standalone Qdrant | - |
| `docker-compose.yaml` | `repos/medical-catalog/infra/` | Catalog Qdrant (port 16333) | `dev` |
| `docker-compose.yaml` | `gcloud-admin/` | DevOps admin container | - |
| `docker-compose.ngrok-nginx.yaml` | `repos/dem2-infra/.../gateway/` | Public gateway tunnel | - |
| `docker-compose.langfuse.yaml` | `repos/dem2-infra/.../monitoring/` | Production Langfuse + OTEL | `monitoring` |
| `docker-compose.ollama.yml` | `repos/dem2-infra/.../experiment-setup/` | Local LLM with GPU | - |
| `docker-compose.vllm.yml` | `repos/dem2-infra/.../experiment-setup/` | vLLM inference server | - |

See `references/compose-files.md` for detailed documentation of each file.

---

## Profile System

All services use the unified `dev` profile:

| Profile | Services | Use Case |
|---------|----------|----------|
| `dev` | All services (databases + backend + frontend + catalog) | Full stack development |

**Starting Services:**

```bash
# Full stack (all services)
docker compose --profile dev up -d

# Or use the just command (recommended)
just dev-up
```

**Note:** The `--profile dev` flag is required for `up`, `down`, `restart`, and `build` operations. It is NOT required for querying running containers (`ps`, `logs`, `stats`, `exec`).

See `references/profiles.md` for detailed profile documentation.

---

## Port Mappings

### Development Ports (localhost)

| Port | Service | Stack | Health Check |
|------|---------|-------|--------------|
| 3000 | Frontend (Next.js) | machina-meta | http://localhost:3000 |
| 5432 | PostgreSQL | machina-meta | `pg_isready -h localhost` |
| 5540 | RedisInsight | machina-meta | http://localhost:5540 |
| 6333 | Qdrant REST API | machina-meta | http://localhost:6333/healthz |
| 6334 | Qdrant Web UI | machina-meta | http://localhost:6334/dashboard |
| 6379 | Redis | machina-meta | `redis-cli ping` |
| 7474 | Neo4j Browser | machina-meta | http://localhost:7474 |
| 7687 | Neo4j Bolt | machina-meta | (used by applications) |
| 8000 | Backend API | machina-meta | http://localhost:8000/docs |
| 8001 | Medical Catalog | machina-meta | http://localhost:8001/health |

### Langfuse Stack Ports

| Port | Service | Purpose |
|------|---------|---------|
| 3003 | Langfuse Web | Observability UI |
| 3030 | Langfuse Worker | Background processing |
| 5433 | Langfuse PostgreSQL | Langfuse database |
| 6380 | Langfuse Redis | Langfuse cache |
| 8123 | ClickHouse HTTP | Analytics queries |
| 9090 | MinIO API | S3-compatible storage |
| 9091 | MinIO Console | MinIO admin UI |

### Specialized Ports

| Port | Service | Purpose |
|------|---------|---------|
| 5050 | pgAdmin | PostgreSQL admin UI (remote-debug) |
| 11434 | Ollama | Local LLM inference |
| 16333 | Qdrant (catalog) | Medical catalog vector store |
| 17474 | Neo4j (remote) | Remote debugging Neo4j |

See `references/ports.md` for complete port documentation.

---

## Common Usage Patterns

### Pattern 1: Full Stack Development (Recommended)

Start everything from workspace root:

```bash
# Start full stack
just dev-up

# Check status
just dev-status

# When done
just dev-down
```

### Pattern 2: Backend Development Only

Start databases, run backend locally:

```bash
# Start full stack (includes databases)
just dev-up

# Stop the containerized backend to run locally
docker stop machina-meta-backend-1

# Run backend locally
(cd repos/dem2 && just run)

# When done
just dev-down
```

### Pattern 3: Frontend Development Only

```bash
# Start full stack
just dev-up

# Or just start frontend locally if backend is running
(cd repos/dem2-webui && pnpm dev)
```

### Pattern 4: Clean Restart with Fresh Data

Reset databases and reload fixtures:

```bash
# Stop and remove volumes
just dev-down
docker volume prune -f  # Warning: removes all unused volumes

# Start fresh
just dev-up
```

### Pattern 5: Local LLM Inference (Ollama)

```bash
# Start Ollama with GPU
(cd repos/dem2-infra/infrastructure/docker/google_cloud/experiment-setup && \
  docker compose -f docker-compose.ollama.yml up -d)

# Pull a model
docker exec -it ollama ollama pull llama3.2

# Test
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "Hello"}'
```

### Pattern 6: Local Langfuse Observability

```bash
# Start Langfuse stack
(cd repos/dem2/infrastructure && docker compose -f docker-compose.langfuse.local.yaml up -d)

# Access UI at http://localhost:3003

# Stop
(cd repos/dem2/infrastructure && docker compose -f docker-compose.langfuse.local.yaml down)
```

### Pattern 7: Remote Debugging Tools

```bash
# Start pgAdmin and Neo4j browser
(cd repos/dem2/infrastructure/remote-debug && docker compose up -d)

# pgAdmin: http://localhost:5050
# Neo4j: http://localhost:17474
```

### Pattern 8: gcloud-admin DevOps

```bash
# First-time setup
just gcloud-admin::setup-nonprod

# Interactive shell
just gcloud-admin::shell

# Run kubectl commands
just gcloud-admin::kubectl get pods -n argocd

# Interactive cluster UI
just gcloud-admin::k9s
```

### Pattern 9: Query Remote Neo4j on GKE (Preview/Dev)

For debugging data issues on preview or dev environments, you can query Neo4j directly:

**Step 1: Port-forward to Neo4j** (requires kubectl configured locally)

```bash
# Port-forward to Neo4j on a specific namespace
# Uses 17474/17687 to avoid conflict with local Neo4j (7474/7687)
kubectl port-forward -n tusdi-preview-92 svc/neo4j 17474:7474 17687:7687 &

# Or for tusdi-dev
kubectl port-forward -n tusdi-dev svc/neo4j 17474:7474 17687:7687 &
```

**Step 2: Get Neo4j credentials from Kubernetes**

```bash
# Get password from secret (username is always 'neo4j')
kubectl get secret -n tusdi-preview-92 neo4j-secrets -o json | \
  jq -r '.data.NEO4J_PASSWORD | @base64d'
```

**Step 3: Query using neo4j-query.py**

```bash
# Set credentials via environment variables
DYNACONF_NEO4J_DB__HTTP_PORT=17474 \
DYNACONF_NEO4J_DB__USER=neo4j \
DYNACONF_NEO4J_DB__PASSWORD=<password-from-step-2> \
./scripts/neo4j-query.py --format json "MATCH (n:ObservationTypeNode) RETURN n.name LIMIT 10"

# Example: Find duplicate biomarkers
DYNACONF_NEO4J_DB__HTTP_PORT=17474 \
DYNACONF_NEO4J_DB__USER=neo4j \
DYNACONF_NEO4J_DB__PASSWORD=<password> \
./scripts/neo4j-query.py --format json "
MATCH (ov:ObservationValueNode)-[:INSTANCE_OF]->(ot:ObservationTypeNode)
WITH ot.name AS name, ov.observed_at AS observed, count(ov) AS cnt
WHERE cnt > 1
RETURN name, observed, cnt
ORDER BY cnt DESC
LIMIT 20
"
```

**Step 4: Clean up port-forward**

```bash
# Find and kill the port-forward process
pkill -f "port-forward.*neo4j"
```

**Common Namespaces:**
- `tusdi-dev` - Development environment
- `tusdi-staging` - Staging environment
- `tusdi-preview-<id>` - Preview environments (e.g., tusdi-preview-92)

**Note:** gcloud-admin port-forwarding runs inside the container, not accessible from host. Use kubectl directly on host for now. See TODO.md for planned improvement.

### Pattern 10: Call Remote Backend API with Authentication

For testing backend APIs on preview/dev environments with full authentication:

**Step 1: Set up environment file** (e.g., `.env.tusdi-preview-92`)

```bash
# Create environment file with all required variables
cat > .env.tusdi-preview-92 << 'EOF'
# Backend API URL (port-forwarded from tusdi-api service)
export BACKEND_URL="http://localhost:18000/api/v1"

# PostgreSQL connection (port-forwarded from postgres service)
export POSTGRES_HOST=localhost
export POSTGRES_PORT=15432
export POSTGRES_USER=tusdi
export POSTGRES_PASSWORD='<password-from-k8s-secret>'
export POSTGRES_DB=tusdi_preview

# Neo4j connection (port-forwarded from neo4j service)
export DYNACONF_NEO4J_DB__HTTP_PORT=17474
export DYNACONF_NEO4J_DB__USER=neo4j
export DYNACONF_NEO4J_DB__PASSWORD=<password-from-k8s-secret>

# Default user for authentication
export AUTH_EMAIL=dbeal@numberone.ai

# Default patient context
export PATIENT_FIRST_NAME=Stuart
export PATIENT_LAST_NAME=McClure
export PATIENT_DATE_OF_BIRTH=1969-03-09
EOF
```

**Step 2: Port-forward all services**

```bash
# Backend API (use port 18000 to avoid conflict with local :8000)
kubectl port-forward -n tusdi-preview-92 svc/tusdi-api 18000:8000 &

# PostgreSQL (use port 15432 to avoid conflict with local :5432)
kubectl port-forward -n tusdi-preview-92 svc/postgres 15432:5432 &

# Neo4j (use ports 17474/17687 to avoid conflict with local :7474/:7687)
kubectl port-forward -n tusdi-preview-92 svc/neo4j 17474:7474 17687:7687 &
```

**Step 3: Use curl_api.sh with authentication**

```bash
# curl_api.sh automatically handles authentication via user_manager.py
# It generates JWT tokens and sets patient context headers

# List observations grouped by type
(. .env.tusdi-preview-92 && cd repos/dem2 && just curl_api '{"function": "get_observations_grouped", "per_type_values_limit": 3}')

# Filter specific biomarker with jq
(. .env.tusdi-preview-92 && cd repos/dem2 && just curl_api '{"function": "get_observations_grouped", "per_type_values_limit": 3}') | jq '.items[]|select(.observation_type.display_name=="Folate").values'

# List documents
(. .env.tusdi-preview-92 && cd repos/dem2 && just curl_api '{"function": "list_documents"}')

# List tasks
(. .env.tusdi-preview-92 && cd repos/dem2 && just curl_api '{"function": "list_tasks"}')
```

**Authentication Scripts:**

- **`user_manager.py`** - Generates JWT tokens for API authentication
  - `uv run scripts/user_manager.py user token --export` - outputs `export AUTH_HEADER="Bearer ..."`
  - `uv run scripts/user_manager.py user token --export-cookie` - for UI/browser authentication
  - Called automatically by `curl_api.sh`

- **`curl_api.sh`** - JSON dispatch system for API calls
  - Automatically handles JWT token generation via `user_manager.py`
  - Sets patient context header (`X-Patient-Context-ID`)
  - Respects `BACKEND_URL` environment variable
  - See `repos/dem2/CLAUDE.md` for full function reference

**Step 4: Clean up port-forwards**

```bash
# Kill all port-forwards
pkill -f "port-forward.*tusdi-preview"
```

### Pattern 11: Multi-Service Port Forwarding (Automated)

For forwarding multiple services simultaneously with automatic restart on failure, use the `port_forward_service.py` script.

**Location**: `scripts/port_forward_service.py`

**Features**:
- Forward multiple services from different namespaces simultaneously
- Automatic restart when port-forwards fail
- JSON configuration for easy scripting
- Async process management

**Basic Usage**:

```bash
# Forward single service
./scripts/port_forward_service.py '{"port_forward": [{"namespace": "tusdi-staging", "service_name": "redis"}]}'

# Forward multiple services from same namespace
./scripts/port_forward_service.py '{"port_forward": [
  {"namespace": "tusdi-staging", "service_name": "neo4j"},
  {"namespace": "tusdi-staging", "service_name": "postgres"},
  {"namespace": "tusdi-staging", "service_name": "redis"}
]}'

# Forward services from DIFFERENT namespaces (key feature)
./scripts/port_forward_service.py '{"port_forward": [
  {"namespace": "tusdi-staging", "service_name": "redis"},
  {"namespace": "tusdi-preview-92", "service_name": "neo4j"}
]}'
```

**Forward All Services from a Namespace**:

```bash
# All tusdi-staging services
./scripts/port_forward_service.py '{
  "port_forward": [
    {"namespace": "tusdi-staging", "service_name": "neo4j"},
    {"namespace": "tusdi-staging", "service_name": "postgres"},
    {"namespace": "tusdi-staging", "service_name": "qdrant"},
    {"namespace": "tusdi-staging", "service_name": "redis"},
    {"namespace": "tusdi-staging", "service_name": "redisinsight"},
    {"namespace": "tusdi-staging", "service_name": "tusdi-api"},
    {"namespace": "tusdi-staging", "service_name": "tusdi-webui"}
  ]
}'
```

**View JSON Schema**:

```bash
./scripts/port_forward_service.py --schema
```

**Port Mapping Behavior**:
- The script uses `targetPort` as the local port (maps service port to targetPort on localhost)
- Multi-port services (like Neo4j with 7474 and 7687) forward all ports automatically
- No port conflict handling - ensure local ports are free before running

**When to Use This vs Manual kubectl**:

| Use Case | Recommended Approach |
|----------|---------------------|
| Quick single-service debug | Manual `kubectl port-forward` |
| Multiple services, same namespace | `port_forward_service.py` |
| Multiple services, different namespaces | `port_forward_service.py` ✓ |
| Long-running port-forward sessions | `port_forward_service.py` (auto-restart) |
| CI/CD scripts | `port_forward_service.py` (JSON config) |

**Stopping Port Forwards**:

Press `Ctrl+C` to stop all port-forwards managed by the script.

---

## Volume Management

### Named Volumes

| Volume | Service | Purpose |
|--------|---------|---------|
| `postgres_data` | PostgreSQL | User data, sessions |
| `neo4j_data` | Neo4j | Graph data |
| `neo4j_logs` | Neo4j | Database logs |
| `redis_data` | Redis | Cache persistence |
| `qdrant_storage` | Qdrant | Vector embeddings |
| `redisinsight_data` | RedisInsight | UI settings |

### Qdrant Snapshot Restore

The `dev_stack.py` script automatically restores Qdrant snapshots on first startup:

```bash
# Manual restore if needed
(cd repos/medical-catalog && just snapshot-restore-all)

# Check Qdrant collections
curl http://localhost:6333/collections
```

### Clearing Volumes

```bash
# Stop services and remove volumes
docker compose down -v

# Remove specific volume
docker volume rm machina-meta_postgres_data

# Remove all unused volumes (DANGEROUS)
docker volume prune -f
```

See `references/volumes.md` for detailed volume documentation.

---

## Health Checks

### dev_stack.py Orchestration

The `scripts/dev_stack.py` script provides intelligent health monitoring:

- **90-second timeout** for service startup
- **HTTP endpoint validation** for web services
- **Container health status** from Docker
- **Automatic error analysis** from logs
- **Qdrant snapshot detection** and restore

### Service Health Endpoints

| Service | Health Endpoint |
|---------|-----------------|
| Backend | `GET /api/v1/health` |
| Medical Catalog | `GET /health` |
| Qdrant | `GET /healthz` |
| Neo4j | `GET :7474` (browser) |
| PostgreSQL | `pg_isready` |
| Redis | `redis-cli ping` |

### Sanity Check Suite

Run the comprehensive sanity check before committing Docker changes:

```bash
just dev-check
```

This runs 6 non-destructive verification tests:
1. **Service Status** - `./scripts/dev_stack.py status`
2. **Container Status** - `docker compose ps`
3. **Health Checks** - Container health inspection
4. **Resource Usage** - `docker stats` snapshot
5. **Volume Status** - List machina volumes
6. **Endpoint Health** - HTTP checks for backend, catalog, and Qdrant

### Manual Health Checks

```bash
# Check all container status
docker compose ps

# Check specific service logs
docker compose logs backend --tail 50

# Check container health
docker inspect --format='{{json .State.Health}}' machina-meta-backend-1
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000
# or
ss -tulpn | grep 8000

# Kill process or stop container
docker ps | grep 8000
docker stop <container-name>
```

### Container Won't Start

```bash
# Check logs
docker compose logs <service> --tail 100

# Check health status
docker inspect --format='{{json .State.Health}}' <container-name>

# Check events
docker events --since 5m
```

### Database Connection Failed

```bash
# Verify containers are healthy
just dev-status

# Check network connectivity
docker network ls
docker network inspect machina-meta_default

# Test connection from host
pg_isready -h localhost -p 5432
redis-cli -h localhost -p 6379 ping
```

### Neo4j Won't Start

```bash
# Check Neo4j logs
docker compose logs neo4j --tail 100

# Common issue: memory limits
# Edit docker-compose.yaml NEO4J_dbms_memory_* settings
```

### Qdrant Snapshots Not Restored

```bash
# Check if volume exists
docker volume ls | grep qdrant

# Manual restore
(cd repos/medical-catalog && just snapshot-restore-all)

# Verify collections
curl http://localhost:6333/collections
```

### Log Extraction

```bash
# Extract backend logs
(cd repos/dem2 && ./scripts/extract_backend_logs.sh -s backend -l ERROR --since 10m)

# Follow all logs
docker compose logs -f

# Follow specific service
docker compose logs -f backend
```

See `references/troubleshooting.md` for comprehensive troubleshooting guide.

---

## API Testing with curl_api

The `curl_api` justfile rule in `repos/dem2` provides a convenient JSON-based interface for testing backend APIs without writing code.

### Overview

**Location**: `repos/dem2/justfile` (rule: `curl_api`)
**Backend Script**: `repos/dem2/scripts/curl_api.sh`
**Purpose**: Call backend API functions using JSON dispatch for development and testing

### How It Works

The `curl_api` rule uses a JSON dispatch system that:
1. Accepts a JSON payload with a `function` field and arguments
2. Routes the call to a registered bash function in `curl_api.sh`
3. Handles authentication automatically (JWT tokens + patient context)
4. Executes the API call and returns the result

### Basic Usage

```bash
# From repos/dem2 directory
(cd repos/dem2 && just curl_api '{"function": "function_name", "arg1": "value1", ...}')
```

**Authentication**:
- Automatically handles JWT token generation via `user_manager.py`
- Sets patient context header (`X-Patient-Context-ID`)
- Default user: `dbeal@numberone.ai`
- Default patient: Stuart McClure, DOB: 1969-03-03

### Available Function Categories

#### Document Management

**List documents**:
```bash
(cd repos/dem2 && just curl_api '{"function": "list_documents"}')
```

**Upload a file**:
```bash
(cd repos/dem2 && just curl_api '{"function": "upload_file", "path": "datasets/documents/test.pdf"}')
```

**Process a specific document**:
```bash
(cd repos/dem2 && just curl_api '{"function": "process_document", "file_id": "uuid-here"}')
```

**Process all uploaded documents**:
```bash
(cd repos/dem2 && just curl_api '{"function": "process_all_documents"}')
```

**Delete all documents**:
```bash
(cd repos/dem2 && just curl_api '{"function": "delete_all_documents"}')
```

#### Task Management

**List all document processing tasks**:
```bash
(cd repos/dem2 && just curl_api '{"function": "list_tasks"}')
```

**Get specific task details**:
```bash
(cd repos/dem2 && just curl_api '{"function": "get_task", "task_id": "uuid-here"}')
```

**List failed tasks only**:
```bash
(cd repos/dem2 && just curl_api '{"function": "list_failed_tasks"}')
```

#### Patient Management

**List all patients**:
```bash
(cd repos/dem2 && just curl_api '{"function": "list_patients"}')
```

#### Agent Session Management

**Create a new agent session**:
```bash
(cd repos/dem2 && just curl_api '{"function": "create_session", "name": "My Session"}')
```

**Set/update session name**:
```bash
(cd repos/dem2 && just curl_api '{"function": "set_session_name", "session_id": "uuid-here", "name": "New Name"}')
```

**List all sessions**:
```bash
(cd repos/dem2 && just curl_api '{"function": "list_sessions"}')
```

#### Agent Query

**Query the medical agent**:
```bash
(cd repos/dem2 && just curl_api '{"function": "query_agent", "query": "What is my cholesterol?"}')
```

**Query with specific session**:
```bash
(cd repos/dem2 && just curl_api '{"function": "query_agent", "query": "What is my cholesterol?", "session_id": "uuid-here"}')
```

#### Agent Diagnostics

**Check agent dependencies**:
```bash
(cd repos/dem2 && just curl_api '{"function": "check_agent_dependencies"}')
```

**Validate agent configuration**:
```bash
(cd repos/dem2 && just curl_api '{"function": "validate_agent_config"}')
```

#### Medical Catalog (Biomarker Enrichment)

**Enrich biomarkers**:
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_enrich", "names": ["ApoA-1", "Factor II"]}')
```

**Check enrichment status**:
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_enrich_status", "task_id": "uuid-here"}')
```

**Search for biomarkers**:
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_search", "names": ["cholesterol"], "limit": 5}')
```

**Search by alias groups**:
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_search_by_alias", "alias_groups": [["LDL"], ["HDL", "HDL-C"]]}')
```

**Search derivative biomarkers** (ratios, calculated values):
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_search_derivatives", "names": ["ApoB/ApoA-1"]}')
```

**Enrich derivatives** (ratios, sums, percentages):
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_enrich_derivatives", "names": ["ApoB/ApoA-1", "TC/HDL-C"]}')
```

**List all derivatives** (with pagination):
```bash
(cd repos/dem2 && just curl_api '{"function": "catalog_list_derivatives", "limit": 100, "offset": 0}')
```

#### Debug

**Debug JSON argument structure**:
```bash
(cd repos/dem2 && just curl_api '{"function": "debug_args", "names": ["test1", "test2"]}')
```

### Common Workflows

#### List Available Test Documents

Before uploading documents for testing, list available test documents in the repository:

```bash
# List all test documents with full paths
just list-test-docs

# Output example:
# [
#   "pdf_tests/medical_records/.../Boston Heart July 2021.pdf",
#   "pdf_tests/medical_records/.../Dutch cortisol 9-01-25.pdf",
#   ...
# ]
```

**Use this to**:
- Find available test documents before testing document processing
- Get correct paths for upload functions
- Identify specific documents for debugging (e.g., Dutch cortisol document for "Estrone (E1)" testing)

#### Upload and Process a Document

```bash
# First, list available test documents
just list-test-docs

# Upload document using path from list-test-docs
(cd repos/dem2 && just curl_api '{"function": "upload_file", "path": "pdf_tests/medical_records/Stuart Mcclure Medical Records (PRIVATE)/Dutch cortisol 9-01-25.pdf"}')

# Process the uploaded document (use the file_id from upload response)
(cd repos/dem2 && just curl_api '{"function": "process_document", "file_id": "file-id-from-upload"}')
```

#### Query Agent About Health Markers

```bash
# Query agent
(cd repos/dem2 && just curl_api '{"function": "query_agent", "query": "What is my latest cholesterol level?"}')
```

#### Check Task Processing Status

```bash
# List all tasks to find IDs
(cd repos/dem2 && just curl_api '{"function": "list_tasks"}')

# Get specific task details
(cd repos/dem2 && just curl_api '{"function": "get_task", "task_id": "abc-123-def"}')
```

#### Enrich and Validate Biomarkers

```bash
# Enrich biomarkers in catalog
(cd repos/dem2 && just curl_api '{"function": "catalog_enrich", "names": ["Total Cholesterol", "LDL", "HDL"]}')

# Search to verify they exist
(cd repos/dem2 && just curl_api '{"function": "catalog_search", "names": ["Total Cholesterol"], "limit": 5}')
```

### How It Differs from Direct curl_api.sh Usage

**Using just curl_api** (recommended):
```bash
(cd repos/dem2 && just curl_api '{"function": "list_documents"}')
```

**Direct script usage** (lower-level):
```bash
(cd repos/dem2 && bash -c 'source scripts/curl_api.sh && dispatch "{\"function\": \"list_documents\"}"')
```

**Benefits of just curl_api**:
- ✅ Cleaner syntax (no need to source or call dispatch)
- ✅ Proper error handling via justfile
- ✅ Consistent working directory handling
- ✅ Part of documented justfile interface

### Environment Variables

**Default settings** (defined in `scripts/curl_api.sh`):
```bash
PATIENT_FIRST_NAME=Stuart
PATIENT_LAST_NAME=McClure
PATIENT_DATE_OF_BIRTH=1969-03-03
AUTH_EMAIL=dbeal@numberone.ai
BACKEND_URL=http://localhost:8000/api/v1
FRONTEND_URL=http://localhost:3000
```

**Override patient context**:
```bash
PATIENT_FIRST_NAME=John PATIENT_LAST_NAME=Doe PATIENT_DATE_OF_BIRTH=1990-01-01 \
  (cd repos/dem2 && just curl_api '{"function": "list_documents"}')
```

**Enable verbose curl output** (for debugging):
```bash
CURL_VERBOSE=1 (cd repos/dem2 && just curl_api '{"function": "list_documents"}')
```

### Error Handling

If a function doesn't exist:
```bash
$ (cd repos/dem2 && just curl_api '{"function": "nonexistent"}')
# ERROR: Unknown function: nonexistent
# Available functions: list_documents, upload_file, process_document, ...
```

If required arguments are missing:
```bash
$ (cd repos/dem2 && just curl_api '{"function": "upload_file"}')
# ERROR: Missing 'path' field in JSON
# Usage: {"function": "upload_file", "path": "path/to/file.pdf"}
```

### When to Use curl_api

**Use curl_api for**:
- ✅ Quick API testing during development
- ✅ One-off administrative tasks (upload, delete, etc.)
- ✅ Debugging API endpoints and responses
- ✅ Validating authentication and patient context
- ✅ Scripting batch operations

**Don't use curl_api for**:
- ❌ Production operations (use proper API clients)
- ❌ Performance testing (use dedicated load testing tools)
- ❌ Automated testing (use pytest with proper fixtures)

### Related Commands

**Low-level curl_api.sh functions** (not dispatched, but useful):
```bash
# Get patient ID and set context
(cd repos/dem2 && bash -c 'source scripts/curl_api.sh && _export_patient_context_id_internal && declare -p X_PATIENT_CONTEXT_ID')

# Call backend API with auth
(cd repos/dem2 && bash -c 'source scripts/curl_api.sh && _export_patient_context_id_internal && auth_backend "/graph-memory/medical/observations/grouped"')
```

**See also**:
- `repos/dem2/scripts/curl_api.sh` - Complete function implementations
- `repos/dem2/justfile` (line 271-347) - curl_api rule documentation
- `.claude/skills/machina-ui/SKILL.md` - UI debugging with curl_api examples

## Environment Variables

### Authoritative Configuration

**The single source of truth for environment variables is `machina-meta/.env`** at the workspace root.

```
machina-meta/.env          # THE authoritative .env file
```

**Important:** Any `.env` files in subdirectories (repos/dem2/.env, repos/medical-catalog/.env, etc.) are **temporary symlinks** to the root `.env` file. Do not treat them as separate configuration files.

### Database Defaults (Docker Compose)

```yaml
# PostgreSQL
POSTGRES_USER: postgres
POSTGRES_PASSWORD: demodemo
POSTGRES_DB: demodemo

# Neo4j
NEO4J_AUTH: neo4j/demodemo

# Redis
# No auth by default in dev
```

---

## Best Practices

### Starting Development

1. Always use workspace-level `just` commands from machina-meta root
2. Use `just dev-status` to verify services before running code
3. Check for port conflicts before starting: `lsof -i :8000`

### Stopping Development

1. Use `just dev-down` to stop all services cleanly
2. Don't use `docker kill` - it doesn't run shutdown hooks
3. Check nothing is left running: `docker ps`

### Resetting Data

1. Stop with `just dev-down`
2. Remove volumes: `docker volume prune -f`
3. Start fresh: `just dev-up`

### Updating Images

```bash
# Pull latest images
docker compose pull

# Rebuild local images
docker compose build --no-cache

# Update and restart
just dev-restart
```

---

## Integration with Other Skills

### machina-git
Use machina-git for all git operations. Docker skill handles containers only.

### kubernetes
Kubernetes skill handles production cluster operations. Docker images built here are deployed via Kubernetes.

### machina-ui
For frontend debugging, use machina-ui skill which can interact with containerized services.

---

## Reference Files

This skill includes detailed documentation in `references/`:

- **compose-files.md** - Complete documentation of all 13 docker-compose files
- **profiles.md** - Profile system (dev, test, prod) detailed guide
- **ports.md** - All port mappings with conflict detection
- **volumes.md** - Volume management, backup, restore
- **troubleshooting.md** - Common issues and solutions
- **scripts.md** - Helper script documentation (dev_stack.py, etc.)

Use `Read` to access specific reference files when detailed information is needed.
