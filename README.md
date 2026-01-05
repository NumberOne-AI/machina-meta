# GCloud Admin Container

A full-featured administrative container for managing GKE deployments on Google Cloud Platform.

## Features

### GCP Tools
- `gcloud` - Google Cloud CLI
- `gsutil` - Cloud Storage CLI
- `bq` - BigQuery CLI
- `gke-gcloud-auth-plugin` - GKE authentication plugin for kubectl

### Kubernetes Tools
- `kubectl` - Kubernetes CLI
- `helm` - Kubernetes package manager
- `kustomize` - Kubernetes configuration management
- `k9s` - Terminal UI for Kubernetes
- `kubectx` / `kubens` - Context and namespace switching
- `stern` - Multi-pod log tailing
- `argocd` - ArgoCD CLI for GitOps

### Kubectl Plugins (via krew)
- `ctx` / `ns` - Context and namespace switching
- `neat` - Clean up YAML output
- `tree` - Show resource hierarchy
- `images` - Show container images
- `get-all` - Get all resources
- `resource-capacity` - Show node resource usage
- `whoami` - Show current user/permissions
- `access-matrix` - Show RBAC access
- `node-shell` - SSH into nodes
- `view-secret` - Decode secrets

### Network Debugging
- `dig` / `nslookup` / `host` - DNS tools
- `curl` / `wget` - HTTP clients
- `nc` (netcat) - TCP/UDP connectivity
- `tcpdump` - Packet capture
- `traceroute` / `mtr` - Route tracing
- `nmap` - Port scanning
- `iperf3` - Bandwidth testing
- `socat` - Socket relay
- `openssl` - TLS/SSL testing

### Container Tools
- `docker` CLI - Build and push images
- `docker buildx` - Multi-platform builds

## Prerequisites

The following tools must be installed on your host machine:

| Tool | Description | Installation |
|------|-------------|--------------|
| Docker | Container runtime | https://docs.docker.com/get-docker/ |
| docker compose | Container orchestration (v2) | Included with Docker Desktop |
| just | Command runner | https://github.com/casey/just#installation |

## Quick Start

```bash
# Build the container
just build

# Start interactive shell
just shell

# Or using docker-compose directly
docker compose run --rm gcloud-admin
```

## First-Time Setup

### Automated Setup (Recommended)

Run a single command to authenticate and configure access to your cluster:

```bash
# For nonprod cluster
just setup-nonprod

# For prod cluster
just setup-prod
```

This will:
1. Authenticate with Google Cloud (opens browser for OAuth)
2. Get GKE cluster credentials
3. Verify the connection

### Manual Setup

If you prefer step-by-step setup:

1. **Authenticate with Google Cloud:**
   ```bash
   just auth
   # Or inside the container:
   gcloud auth login --update-adc
   ```

2. **Get GKE credentials:**
   ```bash
   just get-creds-nonprod
   # Or inside the container:
   gcloud container clusters get-credentials tusdi-nonprod-cluster --region us-central1
   ```

3. **Verify access:**
   ```bash
   just kubectl get nodes
   ```

## Common Operations

### Kubernetes Management
```bash
# Interactive shell
just shell

# Run kubectl commands
just kubectl get pods -n dev
just kubectl logs -f deployment/dem2-backend -n dev

# Use k9s TUI
just k9s

# Tail logs across pods
just stern dem2 -n dev
```

### ArgoCD
```bash
# Login to ArgoCD (uses $ARGOCD_SERVER from .env)
just argocd login $ARGOCD_SERVER

# List applications
just argo-list

# Check app status
just argo-status dem2-dev

# Sync application
just argo-sync dem2-dev
```

### Network Debugging
```bash
# DNS lookup
just dig api.tusdi.dev

# Check connectivity
just nc api.tusdi.dev 443

# Traceroute
just trace api.tusdi.dev
```

### Context Management
```bash
# Show current context
just context

# List all contexts
just contexts

# Switch context
just switch-context gke_n1-machina1_us-central1_tusdi-prod-cluster
```

## Volume Mounts

### Persistent Docker Volumes

The container uses Docker volumes to persist Google Cloud and Kubernetes credentials:

| Volume Name | Container Path | Purpose |
|-------------|----------------|---------|
| `gcloud-config` | `/root/.config/gcloud` | Google Cloud authentication & ADC |
| `kube-config` | `/root/.kube` | Kubernetes contexts & cluster credentials |

### Host Directory Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `~/.ssh` | `/root/.ssh` | SSH keys (read-only) |
| `../` | `/workspace/dem2` | dem2 project |
| `../../dem2-webui` | `/workspace/dem2-webui` | Frontend (read-only) |
| `../../medical-catalog` | `/workspace/medical-catalog` | Catalog (read-only) |
| `../../dem2-infra` | `/workspace/dem2-infra` | Infrastructure |
| `/var/run/docker.sock` | `/var/run/docker.sock` | Docker socket |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUDSDK_CORE_PROJECT` | `n1-machina1` | GCP project ID |
| `CLOUDSDK_COMPUTE_REGION` | `us-central1` | Default region |
| `USE_GKE_GCLOUD_AUTH_PLUGIN` | `True` | Enable GKE auth plugin |

## Aliases

The container includes these aliases:
- `k` = `kubectl`
- `kx` = `kubectx`
- `kn` = `kubens`

## Building Images

The container includes Docker CLI for building images:

```bash
# Inside the container
cd /workspace/dem2
docker build -t us-central1-docker.pkg.dev/n1-machina1/dem2/backend:latest .
docker push us-central1-docker.pkg.dev/n1-machina1/dem2/backend:latest
```

## Troubleshooting

### Authentication Issues
```bash
# Re-authenticate
gcloud auth login --update-adc

# Check current auth
gcloud auth list

# Refresh GKE credentials
gcloud container clusters get-credentials CLUSTER_NAME --region REGION
```

### kubectl Not Working
```bash
# Check context
kubectl config current-context

# List available contexts
kubectl config get-contexts

# Test connectivity
kubectl cluster-info
```

### Network Debugging Inside Cluster
```bash
# Start a debug pod
kubectl run debug --rm -it --image=gcloud-admin -- /bin/bash

# Or use node-shell plugin to access node
kubectl node-shell NODE_NAME
```
