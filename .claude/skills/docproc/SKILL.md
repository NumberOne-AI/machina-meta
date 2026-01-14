# Document Processing (docproc) Skill

**Purpose**: Guide for validating biomarker extraction from medical documents using the document processing pipeline.

## Overview

The document processing pipeline extracts biomarkers from medical PDFs (lab reports, test results) and stores them in Neo4j. The **validation workflow** tests extraction accuracy by comparing extracted biomarkers against ground truth data from the frontend test suite.

## Key Concepts

### 1. Document Processing Pipeline
- **Upload**: PDF documents are uploaded via API (`upload_file`)
- **Process**: Document is processed to extract biomarkers (`process_document`)
- **Storage**: Extracted biomarkers stored in Neo4j graph database
- **Query**: Biomarkers retrieved via graph API (`/graph-memory/medical/observations/grouped`)

### 2. Validation Workflow
- **Ground Truth**: Expected biomarkers stored in `pdf_tests/validation/webui_test_data/*.ts`
- **Extraction**: Actual biomarkers extracted from documents and stored in Neo4j
- **Comparison**: Validation script compares ground truth vs extracted
- **Metrics**: Reports matched count, missing biomarkers, accuracy %

### 3. Catalog Enrichment
- **Medical Catalog**: Qdrant vector database containing known biomarkers
- **Enrichment**: Missing biomarkers can be added to catalog to improve future extractions
- **Two-Run Test**: Run 1 (baseline) → Enrich missing → Run 2 (improved)

## Directory Structure

```
repos/dem2/
├── pdf_tests/
│   ├── medical_records/              # Test PDF documents
│   │   └── Stuart Mcclure Medical Records (PRIVATE)/
│   │       ├── Dutch cortisol 9-01-25.pdf
│   │       ├── Boston Heart June 2025.PDF
│   │       └── ...
│   └── validation/                   # Validation data
│       └── webui_test_data/          # Ground truth from dem2-webui
│           ├── dutch-cortisol-sep-2025-data.ts
│           ├── boston-heart-june-2025-data.ts
│           └── ...
├── scripts/
│   ├── test_extraction_workflow.sh   # Main validation workflow
│   ├── validate_document_biomarkers.py  # Validation script
│   ├── verification.py               # Verification file matching logic
│   └── curl_api.sh                   # API helpers
└── justfile                          # Commands (validate-extraction)
```

## Commands

### List Test Documents
```bash
just list-test-docs
```
Returns JSON array of test PDF paths.

### Upload Document
```bash
cd repos/dem2
just curl_api '{"function": "upload_file", "path": "pdf_tests/medical_records/Stuart Mcclure Medical Records (PRIVATE)/Dutch cortisol 9-01-25.pdf"}'
```
Returns: `{"id": "file-uuid", "filename": "Dutch cortisol 9-01-25.pdf", ...}`

### Process Document
```bash
cd repos/dem2
just curl_api '{"function": "process_document", "file_id": "file-uuid"}'
```
Returns: `{"task_id": "task-uuid", "status": "queued"}`

### Check Task Status
```bash
cd repos/dem2
just curl_api '{"function": "get_task", "task_id": "task-uuid"}'
```
Returns: `{"status": "completed|in_progress|failed", ...}`

### List Documents
```bash
cd repos/dem2
just curl_api '{"function": "list_documents"}'
```
Returns list of all uploaded documents with IDs.

### Validate Extraction
```bash
cd repos/dem2

# Auto-detect first document, full workflow (with enrichment)
just validate-extraction

# Skip Qdrant snapshot reload (faster, assumes catalog is up-to-date)
just validate-extraction --skip-snapshot

# Single run only (no enrichment)
just validate-extraction --skip-enrichment
# OR
just validate-extraction-quick

# Specific document
just validate-extraction FILE_ID FILENAME

# Custom output directory
just validate-extraction --output-dir /path/to/output
```

## Validation Workflow Steps

The `validate-extraction` command runs an 8-step workflow:

### Step 1: Reload Medical Catalog Snapshot
- Restores Qdrant vector database to known state
- Ensures consistent catalog for testing
- **Skip with**: `--skip-snapshot`

### Step 2: Clear Neo4j Biomarkers
- Deletes all existing biomarker nodes from Neo4j
- Ensures clean slate for extraction test
- Prevents contamination from previous runs

### Step 3: Process Document (First Run)
- Extracts biomarkers from uploaded document
- Uses current catalog state
- Stores results in Neo4j

### Step 4: Validate Results (First Run)
- Compares extracted biomarkers against ground truth
- Reports: matched count, missing biomarkers, accuracy %
- Saves results to: `first_run_validation.json`

### Step 5: Enrich Missing Biomarkers
- Identifies biomarkers that failed to extract
- Enriches medical catalog with missing biomarkers
- Uses LLM to generate biomarker definitions
- **Skip with**: `--skip-enrichment`

### Step 6: Re-process Document (Second Run)
- Clears Neo4j again
- Extracts biomarkers with enriched catalog
- Tests if enrichment improved extraction

### Step 7: Validate Results (Second Run)
- Compares second extraction against ground truth
- Reports improvements from enrichment
- Saves results to: `second_run_validation.json`

### Step 8: Generate Comparison Report
- Compares first run vs second run
- Shows extraction improvements
- Generates markdown report: `comparison_report.md`

## Output Files

Default location: `/tmp/extraction_validation/`

### first_run_validation.json
```json
{
  "source_file": "Dutch cortisol 9-01-25.pdf",
  "verification_file": "dutch-cortisol-sep-2025-data.ts",
  "has_verification_data": true,
  "statistics": {
    "total_extracted": 23,
    "total_verified": 25,
    "matched_count": 20,
    "accuracy": 80.0,
    "coverage": 86.9
  },
  "missing_from_extracted": ["Biomarker A", "Biomarker B"],
  "extra_in_extracted": [],
  "matches": [...]
}
```

### second_run_validation.json
Same format as first run, shows results after enrichment.

### comparison_report.md
Markdown report with:
- Statistics comparison (first vs second run)
- Missing biomarkers list
- Improvement metrics
- File paths for results

## Verification File Matching

The validation script matches documents to ground truth using these rules:

### File Name Matching
- **Document**: `Dutch cortisol 9-01-25.pdf` → stem: `Dutch cortisol 9-01-25`
- **Validation file patterns** (searched in order):
  1. `{stem}_verified.json` → `Dutch cortisol 9-01-25_verified.json`
  2. `{stem}_validation.json` → `Dutch cortisol 9-01-25_validation.json`
  3. `{stem}_data.json` → `Dutch cortisol 9-01-25_data.json`
  4. `{stem}.json` → `Dutch cortisol 9-01-25.json`

### Search Locations
Validation files are searched in:
1. `pdf_tests/validation/` (primary)
2. `pdf_tests/verified/`
3. `pdf_tests/webui_test_data/`

### Master Files (Fallback)
If no document-specific file found, checks master files:
- `all_biomarkers_verified.json`
- `webui_expected_values.json`

These contain multiple documents in a `documents` array.

### Name Normalization
The verifier normalizes names for matching:
- Removes extra spaces
- Case-insensitive matching
- Handles abbreviations (e.g., "Sep" vs "September")

**Important**: Validation file name must match the uploaded document filename (ignoring extension and normalization).

## Common Issues

### Issue: "No verification data found"
**Symptoms**:
```json
{
  "verification_file": null,
  "has_verification_data": false,
  "statistics": {"matched_count": 0, "accuracy": 0.0}
}
```

**Cause**: Validation file name doesn't match document filename.

**Solutions**:
1. Rename validation file to match document:
   ```bash
   # Document: Dutch cortisol 9-01-25.pdf
   # Rename: dutch-cortisol-sep-2025-data.ts → Dutch cortisol 9-01-25-data.ts
   mv pdf_tests/validation/webui_test_data/dutch-cortisol-sep-2025-data.ts \
      pdf_tests/validation/webui_test_data/Dutch\ cortisol\ 9-01-25-data.ts
   ```

2. Create symlink:
   ```bash
   ln -s dutch-cortisol-sep-2025-data.ts \
         "Dutch cortisol 9-01-25-data.ts"
   ```

3. Add to master file (`webui_expected_values.json`)

### Issue: "File does not exist" during processing
**Symptoms**: Task fails with "File /tmp/uploads/xxx.PDF does not exist"

**Cause**: Document records exist in database but files were deleted from `/tmp/uploads/`

**Solution**: Re-upload the document:
```bash
cd repos/dem2
just curl_api '{"function": "upload_file", "path": "pdf_tests/medical_records/...pdf"}'
```

### Issue: Processing hangs at "in_progress"
**Symptoms**: Task stuck at 10% progress

**Causes**:
- Backend workers not running
- Database connection issues
- LLM API timeout

**Solution**: Check backend logs and restart services if needed.

## Testing Best Practices

### 1. Use Consistent Test Data
- Keep validation files in `pdf_tests/validation/webui_test_data/`
- Name validation files to match document filenames
- Update validation data when document content changes

### 2. Run Full Workflow for Baseline
```bash
# First time with new document
just validate-extraction
```
This establishes baseline accuracy and identifies missing biomarkers.

### 3. Use Quick Mode for Iteration
```bash
# When iterating on extraction logic
just validate-extraction-quick --skip-snapshot
```
Skips slow Qdrant reload and enrichment steps.

### 4. Clean State Between Tests
The workflow automatically clears Neo4j biomarkers. Manual cleanup if needed:
```bash
cd ../../  # workspace root
python scripts/neo4j-query.py --clear-biomarkers
cd repos/dem2
```

### 5. Monitor Catalog State
```bash
# Check if catalog needs enrichment
cd repos/medical-catalog
just snapshot-restore-all
```

## Integration with Frontend Tests

### Validation Data Source
The `pdf_tests/validation/webui_test_data/` directory contains ground truth data from the frontend test suite (`dem2-webui/tests/test_data/`).

### Syncing Validation Data
```bash
# From machina-meta root
cp repos/dem2-webui/tests/test_data/*.ts \
   repos/dem2/pdf_tests/validation/webui_test_data/
```

**When to sync**:
- After frontend QA creates new test data
- After updating expected values in frontend tests
- When adding new test documents

### Test Data Format
Frontend test data files (TypeScript):
```typescript
export const dutchCortisolSep2025Data = {
  filename: "Dutch cortisol 9-01-25.pdf",
  biomarkers: [
    {
      name: "Testosterone",
      value: "42.63",
      unit: "ng/mg",
      referenceRange: "25 - 115",
      observedAt: "2025-09-11"
    },
    // ... more biomarkers
  ]
};
```

## Related Documentation

- **Backend**: `repos/dem2/CLAUDE.md` - Document processing architecture
- **API Testing**: `repos/dem2/CLAUDE.md` (section: API Testing with curl_api)
- **Medical Catalog**: `repos/medical-catalog/CLAUDE.md` - Catalog service details
- **Frontend Tests**: `repos/dem2-webui/tests/test_data/` - Ground truth source
- **Workflow Script**: `repos/dem2/scripts/test_extraction_workflow.sh` - Implementation
- **Validation Logic**: `repos/dem2/scripts/validate_document_biomarkers.py` - Comparison algorithm
- **Verification Matching**: `repos/dem2/scripts/verification.py` - File matching rules

## Quick Reference

```bash
# List test documents
just list-test-docs

# Upload and process
cd repos/dem2
just curl_api '{"function": "upload_file", "path": "pdf_tests/medical_records/...pdf"}'
just curl_api '{"function": "process_document", "file_id": "uuid"}'

# Validate extraction
just validate-extraction                    # Full workflow
just validate-extraction-quick              # Single run
just validate-extraction --skip-snapshot    # Skip Qdrant reload

# Check results
cat /tmp/extraction_validation/comparison_report.md
jq . /tmp/extraction_validation/first_run_validation.json
jq . /tmp/extraction_validation/second_run_validation.json

# Sync validation data
cp repos/dem2-webui/tests/test_data/*.ts \
   repos/dem2/pdf_tests/validation/webui_test_data/
```
