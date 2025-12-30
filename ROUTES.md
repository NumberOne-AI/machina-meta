# API Routes Documentation

Comprehensive listing of all API routes and pages across all services in the machina-meta workspace.

**Generated**: 2025-12-30T09:34:42.421123
**Total Routes**: 173
**Services**: dem2, dem2-webui, medical-catalog

## Table of Contents

- [dem2](#dem2)
- [dem2-webui](#dem2-webui)
- [medical-catalog](#medical-catalog)

---

## dem2

**Port**: 8000
**Total Routes**: 128

### API Routes

| Service | Port | Method | Path | Description | Example |
|---------|------|--------|------|-------------|---------|
| dem2 | 8000 | GET | /allergies | (No description) | `curl http://localhost:8000/allergies` |
| dem2 | 8000 | POST | /allergies | (No description) | `curl -X POST http://localhost:8000/allergies -d '{}'` |
| dem2 | 8000 | GET | /allergies/grouped | (No description) | `curl http://localhost:8000/allergies/grouped` |
| dem2 | 8000 | DELETE | /allergies/{allergy_id} | (No description) | `curl http://localhost:8000/allergies/alg-789` |
| dem2 | 8000 | PATCH | /allergies/{allergy_id}/status | (No description) | `curl -X PATCH http://localhost:8000/allergies/alg-789/status -d '{}'` |
| dem2 | 8000 | GET | /allergy-records | (No description) | `curl http://localhost:8000/allergy-records` |
| dem2 | 8000 | GET | /allergy-records/{record_id} | (No description) | `curl http://localhost:8000/allergy-records/{record_id}` |
| dem2 | 8000 | GET | /api/v1/medical-sources/drugs/search | (No description) | `curl http://localhost:8000/api/v1/medical-sources/drugs/search` |
| dem2 | 8000 | POST | /api/v1/medical-sources/drugs/search | (No description) | `curl -X POST http://localhost:8000/api/v1/medical-sources/drugs/search -d '{}'` |
| dem2 | 8000 | GET | /api/v1/medical-sources/drugs/search/formatted | (No description) | `curl http://localhost:8000/api/v1/medical-sources/drugs/search/formatted` |
| dem2 | 8000 | GET | /api/v1/medical-sources/health | (No description) | `curl http://localhost:8000/api/v1/medical-sources/health` |
| dem2 | 8000 | GET | /api/v1/medical-sources/papers/search | (No description) | `curl http://localhost:8000/api/v1/medical-sources/papers/search` |
| dem2 | 8000 | POST | /api/v1/medical-sources/papers/search | (No description) | `curl -X POST http://localhost:8000/api/v1/medical-sources/papers/search -d '{}'` |
| dem2 | 8000 | GET | /api/v1/medical-sources/papers/search/formatted | (No description) | `curl http://localhost:8000/api/v1/medical-sources/papers/search/formatted` |
| dem2 | 8000 | GET | /api/v1/medical-sources/trials/search | (No description) | `curl http://localhost:8000/api/v1/medical-sources/trials/search` |
| dem2 | 8000 | POST | /api/v1/medical-sources/trials/search | (No description) | `curl -X POST http://localhost:8000/api/v1/medical-sources/trials/search -d '{}'` |
| dem2 | 8000 | GET | /api/v1/medical-sources/trials/search/formatted | (No description) | `curl http://localhost:8000/api/v1/medical-sources/trials/search/formatted` |
| dem2 | 8000 | GET | /api/v1/medical-sources/variants/search | (No description) | `curl http://localhost:8000/api/v1/medical-sources/variants/search` |
| dem2 | 8000 | POST | /api/v1/medical-sources/variants/search | (No description) | `curl -X POST http://localhost:8000/api/v1/medical-sources/variants/search -d '{}'` |
| dem2 | 8000 | GET | /api/v1/medical-sources/variants/search/formatted | (No description) | `curl http://localhost:8000/api/v1/medical-sources/variants/search/formatted` |
| dem2 | 8000 | GET | /by-tag/{tag_id} | (No description) | `curl http://localhost:8000/by-tag/{tag_id}` |
| dem2 | 8000 | GET | /care_network | (No description) | `curl http://localhost:8000/care_network` |
| dem2 | 8000 | POST | /cleanup/orphaned_resources | (No description) | `curl -X POST http://localhost:8000/cleanup/orphaned_resources -d '{}'` |
| dem2 | 8000 | POST | /complete | (No description) | `curl -X POST http://localhost:8000/complete -d '{}'` |
| dem2 | 8000 | GET | /conditions | (No description) | `curl http://localhost:8000/conditions` |
| dem2 | 8000 | GET | /conditions/{condition_id} | (No description) | `curl http://localhost:8000/conditions/{condition_id}` |
| dem2 | 8000 | GET | /conditions/{condition_id} | (No description) | `curl http://localhost:8000/conditions/{condition_id}` |
| dem2 | 8000 | GET | /count | (No description) | `curl http://localhost:8000/count` |
| dem2 | 8000 | GET | /document_references | (No description) | `curl http://localhost:8000/document_references` |
| dem2 | 8000 | GET | /document_references/{document_id} | (No description) | `curl http://localhost:8000/document_references/{document_id}` |
| dem2 | 8000 | GET | /document_references/{document_id} | (No description) | `curl http://localhost:8000/document_references/{document_id}` |
| dem2 | 8000 | DELETE | /document_references/{document_id} | (No description) | `curl http://localhost:8000/document_references/{document_id}` |
| dem2 | 8000 | GET | /document_references/{document_id}/details | (No description) | `curl http://localhost:8000/document_references/{document_id}/details` |
| dem2 | 8000 | GET | /encounters | (No description) | `curl http://localhost:8000/encounters` |
| dem2 | 8000 | GET | /encounters | (No description) | `curl http://localhost:8000/encounters` |
| dem2 | 8000 | WS | /events | (No description) | `ws://localhost:8000/events` |
| dem2 | 8000 | GET | /files | (No description) | `curl http://localhost:8000/files` |
| dem2 | 8000 | POST | /files/bulk_delete | (No description) | `curl -X POST http://localhost:8000/files/bulk_delete -d '{}'` |
| dem2 | 8000 | POST | /files/upload | (No description) | `curl -X POST http://localhost:8000/files/upload -d '{}'` |
| dem2 | 8000 | POST | /files/upload/bulk | (No description) | `curl -X POST http://localhost:8000/files/upload/bulk -d '{}'` |
| dem2 | 8000 | DELETE | /files/{file_id} | (No description) | `curl http://localhost:8000/files/{file_id}` |
| dem2 | 8000 | GET | /files/{file_id}/download | (No description) | `curl http://localhost:8000/files/{file_id}/download` |
| dem2 | 8000 | POST | /geocode/zip | (No description) | `curl -X POST http://localhost:8000/geocode/zip -d '{}'` |
| dem2 | 8000 | GET | /google/callback | (No description) | `curl http://localhost:8000/google/callback` |
| dem2 | 8000 | GET | /google/login | (No description) | `curl http://localhost:8000/google/login` |
| dem2 | 8000 | GET | /grouped | (No description) | `curl http://localhost:8000/grouped` |
| dem2 | 8000 | GET | /health | Simple health probe. | `curl http://localhost:8000/health` |
| dem2 | 8000 | GET | /health | Simple health probe. | `curl http://localhost:8000/health` |
| dem2 | 8000 | POST | /logout | (No description) | `curl -X POST http://localhost:8000/logout -d '{}'` |
| dem2 | 8000 | GET | /loinc/{loinc_code} | (No description) | `curl http://localhost:8000/loinc/{loinc_code}` |
| dem2 | 8000 | GET | /medication/intake-events | (No description) | `curl http://localhost:8000/medication/intake-events` |
| dem2 | 8000 | POST | /medication/intake-events | (No description) | `curl -X POST http://localhost:8000/medication/intake-events -d '{}'` |
| dem2 | 8000 | POST | /medication/intake-events/bulk | (No description) | `curl -X POST http://localhost:8000/medication/intake-events/bulk -d '{}'` |
| dem2 | 8000 | DELETE | /medication/intake-events/bulk | (No description) | `curl http://localhost:8000/medication/intake-events/bulk` |
| dem2 | 8000 | DELETE | /medication/intake-events/{intake_id} | (No description) | `curl http://localhost:8000/medication/intake-events/{intake_id}` |
| dem2 | 8000 | POST | /medication/intake-regimens | (No description) | `curl -X POST http://localhost:8000/medication/intake-regimens -d '{}'` |
| dem2 | 8000 | GET | /medication/intake-regimens/list | (No description) | `curl http://localhost:8000/medication/intake-regimens/list` |
| dem2 | 8000 | PATCH | /medication/intake-regimens/{regimen_id} | (No description) | `curl -X PATCH http://localhost:8000/medication/intake-regimens/{regimen_id} -d '{}'` |
| dem2 | 8000 | DELETE | /medication/intake-regimens/{regimen_id} | (No description) | `curl http://localhost:8000/medication/intake-regimens/{regimen_id}` |
| dem2 | 8000 | GET | /medication/medications/by_rxcui | (No description) | `curl http://localhost:8000/medication/medications/by_rxcui` |
| dem2 | 8000 | GET | /medication/medications/by_uuid | (No description) | `curl http://localhost:8000/medication/medications/by_uuid` |
| dem2 | 8000 | GET | /medication/medications/search | (No description) | `curl http://localhost:8000/medication/medications/search` |
| dem2 | 8000 | GET | /medication/medications/{medication_id}/ingredients | (No description) | `curl http://localhost:8000/medication/medications/{medication_id}/ingredients` |
| dem2 | 8000 | GET | /medication/supplements/by_ingr_grp | (No description) | `curl http://localhost:8000/medication/supplements/by_ingr_grp` |
| dem2 | 8000 | GET | /medication/supplements/by_ods_label | (No description) | `curl http://localhost:8000/medication/supplements/by_ods_label` |
| dem2 | 8000 | GET | /medication/supplements/by_uuid | (No description) | `curl http://localhost:8000/medication/supplements/by_uuid` |
| dem2 | 8000 | GET | /medication/supplements/search | (No description) | `curl http://localhost:8000/medication/supplements/search` |
| dem2 | 8000 | GET | /medication/supplements/{supplement_id}/ingredients | (No description) | `curl http://localhost:8000/medication/supplements/{supplement_id}/ingredients` |
| dem2 | 8000 | GET | /observations | (No description) | `curl http://localhost:8000/observations` |
| dem2 | 8000 | GET | /observations/body_system/{body_system} | (No description) | `curl http://localhost:8000/observations/body_system/{body_system}` |
| dem2 | 8000 | GET | /observations/grouped | (No description) | `curl http://localhost:8000/observations/grouped` |
| dem2 | 8000 | GET | /observations/stats | (No description) | `curl http://localhost:8000/observations/stats` |
| dem2 | 8000 | GET | /observations/stats | (No description) | `curl http://localhost:8000/observations/stats` |
| dem2 | 8000 | GET | /observations/types/by-uuid/{uuid} | (No description) | `curl http://localhost:8000/observations/types/by-uuid/{uuid}` |
| dem2 | 8000 | GET | /observations/types/search | (No description) | `curl http://localhost:8000/observations/types/search` |
| dem2 | 8000 | GET | /observations/types/{code} | (No description) | `curl http://localhost:8000/observations/types/{code}` |
| dem2 | 8000 | GET | /observations/values | (No description) | `curl http://localhost:8000/observations/values` |
| dem2 | 8000 | PATCH | /observations/values/{uid} | (No description) | `curl -X PATCH http://localhost:8000/observations/values/{uid} -d '{}'` |
| dem2 | 8000 | DELETE | /observations/values/{uid} | (No description) | `curl http://localhost:8000/observations/values/{uid}` |
| dem2 | 8000 | DELETE | /observations/{observation_type_uuid} | (No description) | `curl http://localhost:8000/observations/{observation_type_uuid}` |
| dem2 | 8000 | GET | /organizations | (No description) | `curl http://localhost:8000/organizations` |
| dem2 | 8000 | GET | /patients/statistics | (No description) | `curl http://localhost:8000/patients/statistics` |
| dem2 | 8000 | GET | /patients/{patient_uuid}/statistics | (No description) | `curl http://localhost:8000/patients/{patient_uuid}/statistics` |
| dem2 | 8000 | GET | /practitioners | (No description) | `curl http://localhost:8000/practitioners` |
| dem2 | 8000 | POST | /process_document | (No description) | `curl -X POST http://localhost:8000/process_document -d '{}'` |
| dem2 | 8000 | GET | /queue/stats | (No description) | `curl http://localhost:8000/queue/stats` |
| dem2 | 8000 | POST | /refresh | (No description) | `curl -X POST http://localhost:8000/refresh -d '{}'` |
| dem2 | 8000 | GET | /resource_connections | (No description) | `curl http://localhost:8000/resource_connections` |
| dem2 | 8000 | POST | /run | (No description) | `curl -X POST http://localhost:8000/run -d '{}'` |
| dem2 | 8000 | WS | /run_live | (No description) | `ws://localhost:8000/run_live` |
| dem2 | 8000 | POST | /run_sse | (No description) | `curl -X POST http://localhost:8000/run_sse -d '{}'` |
| dem2 | 8000 | POST | /search | (No description) | `curl -X POST http://localhost:8000/search -d '{}'` |
| dem2 | 8000 | PUT | /survey/answers | (No description) | `curl -X PUT http://localhost:8000/survey/answers -d '{}'` |
| dem2 | 8000 | GET | /survey/questions | (No description) | `curl http://localhost:8000/survey/questions` |
| dem2 | 8000 | GET | /symptom-types | (No description) | `curl http://localhost:8000/symptom-types` |
| dem2 | 8000 | GET | /symptom-types/{type_id} | (No description) | `curl http://localhost:8000/symptom-types/{type_id}` |
| dem2 | 8000 | GET | /symptoms | (No description) | `curl http://localhost:8000/symptoms` |
| dem2 | 8000 | GET | /symptoms/{symptom_id} | (No description) | `curl http://localhost:8000/symptoms/{symptom_id}` |
| dem2 | 8000 | GET | /symptoms/{symptom_id} | (No description) | `curl http://localhost:8000/symptoms/{symptom_id}` |
| dem2 | 8000 | GET | /tasks | (No description) | `curl http://localhost:8000/tasks` |
| dem2 | 8000 | GET | /tasks/stream | (No description) | `curl http://localhost:8000/tasks/stream` |
| dem2 | 8000 | GET | /tasks/{task_id} | (No description) | `curl http://localhost:8000/tasks/{task_id}` |
| dem2 | 8000 | POST | /test-stream | (No description) | `curl -X POST http://localhost:8000/test-stream -d '{}'` |
| dem2 | 8000 | POST | /test_process_document | (No description) | `curl -X POST http://localhost:8000/test_process_document -d '{}'` |
| dem2 | 8000 | DELETE | /user_data | (No description) | `curl http://localhost:8000/user_data` |
| dem2 | 8000 | GET | /users/me | (No description) | `curl http://localhost:8000/users/me` |
| dem2 | 8000 | DELETE | /users/me | (No description) | `curl http://localhost:8000/users/me` |
| dem2 | 8000 | GET | /users/me/patients | (No description) | `curl http://localhost:8000/users/me/patients` |
| dem2 | 8000 | POST | /users/me/patients | (No description) | `curl -X POST http://localhost:8000/users/me/patients -d '{}'` |
| dem2 | 8000 | PATCH | /users/me/patients/{patient_id} | (No description) | `curl -X PATCH http://localhost:8000/users/me/patients/pat-123 -d '{}'` |
| dem2 | 8000 | DELETE | /users/me/patients/{patient_id} | (No description) | `curl http://localhost:8000/users/me/patients/pat-123` |
| dem2 | 8000 | DELETE | /users/me/patients/{patient_id}/data | (No description) | `curl http://localhost:8000/users/me/patients/pat-123/data` |
| dem2 | 8000 | GET | /users/me/settings | (No description) | `curl http://localhost:8000/users/me/settings` |
| dem2 | 8000 | PATCH | /users/me/settings | (No description) | `curl -X PATCH http://localhost:8000/users/me/settings -d '{}'` |
| dem2 | 8000 | GET | /users/sessions | (No description) | `curl http://localhost:8000/users/sessions` |
| dem2 | 8000 | POST | /users/sessions | (No description) | `curl -X POST http://localhost:8000/users/sessions -d '{}'` |
| dem2 | 8000 | GET | /users/sessions/{session_id} | (No description) | `curl http://localhost:8000/users/sessions/abc123` |
| dem2 | 8000 | POST | /users/sessions/{session_id} | (No description) | `curl -X POST http://localhost:8000/users/sessions/abc123 -d '{}'` |
| dem2 | 8000 | POST | /users/sessions/{session_id}/feedback | (No description) | `curl -X POST http://localhost:8000/users/sessions/abc123/feedback -d '{}'` |
| dem2 | 8000 | POST | /users/sessions/{session_id}/name | (No description) | `curl -X POST http://localhost:8000/users/sessions/abc123/name -d '{}'` |
| dem2 | 8000 | POST | /users/sessions/{session_id}/summarize | (No description) | `curl -X POST http://localhost:8000/users/sessions/abc123/summarize -d '{}'` |
| dem2 | 8000 | GET | /{bookmark_id} | (No description) | `curl http://localhost:8000/bmk-456` |
| dem2 | 8000 | PATCH | /{bookmark_id} | (No description) | `curl -X PATCH http://localhost:8000/bmk-456 -d '{}'` |
| dem2 | 8000 | POST | /{bookmark_id}/tags/{tag_id} | (No description) | `curl -X POST http://localhost:8000/bmk-456/tags/{tag_id} -d '{}'` |
| dem2 | 8000 | DELETE | /{bookmark_id}/tags/{tag_id} | (No description) | `curl http://localhost:8000/bmk-456/tags/{tag_id}` |
| dem2 | 8000 | GET | /{layout_type}/available-items | (No description) | `curl http://localhost:8000/{layout_type}/available-items` |
| dem2 | 8000 | GET | /{layout_type}/stored | (No description) | `curl http://localhost:8000/{layout_type}/stored` |
| dem2 | 8000 | PUT | /{layout_type}/stored | (No description) | `curl -X PUT http://localhost:8000/{layout_type}/stored -d '{}'` |

---

## dem2-webui

**Port**: 3000
**Total Routes**: 25

### API Routes

| Service | Port | Method | Path | Description | Example |
|---------|------|--------|------|-------------|---------|
| dem2-webui | 3000 | POST | /api/logout | (No description) | `curl -X POST http://localhost:3000/api/logout -d '{}'` |
| dem2-webui | 3000 | GET | /api/sentry-example-api | A faulty API route to test Sentry's error monitoring | `curl http://localhost:3000/api/sentry-example-api` |

### Pages

| Service | Port | Method | Path | Description | Example |
|---------|------|--------|------|-------------|---------|
| dem2-webui | 3000 | PAGE | / | Index Page (Server Component) | `http://localhost:3000/` |
| dem2-webui | 3000 | PAGE | /allergies | Allergies & Intolerances (Client Component) | `http://localhost:3000/allergies` |
| dem2-webui | 3000 | PAGE | /appointments | My Appointments Page (Client Component) | `http://localhost:3000/appointments` |
| dem2-webui | 3000 | PAGE | /auth | Server Component | `http://localhost:3000/auth` |
| dem2-webui | 3000 | PAGE | /body | Body (Client Component) | `http://localhost:3000/body` |
| dem2-webui | 3000 | PAGE | /bookmarks | My Bookmarks (Client Component) | `http://localhost:3000/bookmarks` |
| dem2-webui | 3000 | PAGE | /conditions | Conditions (Client Component) | `http://localhost:3000/conditions` |
| dem2-webui | 3000 | PAGE | /encounters | Encounters Page (Client Component) | `http://localhost:3000/encounters` |
| dem2-webui | 3000 | PAGE | /healthcare-network | Healthcare Network (Client Component) | `http://localhost:3000/healthcare-network` |
| dem2-webui | 3000 | PAGE | /home | Home Page (Client Component) | `http://localhost:3000/home` |
| dem2-webui | 3000 | PAGE | /markers | Health Markers (Server Component) | `http://localhost:3000/markers` |
| dem2-webui | 3000 | PAGE | /medications | My Medications Page (Client Component) | `http://localhost:3000/medications` |
| dem2-webui | 3000 | PAGE | /onboarding | Onboarding Wizard (Client Component) | `http://localhost:3000/onboarding` |
| dem2-webui | 3000 | PAGE | /reports | Medical Reports (Server Component) | `http://localhost:3000/reports` |
| dem2-webui | 3000 | PAGE | /research | AI Research (Server Component) | `http://localhost:3000/research` |
| dem2-webui | 3000 | PAGE | /sentry-example-page | Page (Client Component) | `http://localhost:3000/sentry-example-page` |
| dem2-webui | 3000 | PAGE | /settings | User Settings Page (Server Component) | `http://localhost:3000/settings` |
| dem2-webui | 3000 | PAGE | /settings/account | Account Settings Page (Client Component) | `http://localhost:3000/settings/account` |
| dem2-webui | 3000 | PAGE | /settings/onboarding | Onboarding Settings Page (Client Component) | `http://localhost:3000/settings/onboarding` |
| dem2-webui | 3000 | PAGE | /settings/patient-profiles | Patient Profiles Settings Page (Client Component) | `http://localhost:3000/settings/patient-profiles` |
| dem2-webui | 3000 | PAGE | /settings/preferences | Preferences Settings Page (Server Component) | `http://localhost:3000/settings/preferences` |
| dem2-webui | 3000 | PAGE | /supplements | My Supplements Page (Client Component) | `http://localhost:3000/supplements` |
| dem2-webui | 3000 | PAGE | /symptoms | Symptoms (Client Component) | `http://localhost:3000/symptoms` |

---

## medical-catalog

**Port**: 8001
**Total Routes**: 20

### API Routes

| Service | Port | Method | Path | Description | Example |
|---------|------|--------|------|-------------|---------|
| medical-catalog | 8001 | POST | /api/v1/biomarkers/derivatives/enrich | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/derivatives/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/derivatives/search | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/derivatives/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/derivatives/search-by-aliases | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/derivatives/search-by-aliases -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/enrich | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/enrich2 | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/enrich2 -d '{}'` |
| medical-catalog | 8001 | GET | /api/v1/biomarkers/enrich2/status/{task_id} | (No description) | `curl http://localhost:8001/api/v1/biomarkers/enrich2/status/{task_id}` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/search | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/search-by-aliases | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/search-by-aliases -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/search2 | (No description) | `curl -X POST http://localhost:8001/api/v1/biomarkers/search2 -d '{}'` |
| medical-catalog | 8001 | GET | /api/v1/catalog/metadata | Get aggregated metadata for catalog filters. | `curl http://localhost:8001/api/v1/catalog/metadata` |
| medical-catalog | 8001 | POST | /api/v1/catalog/search | (No description) | `curl -X POST http://localhost:8001/api/v1/catalog/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/conditions/enrich | (No description) | `curl -X POST http://localhost:8001/api/v1/conditions/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/conditions/search | (No description) | `curl -X POST http://localhost:8001/api/v1/conditions/search -d '{}'` |
| medical-catalog | 8001 | GET | /api/v1/qdrant/{path:path} | (No description) | `curl http://localhost:8001/api/v1/qdrant/collections/info` |
| medical-catalog | 8001 | POST | /api/v1/qdrant/{path:path} | (No description) | `curl -X POST http://localhost:8001/api/v1/qdrant/collections/info -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/substances/enrich | (No description) | `curl -X POST http://localhost:8001/api/v1/substances/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/substances/search | (No description) | `curl -X POST http://localhost:8001/api/v1/substances/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/symptoms/enrich | (No description) | `curl -X POST http://localhost:8001/api/v1/symptoms/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/symptoms/search | (No description) | `curl -X POST http://localhost:8001/api/v1/symptoms/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/symptoms/search-by-aliases | (No description) | `curl -X POST http://localhost:8001/api/v1/symptoms/search-by-aliases -d '{}'` |

---

## Statistics

- **Total Routes**: 173

### Routes by Service

| Service | Routes |
|---------|--------|
| dem2 | 128 |
| dem2-webui | 25 |
| medical-catalog | 20 |

### Routes by Method

| Method | Count |
|--------|-------|
| DELETE | 13 |
| GET | 80 |
| PAGE | 23 |
| PATCH | 6 |
| POST | 47 |
| PUT | 2 |
| WS | 2 |
