---
name: machina-git
description: Git workflow assistance for machina-meta workspace with submodules. Enforces working directory safety, conventional commits, and controlled push policy. Governs ALL git operations.
---

# Machina Git Skill

Git workflow assistance specifically designed for the machina-meta workspace with its submodule architecture.

**This skill governs ALL git operations** including status checks, commits, pushes, and multi-repo workflows.

## When to Use This Skill

This skill activates for ALL git-related requests:
- "commit these changes"
- "commit with message"
- "prepare a commit"
- "stage and commit"
- "check git status"
- "show git diff"
- "push to remote"
- "check repo status"
- "help me with git"
- "draft a commit message"
- Any git command or git workflow question

## Core Principles (from CLAUDE.md)

### 1. Working Directory Safety (CRITICAL)

**ALWAYS explicitly cd into the target repository before ANY git command.**

```bash
# CORRECT - Always cd explicitly
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
git status
git commit -m "message"

# WRONG - Never assume current directory
git status  # Dangerous in submodule environment
```

**Why this matters:**
- machina-meta has 5 independent git repositories (root + 4 submodules)
- Each submodule has independent git history
- Running git commands in wrong repo corrupts state
- Path confusion causes commits in wrong repo

**Repository Paths:**
- Workspace root: `/home/dbeal/repos/NumberOne-AI/machina-meta`
- Backend: `/home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2`
- Frontend: `/home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-webui`
- Infrastructure: `/home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-infra`
- Catalog: `/home/dbeal/repos/NumberOne-AI/machina-meta/repos/medical-catalog`

### 2. Push Policy (CRITICAL)

**NEVER push to git repositories automatically.**

- Always commit changes locally first
- **DO NOT** run `git push` without explicit user confirmation
- **DO NOT** push as part of automated workflows
- Ask: "Should I push these changes to the remote repository?"
- Only push if user explicitly confirms ("yes", "push", "push it")

### 3. Commit Message Policy (CRITICAL)

**NEVER add Claude Code attribution or co-authorship credits.**

- **DO NOT** include `🤖 Generated with [Claude Code]`
- **DO NOT** include `Co-Authored-By: Claude <noreply@anthropic.com>`
- Write clean, concise conventional commit messages
- Follow repository's existing commit style

### 4. Atomic Commits (CRITICAL)

**Unrelated changes should be committed separately and atomically whenever possible.**

- Each commit should represent a single logical change
- Don't mix unrelated changes in one commit (e.g., adding a feature + updating documentation for a different feature)
- Separate concerns even when working on multiple things simultaneously
- Makes git history cleaner and easier to review/revert

**Examples:**

✅ **Good - Atomic commits:**
```bash
# Commit 1: Add new skill
git add .claude/skills/machina-git/
git commit -m "feat: add machina-git custom skill"

# Commit 2: Separate unrelated change
git add .claude/skills/kubernetes/
git commit -m "feat: add kubernetes skill for K8s operations"
```

❌ **Bad - Mixed concerns:**
```bash
# BAD - Two unrelated features in one commit
git add .claude/skills/machina-git/ .claude/skills/kubernetes/
git commit -m "feat: add machina-git and kubernetes skills"
```

**When to separate commits:**
- Different features or bug fixes
- Different subsystems or components
- Documentation updates for different topics
- Dependency updates vs feature changes
- Refactoring vs new functionality

**When commits can be combined:**
- Changes are tightly coupled (e.g., API + corresponding tests)
- Documentation for the code being changed
- Multiple files implementing one logical feature

## Multi-Repo Status Checks

When checking status across multiple repositories, always show which repo you're checking:

```bash
echo "=== Checking machina-meta (workspace root) ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta
git status

echo "=== Checking repos/dem2 (backend) ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
git status

echo "=== Checking repos/dem2-webui (frontend) ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-webui
git status

echo "=== Checking repos/dem2-infra (infrastructure) ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-infra
git status

echo "=== Checking repos/medical-catalog (catalog service) ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/medical-catalog
git status
```

**Alternative:** Use workspace-level just commands:
```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta
just repo-status    # Git status across all repos
just repo-branches  # Show current branches
just repo-diff      # Show diffs across all repos
```

## Workflow Pattern

### Step 1: Identify Target Repository

When user requests a git operation, first identify which repository:

```
User mentions: "commit the backend changes"
→ Target: repos/dem2

User mentions: "commit CLAUDE.md"
→ Target: workspace root (machina-meta)

User mentions: "commit the frontend"
→ Target: repos/dem2-webui

User mentions: "check status of all repos"
→ Target: all repositories (use just repo-status or iterate)
```

If unclear, ask: "Which repository should I work with?"

### Step 2: Explicit Directory Change

Always show and execute the `cd` command:

```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
```

### Step 3: Review Current State

```bash
git status
git diff
```

Show the user what will be committed. Ask if this looks correct.

### Step 4: Stage Changes

**ALWAYS stage specific files explicitly. NEVER use `git add .` or `git add -A`.**

```bash
# CORRECT - Stage specific files
git add path/to/file1.py path/to/file2.py

# WRONG - Never use these
git add .   # BAD
git add -A  # BAD
```

⚠️ **NEVER stage sensitive files:**
- `.env` files containing secrets
- Credential files (`.pem`, `.key`, service account JSON, etc.)
- Configuration files with sensitive data

⚠️ **Why no `git add -A` or `git add .`:**
- Can accidentally stage unintended files
- May include sensitive files (.env, credentials)
- Less explicit and harder to review
- Always specify exactly what should be committed

### Step 5: Craft Commit Message

Use conventional commit format:

**Format:** `<type>(<scope>): <description>`

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, missing semicolons, etc.
- `refactor` - Code change that neither fixes a bug nor adds a feature
- `perf` - Performance improvement
- `test` - Adding or fixing tests
- `chore` - Maintenance tasks, dependency updates
- `ci` - CI/CD changes
- `build` - Build system changes

**Scope (optional):**
- Component, module, or area affected
- Examples: `api`, `frontend`, `auth`, `infra`, `docker`

**Description:**
- Concise summary in imperative mood ("add" not "added")
- No period at the end
- Lowercase first letter
- Max 72 characters for first line

**Examples:**
```
feat(api): add patient biomarker reconciliation endpoint
fix(auth): resolve token refresh race condition
docs: update CLAUDE.md with git rules section
chore(deps): update dem2 submodule to latest dev
refactor(agents): simplify tool calling pattern in medical agent
test(biomarkers): add integration tests for extraction pipeline
```

### Step 6: Execute Commit

```bash
git commit -m "type(scope): description"
```

**For multi-line commits:**
```bash
git commit -m "$(cat <<'EOF'
feat(api): add patient biomarker reconciliation endpoint

- Implement POST /api/v1/biomarkers/reconcile
- Add validation for incoming biomarker data
- Integrate with medical-catalog service for normalization
- Add comprehensive error handling
EOF
)"
```

### Step 7: Verify Commit

```bash
git log -1 --stat
```

Show the user the commit that was created.

### Step 8: Push Confirmation (If Needed)

**Only if user explicitly requests pushing:**

1. Verify commit is correct
2. Ask: "Should I push these changes to the remote repository?"
3. Wait for explicit confirmation
4. If confirmed, execute:
   ```bash
   git push
   ```

## Multi-Line Commit Messages

For complex changes, use multi-line format:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<detailed description>

- Bullet point 1
- Bullet point 2
- Bullet point 3

Additional context or reasoning.
EOF
)"
```

**Example:**
```bash
git commit -m "$(cat <<'EOF'
refactor(agents): consolidate tool calling patterns

Unified tool execution across all agent types:
- Extract common validation logic to SafeAgentTool
- Standardize error handling across medical agents
- Add type safety for tool parameters
- Improve logging for tool invocations

This reduces code duplication and makes the system more maintainable.
Addresses technical debt noted in TODO.md.
EOF
)"
```

## Working with Submodules

### Committing in a Submodule

```bash
# Step 1: cd into submodule
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2

# Step 2: Make changes, stage, commit
git add services/medical-agent/src/machina/medical_agent/agents/config.yml
git commit -m "feat(agents): update medical agent prompt template"

# Step 3: Push to submodule's remote (if confirmed)
git push origin dev
```

### Updating Parent Workspace to Track Submodule Change

After committing in a submodule, the parent workspace needs to track the new commit:

```bash
# Step 1: cd back to workspace root
cd /home/dbeal/repos/NumberOne-AI/machina-meta

# Step 2: Stage the submodule update
git add repos/dem2

# Step 3: Commit in parent workspace
git commit -m "chore: update dem2 submodule to latest dev"

# Step 4: Push parent workspace (if confirmed)
git push
```

## Repository-Specific Commit Patterns

### machina-meta (workspace root)

Common commit types:
- `docs:` - Updates to CLAUDE.md, README.md, docs/
- `chore:` - Submodule updates, dependency updates
- `ci:` - Changes to justfile, scripts/
- `feat:` - New workspace-level features

### repos/dem2 (backend)

Common commit types:
- `feat(agents):` - Agent changes
- `feat(api):` - API endpoint changes
- `fix(biomarkers):` - Biomarker processing fixes
- `refactor(graph):` - Graph model refactoring
- `test:` - Test additions/fixes
- `chore(deps):` - Dependency updates

### repos/dem2-webui (frontend)

Common commit types:
- `feat(ui):` - New UI components
- `fix(auth):` - Authentication fixes
- `style:` - CSS/styling changes
- `refactor:` - Component refactoring
- `chore(deps):` - Dependency updates

### repos/dem2-infra (infrastructure)

Common commit types:
- `feat(k8s):` - Kubernetes manifest changes
- `feat(argocd):` - ArgoCD application changes
- `chore:` - Preview environment updates
- `ci:` - GitHub Actions changes

### repos/medical-catalog (catalog service)

Common commit types:
- `feat(biomarkers):` - Biomarker catalog additions
- `fix(search):` - Search/query fixes
- `refactor:` - Code refactoring
- `chore(deps):` - Dependency updates

## Safety Checklist

Before executing any git operation:

- [ ] Explicitly cd into target repository
- [ ] Show full absolute path in cd command
- [ ] Review git status and git diff (for commits)
- [ ] Confirm changes with user (for commits)
- [ ] Ensure changes are related and atomic (separate unrelated changes)
- [ ] Stage specific files only (NEVER use `git add .` or `git add -A`)
- [ ] Verify no sensitive files are being staged (.env, credentials, keys)
- [ ] Craft conventional commit message (no Claude attribution)
- [ ] Execute commit with heredoc for multi-line
- [ ] Verify commit with git log -1 --stat
- [ ] Only push if explicitly requested and confirmed

## Anti-Patterns (DO NOT DO)

❌ **Assume current directory:**
```bash
# BAD - Never assume you're in the right place
git status
```

❌ **Auto-push without confirmation:**
```bash
# BAD - Never push without explicit confirmation
git commit -m "message" && git push
```

❌ **Add Claude attribution:**
```bash
# BAD - Never add attribution
git commit -m "feat: add feature

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

❌ **Use git add with . or -A:**
```bash
# BAD - Never use blanket staging
git add .
git add -A
```

❌ **Stage sensitive files:**
```bash
# BAD - Never stage secrets or credentials
git add .env
git add config/credentials.json
git add *.key
git add *.pem
```

❌ **Use git commit with -a flag blindly:**
```bash
# BAD - Stages everything including unintended files
git commit -am "message"
```

❌ **Chain push operations:**
```bash
# BAD - No automatic chaining to push
git commit -m "message" && git push
```

## Best Practices

✅ **Always show full paths in cd commands**
✅ **Review changes before staging**
✅ **ALWAYS stage specific files explicitly (never `git add .` or `git add -A`)**
✅ **Verify no .env or credential files are being staged**
✅ **Draft commit message and get user approval**
✅ **Use heredoc for multi-line commits**
✅ **Verify commit after creation**
✅ **Keep commits focused and atomic**
✅ **Separate unrelated changes into different commits**
✅ **Reference issue/PR numbers when applicable**
✅ **Use just repo-* commands for multi-repo operations**

## Integration with TODO.md

When making commits related to TODO.md tasks:

1. Reference the TODO item in commit message if helpful
2. Update TODO.md to mark tasks as DONE (with completion date)
3. Commit TODO.md changes immediately (per CLAUDE.md requirements)

Example workflow:
```bash
# Make code changes
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
git add services/medical-agent/
git commit -m "feat(agents): add biomarker extraction validation"

# Update TODO.md
cd /home/dbeal/repos/NumberOne-AI/machina-meta
# (edit TODO.md to mark task as DONE)
git add TODO.md
git commit -m "docs: mark biomarker validation task as DONE"
```

## Common Scenarios

### Scenario 1: Check Status Across All Repos

```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta
just repo-status
```

Or manually:
```bash
echo "=== machina-meta ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta
git status --short

echo "=== repos/dem2 ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
git status --short

echo "=== repos/dem2-webui ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-webui
git status --short

echo "=== repos/dem2-infra ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-infra
git status --short

echo "=== repos/medical-catalog ==="
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/medical-catalog
git status --short
```

### Scenario 2: Single File Change

```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta
git add CLAUDE.md
git commit -m "docs: consolidate git rules into unified section"
git log -1 --stat
# Ask: "Should I push these changes to the remote repository?"
```

### Scenario 3: Multiple Files in Backend

```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
git status
git add services/medical-agent/src/machina/medical_agent/agents/medical_agent.py
git add services/medical-agent/src/machina/medical_agent/agents/config.yml
git commit -m "$(cat <<'EOF'
refactor(agents): improve error handling in medical agent

- Add try/catch blocks around tool execution
- Log errors with full context
- Return structured error responses to frontend
EOF
)"
git log -1 --stat
```

### Scenario 4: Preview Environment (multi-repo)

```bash
# Step 1: Tag backend
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2
git tag -f preview-my-feature
# Push tag (if confirmed): git push origin preview-my-feature --force

# Step 2: Tag frontend
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-webui
git tag -f preview-my-feature
# Push tag (if confirmed): git push origin preview-my-feature --force

# Step 3: Update infra
cd /home/dbeal/repos/NumberOne-AI/machina-meta/repos/dem2-infra
git checkout -b preview/my-feature
# Make changes, commit, push (if confirmed)
```

## Protected Push Operation

Git push is a **protected operation**. Never execute `git push` without:

1. Showing the commit(s) that will be pushed:
   ```bash
   git log origin/main..HEAD --oneline
   ```

2. Asking explicitly: "Should I push these changes to the remote repository?"

3. Waiting for user confirmation ("yes", "push", "push it")

4. Only then executing:
   ```bash
   git push
   ```

For force pushes (tags, rewrites), extra caution:
```bash
# Show what will be force pushed
git show preview-my-feature

# Ask: "This is a force push. Should I proceed?"
# Only if confirmed:
git push origin preview-my-feature --force
```

## Related Documentation

- [CLAUDE.md](../../../CLAUDE.md) - Full git rules and workspace guidance
- [docs/DEVOPS.md](../../../docs/DEVOPS.md) - Preview environments and deployment workflows
- [docs/DEVOPS_SKILLS.md](../../../docs/DEVOPS_SKILLS.md) - Other DevOps skills available

## Skill Metadata

- **Version:** 1.0.0
- **Created:** 2026-01-06
- **Workspace:** machina-meta
- **Repositories:** 5 (1 root + 4 submodules)
- **Philosophy:** Safety-first, explicit actions, user confirmation for destructive operations
- **Scope:** Governs ALL git operations (status, commit, push, multi-repo workflows)
