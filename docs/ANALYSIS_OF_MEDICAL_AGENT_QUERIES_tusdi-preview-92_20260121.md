# Critical Analysis: Medical Agent Performance

**Source Document:** `MEDICAL_AGENT_QUERIES_tusdi-preview-92_20260121.md`
**Analysis Date:** 2026-01-21
**Environment:** tusdi-preview-92 (GKE Preview)

---

## Executive Assessment

**Overall Rating: CRITICAL**

The medical agent system exhibits severe performance degradation that renders it unsuitable for production use. With 16.7% of requests exceeding 60 seconds and a maximum response time of **11.8 minutes**, users are experiencing unacceptable latency that will drive abandonment and erode trust in the platform.

---

## Critical Findings

### 1. Unacceptable Response Time Distribution

| Category | Threshold | Actual | Target | Gap |
|----------|-----------|--------|--------|-----|
| Excellent | <5s | 31.0% | >80% | **-49pp** |
| Acceptable | <20s | 57.1% | >95% | **-38pp** |
| Critical | >60s | 16.7% | <1% | **+15.7pp** |

**Impact:** One in six user queries results in a wait time exceeding 1 minute. For a medical assistant application where users expect near-instant responses, this is a fundamental failure.

### 2. Tool Execution is the Primary Bottleneck

Analysis of the 8 critical slow queries (>100s) reveals:

| Invocation | Total | LLM Time | Tool Time | Tool % |
|------------|-------|----------|-----------|--------|
| #70 | 710.65s | 8.95s | **701.70s** | 99% |
| #80 | 432.15s | 11.13s | **421.01s** | 97% |
| #68 | 340.34s | -0.14s | **340.48s** | 100% |
| #82 | 451.64s | 57.81s | **393.83s** | 87% |

**Root Cause:** The `query_graph` tool (Neo4j queries) has no timeout mechanism and can hang indefinitely. In 4 of the 8 slowest queries, tool execution consumed >97% of total time.

### 3. Data Quality Anomalies

**Negative LLM Times Detected:**
- Invocation #68: LLM time = **-0.14s**
- Invocation #30: LLM time = **-0.00s**

This indicates timestamp recording errors in the trace logging system. The request timestamp is being recorded *after* the response timestamp in some cases, suggesting:
- Clock skew between logging calls
- Async logging race conditions
- Incorrect timestamp field assignment

**Recommendation:** Audit the `llm-traces` logging code for timing bugs.

### 4. Query Pattern Analysis

**Slow Query Categories:**

| Pattern | Count | Avg Duration | Example |
|---------|-------|--------------|---------|
| "Generate Cypher queries for N questions" | 5 | 205.2s | Multi-part graph queries |
| "tell me everything about X" | 1 | 432.2s | Unbounded data retrieval |
| "suggest a protocol for X" | 1 | 710.7s | Complex reasoning + data |
| "Show status for multiple entities" | 1 | 336.6s | Multi-entity lookup |

**Observation:** Multi-part queries ("4 natural language questions") consistently cause extreme latency. The system attempts to execute all sub-queries sequentially, compounding delays.

### 5. Agent Performance Disparity

| Agent | LLM Calls | Avg Duration | Total Time | % of Total |
|-------|-----------|--------------|------------|------------|
| HealthConsultantAgent | 67 | 16.21s | 1085.8s | **77%** |
| TriageAgent | 44 | 7.16s | 315.0s | 22% |
| UrlHandlerAgent | 2 | 3.11s | 6.2s | <1% |

**Analysis:** HealthConsultantAgent is responsible for 77% of total LLM processing time. This agent:
- Makes tool calls to `query_graph` (Neo4j)
- Often requires multiple LLM round-trips (avg 1.5 calls/invocation)
- Handles the most complex queries

TriageAgent is consistently fast (median ~3s), demonstrating that the LLM inference itself is not the bottleneck.

---

## Architecture Issues

### Issue 1: No Timeout Protection

**Current State:** Tool execution has no timeout. A single slow Neo4j query can block for 11+ minutes.

**Evidence:** Invocation #70 (`e-94b56f2b`) spent 701.70 seconds (11.7 minutes) in tool execution for a simple supplementation query.

**Required Fix:**
```python
# Add timeout to query_graph tool
async def query_graph(query: str, timeout: float = 30.0):
    async with asyncio.timeout(timeout):
        return await execute_neo4j_query(query)
```

### Issue 2: Sequential Multi-Query Execution

**Current State:** When HealthConsultantAgent receives "Generate Cypher queries for 4 questions", it executes each query sequentially.

**Evidence:** Invocation #82 made 4 LLM calls totaling 57.81s LLM time + 393.83s tool time. The queries could have been parallelized.

**Required Fix:** Implement parallel tool execution for independent queries.

### Issue 3: No Request-Level Timeout

**Current State:** There is no gateway-level timeout. Users can wait indefinitely.

**Required Fix:** Add 60-second timeout at API gateway with graceful degradation message.

### Issue 4: Unbounded Query Scope

**Current State:** Queries like "tell me everything" trigger unbounded data retrieval.

**Evidence:** Invocation #80 spent 421 seconds retrieving "everything" about a report.

**Required Fix:** Implement query scope limits and pagination for broad queries.

---

## Performance Targets vs Actual

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| P50 Response Time | 12.82s | <5s | FAIL |
| P95 Response Time | ~130s | <15s | FAIL |
| P99 Response Time | ~450s | <30s | FAIL |
| Max Response Time | 710.65s | <60s | FAIL |
| % Under 10s | 45.2% | >90% | FAIL |
| % Over 60s | 16.7% | <1% | FAIL |

**Assessment:** The system fails ALL performance targets by significant margins.

---

## Immediate Action Items

### P0 - Critical (Block Production)

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Add 30s timeout to `query_graph` tool | Prevents runaway queries | Low |
| 2 | Add 60s gateway timeout with error message | Bounds worst-case UX | Low |
| 3 | Fix timestamp recording bug (negative LLM times) | Data integrity | Low |

### P1 - High (Required for Acceptable UX)

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 4 | Implement parallel tool execution | 2-3x speedup for multi-queries | Medium |
| 5 | Add Neo4j query result caching (5min TTL) | Reduce repeated query latency | Medium |
| 6 | Pre-compute common Cypher patterns | Eliminate "Generate Cypher" overhead | Medium |

### P2 - Medium (Performance Optimization)

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 7 | Add query scope limits for broad requests | Prevent unbounded retrieval | Medium |
| 8 | Implement streaming responses | Perceived latency improvement | High |
| 9 | Add observability alerts for queries >30s | Proactive monitoring | Low |

---

## Risk Assessment

### Production Readiness: NOT READY

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| User abandonment due to latency | HIGH | HIGH | P0 actions |
| System timeout cascade | MEDIUM | MEDIUM | Gateway timeout |
| Data inconsistency (negative times) | LOW | CONFIRMED | Logging fix |
| Neo4j connection exhaustion | HIGH | MEDIUM | Query timeout + pooling |

---

## Conclusions

1. **The system is not production-ready.** 16.7% failure rate (>60s) is unacceptable.

2. **Tool execution is the bottleneck**, not LLM inference. TriageAgent (LLM-only) averages 7s; HealthConsultantAgent (LLM + tools) averages 49s.

3. **Multi-part queries are a design flaw.** "Generate Cypher for 4 questions" should not be sent to the LLM; it should be decomposed at the application layer.

4. **No timeout protection exists.** A single query can block resources for 11+ minutes with no circuit breaker.

5. **Quick wins are available.** Adding timeouts (P0 items) can cap worst-case latency with minimal code changes.

---

## Appendix: Methodology

**Data Source:** 452 LLM trace files from `/app/logs/llm-traces/` on `tusdi-api-6455c47984-dl27l`

**Analysis Period:** 2026-01-21 09:36 - 14:42 UTC (5 hours, 6 minutes)

**Tools Used:**
- `scripts/analyze_llm_traces.py` - Custom trace analyzer
- Manual inspection of slow query JSON files

**Limitations:**
- Preview environment may not reflect production load patterns
- Tool execution time includes network latency to Neo4j
- Sample size (84 invocations) is statistically limited

---

**Report Author:** Claude Code
**Review Status:** Pending engineering review
