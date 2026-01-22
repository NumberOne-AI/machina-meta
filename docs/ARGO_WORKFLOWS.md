# Argo Workflows

Research and implementation notes for using Argo Workflows to orchestrate the document processing pipeline.

## Overview

Argo Workflows is a Kubernetes-native workflow engine for orchestrating parallel jobs. It's implemented as a Kubernetes CRD (Custom Resource Definition) and is a CNCF graduated project.

**Key Constraint**: Argo Workflows requires Kubernetes - it cannot run in plain docker-compose.

## Architecture

### Core Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Workflow Controller** | Reconciles workflows, processes queue | 9090 (metrics) |
| **Argo Server** | HTTP API + Web UI | 2746 |
| **MinIO** (optional) | Artifact storage between steps | 9000 |
| **Postgres/MySQL** (optional) | Workflow archive for history | 5432/3306 |

### Pod Structure

Each workflow step spawns a Pod with 3 containers:

```
┌─────────────────────────────────────────┐
│              Workflow Pod               │
├─────────────┬─────────────┬─────────────┤
│    init     │    main     │    wait     │
│ (artifacts) │ (your code) │  (cleanup)  │
└─────────────┴─────────────┴─────────────┘
```

- **init**: InitContainer that fetches artifacts and parameters
- **main**: Runs user-specified image with `argoexec` utility
- **wait**: Saves parameters and artifacts after completion

### Namespace Organization

```
argo namespace:
  - workflow-controller (Deployment)
  - argo-server (Deployment)

workflows namespace (configurable):
  - Workflow CRDs
  - Generated Pods
```

## Local Development Options

### Option 1: K3D (Recommended)

K3D runs lightweight K3s Kubernetes in Docker containers. Fastest setup for local development.

```bash
# Install k3d
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# Create cluster with port mapping for Argo UI
k3d cluster create argo-local --port "2746:30746@server:0"

# Install Argo Workflows (quick-start)
kubectl create namespace argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/latest/download/quick-start-minimal.yaml

# Wait for pods to be ready
kubectl -n argo wait --for=condition=Ready pods --all --timeout=300s

# Access UI (in separate terminal)
kubectl -n argo port-forward svc/argo-server 2746:2746

# Open https://localhost:2746
```

### Option 2: Docker Desktop with Kubernetes

1. Open Docker Desktop preferences
2. Increase memory to 12GB+
3. Enable Kubernetes
4. Install Argo as above

### Option 3: Minikube

```bash
# Start minikube with sufficient resources
minikube start --memory=8192 --cpus=4

# Install Argo
kubectl create namespace argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/latest/download/quick-start-minimal.yaml
```

### Integration with Existing docker-compose Stack

K3D clusters run as Docker containers and can share networks with docker-compose services:

```bash
# Create K3D cluster on same Docker network as machina services
k3d cluster create argo-local \
  --network machina-meta_default \
  --port "2746:30746@server:0"

# Now Argo workflows can access:
# - neo4j:7687 (graph database)
# - postgres:5432 (relational database)
# - redis:6379 (cache/pubsub)
# - qdrant:6333 (vector search)
```

## Core Concepts

### Workflow

A Workflow is a Kubernetes resource that defines a job to run:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: main
  templates:
    - name: main
      container:
        image: alpine
        command: [echo, "Hello World"]
```

### WorkflowTemplate

Reusable workflow definitions:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: docproc-pipeline
spec:
  entrypoint: process-document
  arguments:
    parameters:
      - name: document-id
  templates:
    - name: process-document
      dag:
        tasks:
          - name: extract
            template: extract-pages
          - name: enrich
            template: enrich-biomarkers
            dependencies: [extract]
          - name: store
            template: store-graph
            dependencies: [enrich]
```

### DAG (Directed Acyclic Graph)

Define task dependencies:

```yaml
templates:
  - name: pipeline
    dag:
      tasks:
        - name: A
          template: task-a
        - name: B
          template: task-b
          dependencies: [A]
        - name: C
          template: task-c
          dependencies: [A]
        - name: D
          template: task-d
          dependencies: [B, C]
```

```
    A
   / \
  B   C
   \ /
    D
```

### Artifacts

Pass data between steps via S3/GCS/MinIO:

```yaml
templates:
  - name: generate
    container:
      image: alpine
      command: [sh, -c, "echo hello > /tmp/message.txt"]
    outputs:
      artifacts:
        - name: message
          path: /tmp/message.txt

  - name: consume
    inputs:
      artifacts:
        - name: message
          path: /tmp/message.txt
    container:
      image: alpine
      command: [cat, /tmp/message.txt]
```

### Parameters

Pass values between steps:

```yaml
templates:
  - name: generate
    container:
      image: alpine
      command: [sh, -c, "echo -n 42 > /tmp/result.txt"]
    outputs:
      parameters:
        - name: result
          valueFrom:
            path: /tmp/result.txt

  - name: consume
    inputs:
      parameters:
        - name: value
    container:
      image: alpine
      command: [echo, "{{inputs.parameters.value}}"]
```

## Document Processing Pipeline Design

### Proposed Workflow Structure

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: docproc-pipeline
  namespace: argo
spec:
  entrypoint: process-document

  arguments:
    parameters:
      - name: document-id
        description: "UUID of uploaded document"
      - name: file-path
        description: "GCS path to document file"
      - name: patient-id
        description: "Patient context ID"
      - name: user-id
        description: "User who uploaded document"

  templates:
    # Main DAG orchestrating the pipeline
    - name: process-document
      dag:
        tasks:
          - name: validate
            template: validate-document
            arguments:
              parameters:
                - name: document-id
                  value: "{{workflow.parameters.document-id}}"

          - name: render-pages
            template: render-pages-parallel
            dependencies: [validate]
            arguments:
              artifacts:
                - name: document
                  from: "{{tasks.validate.outputs.artifacts.document}}"

          - name: extract-pages
            template: extract-pages-parallel
            dependencies: [render-pages]
            arguments:
              parameters:
                - name: page-count
                  value: "{{tasks.render-pages.outputs.parameters.page-count}}"
              artifacts:
                - name: pages
                  from: "{{tasks.render-pages.outputs.artifacts.pages}}"

          - name: aggregate
            template: aggregate-extractions
            dependencies: [extract-pages]
            arguments:
              artifacts:
                - name: extractions
                  from: "{{tasks.extract-pages.outputs.artifacts.extractions}}"

          - name: enrich
            template: enrich-biomarkers
            dependencies: [aggregate]
            arguments:
              artifacts:
                - name: biomarkers
                  from: "{{tasks.aggregate.outputs.artifacts.biomarkers}}"

          - name: store
            template: store-to-graph
            dependencies: [enrich]
            arguments:
              parameters:
                - name: patient-id
                  value: "{{workflow.parameters.patient-id}}"
              artifacts:
                - name: enriched-data
                  from: "{{tasks.enrich.outputs.artifacts.enriched-data}}"

    # Parallel page rendering using withSequence
    - name: render-pages-parallel
      inputs:
        artifacts:
          - name: document
            path: /tmp/document.pdf
      steps:
        - - name: count-pages
            template: count-pages
            arguments:
              artifacts:
                - name: document
                  from: "{{inputs.artifacts.document}}"
        - - name: render-page
            template: render-single-page
            arguments:
              parameters:
                - name: page-num
                  value: "{{item}}"
              artifacts:
                - name: document
                  from: "{{inputs.artifacts.document}}"
            withSequence:
              count: "{{steps.count-pages.outputs.parameters.count}}"

    # Parallel Gemini Vision extraction
    - name: extract-pages-parallel
      inputs:
        parameters:
          - name: page-count
        artifacts:
          - name: pages
            path: /tmp/pages/
      steps:
        - - name: extract-page
            template: gemini-extract
            arguments:
              parameters:
                - name: page-num
                  value: "{{item}}"
            withSequence:
              count: "{{inputs.parameters.page-count}}"

    # Individual templates (container definitions)
    - name: validate-document
      inputs:
        parameters:
          - name: document-id
      container:
        image: gcr.io/PROJECT/docproc-worker:latest
        command: [python, -m, docproc.validate]
        args: ["--document-id", "{{inputs.parameters.document-id}}"]
      outputs:
        artifacts:
          - name: document
            path: /tmp/document.pdf

    - name: gemini-extract
      inputs:
        parameters:
          - name: page-num
        artifacts:
          - name: page-image
            path: /tmp/page.png
      container:
        image: gcr.io/PROJECT/docproc-worker:latest
        command: [python, -m, docproc.extract]
        args: ["--page", "{{inputs.parameters.page-num}}"]
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
      outputs:
        artifacts:
          - name: extraction
            path: /tmp/extraction.json

    - name: enrich-biomarkers
      inputs:
        artifacts:
          - name: biomarkers
            path: /tmp/biomarkers.json
      container:
        image: gcr.io/PROJECT/docproc-worker:latest
        command: [python, -m, docproc.enrich]
        env:
          - name: MEDICAL_CATALOG_URL
            value: "http://medical-catalog:8001"
      outputs:
        artifacts:
          - name: enriched-data
            path: /tmp/enriched.json

    - name: store-to-graph
      inputs:
        parameters:
          - name: patient-id
        artifacts:
          - name: enriched-data
            path: /tmp/enriched.json
      container:
        image: gcr.io/PROJECT/docproc-worker:latest
        command: [python, -m, docproc.store]
        args: ["--patient-id", "{{inputs.parameters.patient-id}}"]
        env:
          - name: NEO4J_URI
            value: "bolt://neo4j:7687"
```

### Pipeline Stages

```
┌──────────────┐
│   Upload     │ (existing: FastAPI endpoint)
└──────┬───────┘
       │ triggers workflow
       ▼
┌──────────────┐
│   Validate   │ Check file type, size, corruption
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Render Pages │ PDF → PNG (parallel per page)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Extract    │ Gemini Vision (parallel per page)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Aggregate   │ Combine page extractions
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Enrich     │ Medical catalog lookup
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Store     │ Neo4j graph storage
└──────────────┘
```

## Comparison with Current Architecture

| Aspect | Current (Celery) | Proposed (Argo) |
|--------|------------------|-----------------|
| Orchestration | Task queue | DAG workflow |
| Parallelism | Worker pool | Pod per task |
| Retry logic | Per-task config | Workflow-level |
| Monitoring | Flower UI | Argo UI |
| Artifacts | Redis/filesystem | S3/GCS/MinIO |
| Scaling | Add workers | K8s autoscaling |
| Local dev | docker-compose | K3D + docker-compose |

## GKE Installation

For production deployment on GKE:

```bash
# Create namespace
kubectl create namespace argo

# Install with Helm (recommended for production)
helm repo add argo https://argoproj.github.io/argo-helm
helm install argo-workflows argo/argo-workflows \
  --namespace argo \
  --set server.serviceType=ClusterIP \
  --set controller.workflowNamespaces="{argo,tusdi-dev,tusdi-prod}"

# Configure artifact repository (GCS)
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: artifact-repositories
  namespace: argo
data:
  default-v1: |
    archiveLogs: true
    gcs:
      bucket: machina-argo-artifacts
      keyFormat: "{{workflow.namespace}}/{{workflow.name}}/{{pod.name}}"
EOF

# Set up Ingress for UI (via Istio/nginx)
kubectl apply -f argo-ingress.yaml
```

## Event Triggers (Argo Events)

Trigger workflows from HTTP webhooks or message queues:

```yaml
# EventSource: Listen for HTTP webhooks
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: docproc-webhook
spec:
  webhook:
    document-uploaded:
      port: "12000"
      endpoint: /document
      method: POST

---
# Sensor: Trigger workflow on event
apiVersion: argoproj.io/v1alpha1
kind: Sensor
metadata:
  name: docproc-sensor
spec:
  dependencies:
    - name: document-uploaded
      eventSourceName: docproc-webhook
      eventName: document-uploaded
  triggers:
    - template:
        name: docproc-trigger
        k8s:
          operation: create
          source:
            resource:
              apiVersion: argoproj.io/v1alpha1
              kind: Workflow
              metadata:
                generateName: docproc-
              spec:
                workflowTemplateRef:
                  name: docproc-pipeline
                arguments:
                  parameters:
                    - name: document-id
                      value: "{{.Input.body.document_id}}"
```

## Monitoring & Observability

### Argo UI

Access at `https://localhost:2746` (local) or via Ingress (production).

Features:
- Real-time workflow visualization
- Log streaming per step
- Artifact browsing
- Retry/resubmit workflows

### Prometheus Metrics

Workflow Controller exposes metrics at `:9090/metrics`:

```
argo_workflows_count{status="Running"}
argo_workflows_count{status="Succeeded"}
argo_workflows_count{status="Failed"}
argo_workflow_duration_seconds
argo_pods_count
```

### Grafana Dashboard

Import Argo Workflows dashboard: ID `13927`

## Security Considerations

### RBAC

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: docproc-workflow-role
  namespace: argo
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["argoproj.io"]
    resources: ["workflows", "workflowtemplates"]
    verbs: ["get", "list", "watch", "create"]
```

### Service Account

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: docproc-workflow-sa
  namespace: argo
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: docproc-workflow-binding
  namespace: argo
subjects:
  - kind: ServiceAccount
    name: docproc-workflow-sa
roleRef:
  kind: Role
  name: docproc-workflow-role
  apiGroup: rbac.authorization.k8s.io
```

### Secrets for External Services

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: docproc-secrets
  namespace: argo
type: Opaque
stringData:
  GEMINI_API_KEY: "..."
  NEO4J_PASSWORD: "..."
  POSTGRES_PASSWORD: "..."
```

## Alternatives Considered

If Kubernetes overhead is too high for local development:

| Engine | docker-compose | DAG Support | UI | Notes |
|--------|---------------|-------------|-----|-------|
| **Temporal** | Yes | Yes | Yes | Excellent for long-running workflows |
| **Prefect** | Yes | Yes | Yes | Python-native, good DX |
| **Dagster** | Yes | Yes | Yes | Strong data pipeline focus |
| **Celery** | Yes | Canvas | Flower | Current solution, simpler |

## Next Steps

1. [ ] Set up K3D cluster for local Argo testing
2. [ ] Create proof-of-concept WorkflowTemplate for single document
3. [ ] Test artifact passing with MinIO
4. [ ] Benchmark parallel extraction vs current sequential
5. [ ] Design migration path from Celery
6. [ ] Add Argo Workflows Helm chart to dem2-infra

## References

- [Argo Workflows Documentation](https://argo-workflows.readthedocs.io/en/latest/)
- [Running Locally](https://argo-workflows.readthedocs.io/en/latest/running-locally/)
- [Architecture](https://argo-workflows.readthedocs.io/en/latest/architecture/)
- [GitHub Repository](https://github.com/argoproj/argo-workflows)
- [Argo Events](https://argoproj.github.io/argo-events/)

---

*Last Updated: 2026-01-21*
*Related TODO: "Research Argo Workflows and install on GKE", "Use Argo Workflows for parallel document processing pipeline"*
