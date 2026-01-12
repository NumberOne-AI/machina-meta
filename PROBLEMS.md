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

- [OPEN] **Skillification context management challenges** - Risk of skills not loading when needed or loading unnecessarily
  - Severity: MEDIUM | Added: 2026-01-12
  - Related TODOs: "Convert CLAUDE.md to skill-based architecture" (TODO.md)
  - **Observations**:
    - Converting CLAUDE.md (1,272 lines) into 16 skills promises 68% token savings (~15,173 tokens)
    - But this assumes skills load correctly and only when needed
    - Risk of skills not invoking when context requires them (missing critical information)
    - Risk of skills loading unnecessarily (defeating the purpose)
    - Risk of circular dependencies between skills
    - Risk of skills becoming out of sync with each other
  - **Specific Concerns**:
    1. **Invocation Accuracy**: Will Claude Code correctly detect when a skill is needed?
       - Example: User asks about "document processing" - should load machina-api-testing?
       - Example: User asks "How do I setup?" - clear trigger for machina-setup
       - Example: User asks general question - might need machina-structure for context
    2. **Critical Context Loss**: Are the 405 lines kept in core CLAUDE.md sufficient?
       - What if a workflow needs information from multiple skills?
       - What if critical safety rules reference content moved to skills?
       - Will Architecture Analysis Protocol still work without full workspace context?
    3. **Skill Dependencies**: Some skills naturally reference others
       - machina-api-testing references machina-setup (need backend running first)
       - machina-docs references machina-todo (task tracking for doc updates)
       - machina-preview references machina-submodules (git workflow)
       - How to handle cascading skill loads without loading everything?
    4. **Maintenance Burden**: Keeping 16+ skills synchronized
       - When CLAUDE.md core changes, which skills need updates?
       - When a skill changes, how to identify dependent skills?
       - Risk of information drift between skills over time
    5. **Token Savings Reality**: Will we actually save tokens?
       - If many workflows require 3-4 skills, might load 300+ lines anyway
       - Initial skill invocation adds metadata overhead
       - Might actually increase tokens if skills invoke incorrectly
  - **Evidence Needed**:
    - [ ] Measure actual skill invocation patterns in real conversations
    - [ ] Track how many skills get loaded per typical workflow
    - [ ] Identify which skills are frequently loaded together (dependency patterns)
    - [ ] Measure real token savings after implementation vs theoretical 68%
    - [ ] Count false negatives (skill should load but doesn't)
    - [ ] Count false positives (skill loads unnecessarily)
  - **Potential Solutions Under Consideration**:
    - **Option 1: Hierarchical Skills** - Group related skills into parent skills
      - machina-dev (includes: setup, dev-patterns, services, troubleshoot)
      - machina-git-workflows (includes: submodules, preview)
      - machina-testing (includes: api-testing, reference)
      - Reduces skill count but increases average skill size
    - **Option 2: Lazy Loading with Cache** - Load skills once per session, keep in context
      - First invocation loads skill, subsequent references use cached version
      - Reduces repeated skill loading overhead
      - But defeats token savings if skills stay loaded
    - **Option 3: Hybrid Approach** - Keep frequently-used content in core, only extract rarely-used
      - Keep: api-testing basics, common setup, troubleshooting (top 20% by usage)
      - Extract: Advanced api-testing, nix, gcloud, env (bottom 80% by usage)
      - Requires usage data to identify the 80/20 split
    - **Option 4: Context-Aware Loading** - Skills know their dependencies and load together
      - machina-api-testing auto-loads machina-setup if not loaded
      - machina-preview auto-loads machina-submodules if not loaded
      - Requires sophisticated skill metadata
  - **Decision Criteria**:
    - Measured token savings > 50% of theoretical (i.e., >7,500 tokens saved in practice)
    - Skill invocation accuracy > 90% (correct skill loaded when needed)
    - False negatives < 5% (rarely miss loading a needed skill)
    - Maintenance time < 10 min/month to keep skills synchronized
    - User experience: No noticeable degradation in response quality/relevance
  - **Next Steps**:
    1. Implement minimal prototype with 3 skills (api-testing, setup, troubleshoot)
    2. Measure real-world invocation patterns over 10 conversations
    3. Calculate actual token savings vs theoretical
    4. Decide: full rollout, adjust approach, or abandon based on data
  - **Status**: Needs investigation and prototyping before full implementation

---

## Repository-Specific Problems

For repository-specific problems, see:
- [repos/dem2/PROBLEMS.md](repos/dem2/PROBLEMS.md) - Backend issues
- [repos/dem2-webui/PROBLEMS.md](repos/dem2-webui/PROBLEMS.md) - Frontend issues (if created)
- [repos/medical-catalog/PROBLEMS.md](repos/medical-catalog/PROBLEMS.md) - Catalog service issues (if created)
- [repos/dem2-infra/PROBLEMS.md](repos/dem2-infra/PROBLEMS.md) - Infrastructure issues (if created)
