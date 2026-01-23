# Implementation Plan: Add Minikube Support to dev_stack.py

## Overview

Add minikube cluster creation and Kubernetes deployment functionality to `scripts/dev_stack.py` as an alternative to Docker Compose. This reuses the existing Kustomize manifests from `repos/dem2-infra/k8s/` with a new minikube overlay.

## User Requirements (Confirmed)

1. **Reuse existing Kustomize manifests** from `repos/dem2-infra/k8s/base/`
2. **Add as alternative commands**: `minikube-up`, `minikube-down`, `minikube-status`, `minikube-destroy`
3. **Build images locally** in minikube's Docker daemon using `eval $(minikube docker-env)`

## Files to Create/Modify

### 1. New Kustomize Overlay: `repos/dem2-infra/k8s/overlays/minikube/`

Create a minikube-specific overlay that adapts production manifests for local development:

```
repos/dem2-infra/k8s/overlays/minikube/
├── kustomization.yaml       # Main overlay config
├── namespace.yaml           # tusdi-minikube namespace
├── local-secrets.yaml       # Replaces External Secrets with local K8s Secrets
├── storage-class.yaml       # Minikube-compatible storage class
├── env-vars-patch.yaml      # Environment variable overrides for local
└── image-pull-policy-patch.yaml  # Set imagePullPolicy: Never for local images
```

**Key adaptations**:
- Replace `expandable-storage` StorageClass with minikube's `standard`
- Replace External Secrets (GCP-dependent) with local Kubernetes Secrets
- Set `imagePullPolicy: Never` to use locally-built images
- Use `tusdi-minikube` namespace
- Override GKE workload identity service accounts
- Set local environment URLs (localhost:3000, localhost:8000)

### 2. Modify: `scripts/dev_stack.py`

Add ~300 lines of new code organized into these sections:

#### Constants
```python
MINIKUBE_CLUSTER_NAME = "machina-dev"
MINIKUBE_NAMESPACE = "tusdi-minikube"
MINIKUBE_KUSTOMIZE_PATH = "repos/dem2-infra/k8s/overlays/minikube"

IMAGES_TO_BUILD = [
    {"name": "tusdi-api", "context": "repos/dem2", "dockerfile": "Dockerfile"},
    {"name": "tusdi-webui", "context": "repos/dem2-webui", "dockerfile": "Dockerfile"},
    {"name": "medical-catalog", "context": "repos/medical-catalog", "dockerfile": "Dockerfile"},
]
```

#### New Functions to Add

| Function | Purpose |
|----------|---------|
| `check_minikube_installed()` | Verify minikube is available |
| `check_kubectl_installed()` | Verify kubectl is available |
| `check_prerequisites()` | Check all required tools |
| `minikube_cluster_exists()` | Check if cluster exists |
| `minikube_cluster_running()` | Check if cluster is running |
| `create_minikube_cluster()` | Create cluster with resources |
| `start_minikube_cluster()` | Start existing cluster |
| `stop_minikube_cluster()` | Stop running cluster |
| `delete_minikube_cluster()` | Delete entire cluster |
| `get_minikube_docker_env()` | Get Docker env vars for minikube |
| `build_image_in_minikube()` | Build single image in minikube |
| `build_all_images()` | Build all required images |
| `apply_kustomize_manifests()` | Apply K8s manifests |
| `delete_kustomize_manifests()` | Delete K8s resources |
| `wait_for_pods_ready()` | Wait for all pods to be Running/Ready |
| `minikube_up()` | Main command: create/start cluster, build, deploy |
| `minikube_down()` | Delete deployments (keep cluster) |
| `minikube_destroy()` | Delete entire cluster |
| `minikube_status()` | Show K8s resource status |

#### Update argparse

Add new commands to CLI:
- `minikube-up` → `minikube_up()`
- `minikube-down` → `minikube_down()`
- `minikube-destroy` → `minikube_destroy()`
- `minikube-status` → `minikube_status()`

### 3. Modify: `justfile`

Add convenience commands:
```just
minikube-up:
    ./scripts/dev_stack.py minikube-up

minikube-down:
    ./scripts/dev_stack.py minikube-down

minikube-destroy:
    ./scripts/dev_stack.py minikube-destroy

minikube-status format="markdown":
    ./scripts/dev_stack.py minikube-status --format {{format}}

minikube-forward:
    # Port forward all services to localhost
```

## Implementation Sequence

1. **Create minikube Kustomize overlay** (`repos/dem2-infra/k8s/overlays/minikube/`)
   - kustomization.yaml referencing base
   - local-secrets.yaml with hardcoded dev passwords + env var refs for API keys
   - storage-class.yaml using minikube's standard provisioner
   - env-vars-patch.yaml for local URLs
   - image-pull-policy-patch.yaml

2. **Add prerequisite checks** to dev_stack.py
   - `check_minikube_installed()`, `check_kubectl_installed()`

3. **Add cluster management functions**
   - Create, start, stop, delete, status checks

4. **Add image building functions**
   - Get minikube docker-env, build images

5. **Add Kubernetes deployment functions**
   - Apply/delete Kustomize manifests, wait for pods

6. **Add main command handlers**
   - `minikube_up()`, `minikube_down()`, `minikube_destroy()`, `minikube_status()`

7. **Update argparse** in `main()`

8. **Add justfile commands**

## Secrets Handling

The minikube overlay will:
- Use hardcoded development passwords for databases (postgres/demodemo for Neo4j)
- Read API keys from environment variables that user must export before running
- Create local Kubernetes Secrets instead of using External Secrets Operator

Required env vars for full functionality:
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `SERPER_API_KEY`
- `VISION_AGENT_API_KEY`
- `GOOGLE_SEARCH_API_KEY`
- `GOOGLE_AUTH_CLIENT_ID`
- `GOOGLE_AUTH_CLIENT_SECRET`

## Minikube Cluster Configuration

```bash
minikube start \
  -p machina-dev \
  --cpus 4 \
  --memory 8192 \
  --disk-size 40g \
  --driver docker \
  --addons ingress \
  --addons storage-provisioner
```

## Access Pattern

After `minikube-up` completes, services are accessed via port-forwarding:
```bash
kubectl port-forward -n tusdi-minikube svc/tusdi-api 8000:8000
kubectl port-forward -n tusdi-minikube svc/tusdi-webui 3000:3000
```

Or use the `minikube-forward` just command to forward all services.
