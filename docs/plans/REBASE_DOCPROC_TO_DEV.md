# Plan: Rebase feature/docproc-extraction-pipeline onto origin/dev

## Overview

Rebase both `repos/dem2` and `repos/dem2-webui` from `feature/docproc-extraction-pipeline` onto `origin/dev`, creating a new branch `dbeal-docproc-dev` without modifying the original feature branch.

**Strategy**: Squash by feature area before rebasing to reduce conflict resolution iterations.

## User Decisions

- **Conflict log location**: Workspace root
- **Commit strategy**: Squash by feature area (reduce 244 commits to ~10-15 logical groups)
- **Partial success handling**: Keep dem2 progress even if dem2-webui fails

## Repository State Summary

| Repository       | Ahead of origin/dev | Behind origin/dev | Conflict Risk |
|------------------|---------------------|-------------------|---------------|
| **dem2**         | 244 commits         | 21 commits        | HIGH          |
| **dem2-webui**   | 13 commits          | 6 commits         | MEDIUM        |

## Key Architectural Conflicts (dem2)

| Area                     | Feature Branch                | origin/dev                                                        |
|--------------------------|-------------------------------|-------------------------------------------------------------------|
| Custom Parsers           | **DELETED** (using generic)   | Added `boston_heart_v4`, `dutch_plus`, `nutr_eval`, `supervisor`  |
| Generic Agent            | Present                       | Deleted                                                           |
| Reference Range Parsing  | Moved to separate agent       | Different approach                                                |
| Strategy Router          | Deleted                       | Added                                                             |

## Execution Plan

### Phase 1: Pre-Rebase Preparation

#### Step 1.1: Verify Clean State
```bash
# Stash any uncommitted work in both repos
(cd repos/dem2 && git stash push -m "pre-rebase-stash-$(date +%Y%m%d)")
(cd repos/dem2-webui && git stash push -m "pre-rebase-stash-$(date +%Y%m%d)")
```

#### Step 1.2: Fetch Latest from Remote
```bash
(cd repos/dem2 && git fetch origin)
(cd repos/dem2-webui && git fetch origin)
```

#### Step 1.3: Create Backup Tags
```bash
# Tag current feature branch state for recovery
(cd repos/dem2 && git tag -f backup/docproc-pre-rebase-$(date +%Y%m%d) HEAD)
(cd repos/dem2-webui && git tag -f backup/docproc-pre-rebase-$(date +%Y%m%d) HEAD)
```

#### Step 1.4: Create Conflict Resolution Log Template
```bash
# Create log file at workspace root
touch CONFLICT_RESOLUTION_LOG_docproc-extraction-pipeline_origin-dev_$(date +%Y%m%d).md
```

Initial log structure:
```markdown
# Conflict Resolution Log

- **Source Branch**: feature/docproc-extraction-pipeline
- **Target Branch**: origin/dev
- **New Branch**: dbeal-docproc-dev
- **Date**: YYYY-MM-DD
- **Status**: IN_PROGRESS

## Summary Statistics

| Repository   | Conflicts Encountered | Resolved | Ours | Theirs | Manual |
|--------------|----------------------:|:--------:|:----:|:------:|:------:|
| dem2         |                     0 |        0 |    0 |      0 |      0 |
| dem2-webui   |                     0 |        0 |    0 |      0 |      0 |

## Conflict Resolution Strategy

### Prefer "Ours" (Feature Branch)
1. Deleted custom parser files (boston_heart_v4, dutch_plus, nutr_eval, supervisor)
2. Deleted strategy.py routing layer
3. Reference range parsing architecture changes
4. Changes to extractor pipeline.py, models.py

### Prefer "Theirs" (origin/dev)
1. Bug fixes unrelated to document processing
2. Non-conflicting feature additions

### Manual Review Required
1. Changes to shared types/interfaces
2. Test file conflicts
3. Configuration changes

## Detailed Conflict Log

### dem2

(Conflicts will be logged here during rebase)

### dem2-webui

(Conflicts will be logged here during rebase)
```

---

### Phase 1.5: Squash dem2 Commits by Feature Area

**Purpose**: Reduce 244 commits to ~10-15 logical feature groups before rebasing onto origin/dev. This dramatically simplifies conflict resolution.

#### Step 1.5.1: Analyze Commits and Group by Feature Area

First, analyze the 244 commits to identify logical groupings:

```bash
# Get commit log with file changes
(cd repos/dem2 && git log --oneline --name-only $(git merge-base origin/dev HEAD)..HEAD > /tmp/dem2-commits.txt)

# Review major feature areas from commit messages
(cd repos/dem2 && git log --oneline $(git merge-base origin/dev HEAD)..HEAD | head -50)
```

**Expected Feature Groups** (based on exploration):

| Group | Feature Area                    | Example Commits                               |
|------:|---------------------------------|-----------------------------------------------|
|     1 | **Generic Extraction Pipeline** | Refactor to single generic agent              |
|     2 | **Custom Parser Removal**       | Delete boston_heart_v4, dutch_plus, nutr_eval |
|     3 | **Reference Range Agent**       | New reference range extraction agent          |
|     4 | **Reference Range Matching**    | Backend interval matching logic               |
|     5 | **Medical Types Updates**       | IntervalCategory, RangeInterval changes       |
|     6 | **Graph Memory/Neo4j**          | Observation query changes, cypher updates     |
|     7 | **API Response Changes**        | ObservationValueResponse with matched_interval|
|     8 | **Unit Tests**                  | Test files for interval matching              |
|     9 | **Integration Tests**           | Integration tests for observations            |
|    10 | **Config/Dependencies**         | pyproject.toml, requirements changes          |
|    11 | **Documentation**               | README, CLAUDE.md updates                     |
|    12 | **Misc Fixes**                  | Bug fixes, typos, small improvements          |

#### Step 1.5.2: Create Squash Branch

```bash
# Create a temporary branch for squashing (preserves original feature branch)
(cd repos/dem2 && git checkout feature/docproc-extraction-pipeline)
(cd repos/dem2 && git checkout -b temp/docproc-squashed)
```

#### Step 1.5.3: Interactive Rebase to Squash

```bash
# Start interactive rebase from merge-base
(cd repos/dem2 && git rebase -i $(git merge-base origin/dev HEAD))
```

In the interactive editor, group commits by feature area:
- Mark first commit of each group as `pick`
- Mark subsequent commits in group as `squash` or `fixup`
- Reorder commits to group related changes together

**Example squash plan:**
```
# Group 1: Generic Extraction Pipeline
pick abc123 refactor: Remove format-specific extractors
squash def456 fix: Generic agent edge cases
squash ghi789 test: Generic pipeline tests

# Group 2: Custom Parser Removal
pick jkl012 chore: Remove boston_heart_v4 files
squash mno345 chore: Remove dutch_plus files
squash pqr678 chore: Remove nutr_eval files

# ... continue for all groups
```

#### Step 1.5.4: Write Descriptive Squash Messages

For each squashed commit, write a comprehensive message:

```
feat(docproc): implement generic extraction pipeline

Replace format-specific extractors (boston_heart, dutch_plus, nutr_eval)
with a single generic extraction agent using LLM-based parsing.

Changes:
- Add GenericAgent with generic.md prompt
- Add GenericConverter for standardized output
- Remove strategy.py routing layer
- Update pipeline.py to use GenericProcessor only

This is a breaking change for document processing architecture.
```

#### Step 1.5.5: Verify Squashed Branch

```bash
# Should have ~10-15 commits instead of 244
(cd repos/dem2 && git log --oneline $(git merge-base origin/dev HEAD)..HEAD)

# Verify diff is identical to original feature branch
(cd repos/dem2 && git diff feature/docproc-extraction-pipeline..temp/docproc-squashed)  # Should be empty
```

---

### Phase 2: Rebase dem2 (High Risk - Do First)

**Note**: This phase uses the squashed branch from Phase 1.5, reducing conflicts from 244 commits to ~10-15.

#### Step 2.1: Create New Branch from origin/dev
```bash
(cd repos/dem2 && git checkout -b dbeal-docproc-dev origin/dev)
```

#### Step 2.2: Cherry-Pick Squashed Commits onto New Branch
```bash
# Cherry-pick the squashed commits from temp/docproc-squashed
# This applies ~10-15 logical commits instead of 244
(cd repos/dem2 && git cherry-pick $(git merge-base origin/dev temp/docproc-squashed)..temp/docproc-squashed)
```

**Why cherry-pick instead of rebase:**
- Squashed commits are already clean and logically grouped
- Cherry-pick allows stopping at each commit to resolve conflicts
- Easier to identify which feature area is conflicting

#### Step 2.3: Conflict Resolution Rules for dem2

**Rule A: Deleted Custom Parser Directories**
When conflicts involve these paths, prefer OURS (delete them):
- `services/docproc/src/machina/docproc/extractor/agents/boston_heart_v4/*`
- `services/docproc/src/machina/docproc/extractor/agents/dutch_plus/*`
- `services/docproc/src/machina/docproc/extractor/agents/nutr_eval/*`
- `services/docproc/src/machina/docproc/extractor/agents/supervisor/*`
- `services/docproc/src/machina/docproc/extractor/converters/boston_heart_v4.py`
- `services/docproc/src/machina/docproc/extractor/converters/dutch_plus.py`
- `services/docproc/src/machina/docproc/extractor/converters/nutr_eval.py`
- `services/docproc/src/machina/docproc/extractor/converters/reference_parser.py`
- `services/docproc/src/machina/docproc/extractor/processors/boston_heart_v4.py`
- `services/docproc/src/machina/docproc/extractor/processors/dutch_plus.py`
- `services/docproc/src/machina/docproc/extractor/processors/nutr_eval.py`
- `services/docproc/src/machina/docproc/extractor/strategy.py`

**Resolution command for deleted files:**
```bash
git rm <conflicting-file>
git add -u
```

**Rule B: __init__.py and Module Registry Files**
When conflicts in these files:
- `services/docproc/src/machina/docproc/extractor/agents/__init__.py`
- `services/docproc/src/machina/docproc/extractor/converters/__init__.py`
- `services/docproc/src/machina/docproc/extractor/processors/__init__.py`

**Resolution**: Take OURS, but review for any new exports from origin/dev that are NOT related to deleted custom parsers.

**Rule C: Core Architecture Files**
Files requiring careful manual review:
- `services/docproc/src/machina/docproc/extractor/pipeline.py`
- `services/docproc/src/machina/docproc/extractor/models.py`
- `services/docproc/src/machina/docproc/extractor/agents/base.py`
- `services/docproc/src/machina/docproc/extractor/converters/base.py`

**Resolution**: Prefer OURS but check for bugfixes in THEIRS that should be incorporated.

**Rule D: Reference Range Parsing**
Any files under these paths:
- `services/medical-data-engine/src/machina/medical_data_engine/engine/processors/biomarker/*`
- `services/docproc/src/machina/docproc/extractor/agents/reference_range/*`

**Resolution**: Always prefer OURS - this is a major architectural change.

#### Step 2.4: Per-Conflict Workflow
```bash
# When a conflict occurs:
# 1. Identify the conflict type
git status

# 2. Log the conflict
echo "### Conflict: <filename>" >> CONFLICT_RESOLUTION_LOG_*.md
echo "- **Type**: <add/delete/modify>" >> CONFLICT_RESOLUTION_LOG_*.md
echo "- **Rule Applied**: <A/B/C/D/Manual>" >> CONFLICT_RESOLUTION_LOG_*.md

# 3. Apply resolution based on rules above
# For Rule A (deleted files):
git rm <file>

# For Rule B/C/D (content conflicts):
# Open file, resolve manually, then:
git add <file>

# 4. Continue rebase
git rebase --continue
```

#### Step 2.5: Rollback Procedure (if needed)
```bash
# If conflicts are too severe or introduce bugs:
(cd repos/dem2 && git rebase --abort)
(cd repos/dem2 && git checkout feature/docproc-extraction-pipeline)
(cd repos/dem2 && git branch -D dbeal-docproc-dev)

# Update log status
echo "**Status**: ABORTED - Reason: <describe issue>" >> CONFLICT_RESOLUTION_LOG_*.md
```

---

### Phase 3: Rebase dem2-webui (Medium Risk)

#### Step 3.1: Create New Branch
```bash
(cd repos/dem2-webui && git checkout -b dbeal-docproc-dev origin/dev)
```

#### Step 3.2: Rebase Feature Commits
```bash
(cd repos/dem2-webui && git rebase --onto dbeal-docproc-dev $(git merge-base origin/dev feature/docproc-extraction-pipeline) feature/docproc-extraction-pipeline)
```

#### Step 3.3: Expected Conflicts
- `src/types/fhir-storage.ts` - Type definitions (prefer OURS)
- `src/components/fhir-storage/*` - UI components (prefer OURS)
- `tests/*` - Test files (manual merge - keep both test sets)

#### Step 3.4: Resolution Strategy
- **Type files**: Prefer OURS (matched_interval fields are core to feature)
- **UI components**: Prefer OURS (interval status badges)
- **Tests**: Merge both - ensure test coverage from both branches

---

### Phase 4: Post-Rebase Verification

#### Step 4.1: Verify Both Repos Are on New Branch
```bash
(cd repos/dem2 && git branch --show-current)  # Should be: dbeal-docproc-dev
(cd repos/dem2-webui && git branch --show-current)  # Should be: dbeal-docproc-dev
```

#### Step 4.2: Run Tests (dem2)
```bash
(cd repos/dem2 && just check)  # Lint + typecheck
(cd repos/dem2 && just test)   # Unit tests
```

#### Step 4.3: Run Tests (dem2-webui)
```bash
(cd repos/dem2-webui && pnpm check)  # Lint + typecheck
(cd repos/dem2-webui && pnpm test)   # Unit tests
```

#### Step 4.4: Verify Document Processing Pipeline
```bash
# Start dev environment
(cd repos/dem2 && just dev-env-up -d)

# Test document upload and processing
(cd repos/dem2 && just curl_api '{"function": "list_documents"}')
```

#### Step 4.5: Finalize Conflict Resolution Log
```markdown
## Summary Statistics (Final)

| Repository   | Conflicts Encountered | Resolved | Ours | Theirs | Manual |
|--------------|----------------------:|:--------:|:----:|:------:|:------:|
| dem2         |                     X |        X |    X |      X |      X |
| dem2-webui   |                     X |        X |    X |      X |      X |

**Status**: COMPLETED / PARTIAL / ABORTED
**Final Commit (dem2)**: <sha>
**Final Commit (dem2-webui)**: <sha>
```

---

### Phase 5: Cleanup

#### Step 5.1: Remove Backup Tags (Optional - Keep for 2 weeks)
```bash
# After confirming rebase is stable:
# (cd repos/dem2 && git tag -d backup/docproc-pre-rebase-YYYYMMDD)
# (cd repos/dem2-webui && git tag -d backup/docproc-pre-rebase-YYYYMMDD)
```

#### Step 5.2: Restore Stashed Changes (if any)
```bash
(cd repos/dem2 && git stash pop)
(cd repos/dem2-webui && git stash pop)
```

#### Step 5.3: Push New Branches to Origin (User Confirmation Required)
```bash
# Only after user approval:
# (cd repos/dem2 && git push -u origin dbeal-docproc-dev)
# (cd repos/dem2-webui && git push -u origin dbeal-docproc-dev)
```

---

## Risk Mitigation

### High-Risk Scenarios

1. **Rebase Conflicts Too Complex**
   - Symptom: Multiple consecutive conflicts requiring manual resolution
   - Action: Abort rebase, consider squash-and-merge strategy instead

2. **Tests Fail After Rebase**
   - Symptom: Unit tests or type checks fail
   - Action: Fix on dbeal-docproc-dev, do NOT abort (commits are preserved)

3. **Runtime Errors in Document Processing**
   - Symptom: Pipeline fails to process documents
   - Action: Debug on dbeal-docproc-dev; if unfixable, abort and investigate

### Rollback Commands
```bash
# Full rollback for dem2:
(cd repos/dem2 && git checkout feature/docproc-extraction-pipeline)
(cd repos/dem2 && git branch -D dbeal-docproc-dev)

# Full rollback for dem2-webui:
(cd repos/dem2-webui && git checkout feature/docproc-extraction-pipeline)
(cd repos/dem2-webui && git branch -D dbeal-docproc-dev)
```

---

## Files to Create During Execution

1. **`docs/plans/REBASE_DOCPROC_TO_DEV.md`** - This plan (moved from Claude plan file)
2. **`CONFLICT_RESOLUTION_LOG_docproc-extraction-pipeline_origin-dev_YYYYMMDD.md`** - Conflict tracking
3. **`TODO.md`** - Add brief task item with link to plan

## TODO.md Entry

This will supersede the existing PROPOSED task "Merge dem2 branch with origin/dev" (lines 95-113).

```markdown
### Rebase feature/docproc-extraction-pipeline onto origin/dev

- **State**: [STARTED]
- **Impact**: HIGH
- **Added**: 2026-01-13
- **Plan**: [docs/plans/REBASE_DOCPROC_TO_DEV.md](docs/plans/REBASE_DOCPROC_TO_DEV.md)

Rebase both repos/dem2 (244 commits) and repos/dem2-webui (13 commits) from feature/docproc-extraction-pipeline onto origin/dev, creating new branch dbeal-docproc-dev. Heavy conflicts expected due to custom parser deletions vs upstream additions. Using squash-by-feature-area strategy to reduce conflict resolution complexity.

- [ ] Phase 1: Pre-rebase preparation (backup tags, conflict log template)
- [ ] Phase 1.5: Squash dem2 commits by feature area (~244 → ~10-15 commits)
- [ ] Phase 2: Cherry-pick squashed commits onto dbeal-docproc-dev (dem2)
- [ ] Phase 2: Resolve dem2 conflicts (prefer ours for deleted custom parsers)
- [ ] Phase 3: Rebase dem2-webui onto dbeal-docproc-dev
- [ ] Phase 3: Resolve dem2-webui conflicts
- [ ] Phase 4: Run tests and verification
- [ ] Phase 5: Finalize conflict resolution log
```

---

## Verification Checklist

- [ ] Both repos on `dbeal-docproc-dev` branch
- [ ] All custom parser directories removed (not re-added)
- [ ] Generic extraction pipeline intact
- [ ] Reference range agent intact
- [ ] `just check` passes in dem2
- [ ] `pnpm check` passes in dem2-webui
- [ ] Document processing pipeline functional
- [ ] Conflict resolution log complete

---

## Quick Reference: Files to Create

| File                                                                         | Location         | Purpose                                     |
|------------------------------------------------------------------------------|------------------|---------------------------------------------|
| `REBASE_DOCPROC_TO_DEV.md`                                                   | `docs/plans/`    | Full rebase plan (copy of this document)    |
| `CONFLICT_RESOLUTION_LOG_docproc-extraction-pipeline_origin-dev_YYYYMMDD.md` | Workspace root   | Track all conflict resolutions              |
| Updated `TODO.md`                                                            | Workspace root   | Add task entry with plan link               |

## Quick Reference: Branches

| Branch                                   | Repo   | Purpose                                        |
|------------------------------------------|--------|------------------------------------------------|
| `feature/docproc-extraction-pipeline`    | Both   | **DO NOT MODIFY** - original feature branch    |
| `temp/docproc-squashed`                  | dem2   | Intermediate squashed commits                  |
| `dbeal-docproc-dev`                      | Both   | Final rebased branch                           |
| `backup/docproc-pre-rebase-YYYYMMDD`     | Both   | Recovery tag                                   |

## Estimated Effort

| Phase                     | Effort       | Notes                                          |
|---------------------------|-------------:|------------------------------------------------|
| Phase 1: Preparation      |      ~10 min | Backup, fetch, log setup                       |
| Phase 1.5: Squash dem2    |   ~30-60 min | Interactive rebase to group 244 commits        |
| Phase 2: Rebase dem2      |  ~60-120 min | Depends on conflict count                      |
| Phase 3: Rebase dem2-webui|   ~15-30 min | Lower risk, fewer commits                      |
| Phase 4: Verification     |   ~15-30 min | Tests, manual checks                           |
| **Total**                 | **~2-4 hours** | Depends on conflict complexity               |
