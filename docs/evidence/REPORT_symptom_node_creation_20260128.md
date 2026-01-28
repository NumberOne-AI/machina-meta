# SymptomNode Creation Test Results

**Date:** 2026-01-28
**Test Query:** "I have a headache that gets worse when I'm stressed or in bright light, and gets better when I rest in a dark room."
**Evidence:** [symptom-node-creation-test-results-20260127.json](symptom-node-creation-test-results-20260127.json)

| Environment      | Result   | Explanation                                                                                                                  |
|------------------|----------|------------------------------------------------------------------------------------------------------------------------------|
| local-dev        | FAIL     | Symptom created but `aggravating_factors` and `relieving_factors` stored as stringified Python lists instead of Neo4j arrays |
| tusdi-preview-92 | FAIL     | SymptomEpisodeNode NOT created - agent only queried existing graph, did not trigger extraction                               |
| tusdi-dev        | FAIL     | Symptom extracted (visible in session state) but NOT persisted to Neo4j graph                                                |
| tusdi-staging    | FAIL     | Symptom created but `aggravating_factors` and `relieving_factors` are NULL - modifiers lost during processing                |
