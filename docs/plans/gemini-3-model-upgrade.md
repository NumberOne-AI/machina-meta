# Model Upgrade Plan for ADK Multi-Agent Framework

**Status:** IMPLEMENTED (2026-01-16)
**Implementation:** See [docs/MODEL_CHANGES.md](../MODEL_CHANGES.md)

---

## Final Decision

After brainstorming multiple options, the following approach was chosen:

### Decision: Uniform Gemini 3.0 Preview Upgrade

**Rationale:**
- **Primary goal:** Quality improvement (not cost optimization)
- **Constraint:** Must use Google ADK (Gemini models only)
- **Risk tolerance:** Preview models acceptable with monitoring
- **Rule:** No downgrades - all agents upgrade to latest available

**Implementation:**
- **8 agents:** `gemini-2.5-pro` → `gemini-3-pro-preview`
- **6 agents:** `gemini-2.5-flash` → `gemini-3-flash-preview`
- **14 total agents** upgraded

**Why no downgrades:**
- Downgrades were considered for cost optimization but rejected
- Quality improvement is the primary goal
- Uniform upgrade simplifies testing and rollback

**Verification Plan:**
1. Deploy to preview environment
2. Run manual QA on all agent types
3. Monitor for prompt compatibility issues
4. Compare response quality against 2.5 baseline
5. Gradual production rollout based on metrics

---

# Brainstorming Document (Historical)

The following sections document the analysis and options that were considered before making the final decision.

---

## Current State Analysis (Before Upgrade)

### Models in Use

| Model | Agents Using It | Purpose |
|-------|-----------------|---------|
| `gemini-2.5-flash` | TriageAgent, CypherAgent, FastGraphSummaryAgent, GraphMapAgent, GraphReduceSummaryAgent, AskTusdiAIHandlerAgent | Fast routing, simple queries |
| `gemini-2.5-pro` | HealthConsultantAgent, HealthConsultantLiteAgent, DataExtractorAgent, MedicalMeasurementsAgent, MedicalContextAgent, GoogleSearchAgent, DataEntryAgent, UrlHandlerAgent | Complex reasoning, medical consultation |

### Architecture Constraints

1. **Gemini-only validation** in `configurator.py:42`:
   ```python
   if not v.startswith("gemini"):
       raise ValueError(f"Only 'gemini' models are supported, not {v}")
   ```

2. **Google ADK dependency** - Framework tied to Google ecosystem

3. **Config-driven models** - Each agent has `model:` in its `config.yml`

4. **Environment override** - `CONFIGURATOR_MODEL_OVERRIDE` allows runtime switching

### Key Files
- Agent configs: `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/*/config.yml`
- Factory: `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/factory.py`
- Configurator: `repos/dem2/services/medical-agent/src/machina/medical_agent/common/configurator.py`

---

## Brainstorming Options

### Option 1: Upgrade to Gemini 2.5 Flash-002 / Pro-002

**What**: Use the latest Gemini 2.5 point releases

**Pros**:
- Minimal code changes (just update model strings in configs)
- Better performance/quality from updated models
- Maintains current architecture

**Cons**:
- Incremental improvement, not transformative
- Limited by Google's release schedule

**Effort**: Low - config changes only

---

### Option 2: Introduce Gemini 2.5 Pro Exp (Experimental)

**What**: Use `gemini-2.5-pro-exp-03-25` or similar experimental models for specific agents

**Pros**:
- Access to cutting-edge capabilities
- Can A/B test against stable models

**Cons**:
- Experimental models may be unstable
- Could be deprecated without notice

**Effort**: Low - add experimental config versions

---

### Option 3: Upgrade to Gemini 3.0 Preview

**What**: Already referenced in codebase (`gemini-3.0-pro-preview`, `config_3.yml`)

**Pros**:
- Already partially implemented (version configs exist)
- Significant capability jump expected
- Long context, better reasoning

**Cons**:
- Preview may have rough edges
- Need to update/test all prompts for new model
- Unknown release timeline for GA

**Effort**: Medium - testing and prompt tuning required

---

### Option 4: Multi-Provider Support (Claude, GPT-4)

**What**: Remove Gemini-only restriction, enable Claude/OpenAI models

**Pros**:
- Access to Claude 4.5 Opus for complex medical reasoning
- GPT-4 as fallback/alternative
- Provider redundancy for reliability
- Already have Anthropic integration in docproc/medical-catalog

**Cons**:
- Significant code changes to ADK integration
- Different tool calling patterns between providers
- Higher complexity in testing/maintenance
- Google ADK designed for Gemini

**Effort**: High - requires ADK abstraction layer

---

### Option 5: Task-Based Model Routing

**What**: Dynamic model selection based on query complexity/type

**Pros**:
- Optimize cost (Flash for simple, Pro for complex)
- Better latency for simple queries
- Adaptive quality based on need

**Implementation Ideas**:
- Complexity classifier before routing
- Token budget estimation
- Query type detection (lookup vs reasoning)

**Cons**:
- Added latency for classification step
- More complex debugging
- Potential misclassification issues

**Effort**: Medium - new routing logic needed

---

### Option 6: Flash-First Architecture

**What**: Default to Flash, escalate to Pro only when needed

**Current**:
```
User Query → TriageAgent (Flash) → HealthConsultant (Pro)
```

**Proposed**:
```
User Query → TriageAgent (Flash) → HealthConsultantLite (Flash)
                                 → [if complex] → HealthConsultant (Pro)
```

**Pros**:
- Significant cost reduction (Flash is ~8x cheaper)
- Faster response times for simple queries
- Better user experience for quick lookups

**Cons**:
- Risk of quality degradation for edge cases
- Need robust complexity detection
- More agents to maintain

**Effort**: Medium - add complexity detection, adjust agent hierarchy

---

### Option 7: Context Window Optimization

**What**: Leverage Gemini 2.5 Pro's 2M token context window better

**Ideas**:
- Pre-load full patient history into context
- Include complete medical knowledge base
- Enable multi-document reasoning in single call

**Pros**:
- Richer context for better answers
- Reduced tool calling overhead
- Better multi-turn conversations

**Cons**:
- Higher input token costs
- Longer initial response time
- Context management complexity

**Effort**: Medium - prompt engineering and context loading changes

---

### Option 8: Specialized Model Fine-Tuning

**What**: Fine-tune Gemini models for medical domain

**Pros**:
- Domain-specific performance improvements
- Better medical terminology handling
- More consistent outputs

**Cons**:
- Requires training data curation
- Google fine-tuning APIs needed
- Ongoing maintenance of fine-tuned models
- Significant upfront investment

**Effort**: High - data preparation, training, evaluation pipeline

---

### Option 9: Hybrid Extraction Pipeline

**What**: Use different models for different extraction types

**Current**: All extractors use same model
**Proposed**:
- MedicalMeasurementsAgent: Flash (structured, well-defined)
- MedicalContextAgent: Flash (relationship extraction)
- DataExtractorAgent: Pro (nuanced medical understanding)

**Pros**:
- Cost optimization
- Faster parallel extraction
- Appropriate model for each task

**Cons**:
- More configs to maintain
- Need to validate extraction quality per agent

**Effort**: Low - config changes + validation

---

### Option 10: Thinking Models (o1-style)

**What**: Use Gemini's thinking/reasoning models when available

**Pros**:
- Better for complex medical reasoning chains
- Self-correcting outputs
- More reliable for diagnostic suggestions

**Cons**:
- Not yet generally available for Gemini
- Higher latency and cost
- May be overkill for simple queries

**Effort**: Low when available - config changes

---

## Questions for Discussion

1. **Primary goal**: Cost reduction, quality improvement, or both?

2. **Provider flexibility**: Is staying Google-only acceptable, or is multi-provider a requirement?

3. **Timeline**: Are there upcoming Gemini releases we should wait for?

4. **Risk tolerance**: Comfortable with experimental/preview models in production?

5. **Budget**: Current LLM costs? Target reduction percentage?

6. **Quality metrics**: How are we measuring consultation quality today?

7. **Specific pain points**: Which agents have quality issues that need attention?

8. **Document processing**: Should we align models with docproc (which uses Claude)?

---

## Recommended Starting Points

### Quick Wins (Low Effort, Immediate Value)
1. **Update Flash agents to Flash-002** if available
2. **Move MedicalMeasurementsAgent to Flash** (structured extraction doesn't need Pro)
3. **Add Gemini 3.0 preview configs** for A/B testing

### Medium-Term (Requires Planning)
4. **Implement task-based routing** with complexity detection
5. **Evaluate Claude for HealthConsultant** via abstraction layer

### Strategic (Longer Term)
6. **Multi-provider abstraction** for resilience
7. **Fine-tuning evaluation** for medical domain

---

## User Requirements

Based on discussion:
- **Primary Goal**: Quality improvement
- **Constraint**: Staying with Google ADK (Gemini models only)
- **Risk Tolerance**: Preview models OK with monitoring

---

## Recommended Implementation Plan (Gemini-Only)

### Phase 1: Gemini Model Upgrades

**Available Gemini Models** (verified from `gcloud ai model-garden models list`):

| Model | Status | Context | Best For |
|-------|--------|---------|----------|
| `gemini-2.5-flash` | GA | 1M | **Current** - Routing, simple tasks |
| `gemini-2.5-flash-lite` | GA | 1M | Even cheaper/faster for trivial tasks |
| `gemini-2.5-pro` | GA | 2M | **Current** - Complex medical reasoning |
| `gemini-3-flash-preview` | Preview | ? | **NEW** - Next-gen fast model |
| `gemini-3-pro-preview` | Preview | ? | **NEW** - Next-gen reasoning |
| `gemini-3-pro-image-preview` | Preview | ? | Multimodal (image understanding) |

**Note**: No `-002` versions available. The models you have are already the latest GA versions.

**Immediate Actions**:
1. Test `gemini-3-pro-preview` for HealthConsultantAgent (quality improvement focus)
2. Evaluate `gemini-2.5-flash-lite` for structured extraction agents (cost optimization)
3. Prepare `config_3.yml` configs for Gemini 3.0 preview rollout

### Phase 2: Agent-Specific Model Optimization

> **NOTE:** This section shows the original analysis. The final decision was to upgrade ALL agents uniformly (no downgrades). See "Final Decision" section at top.

**Original Analysis (SUPERSEDED)**:

| Agent | Before | Originally Proposed | Final Decision |
|-------|--------|---------------------|----------------|
| TriageAgent | 2.5-flash | 3-flash-preview | ✅ 3-flash-preview |
| HealthConsultantAgent | 2.5-pro | 3-pro-preview | ✅ 3-pro-preview |
| HealthConsultantLiteAgent | 2.5-pro | ~~2.5-flash~~ | ✅ 3-pro-preview (no downgrade) |
| DataExtractorAgent | 2.5-pro | 3-pro-preview | ✅ 3-pro-preview |
| MedicalMeasurementsAgent | 2.5-pro | ~~2.5-flash-lite~~ | ✅ 3-pro-preview (no downgrade) |
| MedicalContextAgent | 2.5-pro | ~~2.5-flash-lite~~ | ✅ 3-pro-preview (no downgrade) |
| CypherAgent | 2.5-flash | ~~keep~~ | ✅ 3-flash-preview (upgrade) |
| FastGraphSummaryAgent | 2.5-flash | ~~2.5-flash-lite~~ | ✅ 3-flash-preview (no downgrade) |
| UrlHandlerAgent | 2.5-pro | 3-pro-preview | ✅ 3-pro-preview |
| GoogleSearchAgent | 2.5-pro | ~~2.5-flash~~ | ✅ 3-pro-preview (no downgrade) |
| DataEntryAgent | 2.5-pro | ~~2.5-flash~~ | ✅ 3-pro-preview (no downgrade) |
| GraphMapAgent | 2.5-flash | 3-flash-preview | ✅ 3-flash-preview |
| GraphReduceSummaryAgent | 2.5-flash | 3-flash-preview | ✅ 3-flash-preview |
| AskTusdiAIHandlerAgent | 2.5-flash | 3-flash-preview | ✅ 3-flash-preview |

**Final Strategy (IMPLEMENTED)**:
- **ALL Pro agents** → `gemini-3-pro-preview` (8 agents)
- **ALL Flash agents** → `gemini-3-flash-preview` (6 agents)
- **No downgrades** - rejected cost optimization in favor of quality improvement

### Phase 3: Gemini 3.0 Preview Evaluation

**Models Available**:
- `gemini-3-pro-preview` - Advanced reasoning (use for medical consultation)
- `gemini-3-flash-preview` - Fast routing (use for triage, simple tasks)

**Evaluation Plan**:
1. Deploy Gemini 3.0 preview to **preview environment only**
2. Run quality benchmark suite (if exists) or manual testing
3. Compare against 2.5-pro baseline
4. Measure: accuracy, latency, token usage, edge cases

**Rollout Strategy**:
- Phase A: Test in preview environment with manual QA
- Phase B: A/B test with 10% traffic (via environment variable override)
- Phase C: Gradual increase based on quality metrics

### Phase 4: Prompt Optimization for New Models

**When upgrading models, prompts may need adjustment**:

1. **Review system prompts** for deprecated patterns
2. **Test structured output** with new models
3. **Tune temperature** - newer models may need adjustment
4. **Verify tool calling** behavior unchanged

**Key Prompts to Review**:
- `HealthConsultantAgent/config.yml` - 184 lines, complex reasoning
- `TriageAgent/config.yml` - 157 lines, routing logic
- `DataExtractorAgent/config.yml` - extraction rules

### Phase 5: Quality Measurement Framework

**Metrics to Track**:
1. **Medical accuracy** - Correctness of health information
2. **Extraction completeness** - All entities captured
3. **Routing accuracy** - Correct agent selection
4. **Hallucination rate** - Made-up information
5. **Response latency** - Time to first token, total time

**Implementation**:
- Log all agent inputs/outputs with model version
- Build evaluation dataset from production queries
- Automated regression tests on model changes

---

## Critical Files Modified

### Agent Configs (model field) - UPDATED 2026-01-16
```
repos/dem2/services/medical-agent/src/machina/medical_agent/agents/
├── HealthConsultantAgent/config.yml      # gemini-3-pro-preview
├── DataExtractorAgent/config.yml         # gemini-3-pro-preview
├── UrlHandlerAgent/config.yml            # gemini-3-pro-preview
├── HealthConsultantLiteAgent/config.yml  # gemini-3-pro-preview
├── MedicalMeasurementsAgent/config.yml   # gemini-3-pro-preview
├── MedicalContextAgent/config.yml        # gemini-3-pro-preview
├── DataEntryAgent/config.yml             # gemini-3-pro-preview
├── GoogleSearchAgent/config.yml          # gemini-3-pro-preview
├── TriageAgent/config.yml                # gemini-3-flash-preview
├── CypherAgent/config.yml                # gemini-3-flash-preview
├── FastGraphSummaryAgent/config.yml      # gemini-3-flash-preview
├── GraphMapAgent/config.yml              # gemini-3-flash-preview
├── GraphReduceSummaryAgent/config.yml    # gemini-3-flash-preview
└── AskTusdiAIHandlerAgent/config.yml     # gemini-3-flash-preview
```

### Configurator (if model names change format)
```
repos/dem2/services/medical-agent/src/machina/medical_agent/common/configurator.py
```

---

## Verification Plan

1. **Unit tests** - Ensure configs load correctly
2. **Integration tests** - Agent responses valid
3. **Quality benchmarks** - Compare old vs new models
4. **Preview environment** - Full stack testing
5. **Gradual rollout** - Monitor production metrics

---

## Open Questions (RESOLVED)

1. **Gemini 3.0 preview stability**: Comfortable using preview models for key agents (HealthConsultant, DataExtractor)?
   - ✅ **RESOLVED**: Yes, preview models acceptable with monitoring

2. **Quality benchmarks**: Do you have an existing evaluation dataset, or need to create one for regression testing?
   - 🔄 **PENDING**: Manual QA in preview environment first

3. **Flash-lite downgrade concerns**: Any agents where downgrading to flash-lite might hurt quality? (Proposed for MedicalMeasurements, MedicalContext, FastGraphSummary)
   - ✅ **RESOLVED**: No downgrades - decision made to upgrade all agents uniformly

4. **Rollout approach**: Start with preview environment testing, or jump to A/B in production?
   - ✅ **RESOLVED**: Preview environment testing first, then gradual rollout
