# Programming Languages Analysis

This document provides a comprehensive analysis of programming languages and file types used across the MachinaMed (machina-meta) workspace.

**Analysis Date:** 2025-12-26
**Repositories Analyzed:** dem2, dem2-webui, dem2-infra, medical-catalog

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 2,158 |
| **Total Lines of Code** | 543,320 |
| **Programming Languages** | 48+ |
| **Repositories** | 4 |

## Language Distribution by Lines of Code

| Language | Files | Lines | % of Total | Repos | Extensions |
|----------|-------|-------|------------|-------|------------|
| **Python** | 782 | 159,136 | 29.3% | dem2, dem2-infra, medical-catalog | `.py` |
| **JSON** | 86 | 133,321 | 24.5% | dem2, dem2-infra, dem2-webui, medical-catalog | `.json` |
| **YAML** | 542 | 118,079 | 21.7% | dem2, dem2-infra, dem2-webui, medical-catalog | `.yaml`, `.yml` |
| **TypeScript (JSX)** | 239 | 24,679 | 4.5% | dem2-infra, dem2-webui | `.tsx` |
| **TypeScript** | 191 | 20,656 | 3.8% | dem2, dem2-infra, dem2-webui, medical-catalog | `.ts` |
| **Markdown** | 116 | 16,036 | 3.0% | dem2, dem2-infra, dem2-webui, medical-catalog | `.md` |
| **Lock Files** | 4 | 11,950 | 2.2% | dem2, dem2-infra, dem2-webui, medical-catalog | `.lock` |
| **Shell** | 28 | 3,372 | 0.6% | dem2, dem2-infra | `.sh` |
| **Text Files** | 22 | 2,050 | 0.4% | dem2, dem2-infra, dem2-webui | `.txt` |
| **Cypher** | 18 | 1,452 | 0.3% | dem2 | `.cypher` |
| **Terraform** | 5 | 1,321 | 0.2% | dem2-infra | `.tf` |
| **TOML** | 35 | 1,241 | 0.2% | dem2, dem2-infra, medical-catalog | `.toml` |
| **CSS** | 6 | 831 | 0.2% | dem2-infra, dem2-webui, medical-catalog | `.css` |
| **Nix** | 2 | 810 | 0.1% | dem2 | `.nix` |
| **Makefile** | 3 | 780 | 0.1% | dem2, dem2-infra | `Makefile` |
| **Svelte** | 6 | 764 | 0.1% | medical-catalog | `.svelte` |
| **Just** | 4 | 584 | 0.1% | dem2, dem2-infra, dem2-webui, medical-catalog | `justfile` |
| **Dockerfile** | 6 | 263 | <0.1% | dem2, dem2-infra, dem2-webui, medical-catalog | `Dockerfile` |
| **JavaScript** | 3 | 33 | <0.1% | medical-catalog | `.js` |

## Language Usage by Repository

### dem2 (Backend - Python)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| Python | 660 | ~140,000 | Core backend logic, services, API endpoints |
| YAML | 310 | ~60,000 | Configuration, CI/CD, fixtures |
| JSON | 45 | ~50,000 | API schemas, config, test data |
| Cypher | 18 | 1,452 | Neo4j graph queries |
| Markdown | 45 | ~8,000 | Documentation |
| Shell | 15 | ~2,000 | Deployment, utility scripts |
| TOML | 30 | ~1,000 | Python project config (pyproject.toml) |

**Tech Stack:** Python 3.13, FastAPI, Neo4j (Cypher), PostgreSQL, Redis, Qdrant

### dem2-webui (Frontend - TypeScript/React)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| TypeScript (JSX) | 235 | ~24,000 | React components, UI logic |
| TypeScript | 150 | ~18,000 | Type definitions, utilities, hooks |
| YAML | 120 | ~30,000 | CI/CD, configuration |
| JSON | 25 | ~50,000 | Package config, API schemas |
| CSS/SCSS | 8 | ~850 | Styling |
| Markdown | 30 | ~5,000 | Documentation |

**Tech Stack:** Next.js 15, React 19, TypeScript, pnpm, Biome

### dem2-infra (Infrastructure - Kubernetes/Terraform)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| YAML | 110 | ~25,000 | Kubernetes manifests, ArgoCD configs |
| Terraform | 5 | 1,321 | GCP infrastructure as code |
| Shell | 10 | ~1,000 | Deployment automation |
| TypeScript | 8 | ~500 | Build scripts, tooling |
| Markdown | 15 | ~2,000 | Infrastructure docs |

**Tech Stack:** Kubernetes (GKE), ArgoCD, Terraform, Kustomize, GitHub Actions

### medical-catalog (Catalog Service - Python)
| Language | Files | Lines | Primary Use |
|----------|-------|-------|-------------|
| Python | 85 | ~15,000 | Biomarker catalog API |
| Svelte | 6 | 764 | Admin UI components |
| YAML | 2 | ~3,000 | Configuration |
| JSON | 5 | ~20,000 | Biomarker data, schemas |
| Markdown | 10 | ~1,500 | Documentation |

**Tech Stack:** Python, FastAPI, Qdrant, Svelte

## Key Insights

### Language Breakdown
1. **Python dominates** with 159K lines (29.3%) - primary backend language
2. **Configuration as Code** (JSON + YAML) represents 253K lines (46.2%) - extensive use of declarative configs
3. **TypeScript** (TSX + TS) totals 45K lines (8.3%) - modern type-safe frontend
4. **Infrastructure as Code** - significant YAML for Kubernetes, Terraform for GCP

### Code Organization
- **Microservices Architecture**: Each repo is independently deployable
- **Type Safety**: Heavy use of Python type hints, TypeScript, Pydantic schemas
- **Configuration**: Extensive YAML for configs, CI/CD, fixtures
- **Documentation**: 116 Markdown files with 16K lines of docs

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
| **Terraform** | GCP infrastructure | 5 files, 1,321 lines |
| **Svelte** | Catalog admin UI | 6 files, 764 lines |
| **Nix** | Reproducible dev environments | 2 files, 810 lines |

## File Type Distribution

### Source Code (49.8% of lines)
- Python: 159,136 lines
- TypeScript/TSX: 45,335 lines
- JavaScript: 33 lines
- Svelte: 764 lines
- Shell: 3,372 lines

### Configuration (46.5% of lines)
- JSON: 133,321 lines (API schemas, package.json, configs)
- YAML: 118,079 lines (Kubernetes, CI/CD, fixtures)
- TOML: 1,241 lines (Python project configs)

### Documentation (3.0% of lines)
- Markdown: 16,036 lines
- Text files: 2,050 lines

### Infrastructure (0.7% of lines)
- Dockerfile: 263 lines
- Terraform: 1,321 lines
- Makefile: 780 lines
- Just: 584 lines

## Development Tools

### Build & Task Runners
- **just** - Modern task runner (4 justfiles, 584 lines)
- **make** - Traditional build tool (3 Makefiles, 780 lines)
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
- 116 Markdown files
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

## Growth Trends

Based on git history and file organization:
1. **Active Development** on document processing pipeline
2. **Expanding** medical catalog with biomarker data
3. **Iterating** on frontend UX with React 19 features
4. **Maturing** infrastructure with comprehensive K8s configs

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
| Lines per Python file | ~203 avg | ✅ Good (200-400 typical) |
| Lines per TS file | ~105 avg | ✅ Excellent (<200 ideal) |

## Conclusion

The MachinaMed codebase demonstrates:
- ✅ **Modern Technology Stack** - Latest versions of Python, TypeScript, Next.js
- ✅ **Strong Type Safety** - Extensive use of type systems
- ✅ **Cloud-Native Architecture** - Kubernetes, microservices, containers
- ✅ **Comprehensive Documentation** - 16K+ lines of documentation
- ✅ **Infrastructure as Code** - Declarative configs for reproducibility
- ✅ **Developer Experience** - Fast tooling (uv, pnpm), clear organization

**Total Codebase Size:** 543,320 lines across 2,158 files in 4 repositories.
