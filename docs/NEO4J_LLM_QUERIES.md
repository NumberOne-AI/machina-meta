# Neo4j Query Generation in MachinaMed

This document details how MachinaMed agents generate and execute Cypher queries against the Neo4j graph database.

## Overview

The system employs a dual-strategy approach for querying the graph:
1.  **Dynamic Generation**: LLM-driven generation for novel or complex natural language questions.
2.  **Static Templates**: Pre-defined, optimized queries for common use cases (semantic routing).

In both cases, queries are handled as **raw Cypher strings**. The system does not use a programmatic query builder (ORM/DSL) for construction.

---

## 1. Dynamic Generation (CypherAgent)

The `CypherGeneratorAgent` is responsible for translating natural language into executable Cypher.

### Mechanism
*   **Input**: Natural language query + Graph Schema + Few-shot examples.
*   **Model**: Gemini (e.g., `gemini-1.5-flash`).
*   **Output**: A JSON object containing a list of raw Cypher query strings.
    ```json
    {"queries": ["MATCH (p:PatientNode)... RETURN ..."]}
    ```

### Configuration & Rules
The generation is strictly controlled via `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/config.yml`.

**Key Constraints Enforced via Prompt:**
*   **Tenant Scoping**: MUST use `(instance)-[:INSTANCE_OF]->(type)` pattern (e.g., `MATCH (se:SymptomEpisodeNode)-[:INSTANCE_OF]->(st:SymptomTypeNode)`). Direct queries on ontology nodes (e.g., `MATCH (st:SymptomTypeNode)`) are forbidden to prevent data leakage.
*   **Case Insensitivity**: MUST use `WHERE toLower(node.property) CONTAINS toLower('term')`.
*   **Temporal Logic**: MUST use literal expressions like `timestamp() / 1000` for current time comparisons.
*   **Body Systems**: Specific patterns for querying `BodySystemNode` via `AFFECTS` or `BELONGS_TO` relationships.

### Validation
*   The agent has access to a `test_cypher(cypher_query="...")` tool defined in `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/cypher_agent_tools.py`.
*   **Optimization**: The agent is instructed to **SKIP** validation for "standard patterns" (simple lookups) to conserve latency and tokens. Validation is reserved for complex or uncertain queries.

### Execution Flow
1.  Agent receives user input.
2.  Agent generates JSON with Cypher strings (based on `config.yml` instructions).
3.  System parses JSON.
4.  `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/query_runner.py` executes the strings against Neo4j driver.

---

## 2. Static Templates (Semantic Router)

For high-frequency, predictable queries (e.g., "show my medications", "upcoming appointments"), the system uses a semantic routing layer to bypass the LLM generator.

### Mechanism
*   **Storage**: `repos/dem2/services/medical-agent/src/machina/medical_agent/semantic_router/cypher_templates.py`.
*   **Format**: A Python dictionary mapping `(category, intent)` tuples to `CypherTemplate` objects.
*   **Selection**: Vector semantic search matches user intent to a template description.

### Structure
Each `CypherTemplate` contains:
1.  **Raw Query**: A parameterized Cypher string.
    ```cypher
    MATCH (e:EncounterNode {patient_id: $patient_id}) ... RETURN ...
    ```
2.  **Params Builder**: A Python function (e.g., `_build_encounters_upcoming_params`) that constructs the `$patient_id` and other parameters from the context.
3.  **Description**: Used for semantic matching.

### Execution Flow
1.  Router matches intent (e.g., "medications", "current_active").
2.  System retrieves the corresponding `CypherTemplate`.
3.  System calls the `params_builder` to generate the parameter dict.
4.  System executes `db.cypher_query(template.query, params)`.

---

## Summary of Query Patterns

| Feature         | Dynamic Generation                 | Static Templates               |
| :-------------- | :--------------------------------- | :----------------------------- |
| **Source**      | LLM (Gemini)                       | Developer (Python code)        |
| **Format**      | Raw Cypher String                  | Raw Cypher String              |
| **Flexibility** | High (any question)                | Low (pre-defined intents)      |
| **Reliability** | Variable (depends on prompt/model) | High (tested code)             |
| **Validation**  | Optional (`test_cypher` tool)      | Pre-validated                  |
| **Primary Use** | Exploration, complex questions     | Dashboard data, common lists   |

---

## Index Usage

The system leverages Neo4j indexes to optimize query performance, though the usage differs between generation modes.

### 1. Property Indexes & Constraints
*   **Usage**: Heavily used by **Static Templates** and **Dynamic Generation**.
*   **Definition**: Defined in `repos/dem2/services/graph-memory/src/machina/graph_memory/medical/graph/schema.yml` (e.g., `unique_index=True`, `index=True`).
*   **Key Indexes**:
    *   `uuid` (Unique Constraint): Used for fast node retrieval by ID.
    *   `patient_id` (Index): **Critical** for tenant isolation. All queries filter by `patient_id` (either explicitly or via filtered relationships), leveraging these indexes.
    *   `user_id` (Index): Secondary tenant filter.

### 2. Vector Indexes
*   **Usage**: Primarily used by **Retrieval Tools** (e.g., `vector_search`) and internally by `semantic_router` for intent matching.
*   **Dynamic Generation**: The `CypherAgent` typically does **NOT** generate vector queries (`CALL db.index.vector...`) directly. Instead, it relies on `CONTAINS` for text matching. The prompt advises: "Do NOT add `score` to RETURN unless using `CALL db.index.vector.queryNodes`".
*   **Definition**: `embedding` properties in `schema.yml` are configured with `vector_index`.

### 3. Fulltext Search
*   **Usage**: The agent uses `toLower(n.summary) CONTAINS toLower('term')` for case-insensitive search.
*   **Performance**: This pattern typically performs a **label scan** (filtered by `patient_id` if present) rather than using a Fulltext Index, as standard B-tree indexes don't support `CONTAINS` efficiently. Since the search is usually scoped to a specific `patient_id` or a small set of ontology nodes (`TypeNodes`), performance remains acceptable without dedicated Fulltext Indexes.

---

## Logging & Tracing

Observability is built into the `query_runner.py` and infrastructure layers.

### Application Logging
*   **File**: `repos/dem2/services/medical-agent/src/machina/medical_agent/agents/CypherAgent/query_runner.py`
*   **Behavior**: Logs full query details including:
    *   Generated Cypher string
    *   Execution time
    *   Result count
    *   Errors (syntax errors, timeouts)
*   **Level**: `DEBUG` logs contain full query text/results; `INFO` logs contain summary stats.

### Langfuse Tracing
*   **Integration**: Uses `context_enrich_plugin.py` and `logging_plugin.py`.
*   **Spans**:
    *   `CypherGeneratorAgent`: Traces the LLM generation step.
    *   `test_cypher`: Traces validation execution.
    *   `neo4j_query`: Traces the actual database driver execution time.
*   **Metadata**: Cypher queries are captured as span metadata/input, allowing visual inspection of generated queries in the Langfuse UI.
