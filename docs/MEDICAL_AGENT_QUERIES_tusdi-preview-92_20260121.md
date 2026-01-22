# LLM Trace Timing Analysis Report

**Environment:** tusdi-preview-92 (GKE)
**Pod:** tusdi-api-6455c47984-dl27l
**Report Date:** 2026-01-21
**Analysis Period:** 2026-01-21 09:36 - 14:42 UTC

---

## Executive Summary

Analysis of 113 LLM trace files across 84 agent invocations reveals significant performance variability. While 45% of requests complete in under 10 seconds, 17% exceed 60 seconds, with the worst case reaching **711 seconds (11.8 minutes)**.

| Metric                          | Value        |
|---------------------------------|--------------|
| Total Invocations Analyzed      | 84           |
| Total LLM API Calls             | 113          |
| Median Response Time            | 12.82s       |
| Average Response Time           | 49.76s       |
| Requests Exceeding 60s          | 14 (16.7%)   |

---

## Summary Statistics

| Metric                              |    Min |     Max |    Avg | Median |
|-------------------------------------|-------:|--------:|-------:|-------:|
| Total Invocation Time               |   1.02s |  710.65s |  49.76s |  12.82s |
| LLM Call Time (Gemini API)          |  -0.14s |  320.12s |  16.75s |   9.41s |
| Processing Time (tools/graph)       |   0.00s |  701.70s |  33.00s |   0.09s |

---

## Agent Performance Summary

| Agent                    | LLM Calls |    Min |     Max |    Avg |   Total |
|--------------------------|----------:|-------:|--------:|-------:|--------:|
| HealthConsultantAgent    |        67 |  -0.14s |  314.79s |  16.21s |  1085.8s |
| TriageAgent              |        44 |   0.91s |   41.14s |   7.16s |   315.0s |
| UrlHandlerAgent          |         2 |   3.06s |    3.17s |   3.11s |     6.2s |

**Column Definitions:**
- **LLM Calls**: Number of round-trips to the Gemini API per invocation. Multiple calls occur due to the **agent loop pattern**:
  1. Agent sends query to LLM → LLM requests a tool (e.g., `query_graph`)
  2. Tool executes → result returned to LLM → LLM may request another tool
  3. Loop continues until LLM produces final response without tool calls

  Example: 3 LLM calls = initial request + 2 tool-use cycles before final answer.

---

## Response Time Distribution

| Duration Range | Count | Percentage | Cumulative | Assessment       |
|----------------|------:|-----------:|-----------:|------------------|
| 0-5s           |    26 |       31.0% |       31.0% | Excellent        |
| 5-10s          |    12 |       14.3% |       45.2% | Good             |
| 10-20s         |    10 |       11.9% |       57.1% | Acceptable       |
| 20-30s         |     6 |        7.1% |       64.3% | Slow             |
| 30-60s         |    16 |       19.0% |       83.3% | Very Slow        |
| >60s           |    14 |       16.7% |      100.0% | **Critical**     |

---

## Detailed Invocation Timing

| #  | Time (UTC) | Invocation ID              | Agent(s)                | LLM Calls | Total    |  LLM    | Tools   | LLM % |
|---:|:-----------|:---------------------------|:------------------------|----------:|---------:|--------:|--------:|------:|
|  1 | 09:36:29 | `e-84dbea66-68ec-4dbb-a8b...` | TriageAgent             |         1 |    41.48s |   41.14s |    0.34s |    99% |
|  2 | 09:37:11 | `e-12eb37b8-5964-4a4d-9ac...` | HealthConsultantAgent   |         1 |    35.80s |   12.37s |   23.43s |    35% |
|  3 | 10:18:53 | `e-1632b6d3-e0e1-47ac-b72...` | TriageAgent             |         1 |     2.21s |    2.12s |    0.09s |    96% |
|  4 | 10:18:55 | `e-c39446ac-4a6d-44d5-9ee...` | HealthConsultantAgent   |         3 |    52.31s |   30.97s |   21.33s |    59% |
|  5 | 10:22:33 | `e-fa2f3ddf-5e2e-48f2-ac0...` | TriageAgent             |         1 |     2.33s |    2.28s |    0.05s |    98% |
|  6 | 10:22:36 | `e-26cbeb97-f637-462e-98c...` | HealthConsultantAgent   |         2 |    34.05s |   11.33s |   22.72s |    33% |
|  7 | 10:23:36 | `e-a9dde1e3-4a99-4c27-b34...` | TriageAgent             |         1 |     2.89s |    2.84s |    0.05s |    98% |
|  8 | 10:23:39 | `e-451cd65b-ce56-4ca5-bc7...` | HealthConsultantAgent   |         2 |    32.99s |   13.80s |   19.19s |    42% |
|  9 | 10:24:38 | `e-84c21651-d33b-491a-b84...` | TriageAgent             |         1 |     2.01s |    1.97s |    0.05s |    98% |
| 10 | 10:24:40 | `e-f91dce0c-9644-4c68-a51...` | HealthConsultantAgent   |         2 |    61.22s |   47.25s |   13.97s |    77% |
| 11 | 10:26:08 | `e-d503bc68-d18f-4068-8e0...` | TriageAgent             |         1 |     2.62s |    2.58s |    0.05s |    98% |
| 12 | 10:26:10 | `e-babdedf6-1d7a-4259-a85...` | HealthConsultantAgent   |         1 |     8.57s |    8.56s |    0.00s |   100% |
| 13 | 10:26:45 | `e-eeb440b1-8faa-4b6f-ae8...` | TriageAgent             |         1 |     2.62s |    2.57s |    0.05s |    98% |
| 14 | 10:27:18 | `e-737d8bdb-430d-4f6f-bd3...` | TriageAgent             |         1 |     4.49s |    4.45s |    0.04s |    99% |
| 15 | 10:27:23 | `e-9fcdc095-9766-417f-a4c...` | HealthConsultantAgent   |         2 |    26.62s |   16.12s |   10.51s |    61% |
| 16 | 10:28:20 | `e-ac1b2e10-2f83-4900-874...` | TriageAgent             |         1 |     2.74s |    2.70s |    0.05s |    98% |
| 17 | 10:28:23 | `e-a3c1e752-d2b0-4d41-abb...` | HealthConsultantAgent   |         2 |    27.01s |   17.17s |    9.84s |    64% |
| 18 | 10:29:15 | `e-c40f40c5-e64d-4939-85c...` | TriageAgent             |         1 |     2.92s |    2.87s |    0.05s |    98% |
| 19 | 10:29:18 | `e-12357853-b8dd-4a48-b9e...` | HealthConsultantAgent   |         1 |    14.10s |   14.10s |    0.00s |   100% |
| 20 | 10:29:58 | `e-4450ef46-9ecb-4734-90c...` | TriageAgent             |         1 |     7.95s |    7.89s |    0.06s |    99% |
| 21 | 10:30:06 | `e-2ff8108f-e5d6-4106-80a...` | HealthConsultantAgent   |         1 |     8.75s |    8.75s |    0.00s |   100% |
| 22 | 10:30:40 | `e-b3cf49f4-dd5d-4359-9c4...` | TriageAgent             |         1 |     2.57s |    2.52s |    0.05s |    98% |
| 23 | 10:31:19 | `e-1d9ae029-809f-44c2-989...` | TriageAgent             |         1 |     3.67s |    3.62s |    0.05s |    99% |
| 24 | 10:31:23 | `e-e3f0b839-c6ab-405e-b3d...` | UrlHandlerAgent         |         1 |     3.19s |    3.17s |    0.02s |    99% |
| 25 | 10:34:38 | `e-1661e1d0-eed8-4567-a5b...` | TriageAgent             |         1 |     3.24s |    3.20s |    0.05s |    99% |
| 26 | 10:34:42 | `e-c5a289b6-d0f3-43a8-a5c...` | HealthConsultantAgent   |         2 |    47.30s |   34.95s |   12.34s |    74% |
| 27 | 10:35:58 | `e-6f574690-0ece-47ba-bfb...` | TriageAgent             |         1 |     2.42s |    2.37s |    0.05s |    98% |
| 28 | 10:36:01 | `e-165f4d22-d835-4f49-ae5...` | HealthConsultantAgent   |         2 |    33.34s |   20.82s |   12.51s |    62% |
| 29 | 10:37:01 | `e-3edf692b-12c3-4a40-894...` | TriageAgent             |         1 |     1.69s |    1.64s |    0.05s |    97% |
| 30 | 10:37:03 | `e-e639b820-0ebb-4817-b2c...` | HealthConsultantAgent   |         1 |     8.16s |   -0.00s |    8.17s |    -0% |
| 31 | 10:38:10 | `e-06b10c8e-0c8c-42f1-8f3...` | TriageAgent             |         1 |     2.91s |    2.82s |    0.08s |    97% |
| 32 | 10:38:13 | `e-dcac5cac-a234-44fa-9f4...` | HealthConsultantAgent   |         2 |    36.08s |   16.24s |   19.84s |    45% |
| 33 | 10:39:07 | `e-e8a9e789-2881-4db2-b6d...` | TriageAgent             |         1 |     5.82s |    5.73s |    0.08s |    99% |
| 34 | 10:39:13 | `e-4c031b92-f75e-44a5-895...` | HealthConsultantAgent   |         2 |   336.61s |  320.12s |   16.49s |    95% |
| 35 | 10:40:20 | `e-d234742e-ed09-4027-bfd...` | TriageAgent             |         1 |     1.74s |    1.70s |    0.05s |    97% |
| 36 | 10:40:21 | `e-e62edae2-c094-45bf-98c...` | HealthConsultantAgent   |         2 |    26.45s |    9.41s |   17.04s |    36% |
| 37 | 10:41:15 | `e-02e229f3-e297-4799-880...` | TriageAgent             |         1 |     2.56s |    2.50s |    0.06s |    98% |
| 38 | 10:41:17 | `e-89d929a2-ab9d-43f6-969...` | HealthConsultantAgent   |         1 |    11.02s |   11.02s |    0.00s |   100% |
| 39 | 10:48:44 | `e-3c30816a-ec8d-4947-830...` | TriageAgent             |         1 |    23.62s |   23.57s |    0.05s |   100% |
| 40 | 10:49:08 | `e-59e1bc3c-a55d-4155-930...` | HealthConsultantAgent   |         2 |    46.83s |   34.98s |   11.85s |    75% |
| 41 | 10:51:44 | `e-6404df56-14e8-440d-bb2...` | TriageAgent             |         1 |     1.02s |    0.91s |    0.11s |    89% |
| 42 | 10:51:45 | `e-a6b459f0-06e7-4a71-856...` | UrlHandlerAgent         |         1 |     3.06s |    3.06s |    0.00s |   100% |
| 43 | 11:09:23 | `e-daee776d-6c13-416c-a95...` | TriageAgent             |         1 |     1.53s |    1.32s |    0.20s |    87% |
| 44 | 11:09:25 | `e-8d3ed940-b876-4ac0-861...` | HealthConsultantAgent   |         2 |    57.43s |   21.09s |   36.34s |    37% |
| 45 | 11:31:38 | `e-d40e8178-c707-43ae-869...` | TriageAgent             |         1 |     9.16s |    9.08s |    0.08s |    99% |
| 46 | 11:31:47 | `e-a71ae9c1-3b26-4669-b0d...` | HealthConsultantAgent   |         2 |   130.86s |   36.57s |   94.29s |    28% |
| 47 | 11:37:49 | `e-1878d026-084d-4a49-a63...` | TriageAgent             |         1 |     5.45s |    5.33s |    0.12s |    98% |
| 48 | 11:37:55 | `e-703d3f6d-ec11-4d1b-822...` | HealthConsultantAgent   |         1 |    63.07s |   11.92s |   51.15s |    19% |
| 49 | 11:50:11 | `e-e93f31a7-1a59-4856-80d...` | TriageAgent             |         1 |     7.38s |    7.30s |    0.08s |    99% |
| 50 | 11:50:18 | `e-60d0f580-4f87-48e7-97f...` | HealthConsultantAgent   |         2 |    95.22s |   47.78s |   47.44s |    50% |
| 51 | 11:53:20 | `e-260be616-ed7a-483f-a6c...` | TriageAgent             |         1 |    17.64s |   17.56s |    0.08s |   100% |
| 52 | 11:53:37 | `e-d35b98a5-115d-4b0a-b6d...` | HealthConsultantAgent   |         1 |    41.17s |   13.79s |   27.39s |    33% |
| 53 | 11:55:08 | `e-8fc4a267-5ad0-4b81-a33...` | TriageAgent             |         1 |     5.56s |    5.47s |    0.08s |    98% |
| 54 | 11:55:13 | `e-26bd5683-f7ed-46d7-996...` | HealthConsultantAgent   |         1 |    52.52s |   12.18s |   40.34s |    23% |
| 55 | 12:01:29 | `e-7013f695-288f-4068-ab0...` | TriageAgent             |         1 |    13.04s |   12.96s |    0.08s |    99% |
| 56 | 12:01:42 | `e-027e6b42-086b-4061-a31...` | HealthConsultantAgent   |         1 |    36.60s |    8.81s |   27.79s |    24% |
| 57 | 12:03:44 | `e-081cd19a-706b-4e10-a9c...` | TriageAgent             |         1 |     1.31s |    1.22s |    0.09s |    93% |
| 58 | 12:03:46 | `e-fbbe967e-3ab4-48b0-abc...` | HealthConsultantAgent   |         2 |    73.04s |   23.78s |   49.25s |    33% |
| 59 | 12:06:30 | `e-fffc17ea-8ae0-4088-88e...` | TriageAgent             |         1 |     1.76s |    1.68s |    0.08s |    95% |
| 60 | 12:06:51 | `e-11490e62-e04a-4f0c-bf2...` | TriageAgent             |         1 |    16.39s |   16.30s |    0.08s |    99% |
| 61 | 12:07:08 | `e-24e4645d-694f-44ed-baa...` | HealthConsultantAgent   |         3 |   103.27s |   54.82s |   48.45s |    53% |
| 62 | 12:16:13 | `e-be664be9-dfec-454f-9f2...` | TriageAgent             |         1 |     9.14s |    9.06s |    0.08s |    99% |
| 63 | 12:17:06 | `e-540e6719-1f54-4dda-a29...` | TriageAgent             |         1 |    11.12s |   11.04s |    0.08s |    99% |
| 64 | 12:17:17 | `e-5be9f24e-213e-4ebf-bf7...` | HealthConsultantAgent   |         2 |   100.08s |   24.10s |   75.97s |    24% |
| 65 | 12:22:35 | `e-c2821975-cce7-486b-863...` | TriageAgent             |         1 |    14.57s |   14.49s |    0.08s |    99% |
| 66 | 12:22:49 | `e-6105b33a-2f08-47fb-b37...` | HealthConsultantAgent   |         1 |    42.18s |    9.88s |   32.30s |    23% |
| 67 | 12:26:24 | `e-fd5870c6-662e-4c06-af5...` | TriageAgent             |         1 |     2.03s |    1.95s |    0.08s |    96% |
| 68 | 12:26:26 | `e-307bbfac-54b2-47e8-af6...` | HealthConsultantAgent   |         1 |   340.34s |   -0.14s |  340.48s |    -0% |
| 69 | 12:41:49 | `e-a21bd62e-9ed0-4805-bf9...` | TriageAgent             |         1 |     6.14s |    5.89s |    0.25s |    96% |
| 70 | 12:41:55 | `e-94b56f2b-dec6-411e-965...` | HealthConsultantAgent   |         1 |   710.65s |    8.95s |  701.70s |     1% |
| 71 | 13:33:32 | `e-40f41d7e-b534-4694-886...` | TriageAgent             |         1 |     6.01s |    5.96s |    0.05s |    99% |
| 72 | 13:33:38 | `e-f5de890f-9e3c-4f21-840...` | HealthConsultantAgent   |         3 |    34.61s |   17.85s |   16.76s |    52% |
| 73 | 13:37:28 | `e-44dc64ee-70b8-4860-b07...` | TriageAgent             |         1 |    12.82s |   12.78s |    0.04s |   100% |
| 74 | 13:37:41 | `e-de2724b9-62a0-472a-826...` | HealthConsultantAgent   |         2 |    29.11s |   19.10s |   10.01s |    66% |
| 75 | 14:11:16 | `e-580f0e90-39c3-49a7-883...` | TriageAgent             |         1 |    10.33s |   10.07s |    0.25s |    98% |
| 76 | 14:11:27 | `e-74960373-82ac-44d4-968...` | HealthConsultantAgent   |         2 |    94.04s |   32.44s |   61.60s |    34% |
| 77 | 14:20:11 | `e-78bd9965-e554-44e0-87c...` | TriageAgent             |         1 |    11.20s |   11.14s |    0.05s |   100% |
| 78 | 14:20:22 | `e-7977baee-4489-417e-b93...` | HealthConsultantAgent   |         1 |    37.70s |    5.96s |   31.74s |    16% |
| 79 | 14:22:33 | `e-ff66e1a4-3c69-4c52-989...` | TriageAgent             |         1 |    22.64s |   22.58s |    0.06s |   100% |
| 80 | 14:22:55 | `e-5eabae49-9bc5-476c-878...` | HealthConsultantAgent   |         1 |   432.15s |   11.13s |  421.01s |     3% |
| 81 | 14:35:55 | `e-a5970fef-4cd2-414a-b38...` | TriageAgent             |         1 |     4.09s |    4.04s |    0.06s |    99% |
| 82 | 14:35:59 | `e-0d9b988a-4158-438d-9cf...` | HealthConsultantAgent   |         4 |   451.64s |   57.81s |  393.83s |    13% |
| 83 | 14:42:40 | `e-0857a6c8-a11d-48a0-b4b...` | TriageAgent             |         1 |     3.86s |    3.80s |    0.06s |    98% |
| 84 | 14:42:44 | `e-9d17bd0c-ccab-4345-879...` | HealthConsultantAgent   |         3 |    81.61s |   40.06s |   41.55s |    49% |

---

## Critical Slow Queries (>100s)

| Rank | Timestamp  | Invocation ID                          |   Total |     LLM |   Tools | User Query Summary                                              |
|-----:|:-----------|:---------------------------------------|--------:|--------:|--------:|:----------------------------------------------------------------|
|    1 | 12:41:55   | `e-94b56f2b-dec6-411e-965b-2f7ca5254363` |  710.65s |    8.95s |  701.70s | suggest a supplementation and diet protocol to improve my liver results |
|    2 | 14:35:59   | `e-0d9b988a-4158-438d-9cf5-fe7436278782` |  451.64s |   57.81s |  393.83s | Generate Cypher queries for the following 4 natural language questions: 1. Find all active conditions 2. Find all active medications and supplements 3. Find recent observations for Cortisol, Vitamin D, Magnesium, Iron, Ferritin, TSH 4. Find all reported symptoms related to sleep or fatigue |
|    3 | 14:22:55   | `e-5eabae49-9bc5-476c-8789-a9fcc85e939e` |  432.15s |   11.13s |  421.01s | tell me everything I need to know about this report |
|    4 | 12:26:26   | `e-307bbfac-54b2-47e8-af66-a6a6058c3964` |  340.34s |   -0.14s |  340.48s | Generate Cypher queries for the following 4 natural language questions: 1. Show recent liver function tests including ALT, AST, GGT, Bilirubin, and Albumin 2. Show all active medical conditions 3. Show current medications and supplements 4. Show active allergies |
|    5 | 10:39:13   | `e-4c031b92-f75e-44a5-8957-6e814114a38b` |  336.61s |  320.12s |   16.49s | Show current status for Penicillin allergy, Hazelnut pollen allergy, and Lactose intolerance condition. |
|    6 | 11:31:47   | `e-a71ae9c1-3b26-4669-b0d0-c5aa79845c93` |  130.86s |   36.57s |   94.29s | Generate Cypher queries for the following 3 natural language questions: 1. Find all active conditions 2. Get recent laboratory observations 3. List all active medications and supplements |
|    7 | 12:07:08   | `e-24e4645d-694f-44ed-baa4-6bf96d256592` |  103.27s |   54.82s |   48.45s | Generate Cypher queries for the following 4 natural language questions: 1. Find active conditions 2. Find current medications 3. Find recent encounters 4. Find allergies |
|    8 | 12:17:17   | `e-5be9f24e-213e-4ebf-bf7b-ee94aab3aee5` |  100.08s |   24.10s |   75.97s | Generate Cypher queries for the following 5 natural language questions: 1. Find all active conditions 2. Find all active medications and supplements 3. Find recent lab results for Vitamin D, Magnesium, Cortisol, TSH, Ferritin, Vitamin B12 4. Find all reported symptoms 5. Find all active allergies |

---

## LLM Call Breakdown (Sample of First 30 Calls)

| Invocation       | Agent                   | Call # | Duration | Time Range (UTC)      |
|:-----------------|:------------------------|-------:|---------:|:----------------------|
| `e-84dbea66-6...` | TriageAgent             |      1 |    41.14s | 09:36:29 - 09:37:10   |
| `e-12eb37b8-5...` | HealthConsultantAgent   |      0 |    12.37s | 09:37:34 - 09:37:46   |
| `e-1632b6d3-e...` | TriageAgent             |      1 |     2.12s | 10:18:53 - 10:18:55   |
| `e-c39446ac-4...` | HealthConsultantAgent   |      0 |    18.46s | 10:19:05 - 10:19:24   |
| `e-c39446ac-4...` | HealthConsultantAgent   |      1 |     4.92s | 10:19:35 - 10:19:40   |
| `e-c39446ac-4...` | HealthConsultantAgent   |      2 |     7.59s | 10:19:40 - 10:19:47   |
| `e-fa2f3ddf-5...` | TriageAgent             |      1 |     2.28s | 10:22:33 - 10:22:35   |
| `e-26cbeb97-f...` | HealthConsultantAgent   |      0 |     2.16s | 10:22:55 - 10:22:57   |
| `e-26cbeb97-f...` | HealthConsultantAgent   |      1 |     9.17s | 10:23:00 - 10:23:10   |
| `e-a9dde1e3-4...` | TriageAgent             |      1 |     2.84s | 10:23:36 - 10:23:39   |
| `e-451cd65b-c...` | HealthConsultantAgent   |      0 |     7.59s | 10:23:57 - 10:24:05   |
| `e-451cd65b-c...` | HealthConsultantAgent   |      1 |     6.21s | 10:24:06 - 10:24:12   |
| `e-84c21651-d...` | TriageAgent             |      1 |     1.97s | 10:24:38 - 10:24:40   |
| `e-f91dce0c-9...` | HealthConsultantAgent   |      0 |    39.15s | 10:24:54 - 10:25:33   |
| `e-f91dce0c-9...` | HealthConsultantAgent   |      1 |     8.10s | 10:25:34 - 10:25:42   |
| `e-d503bc68-d...` | TriageAgent             |      1 |     2.58s | 10:26:08 - 10:26:10   |
| `e-babdedf6-1...` | HealthConsultantAgent   |      0 |     8.56s | 10:26:10 - 10:26:19   |
| `e-eeb440b1-8...` | TriageAgent             |      1 |     2.57s | 10:26:45 - 10:26:47   |
| `e-737d8bdb-4...` | TriageAgent             |      1 |     4.45s | 10:27:18 - 10:27:23   |
| `e-9fcdc095-9...` | HealthConsultantAgent   |      0 |     8.69s | 10:27:32 - 10:27:41   |
| `e-9fcdc095-9...` | HealthConsultantAgent   |      1 |     7.42s | 10:27:42 - 10:27:49   |
| `e-ac1b2e10-2...` | TriageAgent             |      1 |     2.70s | 10:28:20 - 10:28:23   |
| `e-a3c1e752-d...` | HealthConsultantAgent   |      0 |    10.80s | 10:28:31 - 10:28:42   |
| `e-a3c1e752-d...` | HealthConsultantAgent   |      1 |     6.37s | 10:28:43 - 10:28:50   |
| `e-c40f40c5-e...` | TriageAgent             |      1 |     2.87s | 10:29:15 - 10:29:18   |
| `e-12357853-b...` | HealthConsultantAgent   |      0 |    14.10s | 10:29:18 - 10:29:32   |
| `e-4450ef46-9...` | TriageAgent             |      1 |     7.89s | 10:29:58 - 10:30:06   |
| `e-2ff8108f-e...` | HealthConsultantAgent   |      0 |     8.75s | 10:30:06 - 10:30:15   |
| `e-b3cf49f4-d...` | TriageAgent             |      1 |     2.52s | 10:30:40 - 10:30:43   |
| `e-1d9ae029-8...` | TriageAgent             |      1 |     3.62s | 10:31:19 - 10:31:23   |

*(Showing first 30 of 113 calls)*

---

**Report generated:** 2026-01-21T16:17:29Z
**Analyzed by:** analyze_llm_traces.py
**Trace files:** 226
**Invocations:** 84
