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
