# Proposal: Migrating to `neo4j-graphrag` for Text-to-Cypher

**Status:** PROPOSED
**Date:** 2026-01-26
**Target:** `services/medical-agent` (replacing `CypherAgent`)

## 1. Executive Summary

The current `CypherAgent` relies on a custom, fragile implementation of Text-to-Cypher (static schema injection, regex-based parsing, manual validation logic). It suffers from maintenance burden (e.g., recent variable scoping bugs, parsing errors) and lacks dynamic schema awareness.

We propose migrating to **`neo4j-graphrag`**, the official Python library from Neo4j. This library standardizes schema introspection (via APOC), prompt engineering, and query sanitization. By wrapping it with a custom security layer, we can achieve robust, schema-aware querying while enforcing strict tenant isolation.

## 2. Comparison: Current vs. Proposed

| Feature              | Current (`CypherAgent`)                                                                                          | Proposed (`neo4j-graphrag`)                                                       | Verdict                 |
|----------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-------------------------|
| **Schema Source**    | **Static JSON/YAML** (`schema.json`). Must be manually updated/synced.                                           | **Dynamic Introspection** (`apoc.meta.data`). Always in sync with DB.             | ✅ **GraphRAG**         |
| **Query Generation** | Custom prompt template + regex parsing. Prone to syntax errors (e.g., `WITH` clause bugs).                       | Optimized prompt + `extract_cypher` regex sanitization (fixes backticks, quotes). | ✅ **GraphRAG**         |
| **Security (RLS)**   | **Prompt Engineering + Regex Validation**. Injects `patient_id` via `TenantInjector` (complex, sometimes buggy). | **Neo4j PBAC + Impersonation**. Enforced by database kernel.                      | ✅ **GraphRAG**         |
| **Parameters**       | Supports bind params (`$patient_id`).                                                                            | **No native bind param support** in Text2Cypher (uses literals).                  | ❌ **Current is safer** |
| **Maintenance**      | High. We maintain the prompt, parser, and validator.                                                             | Low. Maintained by Neo4j.                                                         | ✅ **GraphRAG**         |
| **Licensing**        | Proprietary (Our code).                                                                                          | **Apache 2.0** (Open Source).                                                     | ✅ **GraphRAG**         |

## 3. Vector Search Deep Dive & Qdrant

A key question is how `neo4j-graphrag` handles vector search compared to our current architecture, especially regarding Qdrant.

### 3.1. Architecture Comparison

| Feature           | Our Current Code                                                                                                                                                   | `neo4j-graphrag`                                                                                                    |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| **Vector Store**  | **Qdrant** (via `rag_plugin.py`).                                                                                                                                  | **Qdrant** (supported via `QdrantNeo4jRetriever`).                                                                  |
| **Integration**   | **Separate Lanes**. The agent calls `rag_plugin` for docs (chunks) and `CypherAgent` for graph (nodes). They do not query together.                                | **ID Linking**. `QdrantNeo4jRetriever` queries Qdrant → gets IDs → fetches Nodes from Neo4j.                        |
| **Hybrid Cypher** | **Theoretically**. `CypherAgent` prompt mentions `db.index.vector`, but the tool code does **not** inject embeddings, so it cannot actually execute these queries. | **No Native Support**. The `Text2CypherRetriever` does not support embedding injection for `db.index.vector` calls. |
| **Retrievers**    | Custom `rag_plugin` + `semantic_router`.                                                                                                                           | Standardized `VectorRetriever`, `HybridRetriever`, `ExternalRetriever`.                                             |

### 3.2. Integration Strategy

Since `neo4j-graphrag` separates "Text-to-Cypher" (structured) from "Vector Search" (unstructured), the migration path is:

1.  **Structured Data:** Migrate `CypherAgent` to `Text2CypherRetriever` (as proposed).
2.  **Unstructured Data:** We can either:
    *   **Keep** existing `rag_plugin.py` (Low effort, already works).
    *   **Migrate** to `QdrantNeo4jRetriever` (Standardization, but requires ensuring Qdrant payload contains Neo4j IDs).

**Recommendation:** Focus on migrating **Text-to-Cypher** first. Our vector search (RAG) is currently functional and decoupled. The `neo4j-graphrag` library does *not* offer a magic "Cypher + Vector in one query" solution that we are missing; it treats them as separate retrieval strategies just like we do.

## 4. Cost Estimate

*   **Licensing:** **$0**. `neo4j-graphrag` is Apache 2.0 licensed.
*   **LLM Costs:**
    *   **Input Tokens:** Increases slightly due to richer schema context. `apoc.meta.data` produces a detailed schema representation (labels, properties, types, relationships) compared to our current "minimal" schema formatter.
    *   *Estimate:* ~2k-4k tokens per query for full schema (vs ~1k current).
    *   *Mitigation:* Use `neo4j-graphrag`'s filtering options to exclude system nodes (e.g., `_Neomodel*`) from the context window.

## 4. Security Deep Dive: Neo4j PBAC & Impersonation

The user requirement is to achieve **PatientNode LOCK** using **Neo4j Enterprise PBAC** (Policy Based Access Control). This shifts security enforcement from the application layer (fragile regex) to the database kernel (robust policies).

### 4.1. The Mechanism: Policy Based Access Control (PBAC)

Instead of injecting `WHERE` clauses into every query, we rely on Neo4j's native security:
1.  **Policies:** Define roles that restrict traversal to nodes connected to the user/patient.
    *   *Example Policy:* `GRANT TRAVERSE ON GRAPH * NODES Patient WHERE (n)-[:HAS_ACCESS]-(u:User {id: $currentUserId})`
2.  **Enforcement:** The database automatically filters out any nodes the user cannot see. If the LLM generates a query for "all patients", the result returns *only the authorized patient*.

### 4.2. Implementation: Impersonation via Custom Retriever

`neo4j-graphrag`'s `Text2CypherRetriever` executes queries using the provided driver. To leverage PBAC per-request, we must tell the driver **who** is executing the query. This is done via **Impersonation**.

**Gap:** The standard `Text2CypherRetriever` does not expose a way to pass the `impersonated_user` parameter to the driver's `execute_query` method (it is hardcoded).

**Solution:** Subclass `Text2CypherRetriever` to inject the user context.

```python
class PBACText2CypherRetriever(Text2CypherRetriever):
    def get_search_results(self, query_text: str, user_id: str, prompt_params: dict = None):
        # 1. Generate Query (reusing parent logic or accessing internal components)
        # Note: We must duplicate some logic because `get_search_results` does generation AND execution.
        
        # ... prompt construction using self.custom_prompt template ...
        # Use prompt_params to inject dynamic context (e.g. {patient_id}) into the template
        
        llm_result = self.llm.invoke(prompt)
        t2c_query = extract_cypher(llm_result.content)
        
        # 2. Execute with Impersonation
        # Neo4j applies policies based on 'user_id'
        records, _, _ = self.driver.execute_query(
            query_=t2c_query,
            database_=self.neo4j_database,
            routing_=neo4j.RoutingControl.READ,
            impersonated_user=user_id  # <--- CRITICAL INJECTION
        )
        
        return RawSearchResult(records=records, metadata={"cypher": t2c_query})
```

**Prompt Engineering Strategy:**
While PBAC enforces security, we still need the LLM to write meaningful queries. We will use `custom_prompt` templates with `prompt_params` to inject context:
*   Template: `... Context: You are user {user_id} viewing patient {patient_id} ...`
*   Injection: `retriever.get_search_results(..., prompt_params={"patient_id": "123"})`

### 4.3. Comparison

| Feature        | TenantInjector (Old)              | GraphRAG + PBAC (Proposed)          |
|----------------|-----------------------------------|-------------------------------------|
| **Mechanism**  | Regex Injection (`WHERE ...`)     | Database Policy + Impersonation     |
| **Robustness** | Low (Fragile parsing)             | High (Kernel enforcement)           |
| **LLM Risk**   | High (Leakage if injection fails) | None (LLM cannot bypass DB policy)  |
| **Complexity** | High App Complexity               | High DB Config / Low App Complexity |

**Conclusion:** This is the ideal architecture. It removes the need for complex/fragile query parsing in Python and leverages the Enterprise database features we are paying for.


## 5. Migration Plan

### Phase 1: Integration & Proof of Concept (Done)
*   [x] Add `neo4j-graphrag` dependency.
*   [x] Create `graphrag_cli.py` to verify connectivity and schema introspection.
*   [x] Enable APOC in infrastructure (Prerequisite for native schema introspection).

### Phase 2: Implementation of Safe Components
*   [ ] Create `PBACText2CypherRetriever` class (implements impersonation).
*   [ ] Integrate with `GoogleGenAILLM` adapter.

### Phase 3: Agent Migration
*   [ ] Modify `CypherAgent` (or `ExpertCypherAgent`) to use `SafeText2CypherRetriever` for query generation instead of the current custom prompt templates.
*   [ ] Replace `GraphTraversalService.execute_query` calls with the new flow (or wrap the new flow inside `GraphTraversalService`).

### Phase 4: Cleanup
*   [ ] Remove legacy schema formatting code (`schema_formatter.py`).
*   [ ] Remove manual regex parsing logic in `CypherAgent`.

## 6. Addressing Current Problems

This migration directly addresses several open issues in `TODO.md` and `PROBLEMS.md`:

*   **"Neo4j agent queries slow without visibility"**: While GraphRAG doesn't fix performance per se, standardizing the generation pipeline makes it easier to inject `PROFILE` commands consistently.
*   **"Variable scope errors" (CypherAgent)**: The `neo4j-graphrag` prompt templates are battle-tested by Neo4j's team to handle variable scoping (WITH clauses) more robustly than our custom template.
*   **"Enhance schema discovery capabilities"**: This is the core value proposition. The agent will always see the *actual* database schema via APOC, eliminating drift between `schema.json` and reality.
