# LLM.md Regeneration Guide

**Version:** 1.0
**Last Updated:** 2026-01-06
**Purpose:** Instructions for regenerating and maintaining LLM.md

---

## Table of Contents

1. [Purpose](#purpose)
2. [How LLM.md Was Produced](#how-llmmd-was-produced)
3. [When to Update LLM.md](#when-to-update-llmmd)
4. [Regeneration Process](#regeneration-process)
5. [Verification Requirements](#verification-requirements)
6. [Maintenance Checklist](#maintenance-checklist)

---

## Purpose

**LLM.md** is a comprehensive reference document for LLM integration and prompt engineering across the machina-meta workspace. It focuses specifically on:

- LLM provider integrations (Google, Anthropic, OpenAI)
- Prompt engineering patterns and best practices
- System prompt architecture and design
- Template systems and context injection
- Model configuration and cost management
- Prompt versioning and testing

**Related Documents**:
- [MULTI_AGENT_ARCHITECTURE.md](docs/MULTI_AGENT_ARCHITECTURE.md) - Covers agent architecture and tool use patterns (referenced by LLM.md)
- [DATAFLOW.md](docs/DATAFLOW.md) - System-wide data flow including LLM interactions
- [CITATIONS.md](docs/CITATIONS.md) - Citation system used for verification

---

## How LLM.md Was Produced

### Initial Creation Process (2026-01-06)

**Step 1: Comprehensive Exploration**
```bash
# Used Explore agent to systematically search entire workspace
# Prompt: "Search the entire machina-meta workspace to find all LLM/AI integrations..."
# Agent ID: ad080fb (for resuming if needed)
```

**Areas Searched**:
1. **LLM Provider Integrations**
   - repos/dem2/services/medical-agent/
   - repos/dem2/services/docproc/
   - repos/medical-catalog/
   - API clients, configurations, proxy implementations

2. **System Prompts and Instructions**
   - All agent config YAML files
   - Prompt template files
   - Instruction composition patterns

3. **Tool Use Patterns**
   - Google ADK agents and tools
   - Function calling patterns
   - Tool definitions and wrappers

4. **Agent Configurations**
   - Agent config files (YAML)
   - Model selections
   - Generate content parameters

5. **Prompt Engineering Patterns**
   - How prompts are built dynamically
   - Prompt chaining
   - Context injection methods

6. **Frontend LLM Interactions**
   - repos/dem2-webui/src/lib/*-prompt.ts
   - Prompt utility files

**Step 2: Document Structure Design**
- Focused on prompt engineering (not agent architecture)
- Removed redundancy with MULTI_AGENT_ARCHITECTURE.md
- Added cross-references to related documentation
- Organized by functional areas (providers, prompts, templates, etc.)

**Step 3: Citation System Implementation**
- Added 55 citations following docs/CITATIONS.md guidelines
- Used yq/jq for structured files (YAML/JSON)
- Used grep for code patterns
- All citations are executable commands that return exit code 0

**Step 4: Verification**
- All facts verified from actual source code
- No assumptions or speculative claims
- All file paths confirmed to exist
- All configuration values verified

---

## When to Update LLM.md

Update LLM.md when ANY of these changes occur:

### 1. LLM Provider Changes
- [ ] New LLM provider added (e.g., new Anthropic/OpenAI/Google model)
- [ ] Provider integration code modified
- [ ] API client configuration changed
- [ ] Proxy architecture updated

**Example**: Adding support for GPT-5.5 or Claude 5.0

### 2. System Prompt Changes
- [ ] Agent prompts modified (any config.yml file)
- [ ] New routing rules added to TriageAgent
- [ ] Reasoning framework changed in HealthConsultantAgent
- [ ] Extraction granularity rules updated in DataExtractorAgent
- [ ] New agent types added

**Example**: HealthConsultantAgent prompt updated with new body system mappings

### 3. Prompt Template System Changes
- [ ] Template rendering engine modified
- [ ] New context variables added
- [ ] Schema injection patterns changed
- [ ] Callback system updated

**Example**: Adding new {patient_medications?} context variable

### 4. Model Configuration Changes
- [ ] New models added or removed
- [ ] Model selection strategy changed
- [ ] Generate content configuration updated (temperature, tokens, etc.)
- [ ] Cost structure modified

**Example**: Switching DataExtractorAgent from gemini-2.5-pro to gemini-3.0-pro

### 5. Cost Management Changes
- [ ] Rate limiting configuration modified
- [ ] Token tracking implementation changed
- [ ] Streaming threshold adjusted
- [ ] Model pricing updated

**Example**: Changing rate limit from 60 to 120 requests/minute

### 6. New Prompt Engineering Patterns
- [ ] New domain-specific prompts added
- [ ] New structured output schemas created
- [ ] New context injection patterns implemented
- [ ] Multi-agent coordination patterns changed

**Example**: Adding new medical catalog prompt for Phase 4 validation

---

## Regeneration Process

### Full Regeneration (Recommended for Major Changes)

**When**: Major architectural changes, multiple agent updates, or quarterly review

**Process**:

```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta

# Step 1: Launch Explore agent for comprehensive search
# Use claude-code with this prompt:
```

**Prompt Template**:
```
Update LLM.md to reflect recent changes in the codebase.

Search the entire machina-meta workspace for:

1. LLM Provider Integrations
   - New providers or models
   - Configuration changes
   - Proxy updates

2. System Prompts (ALL agent config.yml files)
   - Changed prompts
   - New agents
   - Modified instructions

3. Prompt Engineering Patterns
   - Template system changes
   - New context variables
   - Updated schemas

4. Model Configuration
   - Model selection changes
   - Generate config updates
   - Cost structure changes

5. Frontend Prompt Utilities
   - New prompt helper files
   - Updated TypeScript utilities

Verify all information from actual source code. Update:
- docs/LLM.md
- Update version number
- Update "Last Updated" date
- Update all affected citations

Test all citations before committing.
```

**Step 2: Manual Review**
```bash
# Read the updated LLM.md
cat docs/LLM.md | less

# Verify structure:
# - Clear organization
# - No redundancy with MULTI_AGENT_ARCHITECTURE.md
# - Proper cross-references
# - All citations present
```

**Step 3: Verification**
```bash
# Create verification script
cat > /tmp/verify_llm_citations.sh << 'EOF'
#!/bin/bash
set -e
cd /home/dbeal/repos/NumberOne-AI/machina-meta

echo "=== Verifying LLM.md Citations ==="

# Extract and test each citation command
# (Add all citation verification commands here)

echo "✅ All citations verified"
EOF

chmod +x /tmp/verify_llm_citations.sh
./tmp/verify_llm_citations.sh
```

**Step 4: Update Documentation Cross-References**
```bash
# Ensure CLAUDE.md references LLM.md appropriately
# Ensure README.md references LLM.md appropriately
grep -n "LLM.md" CLAUDE.md README.md
```

**Step 5: Commit**
```bash
git add docs/LLM.md docs/LLM_README.md
git commit -m "docs: update LLM.md for [describe changes]

- Updated [section] for [reason]
- Added [new pattern/provider/etc]
- Verified all [N] citations
- Version [X.Y]"
```

### Incremental Update (for Specific Changes)

**When**: Single agent prompt update, model config change, or isolated modification

**Process**:

**Step 1: Identify Affected Section**
```bash
# Determine which section needs updating
# Examples:
# - "System Prompt Architecture" for prompt changes
# - "Model Configuration" for model updates
# - "LLM Provider Integrations" for new providers
```

**Step 2: Research Change**
```bash
# Read the modified files
cat repos/dem2/services/medical-agent/src/machina/medical_agent/agents/AgentName/config.yml

# Verify configuration
yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/AgentName/config.yml
```

**Step 3: Update Specific Section**
```bash
# Edit docs/LLM.md
# Update only the affected section
# Update citations if needed
# Update "Last Updated" date
```

**Step 4: Test Affected Citations**
```bash
# Test only the citations for updated section
yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/AgentName/config.yml
# Should return expected value
```

**Step 5: Commit**
```bash
git add docs/LLM.md
git commit -m "docs: update LLM.md [AgentName] prompt

- Updated [specific change]
- Verified citation [^N]"
```

---

## Verification Requirements

### Citation Verification

**All citations MUST return exit code 0**

**Test Individual Citation**:
```bash
cd /home/dbeal/repos/NumberOne-AI/machina-meta

# Example citation test
yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml
# Expected: gemini-2.5-flash
echo $?
# Expected: 0
```

**Test All Citations**:
```bash
# Create comprehensive test script with ALL citation commands
# Run before committing any changes to LLM.md

#!/bin/bash
set -e
cd /home/dbeal/repos/NumberOne-AI/machina-meta

# Test each citation command
ls repos/medical-catalog/src/llm/providers/*.py | wc -l  # Should be 3
grep 'from google.adk.agents import' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py
yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/TriageAgent/config.yml
# ... (all 55 citations)

echo "✅ All citations verified"
```

### Content Verification

**Verify Against Source Code**:
- [ ] All file paths exist
- [ ] All configuration values are accurate
- [ ] All code patterns match actual implementation
- [ ] All prompt excerpts match actual config.yml files
- [ ] Model names and versions are current
- [ ] Pricing information is up-to-date

**Cross-Reference Verification**:
- [ ] References to MULTI_AGENT_ARCHITECTURE.md are accurate
- [ ] No redundant information with MULTI_AGENT_ARCHITECTURE.md
- [ ] All links work (internal and external)

---

## Maintenance Checklist

### Monthly Review
- [ ] Check for new LLM providers or models
- [ ] Verify model pricing is current
- [ ] Review agent config.yml files for changes
- [ ] Test all citations (run verification script)
- [ ] Update "Last Updated" date if changes made

### After Major Releases
- [ ] Full regeneration recommended
- [ ] Verify all agent prompts
- [ ] Check for new prompt engineering patterns
- [ ] Update cost management section
- [ ] Test all citations

### After Prompt Changes
- [ ] Update affected agent prompt section
- [ ] Update prompt length if changed significantly
- [ ] Verify citation for that agent's config
- [ ] Update version number
- [ ] Update "Last Updated" date

### After Model Changes
- [ ] Update model configuration section
- [ ] Update model selection matrix
- [ ] Update pricing table if affected
- [ ] Verify citations for model configs
- [ ] Update related agents

---

## Quick Reference Commands

### Find All Agent Configs
```bash
find repos/dem2/services/medical-agent/src/machina/medical_agent/agents/ -name "config.yml" | sort
```

### Count Agent Types
```bash
grep 'class AgentName' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/names.py
```

### List LLM Providers
```bash
ls repos/medical-catalog/src/llm/providers/*.py
```

### Check Model Configurations
```bash
yq -r '.model' repos/dem2/services/medical-agent/src/machina/medical_agent/agents/*/config.yml | sort | uniq -c
```

### Find Prompt Length
```bash
wc -l repos/dem2/services/medical-agent/src/machina/medical_agent/agents/*/config.yml
```

### Check LLM Proxy Config
```bash
grep 'rate_limit_per_minute\|max_concurrent' repos/medical-catalog/src/llm/proxy.py
```

---

## Document Structure

LLM.md follows this organization:

1. **Overview** - Summary and related docs
2. **LLM Provider Integrations** - Google, Anthropic, OpenAI, Proxy
3. **Prompt Engineering Fundamentals** - Core principles
4. **System Prompt Architecture** - Agent prompts in detail
5. **Prompt Template System** - Rendering and injection
6. **Domain-Specific Prompts** - Frontend, DocProc, Medical Catalog
7. **Structured Output Prompting** - Pydantic schemas
8. **Context Injection Patterns** - Dynamic context
9. **Multi-Agent Prompt Coordination** - Agent-as-tool patterns
10. **Model Configuration** - Model selection and settings
11. **Cost Management** - Rate limiting, token tracking
12. **Prompt Versioning and Testing** - Version control, testing
13. **Citations** - All verifiable claims

---

## Version History

- **1.0** (2026-01-06) - Initial creation
  - Comprehensive exploration of entire workspace
  - 55 citations following CITATIONS.md guidelines
  - Focus on prompt engineering (not agent architecture)
  - Clear separation from MULTI_AGENT_ARCHITECTURE.md
  - Cross-references to related documentation

---

## See Also

- [LLM.md](docs/LLM.md) - The actual LLM integration and prompt engineering documentation
- [MULTI_AGENT_ARCHITECTURE.md](docs/MULTI_AGENT_ARCHITECTURE.md) - Agent architecture and tool use patterns
- [CITATIONS.md](docs/CITATIONS.md) - Citation system guidelines
- [DATAFLOW.md](docs/DATAFLOW.md) - System data flow architecture
- [DATAFLOW_README.md](docs/DATAFLOW_README.md) - Similar regeneration guide for DATAFLOW.md
