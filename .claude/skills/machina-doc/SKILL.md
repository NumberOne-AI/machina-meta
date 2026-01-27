---
name: machina-doc
description: Automated documentation generation for accomplishments reports and contribution summaries from git history.
---

# machina-doc Skill

Automated documentation generation for accomplishments reports and contribution summaries.

## Purpose

Generate comprehensive accomplishment reports from git history, similar in format to PR summaries. This skill captures the methodology for creating impact-ordered documentation of engineering contributions.

## Invocation

Use when the user requests:
- Accomplishment reports
- Contribution summaries
- Work documentation from git history
- Impact analysis of commits
- Engineering portfolio generation

## Process Overview

### Phase 1: Data Collection

1. **Gather commits across all repositories**
   ```bash
   # For each repo (dem2, dem2-webui, medical-catalog, dem2-infra, machina-meta):
   (cd repos/<repo> && git log --author="<author>" --since="<date>" --pretty=format:"%h|%ad|%s" --date=short)
   ```

2. **Collect statistics**
   ```bash
   # Commit counts and line changes:
   (cd repos/<repo> && git log --author="<author>" --since="<date>" --shortstat --pretty=format:"" | \
     awk '/files? changed/ { files+=$1; insertions+=$4; deletions+=$6; commits++ } END { print commits, files, insertions, deletions }')

   # Simple commit count:
   (cd repos/<repo> && git log --author="<author>" --since="<date>" --oneline | wc -l)
   ```

3. **Categorize by type**
   ```bash
   # Count commits by conventional commit type:
   (cd repos/<repo> && git log --author="<author>" --since="<date>" --pretty=format:"%s" | \
     cut -d: -f1 | cut -d'(' -f1 | sort | uniq -c | sort -rn)
   ```

4. **Find domain-specific commits**
   ```bash
   # Search by keyword (case-insensitive with grep):
   (cd repos/<repo> && git log --author="<author>" --since="<date>" --grep="<keyword>" --oneline)

   # Examples:
   (cd repos/dem2 && git log --author="dbeal" --since="2024-12-01" --grep="Gemini\|gemini" --oneline)
   (cd repos/dem2 && git log --author="dbeal" --since="2024-12-01" --grep="docproc\|extraction\|document" --oneline)
   (cd repos/dem2 && git log --author="dbeal" --since="2024-12-01" --grep="agent" --oneline)
   ```

### Phase 2: Impact Classification

Classify each significant commit into impact categories:

| Category | Description | Examples |
|----------|-------------|----------|
| **Cost Optimization** | Reduces operational costs | LLM cost reduction, API call reduction |
| **Performance** | Improves speed/efficiency | Processing time reduction, batch optimization |
| **Architecture** | Structural improvements | Code simplification, pattern unification |
| **Quality** | Accuracy/reliability improvements | Verification systems, test coverage |
| **Developer Experience** | Tooling and workflow | Skills, scripts, documentation |
| **Infrastructure** | DevOps and deployment | Preview environments, CI/CD |

### Phase 3: Report Structure

Generate `docs/ACCOMPLISHMENTS_<AUTHOR>.md` with this structure:

```markdown
# Engineering Accomplishments Report

## Authorship

**Author**: [Full Name] ([email])
**Period**: [Start Date] - [End Date]
**Generated**: [Generation Date]

---

## Executive Summary

[High-level description of work across all repositories]

**Overall Statistics**:
| Repository | Commits | Files Changed | Lines Added | Lines Deleted |
|------------|---------|---------------|-------------|---------------|
| dem2 (Backend) | X | Y | +Z | -W |
| machina-meta (Workspace) | X | Y | +Z | -W |
| ... | ... | ... | ... | ... |
| **Total** | **X** | **Y** | **+Z** | **-W** |

---

## Performance Improvements

| Metric | Baseline | Current | Impact |
|--------|----------|---------|--------|
| **[Metric name]** | [Before] | [After] | **[% improvement]** |

---

## Categorical Summary (Ordered by Impact)

| Impact | Category | Technical Area | Business Value | Key Results |
|--------|----------|----------------|----------------|-------------|
| **HIGH** | [Category] | [What] | [Why it matters] | [Numbers] |
| **MEDIUM** | ... | ... | ... | ... |
| **LOW** | ... | ... | ... | ... |

---

## Repository Breakdown

### [repo-name] (X commits)

#### Commit Type Distribution
| Type | Count | Percentage |
|------|-------|------------|
| feat | X | Y% |
| fix | X | Y% |
| ... | ... | ... |

#### HIGH Impact Changes

**1. [Feature/Fix Name]**
- `<commit-hash>` <commit message>
- `<commit-hash>` <commit message>
- **Result**: [Quantifiable outcome]

#### MEDIUM Impact Changes

**2. [Feature/Fix Name]**
- `<commit-hash>` <commit message>
- **Result**: [Outcome]

---

## Timeline Highlights

### [Date Range]: [Theme]
- `<commit-hash>` <commit message>
- **Focus**: [Summary of work]

---

## Impact Metrics Summary

| Category | Key Metric | Value |
|----------|-----------|-------|
| Cost | [Metric] | [Value] |
| Performance | [Metric] | [Value] |
| ... | ... | ... |
```

### Phase 4: Ordering Rules

All tables MUST be ordered by:
1. **Impact** - HIGH > MEDIUM > LOW
2. **Value** - Quantifiable business value (cost savings, performance gains)
3. **Benefit** - User/developer experience improvement

### Phase 5: Incremental Writing

**IMPORTANT**: Write the accomplishments document incrementally as you analyze:

1. Start with the skeleton structure (Authorship, Summary, Statistics tables)
2. Add repository sections as you analyze each repo
3. Fill in commit hashes as you discover important commits
4. Update impact classifications as patterns emerge
5. Refine timeline as you understand the chronological narrative

## Output Location

- Primary: `docs/ACCOMPLISHMENTS_<AUTHOR>.md` (e.g., `ACCOMPLISHMENTS_DBEAL.md`)
- Skill: `.claude/skills/machina-doc/SKILL.md` (this file)

## Example Reference: PR 421 Format

The accomplishment report should match the format of PR 421 in repos/dem2:
- Performance table with Baseline | Current | Impact columns
- Categorical summary with Product Category | Technical Section | Business Impact | Quantifiable Results
- Commit lists with hash prefixes

Fetch reference format:
```bash
(cd repos/dem2 && gh pr view 421 --json title,body)
```

## Skill Revision Notes

**Key learnings from January 2026 execution:**

1. **Statistics collection**: Use `--shortstat --pretty=format:""` pattern for accurate line counts
2. **Commit discovery**: Use `--grep` with multiple patterns separated by `\|` for OR matching
3. **Author identification**: Include authorship as prominent heading for single-author reports
4. **File naming**: Use `ACCOMPLISHMENTS_<AUTHOR>.md` pattern for author-specific reports
5. **Commit hashes**: Include short hashes (first 7-8 chars) for traceability
6. **Result emphasis**: Each section should end with **Result**: line showing quantifiable outcome
7. **Timeline structure**: Group commits by date ranges with thematic focus descriptions
8. **Repository stats**: Include all 5 repos: dem2, dem2-webui, medical-catalog, dem2-infra, machina-meta
9. **Impact categories**: Cost > Performance > Architecture > Quality > DevEx > Infrastructure ordering
10. **Cross-reference PRs**: Reference existing PR summaries for format consistency

**Statistics discovered in initial run (Dec 2024 - Jan 2026):**
- dem2: 283 commits, 3,787 files, +598,609/-289,350 lines
- machina-meta: 156 commits, 402 files, +141,393/-10,713 lines
- dem2-webui: 10 commits, 25 files, +2,055/-41 lines
- medical-catalog: 3 commits, 3 files, +85/-6 lines
- dem2-infra: 1 commit, 4 files, +2/-18 lines

**Last Updated**: January 16, 2026
