# PROBLEMS

This file tracks known problems, issues, and challenges that may or may not have solutions yet.
Problems are observations that need investigation before becoming actionable TODO items.

## ⚠️ CRITICAL: Immediate Commit Requirement

**Changes to this file (and TODO.md) MUST be committed to git immediately after modification.**

Do not batch changes to PROBLEMS.md or TODO.md with other work. These files track project state and must be version-controlled as soon as they are updated.

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

- **OPEN** problems need investigation to understand root cause
- **INVESTIGATING** problems have active analysis or proposed solutions
- **SOLVED** problems have completed TODO items addressing them
- **WONT_FIX** problems are acknowledged but intentionally not addressed

## Problem Format

Each problem includes:
- State: `[OPEN]`, `[INVESTIGATING]`, `[SOLVED]`, or `[WONT_FIX]`
- Severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- Added: Date problem was identified
- Related TODOs: Links to TODO.md items addressing this problem
- Observations: Evidence or symptoms of the problem

**Severity Levels**:
- `CRITICAL` - Blocking production or core functionality
- `HIGH` - Significant impact on users or development
- `MEDIUM` - Notable issue worth tracking
- `LOW` - Minor annoyance or edge case

---

## Workspace - Multi-Repo Coordination

<!-- Add workspace-level problems that affect multiple repositories -->

---

## Workspace - Infrastructure

<!-- Add infrastructure problems affecting the entire workspace (CI/CD, deployments, etc.) -->

---

## Workspace - Documentation & Tooling

<!-- Add documentation and tooling problems affecting workspace-wide development -->

---

## Repository-Specific Problems

For repository-specific problems, see:
- [repos/dem2/PROBLEMS.md](repos/dem2/PROBLEMS.md) - Backend issues
- [repos/dem2-webui/PROBLEMS.md](repos/dem2-webui/PROBLEMS.md) - Frontend issues (if created)
- [repos/medical-catalog/PROBLEMS.md](repos/medical-catalog/PROBLEMS.md) - Catalog service issues (if created)
- [repos/dem2-infra/PROBLEMS.md](repos/dem2-infra/PROBLEMS.md) - Infrastructure issues (if created)
