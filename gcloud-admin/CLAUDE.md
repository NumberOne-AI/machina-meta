# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**gcloud-admin** is a DevOps administrative container for managing GKE deployments on Google Cloud Platform. It provides a consistent, fully-featured environment for Kubernetes cluster operations, debugging, and deployment management.

**Integration with machina-meta**: This repository is integrated into the machina-meta workspace. Commands can be run from the machina-meta root using the module syntax: `just gcloud-admin::<command>`. See `../CLAUDE.md` for more details.

## Project Structure

```
gcloud-admin/
├── Dockerfile           # Container definition with all tools
├── docker-compose.yaml  # Container orchestration and volume mounts
├── justfile             # Common operations (just <command>)
├── .env.example         # Environment template
├── .env                 # Local environment (copy from .env.example)
├── README.md            # User documentation
├── CLAUDE.md            # AI assistant guidance (this file)
├── TODO.md              # Task tracking
└── PROBLEMS.md          # Issue tracking
```

## Common Commands

All commands run via `just` from the project directory:

```bash
# Container management
just build              # Build the container image
just build-fresh        # Build with no cache
just shell              # Start interactive shell

# First-time setup (automated)
just setup-nonprod      # Complete setup: auth + nonprod credentials + verify
just setup-prod         # Complete setup: auth + prod credentials + verify

# GCP/GKE operations
just auth               # Authenticate with Google Cloud
just get-creds-nonprod  # Get nonprod cluster credentials
just get-creds-prod     # Get prod cluster credentials
just list-clusters      # List all GKE clusters

# Kubernetes operations
just kubectl <args>     # Run kubectl command
just helm <args>        # Run helm command
just k9s                # Start k9s TUI
just pods               # List all pods
just deployments        # List all deployments
just services           # List all services

# ArgoCD operations
just argocd-login       # Login to ArgoCD server (SSO)
just argocd-logout      # Logout from ArgoCD server
just argo-list          # List ArgoCD applications
just argo-status <app>  # Check app status
just argo-sync <app>    # Sync application

# Network debugging
just dig <host>         # DNS lookup
just nc <host> <port>   # TCP connectivity test
just trace <host>       # Traceroute

# Utilities
just versions           # Show all tool versions
just context            # Show current kubectl context
just contexts           # List all contexts
```

## Installed Tools

### GCP Tools
- `gcloud` - Google Cloud CLI
- `gsutil` - Cloud Storage CLI
- `bq` - BigQuery CLI
- `gke-gcloud-auth-plugin` - GKE authentication plugin

### Kubernetes Tools
- `kubectl` - Kubernetes CLI (with krew plugins)
- `helm` - Package manager
- `kustomize` - Configuration management
- `k9s` - Terminal UI
- `kubectx` / `kubens` - Context/namespace switching
- `stern` - Multi-pod log tailing
- `argocd` - ArgoCD CLI

### kubectl Plugins (via krew)
- `ctx`, `ns` - Context/namespace switching
- `neat` - Clean YAML output
- `tree` - Resource hierarchy
- `images` - Container images
- `get-all` - All resources
- `resource-capacity` - Node resource usage
- `whoami` - Current user/permissions
- `access-matrix` - RBAC access
- `node-shell` - SSH into nodes
- `view-secret` - Decode secrets

### Network Debugging
- `dig`, `nslookup`, `host` - DNS
- `curl`, `wget` - HTTP clients
- `nc` (netcat) - TCP/UDP connectivity
- `tcpdump` - Packet capture
- `traceroute`, `mtr` - Route tracing
- `nmap` - Port scanning
- `iperf3` - Bandwidth testing
- `socat` - Socket relay
- `openssl` - TLS/SSL testing

### Container Tools
- `docker` CLI - Build and push images
- `docker buildx` - Multi-platform builds

## Environment Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `CLOUDSDK_CORE_PROJECT` | No | GCP project ID (default: n1-machina1) |
| `CLOUDSDK_COMPUTE_REGION` | No | Default region (default: us-central1) |
| `ARGOCD_SERVER` | Yes | ArgoCD server URL |

## Volume Mounts

### Docker Volumes (Persistent)

| Volume Name | Container Path | Purpose |
|-------------|----------------|---------|
| `gcloud-config` | `/root/.config/gcloud` | Google Cloud authentication & config |
| `kube-config` | `/root/.kube` | Kubernetes config & contexts |
| `argocd-config` | `/root/.config/argocd` | ArgoCD authentication tokens |

**ArgoCD Authentication:**

First-time setup with SSO:
```bash
# Login to ArgoCD using SSO (prints URL for manual browser authentication)
just argocd-login

# The command will print a URL like:
# https://argo.n1-machina.dev/api/dex/auth?...
# Open this URL in your browser to authenticate

# After authentication, credentials are stored in argocd-config volume

# Verify authentication
just argo-list

# Logout (if needed)
just argocd-logout
```

The `argocd-login` command uses SSO with manual URL opening (no automatic browser launch).
Uses host networking so the OAuth callback on localhost:8085 is accessible from your browser.
Credentials persist across container restarts.

**Managing credentials volumes:**
```bash
# List volumes
docker volume ls | grep -E 'gcloud-config|kube-config|argocd-config'

# Backup credentials
docker run --rm -v gcloud-admin_gcloud-config:/data -v $(pwd):/backup alpine tar czf /backup/gcloud-config-backup.tar.gz -C /data .
docker run --rm -v gcloud-admin_kube-config:/data -v $(pwd):/backup alpine tar czf /backup/kube-config-backup.tar.gz -C /data .
docker run --rm -v gcloud-admin_argocd-config:/data -v $(pwd):/backup alpine tar czf /backup/argocd-config-backup.tar.gz -C /data .

# Restore credentials
docker run --rm -v gcloud-admin_gcloud-config:/data -v $(pwd):/backup alpine tar xzf /backup/gcloud-config-backup.tar.gz -C /data
docker run --rm -v gcloud-admin_kube-config:/data -v $(pwd):/backup alpine tar xzf /backup/kube-config-backup.tar.gz -C /data
docker run --rm -v gcloud-admin_argocd-config:/data -v $(pwd):/backup alpine tar xzf /backup/argocd-config-backup.tar.gz -C /data

# Remove volumes (WARNING: deletes all credentials)
docker volume rm gcloud-admin_gcloud-config gcloud-admin_kube-config gcloud-admin_argocd-config
```

### Host Directories

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `~/.ssh` | `/root/.ssh` | SSH keys (read-only) |
| `../dem2` | `/workspace/dem2` | Backend project |
| `../dem2-webui` | `/workspace/dem2-webui` | Frontend project (read-only) |
| `../medical-catalog` | `/workspace/medical-catalog` | Catalog service (read-only) |
| `../dem2-infra` | `/workspace/dem2-infra` | Infrastructure |
| `/var/run/docker.sock` | `/var/run/docker.sock` | Docker socket |

## Related Projects

This container manages deployments for:

| Project | Description | Namespace |
|---------|-------------|-----------|
| dem2 | MachinaMed backend API | tusdi-dev, tusdi-staging |
| dem2-webui | MachinaMed frontend | tusdi-dev, tusdi-staging |
| medical-catalog | Biomarker catalog service | medical-catalog |
| dem2-infra | Infrastructure configs | gateway, argocd, langfuse |

## Development Guidelines

### Dockerfile Changes
- Use specific version tags for tool downloads (not `latest`)
- Update version environment variables at top of Dockerfile
- Test builds with `just build-fresh` after changes
- Document new tools in README.md

### Adding New Tools
1. Add download/install commands to Dockerfile
2. Update version ENV if applicable
3. Add bash completion if available
4. Add to MOTD display
5. Update README.md documentation

### justfile Conventions
- Use descriptive recipe names
- Add comments above each recipe
- Use `docker compose run --rm` for ephemeral operations
- Pass through environment variables from .env

## TODO.md and PROBLEMS.md

Track work and issues using these files:

- **TODO.md** - Planned work, improvements, technical debt
- **PROBLEMS.md** - Known issues, investigations, observations

**Important:** Changes to these files should be committed immediately after modification.

## Git Workflow

- Main branch: `main`
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- No attribution/co-authorship credits in commits
