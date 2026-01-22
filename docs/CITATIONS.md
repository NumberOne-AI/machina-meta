# Citation System for Technical Documentation

**Version:** 1.0
**Last Updated:** 2026-01-06
**Applies to:** DATAFLOW.md, MULTI_AGENT_ARCHITECTURE.md, and all architecture documentation

---

## Table of Contents

1. [Purpose & Philosophy](#purpose--philosophy)
2. [Citation Format](#citation-format)
3. [Tool Selection Guide](#tool-selection-guide)
4. [Writing Effective Citations](#writing-effective-citations)
5. [Verification Requirements](#verification-requirements)
6. [Testing Citations](#testing-citations)
7. [Updating Citations](#updating-citations)
8. [Examples](#examples)
9. [Integration with Existing Docs](#integration-with-existing-docs)

---

## Purpose & Philosophy

### Why Citations?

Technical architecture documentation becomes outdated quickly as codebases evolve. The citation system ensures:

1. **Verifiability** - Every claim is backed by executable proof
2. **Accuracy** - Documentation reflects actual implementation, not assumptions
3. **Maintainability** - Citations can be re-run to detect drift
4. **Trustworthiness** - Readers can verify claims themselves

### Core Principle

> **Every factual claim about the system MUST be provable via an executable command.**

If you can't prove it with a command, either:
- The claim is an assumption (mark as UNVERIFIED and ask user)
- The claim needs investigation (use Explore agent)
- The claim is about behavior, not structure (use different verification method)

---

## Citation Format

Citations use **markdown footnote syntax** with an executable verification command:

```markdown
Main claim text here.[^1]

[^1]: **Claim Summary** - Description of what's being verified; Verify: `command-to-verify`
```

### Anatomy of a Citation

```markdown
[^1]: **Frontend Port 3000** - frontend service in docker-compose.yaml; Verify: `yq -r '.services.frontend.ports[]' docker-compose.yaml`
      ─┬─  ────────┬──────────  ──────────────────┬──────────────────────            ────────────────────────┬─────────────────────────
       │           │                               │                                                          │
    Footnote   Bold claim              Plain description                                        Executable verification command
    number      summary                 (context/location)                                       (must return exit code 0)
```

**Key Components:**
1. **Footnote number** - Sequential numbering `[^1]`, `[^2]`, etc.
2. **Bold claim summary** - The key fact being stated (e.g., **Frontend Port 3000**)
3. **Description** - Context about where/how this is implemented
4. **Verify command** - Executable command in backticks that proves the claim

---

## Tool Selection Guide

Choose the right tool based on the file type and query complexity:

### Decision Tree

```
File type?
├─ JSON → Use jq
├─ YAML → Use yq
├─ TOML → Use grep (no tomlq in environment)
├─ Python (.py) → Use grep or ast-grep
├─ TypeScript/JavaScript → Use grep or ast-grep
└─ Other text → Use grep
```

### Tool Comparison

| Tool | Best For | Strengths | When NOT to Use |
|------|----------|-----------|-----------------|
| **yq** | YAML files | Structural queries, handles formatting variations, precise field extraction | Non-YAML files |
| **jq** | JSON files | Structural queries, handles formatting variations, precise field extraction | Non-JSON files |
| **grep** | Text patterns, Python/TS code | Universal, fast, good for class/function names | Structured data (YAML/JSON) |
| **ast-grep** | Complex code patterns | AST-aware, precise code structure matching | Simple text patterns, config files |

### yq (YAML Query)

**Use for:**
- docker-compose.yaml
- Agent config.yml files
- Kubernetes manifests
- Any YAML configuration

**Examples:**
```bash
# Service ports
yq -r '.services.frontend.ports[]' docker-compose.yaml

# Nested config values
yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml

# Docker image versions
yq -r '.services.postgres.image' docker-compose.yaml
```

**Advantages:**
- Handles whitespace/indentation changes
- Doesn't break if key order changes
- Extracts exact values (no regex needed)
- Clear intent (shows field path)

### jq (JSON Query)

**Use for:**
- package.json
- tsconfig.json
- OpenAPI specs
- Any JSON files

**Examples:**
```bash
# Package dependencies
jq -r '.dependencies.next' repos/dem2-webui/package.json

# Nested objects
jq -r '.scripts.build' package.json

# Array access
jq -r '.engines.node' package.json
```

**Advantages:**
- Same as yq but for JSON
- Handles formatting variations
- Precise field extraction

### grep (Text Pattern Matching)

**Use for:**
- Python class/function definitions
- TypeScript interfaces/types
- Configuration values in TOML files
- Simple text patterns

**Examples:**
```bash
# Class definitions
grep 'class AgentName' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/names.py

# Function definitions
grep 'def _attach_cookies' repos/dem2/services/auth/src/machina/auth/auth_service.py

# TOML values (no tomlq available)
grep 'requires-python' repos/dem2/pyproject.toml

# Constants
grep 'PAGE_RENDER_CONCURRENCY = 3' repos/dem2/services/docproc/src/machina/docproc/extractor/pipeline.py
```

**When to use grep:**
- Searching for specific code constructs (class/function names)
- TOML files (no better tool available)
- When exact text match is sufficient
- Simple patterns that won't change

**When NOT to use grep:**
- YAML files (use yq instead)
- JSON files (use jq instead)
- When whitespace/formatting might change

### ast-grep (AST-Aware Code Search)

**Use for:**
- Complex code structure patterns
- Language-aware queries (Python, TypeScript, etc.)
- When you need to match code semantics, not just text

**Not commonly needed for simple citations** - grep is usually sufficient for class/function names.

---

## Writing Effective Citations

### Good Citation Checklist

- [ ] Uses most appropriate tool (yq/jq for structured data, grep for code)
- [ ] Command returns exit code 0
- [ ] Command output contains the claimed value
- [ ] Robust to minor formatting changes
- [ ] Clear what's being verified
- [ ] Uses semantic patterns (class names, field paths) not line numbers
- [ ] Includes file path in command

### Principles

#### 1. Never Use Line Numbers

**❌ Bad:**
```markdown
[^1]: **Frontend Port 3000** - `docker-compose.yaml:163` - frontend service exposes port 3000
```

**Why it's bad:** Line numbers break every time the file is edited.

**✅ Good:**
```markdown
[^1]: **Frontend Port 3000** - frontend service in docker-compose.yaml; Verify: `yq -r '.services.frontend.ports[]' docker-compose.yaml`
```

**Why it's good:** Semantic query that survives formatting changes.

#### 2. Use Structural Queries for Structured Data

**❌ Bad:**
```bash
grep '"next":' repos/dem2-webui/package.json
```

**Why it's bad:** Text pattern, fragile to quote style, spacing changes.

**✅ Good:**
```bash
jq -r '.dependencies.next' repos/dem2-webui/package.json
```

**Why it's good:** Precise field extraction, format-agnostic.

#### 3. Target Stable Code Patterns

**❌ Bad:**
```bash
grep 'port = 8000' config.py
```

**Why it's bad:** Variable assignment might change.

**✅ Good:**
```bash
grep 'class BackendConfig' config.py
```

**Why it's good:** Class names are stable identifiers.

#### 4. Include Context in Command

**❌ Bad:**
```bash
grep '3000'  # Too vague
```

**✅ Good:**
```bash
yq -r '.services.frontend.ports[]' docker-compose.yaml
```

**Why it's good:** Specific location reduces false positives.

#### 5. Use Specific Patterns Over Generic Ones

**❌ Bad:**
```bash
grep -A10 'postgres:' docker-compose.yaml | grep 'image:'
```

**Why it's bad:** Brittle, depends on context lines, multiple steps.

**✅ Good:**
```bash
yq -r '.services.postgres.image' docker-compose.yaml
```

**Why it's good:** Direct path to the field, single command.

---

## Verification Requirements

### Exit Code 0 Requirement

**Every citation command MUST return exit code 0 when executed from the repository root.**

This is non-negotiable. If a command fails:
- The citation is broken
- The documentation is incorrect
- The claim is unverified

### Testing Protocol

**Before committing any citations:**

1. Create a test script with all citation commands
2. Run the script and verify exit code 0 for ALL commands
3. Only after 100% verification, update the documentation
4. Commit both the documentation and test script

**Example Test Script:**
```bash
#!/bin/bash
set -e  # Exit on any error
cd /home/dbeal/repos/NumberOne-AI/machina-meta

echo "=== CITATION VERIFICATION TEST ==="

# Test each citation
yq -r '.services.frontend.ports[]' docker-compose.yaml > /dev/null && echo "✓ [1] Frontend port"
jq -r '.dependencies.next' repos/dem2-webui/package.json > /dev/null && echo "✓ [2] Next.js"

echo "=== ALL CITATIONS VERIFIED ==="
```

### Continuous Verification

Citations should be re-verified:
- Before any documentation release
- After major refactoring
- When updating architecture docs
- Periodically (e.g., monthly)

Create a `scripts/verify-citations.sh` script for regular testing.

---

## Testing Citations

### Manual Testing

```bash
# From repository root
cd /home/dbeal/repos/NumberOne-AI/machina-meta

# Test individual citation
yq -r '.services.frontend.ports[]' docker-compose.yaml

# Should output: 3000:3000
# Exit code should be 0
echo $?  # Should print: 0
```

### Automated Testing

Create a comprehensive test script:

```bash
#!/bin/bash
# scripts/verify-citations.sh
set -e
cd "$(git rev-parse --show-toplevel)"

echo "=== Verifying DATAFLOW.md Citations ==="

# Infrastructure citations
yq -r '.services.frontend.ports[]' docker-compose.yaml > /dev/null && echo "✓ [1] Frontend Port"
jq -r '.dependencies.next' repos/dem2-webui/package.json > /dev/null && echo "✓ [2] Next.js"
# ... all citations ...

echo "=== Verifying MULTI_AGENT_ARCHITECTURE.md Citations ==="
# ... agent citations ...

echo ""
echo "✅ All citations verified successfully"
```

Run regularly:
```bash
chmod +x scripts/verify-citations.sh
./scripts/verify-citations.sh
```

### CI/CD Integration

Add citation verification to GitHub Actions:

```yaml
name: Verify Documentation Citations

on: [push, pull_request]

jobs:
  verify-citations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          submodules: recursive

      - name: Install yq and jq
        run: |
          sudo apt-get install -y jq
          sudo pip install yq

      - name: Verify Citations
        run: ./scripts/verify-citations.sh
```

---

## Updating Citations

### When to Update

Update citations when:
1. **Code structure changes** - Class renamed, file moved, config restructured
2. **Documentation added** - New claims need new citations
3. **Citation broken** - Verification script fails
4. **Tool improvements** - Replacing grep with yq/jq for better robustness

### Update Process

1. **Identify broken/outdated citations**
   ```bash
   ./scripts/verify-citations.sh  # See which fail
   ```

2. **Research actual implementation**
   ```bash
   # Use tools to find correct patterns
   yq -r '.services' docker-compose.yaml  # Explore structure
   jq '.' package.json | less  # Browse JSON
   ```

3. **Update citations with new commands**

4. **Create comprehensive test script**
   - Test ALL updated citations
   - Verify exit code 0 for each

5. **Run tests before committing**
   ```bash
   bash /tmp/test_updated_citations.sh
   ```

6. **Commit with descriptive message**
   ```bash
   git commit -m "docs: update citations for [component] restructuring

   - Updated N citations in DATAFLOW.md
   - Replaced [old pattern] with [new pattern]
   - All citations verified with exit code 0"
   ```

### Systematic Updates

For bulk updates, use Python scripts:

```python
#!/usr/bin/env python3
"""Update citations systematically."""

replacements = [
    (
        "old citation text here",
        "new citation text here"
    ),
    # ... more replacements
]

def update_file(filepath, replacements):
    with open(filepath, 'r') as f:
        content = f.read()

    for old, new in replacements:
        content = content.replace(old, new)

    with open(filepath, 'w') as f:
        f.write(content)

update_file('docs/DATAFLOW.md', replacements)
```

This ensures consistency and prevents manual errors.

---

## Examples

### Example 1: Infrastructure Port (YAML)

**Claim:** Frontend runs on port 3000

**Citation:**
```markdown
The frontend service runs on port 3000.[^1]

[^1]: **Frontend Port 3000** - frontend service in docker-compose.yaml; Verify: `yq -r '.services.frontend.ports[]' docker-compose.yaml`
```

**Verification:**
```bash
$ yq -r '.services.frontend.ports[]' docker-compose.yaml
3000:3000
$ echo $?
0
```

✅ **Why this is good:**
- Uses yq for YAML structural query
- Direct path to the ports field
- Survives formatting changes
- Clear and unambiguous

---

### Example 2: Dependency Version (JSON)

**Claim:** Project uses Next.js 16.0.10

**Citation:**
```markdown
Built with Next.js 16.0.10.[^2]

[^2]: **Next.js 16.0.10** - Next.js dependency in dem2-webui package.json; Verify: `jq -r '.dependencies.next' repos/dem2-webui/package.json`
```

**Verification:**
```bash
$ jq -r '.dependencies.next' repos/dem2-webui/package.json
16.0.10
$ echo $?
0
```

✅ **Why this is good:**
- Uses jq for JSON field extraction
- Gets exact version number
- Format-agnostic

---

### Example 3: Python Class Definition (grep)

**Claim:** System has 11 agent types

**Citation:**
```markdown
The system implements 11 distinct agent types.[^15]

[^15]: **11 Agent Types** - `class AgentName(StrEnum)` enum in names.py defines 11 agent types; Verify: `grep 'class AgentName' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/names.py`
```

**Verification:**
```bash
$ grep 'class AgentName' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/names.py
class AgentName(StrEnum):
$ echo $?
0
```

✅ **Why this is good:**
- Class name is stable identifier
- Grep is appropriate for code structure
- File path included in command

---

### Example 4: Configuration Constant (grep)

**Claim:** Page rendering uses concurrency of 3

**Citation:**
```markdown
Pages are rendered with concurrency limit of 3.[^28]

[^28]: **Page Rendering Concurrency: 3** - `PAGE_RENDER_CONCURRENCY` constant in pipeline.py; Verify: `grep 'PAGE_RENDER_CONCURRENCY = 3' repos/dem2/services/docproc/src/machina/docproc/extractor/pipeline.py`
```

**Verification:**
```bash
$ grep 'PAGE_RENDER_CONCURRENCY = 3' repos/dem2/services/docproc/src/machina/docproc/extractor/pipeline.py
PAGE_RENDER_CONCURRENCY = 3
$ echo $?
0
```

✅ **Why this is good:**
- Matches exact constant definition
- Includes value in pattern (specific)
- Appropriate use of grep for Python code

---

### ❌ Anti-Pattern Examples

#### Bad Example 1: Line Numbers
```markdown
[^1]: **Frontend Port** - Line 163 of docker-compose.yaml
```
**Problems:**
- No verification command
- Line number will break on edits
- Not executable

#### Bad Example 2: Vague grep
```markdown
[^2]: **React Version** - Verify: `grep react package.json`
```
**Problems:**
- Could match many things (react, react-dom, etc.)
- Doesn't extract version number
- Should use jq for JSON

#### Bad Example 3: Multi-step grep
```markdown
[^3]: **Port** - Verify: `grep frontend docker-compose.yaml | grep ports | grep 3000`
```
**Problems:**
- Brittle multi-step pipeline
- Hard to understand intent
- Should use yq for structured query

#### Bad Example 4: No file path
```markdown
[^4]: **Config** - Verify: `grep 'API_KEY'`
```
**Problems:**
- No file specified
- Incomplete command
- Won't work from repo root

---

## Integration with Existing Docs

### DATAFLOW.md

**Current state:** 37 citations covering:
- Infrastructure (ports, versions, services)
- Agent system (types, models, configs)
- Document processing (concurrency, queues)
- Database schemas
- Authentication

**Citation location:** Bottom of document in "Citations" section

**Update process:** See `docs/DATAFLOW_README.md` Section 5

### MULTI_AGENT_ARCHITECTURE.md

**Current state:** 18 citations covering:
- Agent type enumeration
- Model configurations
- Tool implementations
- State management
- Callback system

**Citation location:** Bottom of document in "Citations" section

**Update process:** Follow same pattern as DATAFLOW.md

### Future Documentation

**Any new architecture documentation should:**
1. Include citations for all factual claims
2. Follow this citation system
3. Provide verification script
4. Document update process

---

## Quick Reference

### Citation Template

```markdown
Claim in main text here.[^N]

[^N]: **Bold Summary** - Description of location/context; Verify: `verification-command`
```

### Tool Selection Quick Guide

```
YAML files → yq -r '.path.to.field' file.yaml
JSON files → jq -r '.path.to.field' file.json
TOML files → grep 'pattern' file.toml
Python code → grep 'class ClassName' file.py
TypeScript → grep 'interface TypeName' file.ts
```

### Verification Quick Check

```bash
# Test one citation
command-from-citation > /dev/null && echo "✓ Works" || echo "✗ Broken"

# Check exit code
command-from-citation
echo $?  # Should be 0
```

### Common Patterns

```bash
# Service ports
yq -r '.services.SERVICE.ports[]' docker-compose.yaml

# Docker images
yq -r '.services.SERVICE.image' docker-compose.yaml

# Package dependencies
jq -r '.dependencies.PACKAGE' package.json

# Python classes
grep 'class ClassName' path/to/file.py

# Constants
grep 'CONSTANT_NAME = VALUE' path/to/file.py

# Function definitions
grep 'def function_name' path/to/file.py
```

---

## Maintenance

### Regular Tasks

**Monthly:**
- [ ] Run citation verification script
- [ ] Check for any failed citations
- [ ] Update broken citations

**Before Major Release:**
- [ ] Full citation verification
- [ ] Update documentation if needed
- [ ] Test all verification commands

**After Refactoring:**
- [ ] Identify affected citations
- [ ] Update and re-verify
- [ ] Commit changes

### Tools

**Verification Script:** `scripts/verify-citations.sh`
**Update Scripts:** `/tmp/update_*_citations.py` (create as needed)
**Test Scripts:** `/tmp/test_*_citations.sh` (create as needed)

---

## Version History

- **1.0** (2026-01-06) - Initial documentation
  - Documented grep → yq/jq upgrade
  - Established verification requirements
  - Created tool selection guide

---

## See Also

- [DATAFLOW_README.md](DATAFLOW_README.md) - Process for regenerating DATAFLOW.md
- [DIAGRAMS.md](DIAGRAMS.md) - Diagram styling standards
- [DATAFLOW.md](DATAFLOW.md) - Example of citation system in use
- [MULTI_AGENT_ARCHITECTURE.md](MULTI_AGENT_ARCHITECTURE.md) - Example of citation system in use
