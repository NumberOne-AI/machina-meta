# PROBLEMS

This file tracks known problems, issues, and challenges related to GKE/GCP operations and the gcloud-admin container.
Problems are observations that need investigation before becoming actionable TODO items.

## ⚠️ CRITICAL: Immediate Commit Requirement

**Changes to this file (and TODO.md) MUST be committed to git immediately after modification.**

Do not batch changes to PROBLEMS.md or TODO.md with other work.

## Relationship to TODO.md

```
PROBLEMS.md                          TODO.md
┌─────────────────┐                 ┌─────────────────┐
│ [OPEN] Problem  │ ──investigate──▶│ [PROPOSED] Task │
│                 │                 │                 │
│ [INVESTIGATING] │ ──solution────▶ │ [STARTED] Task  │
│                 │                 │                 │
│ [SOLVED]        │ ◀──completed─── │ [DONE] Task     │
└─────────────────┘                 └─────────────────┘
```

- **OPEN** - Needs investigation to understand root cause
- **INVESTIGATING** - Active analysis or proposed solutions exist
- **SOLVED** - Completed TODO items address this problem
- **WONT_FIX** - Acknowledged but intentionally not addressed

## Problem Format

Each problem includes:
- State: `[OPEN]`, `[INVESTIGATING]`, `[SOLVED]`, or `[WONT_FIX]`
- Severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- Added: Date problem was identified
- Related TODOs: Links to TODO.md items addressing this problem
- Observations: Evidence or symptoms of the problem

---

## Container Issues

### Authentication

- [SOLVED] **Host kubeconfig uses deprecated legacy GCP auth**
  - Severity: MEDIUM | Added: 2025-12-18 | Solved: 2025-12-18
  - Host-generated kubeconfig uses `auth-provider: gcp` (deprecated)
  - Container kubectl rejects legacy auth in versions 1.26+
  - Solution: Regenerate credentials inside container with `gcloud container clusters get-credentials`
  - The container uses exec-based `gke-gcloud-auth-plugin` correctly

- [WONT_FIX] **Cannot add gke-gcloud-auth-plugin to host Nix shell**
  - Severity: LOW | Added: 2025-12-18
  - nixpkgs `google-cloud-sdk.withExtraComponents` fails due to bundled-python tcl/tk dependency
  - See: https://github.com/NixOS/nixpkgs/issues/211689
  - Workaround: Use this container instead of host tools

---

## Cluster Issues

### Resource Constraints

- [OPEN] **Preview environments consuming significant resources**
  - Severity: MEDIUM | Added: 2025-12-18
  - Multiple preview namespaces (tusdi-preview-*) running
  - Each preview has: postgres, neo4j, qdrant, redis, api, webui
  - Some previews appear stale (21+ days old)
  - Observations:
    - `tusdi-preview-69`: 21d old
    - `tusdi-preview-70`: 21d old
    - `tusdi-preview-83`: 2d old
    - `tusdi-preview-84`: 2d old
    - `tusdi-preview-85`: 24h old
    - `tusdi-preview-86`: 20h old
    - `tusdi-preview-87`: 18h old
    - `tusdi-preview-88`: 164m old (has issues)
  - Potential solutions:
    - Automated cleanup of old previews
    - TTL-based expiration
    - Manual cleanup script

- [OPEN] **tusdi-preview-88 has failing pods**
  - Severity: LOW | Added: 2025-12-18
  - neo4j-0: Pending
  - qdrant-0: Pending
  - tusdi-api: CrashLoopBackOff (32 restarts)
  - Likely cause: Resource constraints or configuration issue
  - Action: Investigate or delete preview

### Node Capacity

- [OPEN] **CPU limits exceed node capacity**
  - Severity: LOW | Added: 2025-12-18
  - `kubectl resource-capacity` shows:
    - Total CPU limits: 123% of capacity
    - Node `7ba3`: 111% CPU limits
    - Node `y5j3`: 135% CPU limits
  - Risk: Pod eviction under load
  - Observations: Limits are soft caps, requests (28%) are reasonable

---

## Deployment Issues

### ArgoCD

(No current issues)

### CI/CD

(No current issues)

---

## Network Issues

(No current issues)

---

## Historical / Resolved

(Move resolved problems here to keep active section clean)
