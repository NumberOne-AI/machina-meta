# API Routes Documentation

Comprehensive listing of all API routes and pages across all services in the machina-meta workspace.

**Generated**: 2025-12-30T10:35:30.514603
**Total Routes**: 172
**Services**: dem2, dem2-webui, medical-catalog

## Table of Contents

- [dem2](#dem2)
- [dem2-webui](#dem2-webui)
- [medical-catalog](#medical-catalog)

---

## dem2

**Port**: 8000
**Total Routes**: 126

### API Routes

| Service | Port | Method | Path | Description | Example |
|---------|------|--------|------|-------------|---------|
| dem2 | 8000 | GET | /api/v1/auth/google/callback | Google Oauth Callback | `curl http://localhost:8000/api/v1/auth/google/callback` |
| dem2 | 8000 | GET | /api/v1/auth/google/login | Google Oauth Init | `curl http://localhost:8000/api/v1/auth/google/login` |
| dem2 | 8000 | POST | /api/v1/auth/logout | Logout | `curl -X POST http://localhost:8000/api/v1/auth/logout -d '{}'` |
| dem2 | 8000 | POST | /api/v1/auth/refresh | Refresh Tokens | `curl -X POST http://localhost:8000/api/v1/auth/refresh -d '{}'` |
| dem2 | 8000 | GET | /api/v1/auth/users/me | User Info | `curl http://localhost:8000/api/v1/auth/users/me` |
| dem2 | 8000 | DELETE | /api/v1/auth/users/me | Delete User | `curl http://localhost:8000/api/v1/auth/users/me` |
| dem2 | 8000 | GET | /api/v1/auth/users/me/patients | List Patients | `curl http://localhost:8000/api/v1/auth/users/me/patients` |
| dem2 | 8000 | POST | /api/v1/auth/users/me/patients | Create Patient | `curl -X POST http://localhost:8000/api/v1/auth/users/me/patients -d '{}'` |
| dem2 | 8000 | PATCH | /api/v1/auth/users/me/patients/{patient_id} | Patch Patient | `curl -X PATCH http://localhost:8000/api/v1/auth/users/me/patients/pat-123 -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/auth/users/me/patients/{patient_id} | Delete Patient | `curl http://localhost:8000/api/v1/auth/users/me/patients/pat-123` |
| dem2 | 8000 | DELETE | /api/v1/auth/users/me/patients/{patient_id}/data | Delete Patient Data | `curl http://localhost:8000/api/v1/auth/users/me/patients/pat-123/data` |
| dem2 | 8000 | GET | /api/v1/auth/users/me/settings | Get User Settings | `curl http://localhost:8000/api/v1/auth/users/me/settings` |
| dem2 | 8000 | PATCH | /api/v1/auth/users/me/settings | Update User Settings | `curl -X PATCH http://localhost:8000/api/v1/auth/users/me/settings -d '{}'` |
| dem2 | 8000 | POST | /api/v1/bookmark-groups | Create Group | `curl -X POST http://localhost:8000/api/v1/bookmark-groups -d '{}'` |
| dem2 | 8000 | GET | /api/v1/bookmark-groups | List Groups | `curl http://localhost:8000/api/v1/bookmark-groups` |
| dem2 | 8000 | GET | /api/v1/bookmark-groups/{group_id} | Get Group | `curl http://localhost:8000/api/v1/bookmark-groups/{group_id}` |
| dem2 | 8000 | PATCH | /api/v1/bookmark-groups/{group_id} | Update Group | `curl -X PATCH http://localhost:8000/api/v1/bookmark-groups/{group_id} -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/bookmark-groups/{group_id} | Delete Group | `curl http://localhost:8000/api/v1/bookmark-groups/{group_id}` |
| dem2 | 8000 | POST | /api/v1/bookmark-tags | Create Tag | `curl -X POST http://localhost:8000/api/v1/bookmark-tags -d '{}'` |
| dem2 | 8000 | GET | /api/v1/bookmark-tags | List Tags | `curl http://localhost:8000/api/v1/bookmark-tags` |
| dem2 | 8000 | GET | /api/v1/bookmark-tags/search | Search Tags | `curl http://localhost:8000/api/v1/bookmark-tags/search` |
| dem2 | 8000 | GET | /api/v1/bookmark-tags/{tag_id} | Get Tag | `curl http://localhost:8000/api/v1/bookmark-tags/{tag_id}` |
| dem2 | 8000 | PATCH | /api/v1/bookmark-tags/{tag_id} | Update Tag | `curl -X PATCH http://localhost:8000/api/v1/bookmark-tags/{tag_id} -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/bookmark-tags/{tag_id} | Delete Tag | `curl http://localhost:8000/api/v1/bookmark-tags/{tag_id}` |
| dem2 | 8000 | POST | /api/v1/bookmarks | Create Bookmark | `curl -X POST http://localhost:8000/api/v1/bookmarks -d '{}'` |
| dem2 | 8000 | GET | /api/v1/bookmarks | List Bookmarks | `curl http://localhost:8000/api/v1/bookmarks` |
| dem2 | 8000 | DELETE | /api/v1/bookmarks | Delete Bookmarks | `curl http://localhost:8000/api/v1/bookmarks` |
| dem2 | 8000 | GET | /api/v1/bookmarks/by-tag/{tag_id} | Get Bookmarks By Tag | `curl http://localhost:8000/api/v1/bookmarks/by-tag/{tag_id}` |
| dem2 | 8000 | GET | /api/v1/bookmarks/count | Count Bookmarks | `curl http://localhost:8000/api/v1/bookmarks/count` |
| dem2 | 8000 | GET | /api/v1/bookmarks/{bookmark_id} | Get Bookmark | `curl http://localhost:8000/api/v1/bookmarks/bmk-456` |
| dem2 | 8000 | PATCH | /api/v1/bookmarks/{bookmark_id} | Update Bookmark | `curl -X PATCH http://localhost:8000/api/v1/bookmarks/bmk-456 -d '{}'` |
| dem2 | 8000 | POST | /api/v1/bookmarks/{bookmark_id}/tags/{tag_id} | Add Tag To Bookmark | `curl -X POST http://localhost:8000/api/v1/bookmarks/bmk-456/tags/{tag_id} -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/bookmarks/{bookmark_id}/tags/{tag_id} | Remove Tag From Bookmark | `curl http://localhost:8000/api/v1/bookmarks/bmk-456/tags/{tag_id}` |
| dem2 | 8000 | GET | /api/v1/calendar | Get Doctor Events | `curl http://localhost:8000/api/v1/calendar` |
| dem2 | 8000 | POST | /api/v1/documents-processor/process_document | Queue document for processing and extract medical data | `curl -X POST http://localhost:8000/api/v1/documents-processor/process_document -d '{}'` |
| dem2 | 8000 | GET | /api/v1/documents-processor/queue/stats | Get queue statistics | `curl http://localhost:8000/api/v1/documents-processor/queue/stats` |
| dem2 | 8000 | GET | /api/v1/documents-processor/tasks | Get list of processing tasks for current user | `curl http://localhost:8000/api/v1/documents-processor/tasks` |
| dem2 | 8000 | GET | /api/v1/documents-processor/tasks/stream | Stream progress events for all user's tasks through a single connection. | `curl http://localhost:8000/api/v1/documents-processor/tasks/stream` |
| dem2 | 8000 | GET | /api/v1/documents-processor/tasks/{task_id} | Get specific task status | `curl http://localhost:8000/api/v1/documents-processor/tasks/{task_id}` |
| dem2 | 8000 | POST | /api/v1/documents-processor/test_process_document | Queue document for processing and extract medical data | `curl -X POST http://localhost:8000/api/v1/documents-processor/test_process_document -d '{}'` |
| dem2 | 8000 | GET | /api/v1/file-storage/files | List Files | `curl http://localhost:8000/api/v1/file-storage/files` |
| dem2 | 8000 | POST | /api/v1/file-storage/files/bulk_delete | Bulk Delete Files | `curl -X POST http://localhost:8000/api/v1/file-storage/files/bulk_delete -d '{}'` |
| dem2 | 8000 | POST | /api/v1/file-storage/files/upload | Upload File | `curl -X POST http://localhost:8000/api/v1/file-storage/files/upload -d '{}'` |
| dem2 | 8000 | POST | /api/v1/file-storage/files/upload/bulk | Bulk Upload Files | `curl -X POST http://localhost:8000/api/v1/file-storage/files/upload/bulk -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/file-storage/files/{file_id} | Delete File | `curl http://localhost:8000/api/v1/file-storage/files/{file_id}` |
| dem2 | 8000 | GET | /api/v1/file-storage/files/{file_id}/download | Download File | `curl http://localhost:8000/api/v1/file-storage/files/{file_id}/download` |
| dem2 | 8000 | POST | /api/v1/geocoding/geocode/zip | Geocode a 5-digit US ZIP code to coordinates. | `curl -X POST http://localhost:8000/api/v1/geocoding/geocode/zip -d '{}'` |
| dem2 | 8000 | GET | /api/v1/geocoding/health | Simple health probe. | `curl http://localhost:8000/api/v1/geocoding/health` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/allergy-records | Get list of allergy records for a patient with optional filtering. | `curl http://localhost:8000/api/v1/graph-memory/medical/allergy-records` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/allergy-records/{record_id} | Get detailed information about a specific allergy record including all related reactions and type. | `curl http://localhost:8000/api/v1/graph-memory/medical/allergy-records/{record_id}` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/care_network | Get network of practitioners and organizations connected through encounters.

Returns:
- List of practitioners involved in care
- List of organizations where care was provided
- Connections showing which practitioners worked with which organizations
  and how many encounters they shared

If patient_id is provided (via x-patient-context-id header), returns network
for that patient only. Otherwise, returns network across all user's patients. | `curl http://localhost:8000/api/v1/graph-memory/medical/care_network` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/conditions | Get list of condition cases for a patient with optional filtering. | `curl http://localhost:8000/api/v1/graph-memory/medical/conditions` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/conditions/{condition_id} | Get detailed information about a specific condition case including type. | `curl http://localhost:8000/api/v1/graph-memory/medical/conditions/{condition_id}` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/document_references | Get all document references with related entities for a user.

Returns documents with organizations, practitioners, and patients,
ordered by creation date (newest first). | `curl http://localhost:8000/api/v1/graph-memory/medical/document_references` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/document_references/{document_id} | Get a specific document reference by ID. | `curl http://localhost:8000/api/v1/graph-memory/medical/document_references/{document_id}` |
| dem2 | 8000 | DELETE | /api/v1/graph-memory/medical/document_references/{document_id} | Delete a document reference and all nodes extracted from it.

Removes:
- The DocumentReference itself
- All medical data nodes where source_type='document' and source_id=document_id | `curl http://localhost:8000/api/v1/graph-memory/medical/document_references/{document_id}` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/document_references/{document_id}/details | Get a document reference with all related organizations and practitioners. | `curl http://localhost:8000/api/v1/graph-memory/medical/document_references/{document_id}/details` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/encounters | Get encounters with their related practitioners and organizations.

Returns encounters with:
- Basic encounter information (uuid, name, dates, etc.)
- List of practitioners involved (via WITH_PRACTITIONER relationship)
- List of organizations where encounter occurred (via AT_ORGANIZATION relationship)

If patient_id is provided (via x-patient-context-id header), filters encounters to that patient only.
Otherwise, returns encounters across all user's patients. | `curl http://localhost:8000/api/v1/graph-memory/medical/encounters` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/intake-events | Get intake events by date range | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/intake-events` |
| dem2 | 8000 | POST | /api/v1/graph-memory/medical/medication/intake-events | Create intake event | `curl -X POST http://localhost:8000/api/v1/graph-memory/medical/medication/intake-events -d '{}'` |
| dem2 | 8000 | POST | /api/v1/graph-memory/medical/medication/intake-events/bulk | Create intake events for regimens of specified type on date | `curl -X POST http://localhost:8000/api/v1/graph-memory/medical/medication/intake-events/bulk -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/graph-memory/medical/medication/intake-events/bulk | Delete intake events for regimens of specified type on date | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/intake-events/bulk` |
| dem2 | 8000 | DELETE | /api/v1/graph-memory/medical/medication/intake-events/{intake_id} | Delete supplement intake | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/intake-events/{intake_id}` |
| dem2 | 8000 | POST | /api/v1/graph-memory/medical/medication/intake-regimens | Create intake regimen | `curl -X POST http://localhost:8000/api/v1/graph-memory/medical/medication/intake-regimens -d '{}'` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/intake-regimens/list | List intake regimens for patient | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/intake-regimens/list` |
| dem2 | 8000 | DELETE | /api/v1/graph-memory/medical/medication/intake-regimens/{regimen_id} | Delete intake regimen | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/intake-regimens/{regimen_id}` |
| dem2 | 8000 | PATCH | /api/v1/graph-memory/medical/medication/intake-regimens/{regimen_id} | Update intake regimen | `curl -X PATCH http://localhost:8000/api/v1/graph-memory/medical/medication/intake-regimens/{regimen_id} -d '{}'` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/medications/by_rxcui | Get or enrich medication by RxNorm ID | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/medications/by_rxcui` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/medications/by_uuid | Get medication by UUID | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/medications/by_uuid` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/medications/search | Search medications using RxNorm approximate match API. | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/medications/search` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/medications/{medication_id}/ingredients | Get medication ingredients | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/medications/{medication_id}/ingredients` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/supplements/by_ingr_grp | Get or enrich supplement by ODS ingredient group (FOR UNBRANDED SUPPLEMENTS) | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/supplements/by_ingr_grp` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/supplements/by_ods_label | Get or enrich supplement by ODS label ID (FOR BRANDED SUPPLEMENTS) | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/supplements/by_ods_label` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/supplements/by_uuid | Get supplement by UUID | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/supplements/by_uuid` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/supplements/search | Search substances using ODS ingredient groups API. | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/supplements/search` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/medication/supplements/{supplement_id}/ingredients | Get supplement ingredients | `curl http://localhost:8000/api/v1/graph-memory/medical/medication/supplements/{supplement_id}/ingredients` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/observations/grouped | Get observation values for a patient grouped by observation type.

Returns observations ordered by clinical importance (descending).

Each group contains:
- observation_type: Metadata about the observation type
- clinical_importance: Weight from TRACKS relationship
- values: Observation values for this type (ordered by observed_at descending)
- body_systems: List of body system relationships

Supports filtering by:
- Body systems: cardiovascular, respiratory, endocrine, etc.
- LOINC codes: filter by specific LOINC codes
- Minimum body system weight: only show observations with strong enough body system links
- Body system impact types: filter by impact type
- Search query: partial name matching (case-insensitive)
- Per-type values limit: limit number of values per observation type
- Out of range: only return values outside normal/optimal reference ranges
- Value status: filter by document_value_color (red, yellow, green, white)
- Page number: filter by page number (only values with this page in page_numbers)

When out_of_range=true:
- Checks if the last (most recent by observed_at) or second-to-last value is out of range
- If either is out of normal/optimal range, returns ALL values for that observation type
- Prioritizes document_reference_range over standard_reference_range
- Excludes observation types without reference ranges
- Excludes groups where both last values are within normal range | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/grouped` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/observations/stats | Get statistics about observation types grouped by document_value_color.

Returns counts of observation types based on their last 1-2 values' document_value_color:
- green_count: At least one value with document_value_color = "green"
- yellow_count: At least one value with document_value_color = "yellow"
- red_count: At least one value with document_value_color = "red"
- white_count: Values with document_value_color = "white" or null
- total_count: Total observation types for this patient | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/stats` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/observations/types/by-uuid/{uuid} | Get detailed observation type information by UUID. | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/types/by-uuid/{uuid}` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/observations/types/search | Search observation types by semantic similarity using embeddings.

Returns observation types ranked by similarity to the query text.
Uses vector search on observation type embeddings (name, display_name, aliases, LOINC metadata).

Examples:
- Search for cholesterol: GET /observations/types/search?q=cholesterol
- Search for vitamin D with high precision: GET /observations/types/search?q=vitamin%20d&min_score=0.8 | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/types/search` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/observations/types/{code} | Get observation types by catalog code.

Multiple observation types can exist for the same code with different units. | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/types/{code}` |
| dem2 | 8000 | PATCH | /api/v1/graph-memory/medical/observations/values/{uid} | Update an observation value by UUID.

Updates one or more fields of an observation value:
- value_numeric: Numeric measurement value
- value_text: Text measurement value
- observed_at: When the observation was taken
- interpretation: Clinical interpretation

Returns the updated observation value. | `curl -X PATCH http://localhost:8000/api/v1/graph-memory/medical/observations/values/{uid} -d '{}'` |
| dem2 | 8000 | DELETE | /api/v1/graph-memory/medical/observations/values/{uid} | Delete an observation value by UUID.

Removes the observation value and automatically cleans up orphaned
TRACKS relationships if this was the last value for the observation type. | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/values/{uid}` |
| dem2 | 8000 | DELETE | /api/v1/graph-memory/medical/observations/{observation_type_uuid} | Delete all observation values for a type and remove patient tracking.

This endpoint:
- Deletes all of the patient's observation values for this type
- Removes the patient's TRACKS relationship to the observation type
- Does NOT delete the ObservationTypeNode itself (it's shared across all patients)

Returns counts of deleted items:
- values_deleted: Number of observation values deleted
- tracks_deleted: Number of TRACKS relationships removed (0 or 1) | `curl http://localhost:8000/api/v1/graph-memory/medical/observations/{observation_type_uuid}` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/symptom-types | Get list of symptom types that the patient has episodes for, ordered by most recent. | `curl http://localhost:8000/api/v1/graph-memory/medical/symptom-types` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/symptom-types/{type_id} | Get detailed information about a symptom type including all patient episodes for that type. | `curl http://localhost:8000/api/v1/graph-memory/medical/symptom-types/{type_id}` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/symptoms | Get list of symptom episodes for a patient with optional filtering. | `curl http://localhost:8000/api/v1/graph-memory/medical/symptoms` |
| dem2 | 8000 | GET | /api/v1/graph-memory/medical/symptoms/{symptom_id} | Get detailed information about a specific symptom episode including type. | `curl http://localhost:8000/api/v1/graph-memory/medical/symptoms/{symptom_id}` |
| dem2 | 8000 | GET | /api/v1/health | Health | `curl http://localhost:8000/api/v1/health` |
| dem2 | 8000 | POST | /api/v1/med-agent/run | Run Agent | `curl -X POST http://localhost:8000/api/v1/med-agent/run -d '{}'` |
| dem2 | 8000 | POST | /api/v1/med-agent/run_sse | Run Agent Sse | `curl -X POST http://localhost:8000/api/v1/med-agent/run_sse -d '{}'` |
| dem2 | 8000 | POST | /api/v1/med-agent/users/sessions | Create Session | `curl -X POST http://localhost:8000/api/v1/med-agent/users/sessions -d '{}'` |
| dem2 | 8000 | GET | /api/v1/med-agent/users/sessions | List Sessions | `curl http://localhost:8000/api/v1/med-agent/users/sessions` |
| dem2 | 8000 | POST | /api/v1/med-agent/users/sessions/{session_id} | Create Session With Id | `curl -X POST http://localhost:8000/api/v1/med-agent/users/sessions/abc123 -d '{}'` |
| dem2 | 8000 | GET | /api/v1/med-agent/users/sessions/{session_id} | Get Session | `curl http://localhost:8000/api/v1/med-agent/users/sessions/abc123` |
| dem2 | 8000 | POST | /api/v1/med-agent/users/sessions/{session_id}/feedback | Submit Feedback By Invocation | `curl -X POST http://localhost:8000/api/v1/med-agent/users/sessions/abc123/feedback -d '{}'` |
| dem2 | 8000 | POST | /api/v1/med-agent/users/sessions/{session_id}/name | Set Session Name | `curl -X POST http://localhost:8000/api/v1/med-agent/users/sessions/abc123/name -d '{}'` |
| dem2 | 8000 | POST | /api/v1/med-agent/users/sessions/{session_id}/summarize | Summarize Session Name | `curl -X POST http://localhost:8000/api/v1/med-agent/users/sessions/abc123/summarize -d '{}'` |
| dem2 | 8000 | POST | /api/v1/medical-data-engine/test-stream | Test Stream | `curl -X POST http://localhost:8000/api/v1/medical-data-engine/test-stream -d '{}'` |
| dem2 | 8000 | POST | /api/v1/medical-data-storage/allergies | Create allergy intolerance record | `curl -X POST http://localhost:8000/api/v1/medical-data-storage/allergies -d '{}'` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/allergies | Get patient allergies | `curl http://localhost:8000/api/v1/medical-data-storage/allergies` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/allergies/grouped | Get allergies grouped by allergen name with complete timeline history.

This endpoint groups multiple allergy records for the same allergen
(e.g., active → resolved → active) into a single response with timeline.

Useful for:
- Avoiding duplicate allergens in UI
- Showing allergy status history
- Understanding timeline of allergy changes

If active_only=True, only returns allergens where the most recent record is active.
The timeline will still include all historical status changes for that allergen. | `curl http://localhost:8000/api/v1/medical-data-storage/allergies/grouped` |
| dem2 | 8000 | DELETE | /api/v1/medical-data-storage/allergies/{allergy_id} | Delete allergy intolerance record | `curl http://localhost:8000/api/v1/medical-data-storage/allergies/alg-789` |
| dem2 | 8000 | PATCH | /api/v1/medical-data-storage/allergies/{allergy_id}/status | Update allergy clinical status | `curl -X PATCH http://localhost:8000/api/v1/medical-data-storage/allergies/alg-789/status -d '{}'` |
| dem2 | 8000 | POST | /api/v1/medical-data-storage/cleanup/orphaned_resources | Clean up orphaned resources with source_document_deleted=true | `curl -X POST http://localhost:8000/api/v1/medical-data-storage/cleanup/orphaned_resources -d '{}'` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/document_references | Get all document references for the current user | `curl http://localhost:8000/api/v1/medical-data-storage/document_references` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/document_references/{document_id} | Get a specific document reference by ID. | `curl http://localhost:8000/api/v1/medical-data-storage/document_references/{document_id}` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/encounters | Get encounters with their related practitioners and organizations.

Returns encounters with:
- Basic encounter information (uuid, name, dates, etc.)
- List of practitioners involved (via WITH_PRACTITIONER relationship)
- List of organizations where encounter occurred (via AT_ORGANIZATION relationship)

If patient_id is provided (via x-patient-context-id header), filters encounters to that patient only.
Otherwise, returns encounters across all user's patients.

Data is retrieved from graph-memory (Neo4j). | `curl http://localhost:8000/api/v1/medical-data-storage/encounters` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/observations | Get observations grouped by LOINC code with metadata and values.

Returns a dictionary where key is LOINC code and value contains 'meta' and 'values'.

The 'meta' contains:
- loinc_code, loinc_name, display_name, unit
- body_system_impacts (same for all observations of this type)

The 'values' contains list of observations with:
- value (numeric or string)
- effective_date (timestamp)
- range (reference range with low/high)

Supports filtering by:
- LOINC codes: specific observation types
- Body systems: cardiovascular, respiratory, endocrine, etc.
- Search query: partial name matching
- Per LOINC limit: limit observations per code (useful for getting latest N values per type)

Results are ordered by effective_date in descending order (newest first). | `curl http://localhost:8000/api/v1/medical-data-storage/observations` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/observations/body_system/{body_system} | DEPRECATED: Use `/observations` instead with body_systems parameter.

This endpoint will be removed in a future version. | `curl http://localhost:8000/api/v1/medical-data-storage/observations/body_system/{body_system}` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/observations/grouped | Get observation values for a patient grouped by observation type.

Returns observations ordered by clinical importance (descending).

Each group contains:
- observation_type: Metadata about the observation type (code, name, unit, etc.)
- clinical_importance: Weight from TRACKS relationship (higher = more important)
- values: Observation values for this type (ordered by observed_at descending)
- document_reference_range: Latest reference range from patient documents (if any)
- standard_reference_range: Latest standard reference range (if any)

The clinical_importance is automatically calculated based on:
- Body system impacts (weight and impact_type)
- Maximum weight from all body system relationships
- Default value of 0.5 if no body system relationships exist

Supports filtering by:
- Body systems: cardiovascular, respiratory, endocrine, etc.
- LOINC codes: filter by specific LOINC codes
- Minimum body system weight: only show observations with strong enough body system links
- Body system impact types: filter by impact type (primary, secondary, etc.)
- Search query: partial name or display_name matching (case-insensitive)
- Per-type values limit: limit number of values per observation type (useful for getting latest N values)

Pagination applies to observation types, not individual values. | `curl http://localhost:8000/api/v1/medical-data-storage/observations/grouped` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/observations/stats | Get observation statistics with trends and reference ranges.

Returns aggregated metrics including:
- Latest and previous values
- Trend direction and percentage change
- Reference ranges
- Body system impacts
- Observation counts

Supports filtering by:
- LOINC codes: specific observation types
- Body systems: cardiovascular, respiratory, endocrine, etc.
- Search query: partial name matching | `curl http://localhost:8000/api/v1/medical-data-storage/observations/stats` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/observations/values | DEPRECATED: Use `/observations` instead with loinc_codes parameter.

This endpoint will be removed in a future version. | `curl http://localhost:8000/api/v1/medical-data-storage/observations/values` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/organizations | Get organizations filtered by user_id and optionally patient_id (from header) | `curl http://localhost:8000/api/v1/medical-data-storage/organizations` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/patients/statistics | Get statistics for all patients | `curl http://localhost:8000/api/v1/medical-data-storage/patients/statistics` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/patients/{patient_uuid}/statistics | Get statistics for a specific patient | `curl http://localhost:8000/api/v1/medical-data-storage/patients/{patient_uuid}/statistics` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/practitioners | Get practitioners filtered by user_id and optionally patient_id (from header) | `curl http://localhost:8000/api/v1/medical-data-storage/practitioners` |
| dem2 | 8000 | GET | /api/v1/medical-data-storage/resource_connections | Get connections between practitioners and organizations based on shared encounters.

Returns a graph structure showing:
- All practitioners
- All organizations
- Connections between them with encounter count and date range

If patient_id is provided (via header), filters connections to that patient only.
Otherwise, returns connections across all user's patients. | `curl http://localhost:8000/api/v1/medical-data-storage/resource_connections` |
| dem2 | 8000 | DELETE | /api/v1/medical-data-storage/user_data | Erase User Data | `curl http://localhost:8000/api/v1/medical-data-storage/user_data` |
| dem2 | 8000 | GET | /api/v1/ui-layouts/{layout_type}/available-items | Get Available Ui Layout Items | `curl http://localhost:8000/api/v1/ui-layouts/{layout_type}/available-items` |
| dem2 | 8000 | GET | /api/v1/ui-layouts/{layout_type}/stored | Get User Ui Layout | `curl http://localhost:8000/api/v1/ui-layouts/{layout_type}/stored` |
| dem2 | 8000 | PUT | /api/v1/ui-layouts/{layout_type}/stored | Store User Ui Layout | `curl -X PUT http://localhost:8000/api/v1/ui-layouts/{layout_type}/stored -d '{}'` |
| dem2 | 8000 | POST | /api/v1/user/onboarding/complete | Store Onboarding Answers | `curl -X POST http://localhost:8000/api/v1/user/onboarding/complete -d '{}'` |
| dem2 | 8000 | PUT | /api/v1/user/onboarding/survey/answers | Submit Answers | `curl -X PUT http://localhost:8000/api/v1/user/onboarding/survey/answers -d '{}'` |
| dem2 | 8000 | GET | /api/v1/user/onboarding/survey/questions | Get Questions | `curl http://localhost:8000/api/v1/user/onboarding/survey/questions` |
| dem2 | 8000 | GET | /health | Health | `curl http://localhost:8000/health` |

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
**Total Routes**: 21

### API Routes

| Service | Port | Method | Path | Description | Example |
|---------|------|--------|------|-------------|---------|
| medical-catalog | 8001 | POST | /api/v1/biomarkers/derivatives/enrich | Start derivative enrichment process from cached derivatives or provided names.

If derivative_names is provided, creates artificial entries and processes them.
Otherwise, processes cached RATIO/SUM/PERCENT derived measurements that were
identified during biomarker categorization.

Parses derivative names, resolves base biomarker IDs, and stores enriched derivatives.

Process runs in background. Check logs for progress and completion. | `curl -X POST http://localhost:8001/api/v1/biomarkers/derivatives/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/derivatives/search | Batch search for biomarker test derivatives using cascading strategy.

Search order for each query (fail-fast):
1. Exact match by test_name (case-insensitive)
2. Match by aliases (case-insensitive)
3. Semantic search by embedding similarity

Returns partial success results - successful queries return results,
failed queries return error messages. | `curl -X POST http://localhost:8001/api/v1/biomarkers/derivatives/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/derivatives/search-by-aliases | Batch search derivatives by alias groups with parallel execution.

Searches the aliases_search array field for ANY match with the provided aliases.
Uses Qdrant's MatchAny filter for efficient array-to-array matching.
Processes multiple alias groups in parallel using asyncio.gather.

This endpoint does NOT normalize aliases - searches them as-is.
All results return with MatchType.ALIAS.

Limits:
- Max 100 alias groups
- Max 5 aliases per group (automatically truncated if exceeded) | `curl -X POST http://localhost:8001/api/v1/biomarkers/derivatives/search-by-aliases -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/enrich | Start biomarker enrichment process by biomarker names.

Creates BiomarkerDatasetMeta objects from provided names and
enriches them through the full pipeline.

Process runs in background. Check logs for progress and completion. | `curl -X POST http://localhost:8001/api/v1/biomarkers/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/enrich2 | Start unified enrichment process using BiomarkerPipeline.

First checks which names already exist in storage. If all exist,
returns immediately with status 'skipped'. Otherwise starts
background task for remaining names.

Use the returned task_id to check status via GET /enrich2/status/{task_id}. | `curl -X POST http://localhost:8001/api/v1/biomarkers/enrich2 -d '{}'` |
| medical-catalog | 8001 | GET | /api/v1/biomarkers/enrich2/status/{task_id} | Get status of an enrichment task by ID.

Returns current status (pending/completed/failed) and processing statistics. | `curl http://localhost:8001/api/v1/biomarkers/enrich2/status/{task_id}` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/search | Batch search for biomarkers using cascading strategy.

Search order for each query (fail-fast):
1. Exact match by short_name (case-insensitive)
2. Match by aliases (case-insensitive)
3. Semantic search by embedding similarity

Returns partial success results - successful queries return results,
failed queries return error messages. | `curl -X POST http://localhost:8001/api/v1/biomarkers/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/search-by-aliases | Batch search biomarkers by alias groups with parallel execution.

Searches the aliases_search array field for ANY match with the provided aliases.
Uses Qdrant's MatchAny filter for efficient array-to-array matching.
Processes multiple alias groups in parallel using asyncio.gather.

This endpoint does NOT normalize aliases - searches them as-is (lowercased).
All results return with MatchType.ALIAS.

Limits:
- Max 100 alias groups
- Max 5 aliases per group (automatically truncated if exceeded) | `curl -X POST http://localhost:8001/api/v1/biomarkers/search-by-aliases -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/biomarkers/search2 | Unified batch search for both biomarkers and derivatives by alias groups.

Searches BOTH biomarkers and derivatives collections in parallel.
Returns separate lists for each entity type per alias group.

Limits:
- Max 100 alias groups
- Max 5 aliases per group (automatically truncated if exceeded) | `curl -X POST http://localhost:8001/api/v1/biomarkers/search2 -d '{}'` |
| medical-catalog | 8001 | GET | /api/v1/catalog/metadata | Get aggregated metadata for catalog filters. | `curl http://localhost:8001/api/v1/catalog/metadata` |
| medical-catalog | 8001 | POST | /api/v1/catalog/search | Perform semantic search with embedding generation. | `curl -X POST http://localhost:8001/api/v1/catalog/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/conditions/enrich | Start condition enrichment process by condition names.

Enriches provided condition names through the full pipeline
(LLM metadata generation, embedding creation, etc.).

Process runs in background. Check logs for progress and completion. | `curl -X POST http://localhost:8001/api/v1/conditions/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/conditions/search | Batch search for conditions using cascading strategy.

Search order for each query (fail-fast):
1. Exact match by name (case-insensitive)
2. Match by infermedica_id
3. Match by ICD-10 code
4. Match by SNOMED CT code
5. Match by synonyms (case-insensitive)
6. Semantic search by embedding similarity

Returns partial success results - successful queries return results,
failed queries return error messages. | `curl -X POST http://localhost:8001/api/v1/conditions/search -d '{}'` |
| medical-catalog | 8001 | GET | /api/v1/qdrant/{path} | Proxy GET requests to Qdrant. | `curl http://localhost:8001/api/v1/qdrant/{path}` |
| medical-catalog | 8001 | POST | /api/v1/qdrant/{path} | Proxy POST requests to Qdrant. | `curl -X POST http://localhost:8001/api/v1/qdrant/{path} -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/substances/enrich | Enrich Substance | `curl -X POST http://localhost:8001/api/v1/substances/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/substances/search | Search Substance | `curl -X POST http://localhost:8001/api/v1/substances/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/symptoms/enrich | Start symptom enrichment process by symptom names.

Enriches provided symptom names through the full pipeline
(categorization, description generation, etc.).

Process runs in background. Check logs for progress and completion. | `curl -X POST http://localhost:8001/api/v1/symptoms/enrich -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/symptoms/search | Batch search for symptoms using cascading strategy.

Search order for each query (fail-fast):
1. Exact match by name (case-insensitive)
2. Match by infermedica_id
3. Match by aliases (case-insensitive)
4. Semantic search by embedding similarity

Returns partial success results - successful queries return results,
failed queries return error messages. | `curl -X POST http://localhost:8001/api/v1/symptoms/search -d '{}'` |
| medical-catalog | 8001 | POST | /api/v1/symptoms/search-by-aliases | Batch search symptoms by alias groups with parallel execution.

Searches the aliases_search array field for ANY match with the provided aliases.
Uses Qdrant's MatchAny filter for efficient array-to-array matching.
Processes multiple alias groups in parallel using asyncio.gather.

This endpoint does NOT normalize aliases - searches them as-is (lowercased).
All results return with MatchType.ALIAS.

Limits:
- Max 100 alias groups
- Max 5 aliases per group (automatically truncated if exceeded) | `curl -X POST http://localhost:8001/api/v1/symptoms/search-by-aliases -d '{}'` |
| medical-catalog | 8001 | GET | /health | Health check endpoint with database connectivity test.

Tests Qdrant connectivity by searching for sample biomarkers.
Returns detailed status including database check results. | `curl http://localhost:8001/health` |

---

## Statistics

- **Total Routes**: 172

### Routes by Service

| Service | Routes |
|---------|--------|
| dem2 | 126 |
| dem2-webui | 25 |
| medical-catalog | 21 |

### Routes by Method

| Method | Count |
|--------|-------|
| DELETE | 16 |
| GET | 78 |
| PAGE | 23 |
| PATCH | 8 |
| POST | 45 |
| PUT | 2 |
