# Agent Model Configuration Changes

**Date:** 2026-01-16
**Purpose:** Upgrade all agents to Gemini 3.0 preview for improved reasoning and quality

## Model Changes Summary

| Agent                      | Before            | After                  | Rationale                                                                                     |
|:---------------------------|:------------------|:-----------------------|:----------------------------------------------------------------------------------------------|
| HealthConsultantAgent      | gemini-2.5-pro    | gemini-3-pro-preview   | Primary medical reasoning; requires best model for accurate consultations and medical advice  |
| DataExtractorAgent         | gemini-2.5-pro    | gemini-3-pro-preview   | Critical extraction accuracy; errors propagate through the system                             |
| UrlHandlerAgent            | gemini-2.5-pro    | gemini-3-pro-preview   | External content comprehension; better understanding of web pages and video content           |
| HealthConsultantLiteAgent  | gemini-2.5-pro    | gemini-3-pro-preview   | General medical knowledge; improved educational responses                                     |
| MedicalMeasurementsAgent   | gemini-2.5-pro    | gemini-3-pro-preview   | Measurement extraction; better parsing of labs, vitals, and biomarkers                        |
| MedicalContextAgent        | gemini-2.5-pro    | gemini-3-pro-preview   | Context extraction; improved recognition of practitioners, encounters, medications            |
| DataEntryAgent             | gemini-2.5-pro    | gemini-3-pro-preview   | FHIR resource extraction; better structured data handling                                     |
| GoogleSearchAgent          | gemini-2.5-pro    | gemini-3-pro-preview   | Search relevance; improved ranking of authoritative medical sources                           |
| TriageAgent                | gemini-2.5-flash  | gemini-3-flash-preview | Request routing; better intent classification and agent selection                             |
| CypherAgent                | gemini-2.5-flash  | gemini-3-flash-preview | Query generation; improved natural language to Cypher translation                             |
| FastGraphSummaryAgent      | gemini-2.5-flash  | gemini-3-flash-preview | Rapid summaries; faster response with maintained quality                                      |
| GraphMapAgent              | gemini-2.5-flash  | gemini-3-flash-preview | Chunk summarization; better topic extraction in map phase                                     |
| GraphReduceSummaryAgent    | gemini-2.5-flash  | gemini-3-flash-preview | Summary merging; improved synthesis in reduce phase                                           |
| AskTusdiAIHandlerAgent     | gemini-2.5-flash  | gemini-3-flash-preview | Lightweight queries; better handling of pre-loaded context                                    |

## Summary

- **8 agents** upgraded from `gemini-2.5-pro` → `gemini-3-pro-preview`
- **6 agents** upgraded from `gemini-2.5-flash` → `gemini-3-flash-preview`
- **14 total agents** now running on Gemini 3.0 preview

## Verification Plan

1. Deploy to preview environment
2. Run manual QA on all agent types
3. Monitor for prompt compatibility issues
4. Compare response quality against 2.5 baseline
5. Gradual production rollout based on metrics
