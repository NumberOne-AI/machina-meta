# Programming Languages Analysis

This document provides a comprehensive analysis of programming languages and file types used across the MachinaMed (machina-meta) workspace.

**Analysis Date:** 2025-12-29
**Repositories Analyzed:** dem2, dem2-infra, dem2-webui, medical-catalog

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 2,158 |
| **Total Lines of Code** | 500,770 |
| **Programming Languages** | 29+ |
| **Repositories** | 4 |

## Language Distribution by Lines of Code

| Language | Files | Lines | % of Total | Repos | Extensions |
|----------|-------|-------|------------|-------|------------|
| **Python** | 817 | 159,136 | 31.8% | dem2, dem2-infra, medical-catalog | `.py` |
| **JSON** | 87 | 136,272 | 27.2% | dem2, dem2-infra, dem2-webui, medical-catalog | `.json` |
| **YAML** | 542 | 118,146 | 23.6% | dem2, dem2-infra, dem2-webui, medical-catalog | `.yaml`, `.yml` |
| **TypeScript (JSX)** | 240 | 24,691 | 4.9% | dem2-infra, dem2-webui | `.tsx` |
| **TypeScript** | 191 | 20,666 | 4.1% | dem2, dem2-infra, dem2-webui, medical-catalog | `.ts` |
| **Markdown** | 126 | 16,044 | 3.2% | dem2, dem2-infra, dem2-webui, medical-catalog | `.md` |
| **Lock File** | 4 | 11,950 | 2.4% | dem2, dem2-infra, dem2-webui, medical-catalog | `.lock` |
| Shell | 28 | 3,388 | 0.7% | dem2, dem2-infra | `.sh` |
| Text | 7 | 1,674 | 0.3% | dem2, dem2-infra, dem2-webui | `.txt` |
| Cypher | 18 | 1,452 | 0.3% | dem2 | `.cypher` |
| Terraform | 6 | 1,344 | 0.3% | dem2-infra | `.tf`, `.tfvars` |
| TOML | 36 | 1,248 | 0.2% | dem2, dem2-infra, medical-catalog | `.toml` |
| CSS | 6 | 832 | 0.2% | dem2-infra, dem2-webui, medical-catalog | `.css` |
| Nix | 2 | 810 | 0.2% | dem2 | `.nix` |
| Makefile | 3 | 782 | 0.2% | dem2, dem2-infra | `Makefile` |
| Svelte | 6 | 764 | 0.2% | medical-catalog | `.svelte` |
| Just | 4 | 584 | 0.1% | dem2, dem2-infra, dem2-webui, medical-catalog | `justfile` |
| Dockerfile | 6 | 264 | 0.1% | dem2, dem2-infra, dem2-webui, medical-catalog | `.dockerfile`, `Dockerfile` |
| Gitignore | 5 | 151 | 0.0% | dem2, dem2-infra, dem2-webui, medical-catalog | `.gitignore` |
| INI | 1 | 147 | 0.0% | dem2 | `.ini` |

## Language Usage by Repository


### dem2 (Backend - Python)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| Python | 675 | 141,539 | Core backend logic, services, API endpoints |
| JSON | 77 | 135,883 | API schemas, config, test data, fixtures |
| YAML | 419 | 99,960 | Configuration, CI/CD, fixtures, data files |
| Markdown | 106 | 10,721 | Documentation, guides, architecture docs |
| Lock File | 1 | 6,397 |  |
| TypeScript | 6 | 3,662 |  |
| Text | 5 | 1,637 |  |
| Cypher | 18 | 1,452 | Neo4j graph database queries |
| TOML | 33 | 1,070 | Python project config (pyproject.toml, config files) |
| Nix | 2 | 810 |  |

**Tech Stack:** Python 3.13, FastAPI, uv, Neo4j, PostgreSQL, Redis, Qdrant

### dem2-infra (Infrastructure - Kubernetes/Terraform)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| YAML | 111 | 5,653 | Kubernetes manifests, ArgoCD configs, Helm charts |
| Shell | 21 | 3,072 | Deployment automation, setup scripts |
| Markdown | 6 | 1,812 | Infrastructure documentation |
| Terraform | 6 | 1,344 | GCP infrastructure as code |
| TypeScript (JSX) | 12 | 1,250 |  |
| Lock File | 1 | 1,196 |  |
| Python | 2 | 874 |  |
| Makefile | 2 | 579 |  |
| TypeScript | 10 | 470 | Build scripts, tooling, automation |
| Config | 2 | 142 |  |

**Tech Stack:** Kubernetes (GKE), ArgoCD, Terraform, Kustomize, GitHub Actions

### dem2-webui (Frontend - TypeScript/React)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| TypeScript (JSX) | 228 | 23,441 | React components, UI logic, pages |
| TypeScript | 170 | 16,169 | Type definitions, utilities, hooks, API clients |
| YAML | 9 | 12,124 | CI/CD, configuration |
| Lock File | 1 | 2,096 |  |
| Markdown | 4 | 1,487 | Documentation, component docs |
| CSS | 4 | 608 | Styling, themes |
| JSON | 5 | 265 | Package config, API schemas, i18n |
| Dockerfile | 2 | 77 |  |
| Gitignore | 1 | 55 |  |
| Text | 1 | 35 |  |

**Tech Stack:** Next.js 15, React 19, TypeScript, pnpm, Biome

### medical-catalog (Catalog Service - Python)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| Python | 140 | 16,723 | Biomarker catalog API, data processing |
| Lock File | 1 | 2,261 |  |
| Markdown | 10 | 2,024 | API documentation, usage guides |
| Svelte | 6 | 764 | Admin UI components |
| YAML | 3 | 409 | Configuration, data schemas |
| TypeScript | 5 | 365 |  |
| Just | 1 | 183 |  |
| CSS | 1 | 167 |  |
| TOML | 2 | 164 |  |
| Dockerfile | 1 | 75 |  |

**Tech Stack:** Python, FastAPI, Qdrant, Svelte

## Language Usage by Repository (Detailed)

This section shows each language used in each repository, with all components using that language.

### dem2

#### Python (675 files, 141,539 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| services/medical-data-storage | 73 | 29,518 |
| services/medical-data-engine | 52 | 20,894 |
| services/medical-agent | 89 | 17,557 |
| services/graph-memory | 73 | 15,799 |
| shared | 110 | 13,376 |
| services/indicators-catalog | 18 | 7,459 |
| pdf_tests | 13 | 7,002 |
| services/medical-sources | 43 | 6,666 |
| services/docproc | 47 | 5,744 |
| packages/medical-types | 31 | 4,034 |
| packages/external | 28 | 3,703 |
| services/file-storage | 21 | 2,406 |
| services/auth | 18 | 1,598 |
| alembic | 13 | 1,283 |
| services/bookmarks | 7 | 1,186 |
| scripts | 1 | 1,077 |
| machina | 12 | 826 |
| services/geocoding | 11 | 604 |
| root | 3 | 456 |
| services/ui-layouts | 7 | 186 |
| services/calendar | 5 | 165 |

#### JSON (77 files, 135,883 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| pdf_tests | 69 | 130,884 |
| root | 4 | 4,797 |
| services/graph-memory | 1 | 91 |
| services/indicators-catalog | 1 | 49 |
| infrastructure | 1 | 36 |
| nix | 1 | 26 |

#### YAML (419 files, 99,960 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| pdf_tests | 360 | 83,972 |
| services/medical-agent | 44 | 12,385 |
| .github | 7 | 1,593 |
| services/medical-data-storage | 1 | 765 |
| services/graph-memory | 1 | 702 |
| infrastructure | 3 | 305 |
| configs | 2 | 214 |
| services/indicators-catalog | 1 | 24 |

#### Markdown (106 files, 10,721 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 8 | 2,678 |
| coding | 7 | 2,087 |
| services/medical-agent | 62 | 2,080 |
| pdf_tests | 5 | 1,470 |
| services/docproc | 4 | 968 |
| services/indicators-catalog | 4 | 763 |
| services/medical-data-engine | 1 | 342 |
| docs | 1 | 151 |
| infrastructure | 1 | 93 |
| .github | 1 | 54 |
| services/geocoding | 1 | 23 |
| packages/medical-types | 1 | 7 |
| shared | 2 | 5 |
| machina | 1 | 0 |
| services/auth | 1 | 0 |
| services/bookmarks | 1 | 0 |
| services/calendar | 1 | 0 |
| services/file-storage | 1 | 0 |
| services/medical-data-storage | 1 | 0 |
| services/medical-sources | 1 | 0 |
| services/ui-layouts | 1 | 0 |

#### Lock File (1 files, 6,397 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 6,397 |

#### TypeScript (6 files, 3,662 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| pdf_tests | 6 | 3,662 |

#### Text (5 files, 1,637 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| pdf_tests | 4 | 1,237 |
| services/indicators-catalog | 1 | 400 |

#### Cypher (18 files, 1,452 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| services/graph-memory | 18 | 1,452 |

#### TOML (33 files, 1,070 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 215 |
| services/indicators-catalog | 2 | 101 |
| services/docproc | 2 | 80 |
| services/medical-agent | 2 | 73 |
| machina | 2 | 69 |
| services/medical-data-engine | 2 | 65 |
| services/geocoding | 2 | 64 |
| services/auth | 2 | 53 |
| services/file-storage | 2 | 50 |
| services/medical-sources | 2 | 42 |
| shared | 1 | 42 |
| services/medical-data-storage | 2 | 41 |
| services/graph-memory | 2 | 37 |
| services/ui-layouts | 2 | 35 |
| services/calendar | 2 | 29 |
| packages/external | 2 | 23 |
| services/bookmarks | 1 | 22 |
| packages/medical-types | 1 | 19 |
| alembic | 1 | 10 |

#### Nix (2 files, 810 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 612 |
| nix | 1 | 198 |

#### Shell (7 files, 316 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| scripts | 4 | 213 |
| infrastructure | 3 | 103 |

#### Just (1 files, 253 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 253 |

#### Makefile (1 files, 203 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 203 |

#### INI (1 files, 147 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 147 |

#### Dockerfile (1 files, 53 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 53 |

#### Gitignore (2 files, 46 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 40 |
| services/medical-agent | 1 | 6 |

#### Dockerignore (1 files, 20 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 20 |

#### Environment (1 files, 18 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 18 |

#### XML (1 files, 2 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| pdf_tests | 1 | 2 |

### dem2-webui

#### TypeScript (JSX) (228 files, 23,441 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| src/components | 190 | 21,037 |
| src/app | 29 | 1,581 |
| src/context | 7 | 521 |
| src/mocks | 1 | 234 |
| src/config | 1 | 68 |

#### TypeScript (170 files, 16,169 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| tests | 33 | 6,767 |
| src/types | 23 | 3,209 |
| src/hooks | 33 | 2,250 |
| src/lib | 34 | 1,663 |
| src/services | 20 | 949 |
| src/store | 12 | 819 |
| src/components | 6 | 238 |
| root | 3 | 187 |
| src/instrumentation-client.ts | 1 | 36 |
| src/app | 3 | 24 |
| src/proxy.ts | 1 | 16 |
| src/instrumentation.ts | 1 | 11 |

#### YAML (9 files, 12,124 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 3 | 11,364 |
| .github | 6 | 760 |

#### Lock File (1 files, 2,096 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 2,096 |

#### Markdown (4 files, 1,487 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 2 | 1,141 |
| tests | 1 | 250 |
| .claude | 1 | 96 |

#### CSS (4 files, 608 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| src/app | 3 | 456 |
| src/styles | 1 | 152 |

#### JSON (5 files, 265 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 5 | 265 |

#### Dockerfile (2 files, 77 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 2 | 77 |

#### Gitignore (1 files, 55 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 55 |

#### Text (1 files, 35 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| tests | 1 | 35 |

#### SCSS (2 files, 21 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| src/components | 2 | 21 |

#### Just (1 files, 20 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 20 |

#### Environment (1 files, 13 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 13 |

#### SVG (5 files, 5 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| public | 5 | 5 |

#### JavaScript (1 files, 5 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 5 |

### medical-catalog

#### Python (140 files, 16,723 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| src | 131 | 14,811 |
| tools | 7 | 1,371 |
| examples | 1 | 331 |
| scripts | 1 | 210 |

#### Lock File (1 files, 2,261 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 2,261 |

#### Markdown (10 files, 2,024 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 6 | 1,304 |
| src | 3 | 526 |
| docs | 1 | 194 |

#### Svelte (6 files, 764 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| frontend | 6 | 764 |

#### YAML (3 files, 409 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| .github | 2 | 389 |
| infra | 1 | 20 |

#### TypeScript (5 files, 365 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| frontend | 5 | 365 |

#### Just (1 files, 183 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 183 |

#### CSS (1 files, 167 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| frontend | 1 | 167 |

#### TOML (2 files, 164 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 96 |
| configs | 1 | 68 |

#### Dockerfile (1 files, 75 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 75 |

#### Dockerignore (1 files, 74 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 74 |

#### JSON (3 files, 60 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| frontend | 2 | 38 |
| snapshots | 1 | 22 |

#### Gitignore (1 files, 42 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 42 |

#### JavaScript (3 files, 33 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| frontend | 3 | 33 |

#### HTML (1 files, 12 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| frontend | 1 | 12 |

### dem2-infra

#### YAML (111 files, 5,653 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| k8s | 98 | 4,588 |
| infrastructure | 9 | 669 |
| .github | 3 | 328 |
| root | 1 | 68 |

#### Shell (21 files, 3,072 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 14 | 1,743 |
| root | 4 | 1,023 |
| scripts | 2 | 234 |
| terraform | 1 | 72 |

#### Markdown (6 files, 1,812 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 4 | 1,047 |
| root | 1 | 585 |
| k8s | 1 | 180 |

#### Terraform (6 files, 1,344 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| terraform | 4 | 1,026 |
| terraform-iam | 2 | 318 |

#### TypeScript (JSX) (12 files, 1,250 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure-manager | 12 | 1,250 |

#### Lock File (1 files, 1,196 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 1,196 |

#### Python (2 files, 874 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 1 | 777 |
| oauth-proxy | 1 | 97 |

#### Makefile (2 files, 579 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 2 | 579 |

#### TypeScript (10 files, 470 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure-manager | 10 | 470 |

#### Config (2 files, 142 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 2 | 142 |

#### Just (1 files, 128 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 128 |

#### Environment (1 files, 67 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 1 | 67 |

#### JSON (2 files, 64 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure-manager | 2 | 64 |

#### Dockerfile (2 files, 59 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure-manager | 1 | 35 |
| oauth-proxy | 1 | 24 |

#### CSS (1 files, 57 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure-manager | 1 | 57 |

#### TOML (1 files, 14 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 14 |

#### JavaScript (1 files, 9 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure-manager | 1 | 9 |

#### Gitignore (1 files, 8 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| root | 1 | 8 |

#### SQL (2 files, 4 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| infrastructure | 2 | 4 |

#### Text (1 files, 2 lines)

| Component | Files | Lines |
|-----------|-------|-------|
| oauth-proxy | 1 | 2 |


## Component Breakdown (All Components)

This section provides a complete breakdown of every language in every component, sorted by lines of code.

| Repository | Component | Language | Files | Lines |
|------------|-----------|----------|-------|-------|
| dem2 | pdf_tests | JSON | 69 | 130,884 |
| dem2 | pdf_tests | YAML | 360 | 83,972 |
| dem2 | services/medical-data-storage | Python | 73 | 29,518 |
| dem2-webui | src/components | TypeScript (JSX) | 190 | 21,037 |
| dem2 | services/medical-data-engine | Python | 52 | 20,894 |
| dem2 | services/medical-agent | Python | 89 | 17,557 |
| dem2 | services/graph-memory | Python | 73 | 15,799 |
| medical-catalog | src | Python | 131 | 14,811 |
| dem2 | shared | Python | 110 | 13,376 |
| dem2 | services/medical-agent | YAML | 44 | 12,385 |
| dem2-webui | root | YAML | 3 | 11,364 |
| dem2 | services/indicators-catalog | Python | 18 | 7,459 |
| dem2 | pdf_tests | Python | 13 | 7,002 |
| dem2-webui | tests | TypeScript | 33 | 6,767 |
| dem2 | services/medical-sources | Python | 43 | 6,666 |
| dem2 | root | Lock File | 1 | 6,397 |
| dem2 | services/docproc | Python | 47 | 5,744 |
| dem2 | root | JSON | 4 | 4,797 |
| dem2-infra | k8s | YAML | 98 | 4,588 |
| dem2 | packages/medical-types | Python | 31 | 4,034 |
| dem2 | packages/external | Python | 28 | 3,703 |
| dem2 | pdf_tests | TypeScript | 6 | 3,662 |
| dem2-webui | src/types | TypeScript | 23 | 3,209 |
| dem2 | root | Markdown | 8 | 2,678 |
| dem2 | services/file-storage | Python | 21 | 2,406 |
| medical-catalog | root | Lock File | 1 | 2,261 |
| dem2-webui | src/hooks | TypeScript | 33 | 2,250 |
| dem2-webui | root | Lock File | 1 | 2,096 |
| dem2 | coding | Markdown | 7 | 2,087 |
| dem2 | services/medical-agent | Markdown | 62 | 2,080 |
| dem2-infra | infrastructure | Shell | 14 | 1,743 |
| dem2-webui | src/lib | TypeScript | 34 | 1,663 |
| dem2 | services/auth | Python | 18 | 1,598 |
| dem2 | .github | YAML | 7 | 1,593 |
| dem2-webui | src/app | TypeScript (JSX) | 29 | 1,581 |
| dem2 | pdf_tests | Markdown | 5 | 1,470 |
| dem2 | services/graph-memory | Cypher | 18 | 1,452 |
| medical-catalog | tools | Python | 7 | 1,371 |
| medical-catalog | root | Markdown | 6 | 1,304 |
| dem2 | alembic | Python | 13 | 1,283 |
| dem2-infra | infrastructure-manager | TypeScript (JSX) | 12 | 1,250 |
| dem2 | pdf_tests | Text | 4 | 1,237 |
| dem2-infra | root | Lock File | 1 | 1,196 |
| dem2 | services/bookmarks | Python | 7 | 1,186 |
| dem2-webui | root | Markdown | 2 | 1,141 |
| dem2 | scripts | Python | 1 | 1,077 |
| dem2-infra | infrastructure | Markdown | 4 | 1,047 |
| dem2-infra | terraform | Terraform | 4 | 1,026 |
| dem2-infra | root | Shell | 4 | 1,023 |
| dem2 | services/docproc | Markdown | 4 | 968 |
| dem2-webui | src/services | TypeScript | 20 | 949 |
| dem2 | machina | Python | 12 | 826 |
| dem2-webui | src/store | TypeScript | 12 | 819 |
| dem2-infra | infrastructure | Python | 1 | 777 |
| dem2 | services/medical-data-storage | YAML | 1 | 765 |
| medical-catalog | frontend | Svelte | 6 | 764 |
| dem2 | services/indicators-catalog | Markdown | 4 | 763 |
| dem2-webui | .github | YAML | 6 | 760 |
| dem2 | services/graph-memory | YAML | 1 | 702 |
| dem2-infra | infrastructure | YAML | 9 | 669 |
| dem2 | root | Nix | 1 | 612 |
| dem2 | services/geocoding | Python | 11 | 604 |
| dem2-infra | root | Markdown | 1 | 585 |
| dem2-infra | infrastructure | Makefile | 2 | 579 |
| medical-catalog | src | Markdown | 3 | 526 |
| dem2-webui | src/context | TypeScript (JSX) | 7 | 521 |
| dem2-infra | infrastructure-manager | TypeScript | 10 | 470 |
| dem2-webui | src/app | CSS | 3 | 456 |
| dem2 | root | Python | 3 | 456 |
| dem2 | services/indicators-catalog | Text | 1 | 400 |
| medical-catalog | .github | YAML | 2 | 389 |
| medical-catalog | frontend | TypeScript | 5 | 365 |
| dem2 | services/medical-data-engine | Markdown | 1 | 342 |
| medical-catalog | examples | Python | 1 | 331 |
| dem2-infra | .github | YAML | 3 | 328 |
| dem2-infra | terraform-iam | Terraform | 2 | 318 |
| dem2 | infrastructure | YAML | 3 | 305 |
| dem2-webui | root | JSON | 5 | 265 |
| dem2 | root | Just | 1 | 253 |
| dem2-webui | tests | Markdown | 1 | 250 |
| dem2-webui | src/components | TypeScript | 6 | 238 |
| dem2-infra | scripts | Shell | 2 | 234 |
| dem2-webui | src/mocks | TypeScript (JSX) | 1 | 234 |
| dem2 | root | TOML | 1 | 215 |
| dem2 | configs | YAML | 2 | 214 |
| dem2 | scripts | Shell | 4 | 213 |
| medical-catalog | scripts | Python | 1 | 210 |
| dem2 | root | Makefile | 1 | 203 |
| dem2 | nix | Nix | 1 | 198 |
| medical-catalog | docs | Markdown | 1 | 194 |
| dem2-webui | root | TypeScript | 3 | 187 |
| dem2 | services/ui-layouts | Python | 7 | 186 |
| medical-catalog | root | Just | 1 | 183 |
| dem2-infra | k8s | Markdown | 1 | 180 |
| medical-catalog | frontend | CSS | 1 | 167 |
| dem2 | services/calendar | Python | 5 | 165 |
| dem2-webui | src/styles | CSS | 1 | 152 |
| dem2 | docs | Markdown | 1 | 151 |
| dem2 | root | INI | 1 | 147 |
| dem2-infra | infrastructure | Config | 2 | 142 |
| dem2-infra | root | Just | 1 | 128 |
| dem2 | infrastructure | Shell | 3 | 103 |
| dem2 | services/indicators-catalog | TOML | 2 | 101 |
| dem2-infra | oauth-proxy | Python | 1 | 97 |
| dem2-webui | .claude | Markdown | 1 | 96 |
| medical-catalog | root | TOML | 1 | 96 |
| dem2 | infrastructure | Markdown | 1 | 93 |
| dem2 | services/graph-memory | JSON | 1 | 91 |
| dem2 | services/docproc | TOML | 2 | 80 |
| dem2-webui | root | Dockerfile | 2 | 77 |
| medical-catalog | root | Dockerfile | 1 | 75 |
| medical-catalog | root | Dockerignore | 1 | 74 |
| dem2 | services/medical-agent | TOML | 2 | 73 |
| dem2-infra | terraform | Shell | 1 | 72 |
| dem2 | machina | TOML | 2 | 69 |
| dem2-infra | root | YAML | 1 | 68 |
| dem2-webui | src/config | TypeScript (JSX) | 1 | 68 |
| medical-catalog | configs | TOML | 1 | 68 |
| dem2-infra | infrastructure | Environment | 1 | 67 |
| dem2 | services/medical-data-engine | TOML | 2 | 65 |
| dem2-infra | infrastructure-manager | JSON | 2 | 64 |
| dem2 | services/geocoding | TOML | 2 | 64 |
| dem2-infra | infrastructure-manager | CSS | 1 | 57 |
| dem2-webui | root | Gitignore | 1 | 55 |
| dem2 | .github | Markdown | 1 | 54 |
| dem2 | root | Dockerfile | 1 | 53 |
| dem2 | services/auth | TOML | 2 | 53 |
| dem2 | services/file-storage | TOML | 2 | 50 |
| dem2 | services/indicators-catalog | JSON | 1 | 49 |
| dem2 | services/medical-sources | TOML | 2 | 42 |
| dem2 | shared | TOML | 1 | 42 |
| medical-catalog | root | Gitignore | 1 | 42 |
| dem2 | services/medical-data-storage | TOML | 2 | 41 |
| dem2 | root | Gitignore | 1 | 40 |
| medical-catalog | frontend | JSON | 2 | 38 |
| dem2 | services/graph-memory | TOML | 2 | 37 |
| dem2-webui | src/instrumentation-client.ts | TypeScript | 1 | 36 |
| dem2 | infrastructure | JSON | 1 | 36 |
| dem2-infra | infrastructure-manager | Dockerfile | 1 | 35 |
| dem2-webui | tests | Text | 1 | 35 |
| dem2 | services/ui-layouts | TOML | 2 | 35 |
| medical-catalog | frontend | JavaScript | 3 | 33 |
| dem2 | services/calendar | TOML | 2 | 29 |
| dem2 | nix | JSON | 1 | 26 |
| dem2-infra | oauth-proxy | Dockerfile | 1 | 24 |
| dem2-webui | src/app | TypeScript | 3 | 24 |
| dem2 | services/indicators-catalog | YAML | 1 | 24 |
| dem2 | packages/external | TOML | 2 | 23 |
| dem2 | services/geocoding | Markdown | 1 | 23 |
| dem2 | services/bookmarks | TOML | 1 | 22 |
| medical-catalog | snapshots | JSON | 1 | 22 |
| dem2-webui | src/components | SCSS | 2 | 21 |
| dem2-webui | root | Just | 1 | 20 |
| dem2 | root | Dockerignore | 1 | 20 |
| medical-catalog | infra | YAML | 1 | 20 |
| dem2 | packages/medical-types | TOML | 1 | 19 |
| dem2 | root | Environment | 1 | 18 |
| dem2-webui | src/proxy.ts | TypeScript | 1 | 16 |
| dem2-infra | root | TOML | 1 | 14 |
| dem2-webui | root | Environment | 1 | 13 |
| medical-catalog | frontend | HTML | 1 | 12 |
| dem2-webui | src/instrumentation.ts | TypeScript | 1 | 11 |
| dem2 | alembic | TOML | 1 | 10 |
| dem2-infra | infrastructure-manager | JavaScript | 1 | 9 |
| dem2-infra | root | Gitignore | 1 | 8 |
| dem2 | packages/medical-types | Markdown | 1 | 7 |
| dem2 | services/medical-agent | Gitignore | 1 | 6 |
| dem2-webui | public | SVG | 5 | 5 |
| dem2-webui | root | JavaScript | 1 | 5 |
| dem2 | shared | Markdown | 2 | 5 |
| dem2-infra | infrastructure | SQL | 2 | 4 |
| dem2-infra | oauth-proxy | Text | 1 | 2 |
| dem2 | pdf_tests | XML | 1 | 2 |
| dem2 | machina | Markdown | 1 | 0 |
| dem2 | services/auth | Markdown | 1 | 0 |
| dem2 | services/bookmarks | Markdown | 1 | 0 |
| dem2 | services/calendar | Markdown | 1 | 0 |
| dem2 | services/file-storage | Markdown | 1 | 0 |
| dem2 | services/medical-data-storage | Markdown | 1 | 0 |
| dem2 | services/medical-sources | Markdown | 1 | 0 |
| dem2 | services/ui-layouts | Markdown | 1 | 0 |

## Key Insights

### Language Breakdown
1. **Python** with 159,136 lines (31.8%)
2. **JSON** with 136,272 lines (27.2%)
3. **YAML** with 118,146 lines (23.6%)

**Configuration as Code** (JSON + YAML): 254,418 lines (50.8%)
**TypeScript** (TS + TSX): 45,357 lines (9.1%)

### Code Organization
- **Microservices Architecture**: Each repo is independently deployable
- **Type Safety**: Heavy use of Python type hints, TypeScript, Pydantic schemas
- **Configuration**: Extensive YAML for configs, CI/CD, fixtures
- **Documentation**: Comprehensive Markdown documentation

### Technology Patterns
- **Backend**: Python 3.13 + FastAPI (async/await patterns)
- **Frontend**: Next.js 15 + React 19 (App Router, Server Components)
- **Database**: Neo4j (Cypher), PostgreSQL, Qdrant (vector)
- **DevOps**: Kubernetes, ArgoCD, GitHub Actions
- **Package Management**: uv (Python), pnpm (Node.js)
- **Task Runners**: just, make

### Notable Technologies
| Technology | Purpose | Files |
|------------|---------|-------|
| **Cypher** | Neo4j graph queries | 18 files, 1,452 lines |
| **Terraform** | GCP infrastructure | 6 files, 1,344 lines |
| **Svelte** | Catalog admin UI | 6 files, 764 lines |
| **Nix** | Reproducible dev environments | 2 files, 810 lines |

## File Type Distribution

### Configuration (51.1% of lines)
- JSON: 136,272 lines
- YAML: 118,146 lines
- TOML: 1,248 lines

### Source Code (41.7% of lines)
- Python: 159,136 lines
- TypeScript (JSX): 24,691 lines
- TypeScript: 20,666 lines
- Shell: 3,388 lines
- Svelte: 764 lines
- JavaScript: 47 lines

### Documentation (3.5% of lines)
- Markdown: 16,044 lines
- Text: 1,674 lines

### Data (2.4% of lines)

### Infrastructure (0.6% of lines)
- Terraform: 1,344 lines
- Makefile: 782 lines
- Just: 584 lines
- Dockerfile: 264 lines

### Database (0.3% of lines)
- Cypher: 1,452 lines
- SQL: 4 lines

### Other (0.2% of lines)

### Styling (0.2% of lines)
- CSS: 832 lines
- SCSS: 21 lines

## Development Tools

### Build & Task Runners
- **just** - Modern task runner (justfiles)
- **make** - Traditional build tool (Makefiles)
- **pnpm** - Fast Node.js package manager
- **uv** - Fast Python package manager

### Linting & Formatting
- **Python**: ruff (linting), mypy (type checking)
- **TypeScript**: biome (linting + formatting)

### Testing
- **Python**: pytest
- **TypeScript**: Jest, Vitest

### CI/CD
- **GitHub Actions** - Primary CI/CD platform
- **ArgoCD** - GitOps continuous delivery

## Repository Health

### Code Quality Indicators
✅ **Extensive Type Coverage**
- Python: Type hints + Pydantic models
- TypeScript: Strict mode enabled

✅ **Comprehensive Documentation**
- Markdown documentation throughout
- Per-repo CLAUDE.md for AI assistant guidance
- API documentation (OpenAPI/Swagger)

✅ **Modern Tooling**
- Fast package managers (uv, pnpm)
- Modern linters (ruff, biome)
- Container-based development

✅ **Infrastructure as Code**
- Kubernetes manifests
- Terraform for cloud resources
- Docker for containerization

### Areas of Focus
- **Backend**: Python microservices with FastAPI
- **Frontend**: Next.js with TypeScript and React 19
- **Data**: Neo4j graph database with Cypher queries
- **DevOps**: Kubernetes with ArgoCD GitOps

## File Size Analysis
- **Python files**: Average 195 lines per file
- **TypeScript files**: Average 108 lines per file
- **TypeScript (JSX) files**: Average 103 lines per file

## Comparison to Industry Standards

| Metric | machina-meta | Industry Typical |
|--------|-------------|------------------|
| Backend Language | Python 3.13 | ✅ Modern (Python 3.10+) |
| Frontend Language | TypeScript | ✅ Industry standard |
| Frontend Framework | Next.js 15 | ✅ Cutting edge |
| Database | Neo4j + PostgreSQL | ✅ Multi-model approach |
| Container Orchestration | Kubernetes | ✅ Industry standard |
| CI/CD | GitHub Actions + ArgoCD | ✅ Modern GitOps |
| Package Management | uv + pnpm | ✅ Fast modern tools |
| Lines per Python file | 195 avg | ✅ Good (200-400 typical) |
| Lines per TS file | 108 avg | ✅ Excellent (<200 ideal) |

## Conclusion

The MachinaMed codebase demonstrates:
- ✅ **Modern Technology Stack** - Latest versions of Python, TypeScript, Next.js
- ✅ **Strong Type Safety** - Extensive use of type systems
- ✅ **Cloud-Native Architecture** - Kubernetes, microservices, containers
- ✅ **Comprehensive Documentation** - Extensive Markdown documentation
- ✅ **Infrastructure as Code** - Declarative configs for reproducibility
- ✅ **Developer Experience** - Fast tooling (uv, pnpm), clear organization

**Total Codebase Size:** 500,770 lines across 2,158 files in 4 repositories.
