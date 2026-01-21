# DOCX Document Support Analysis

This document analyzes DOCX (Microsoft Word) document support for the MachinaMed platform, including current state, Gemini API capabilities, and implementation plan.

**Last Updated:** 2026-01-21

## 1. Current DOCX Support in Codebase

### Summary

| Component                        | DOCX Support |                                    Notes |
|:---------------------------------|:------------:|-----------------------------------------:|
| **docproc pipeline** (atlas-dev) |      No      |                       PDF, PNG, JPEG only |
| **file-storage service**         |   Partial    |        Stores files but no processing |
| **shell.nix**                    |  Available   | `pandoc` installed for text conversion |
| **Python services**              |      No      |            No `python-docx` dependency |

### Document Processing Pipeline (atlas-dev)

The current extraction pipeline in `services/docproc/src/machina/docproc/extractor/pipeline.py` explicitly rejects non-PDF formats:

```python
SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg"}

# ...
if mime_type != "application/pdf":
    raise ValueError(f"Unsupported file type: {mime_type}. Supported: PDF, PNG, JPEG.")
```

### File Storage Service

The file-storage service accepts any file type for upload but provides no document processing capabilities. Files are stored with their original `content_type` MIME type.

### Available System Tools

| Tool     | Location  |                    Purpose | Used by Python |
|:---------|:----------|---------------------------:|:--------------:|
| `pandoc` | shell.nix | Universal document converter |       No       |

### Test Data Available

DOCX files exist in the test data directory:

| File                                    | Size (chars) |   Content Type |
|:----------------------------------------|-------------:|---------------:|
| 1. Master context and prompt.docx       |        2,964 | Context/prompts |
| 2. Lifestyle and Medical History.docx   |       15,485 | Medical history |
| 3. Full Genetics Profile.docx           |           21 | Placeholder/link |
| 4. Supplementation Considerations.docx  |        5,465 | Supplement list |
| RPT - Full Genetics Profile.docx        |       13,341 | Genetics report |

## 2. Gemini API DOCX Support

### Official Support Status

| Feature                        | DOCX Support |                                         Notes |
|:-------------------------------|:------------:|----------------------------------------------:|
| **Files API (document vision)** |      No      |              PDF only for layout understanding |
| **Files API (text upload)**    |   Partial    | Extracted as plain text, loses formatting |
| **Web/Mobile App**             |     Yes      |               DOC, DOCX, PDF, RTF supported |
| **File Search**                |   Partial    |                  Should support .doc, .docx |

**Key Limitation:** Gemini's document vision only meaningfully understands PDFs. Other formats are "extracted as pure text, and the model won't be able to interpret what we see in the rendering of those files."

### POC Implementation

Created `scripts/gemini_docx_poc.py` supporting two extraction modes:

| Mode        | Method                                     |                               Use Case |
|:------------|:-------------------------------------------|---------------------------------------:|
| **text**    | Extract text via `python-docx`, send as prompt | Fast, text-heavy documents |
| **image**   | Convert DOCX → PDF → Images, use Gemini vision | Preserves layout, handles charts |
| **compare** | Run both modes, compare results            |                     Mode evaluation |

**Text Mode Pipeline:**
1. Extract text from DOCX using `python-docx`
2. Preserve table structure with `[TABLE]` markers
3. Send extracted text to Gemini for structured extraction
4. Return JSON with biomedical/genetic information

**Image Mode Pipeline:**
1. Convert DOCX to PDF using LibreOffice headless
2. Render PDF pages to images using `pdf2image`
3. Send images to Gemini vision API
4. Return JSON with biomedical/genetic information

### Text Mode Results (gemini-3-pro-preview)

| File                                    | Text Length | Biomarkers | Genetic Variants | Diagnoses | Medications |
|:----------------------------------------|------------:|-----------:|-----------------:|----------:|------------:|
| 1. Master context and prompt.docx       |       2,964 |          0 |                0 |         0 |           0 |
| 2. Lifestyle and Medical History.docx   |      15,485 |          8 |                5 |        24 |           4 |
| 3. Full Genetics Profile.docx           |          21 |          0 |                0 |         0 |           0 |
| 4. Supplementation Considerations.docx  |       5,465 |          0 |                0 |         1 |          33 |
| RPT - Full Genetics Profile.docx        |      13,341 |          3 |               33 |        12 |          18 |

## 3. Text Mode vs Image Mode Comparison

### Holistic Comparative Analysis (All 5 Test Documents)

Ran both extraction modes on all 5 Stuart McClure DOCX test documents using `gemini-3-pro-preview`:

| Document                             | Text Items | Image Items | Winner | Text Time | Image Time | Time Ratio |
|:-------------------------------------|----------:|-----------:|:------:|----------:|-----------:|-----------:|
| 1. Master context and prompt.docx    |         7 |          7 |   Tie  |    17.2s  |     41.7s  |      2.4x  |
| 2. Lifestyle and Medical History.docx|        51 |         57 |  Image |    58.7s  |     73.7s  |      1.3x  |
| 3. Full Genetics Profile.docx        |         1 |        373 |  Image |    30.5s  |    402.3s  |     13.2x  |
| 4. Supplementation Considerations.docx|       34 |         39 |  Image |    48.4s  |     80.7s  |      1.7x  |
| RPT - Full Genetics Profile.docx     |        66 |         64 |  Text  |    62.7s  |     67.9s  |      1.1x  |
| **TOTAL**                            |   **159** |    **540** | **Image** | **217.4s** | **666.3s** | **3.1x** |

**Key Metrics:**
- Image mode extracts **3.4x more data** (540 vs 159 items)
- Image mode takes **3.1x longer** (666s vs 217s total)
- Trade-off: ~1 additional item extracted per 1.3 seconds of additional processing

### Per-Document Extraction Breakdown

#### 1. Master context and prompt.docx (Tie: 7 vs 7)

| Category        | Text Mode | Image Mode |
|:----------------|----------:|-----------:|
| Recommendations |         7 |          7 |
| **Total**       |     **7** |      **7** |

Both modes extracted the same 7 supplement/therapy recommendations.

#### 2. Lifestyle and Medical History.docx (Image wins: 57 vs 51)

| Category         | Text Mode | Image Mode | Difference |
|:-----------------|----------:|-----------:|-----------:|
| Biomarkers       |         8 |         10 |         +2 |
| Genetic Variants |         5 |          5 |          0 |
| Diagnoses        |        26 |         28 |         +2 |
| Medications      |         4 |          4 |          0 |
| Recommendations  |         7 |          9 |         +2 |
| **Total**        |    **51** |     **57** |     **+6** |

Image mode captured more biomarkers, diagnoses, and recommendations.

#### 3. Full Genetics Profile.docx (Image wins dramatically: 373 vs 1)

| Category         | Text Mode | Image Mode | Difference |
|:-----------------|----------:|-----------:|-----------:|
| Genetic Variants |         1 |        373 |       +372 |
| **Total**        |     **1** |    **373** |   **+372** |

**Critical finding**: This document has only 21 characters of extractable text (a link/placeholder) but renders to 17 pages with 373 genetic variants. Text mode fails completely; image mode is mandatory.

#### 4. Supplementation Considerations.docx (Image wins: 39 vs 34)

| Category         | Text Mode | Image Mode | Difference |
|:-----------------|----------:|-----------:|-----------:|
| Diagnoses        |         4 |          4 |          0 |
| Medications      |        28 |         33 |         +5 |
| Recommendations  |         2 |          2 |          0 |
| **Total**        |    **34** |     **39** |     **+5** |

Image mode extracted 5 additional medications from the 36-page supplement list.

#### RPT - Full Genetics Profile.docx (Text wins: 66 vs 64)

| Category         | Text Mode | Image Mode | Difference |
|:-----------------|----------:|-----------:|-----------:|
| Biomarkers       |         3 |          1 |         -2 |
| Genetic Variants |        33 |         33 |          0 |
| Diagnoses        |        12 |          6 |         -6 |
| Medications      |        13 |          3 |        -10 |
| Lab Panels       |         1 |          1 |          0 |
| Risk Scores      |         1 |          1 |          0 |
| Recommendations  |         3 |         19 |        +16 |
| **Total**        |    **66** |     **64** |     **-2** |

Text mode extracted more medications (13 vs 3), but image mode captured more detailed recommendations (19 vs 3).

### Aggregate Category Analysis

| Category         | Text Mode | Image Mode | Difference |     Winner |
|:-----------------|----------:|-----------:|-----------:|-----------:|
| Biomarkers       |        11 |         11 |          0 |        Tie |
| Genetic Variants |        39 |        411 |       +372 | **Image**  |
| Diagnoses        |        42 |         38 |         -4 |       Text |
| Medications      |        45 |         40 |         -5 |       Text |
| Lab Panels       |         1 |          1 |          0 |        Tie |
| Risk Scores      |         1 |          1 |          0 |        Tie |
| Recommendations  |        19 |         37 |        +18 | **Image**  |
| **TOTAL**        |   **159** |    **540** |   **+381** | **Image**  |

### Processing Time Analysis

| Document                              | Pages | Text Time | Image Time | Conversion | LLM Time | Ratio |
|:--------------------------------------|------:|----------:|-----------:|-----------:|---------:|------:|
| 1. Master context and prompt.docx     |     2 |    17.2s  |     41.7s  |      0.9s  |   22.8s  |  2.4x |
| 2. Lifestyle and Medical History.docx |     6 |    58.7s  |     73.7s  |      1.2s  |   72.5s  |  1.3x |
| 3. Full Genetics Profile.docx         |    17 |    30.5s  |    402.3s  |     16.5s  |  385.8s  | 13.2x |
| 4. Supplementation Considerations.docx|    36 |    48.4s  |     80.7s  |      4.7s  |   76.1s  |  1.7x |
| RPT - Full Genetics Profile.docx      |    10 |    62.7s  |     67.9s  |      1.1s  |   66.8s  |  1.1x |
| **TOTAL**                             |**71** |**217.4s** | **666.3s** |  **24.4s** |**624.0s**|**3.1x**|

**Processing Time Observations:**
- **Conversion overhead is minimal**: Only 24.4s total (3.7% of image mode time)
- **LLM processing dominates**: 624s of 666s total image time (93.7%)
- **Page count correlates with time**: 17-page genetics doc took 402s (6.7 minutes)
- **Text mode is 3.1x faster** overall but extracts 3.4x less data
- **Best efficiency**: RPT - Full Genetics (1.1x slower for similar extraction quality)

### Key Findings

**When Image Mode is Essential:**
- **Embedded/linked content**: Documents with minimal extractable text but rich visual content (e.g., 3. Full Genetics Profile.docx with 21 chars → 373 genetic variants)
- **Complex table layouts**: Visual rendering preserves table structure better
- **Charts and diagrams**: Visual context required for interpretation

**When Text Mode Excels:**
- **Medication/supplement extraction**: Better categorization
- **Diagnosis capture**: Slightly better in some cases
- **Processing speed**: 3.1x faster overall
- **Simpler dependencies**: Only requires `python-docx`

**Document Type Patterns:**

| Document Type                        |       Recommended Mode |                                   Reason |
|:-------------------------------------|----------------------:|-----------------------------------------:|
| Embedded content (links, placeholders)|            Image Mode | Text extraction yields nothing           |
| Genetics reports with visual tables  |            Image Mode | 411 variants only visible in rendered view |
| Medical history narratives           |            Image Mode | Captures more diagnoses and recommendations |
| Structured supplement lists          |           Either Mode | Both perform identically                 |
| Text-heavy detailed reports          |             Text Mode | Better medication categorization         |

### Category Interpretation Differences

| Content Type              |  Text Mode Classification |           Image Mode Classification |
|:--------------------------|-------------------------:|-----------------------------------:|
| "CoQ10 supplement"        |              Medication |                    Recommendation |
| "Broccoli Sprout Powder"  |              Medication |                    Recommendation |
| "KetoFlex 12/3 Diet"      |           Recommendation |                    Recommendation |

Text mode treats supplements as medications (structured list), while image mode treats them as recommendations with detailed rationale (includes gene associations like "Calcium-D-Glucarate to support glucuronidation pathway (UGT1A1)").

## 4. Implementation Plan

### Phase 1: Text Extraction Module

**Goal:** Add DOCX text extraction capability to docproc service

| Task                               | Priority |      Dependencies |
|:-----------------------------------|:--------:|------------------:|
| Add `python-docx` dependency       |   High   |              None |
| Create `DocxTextExtractor` class   |   High   |        python-docx |
| Integrate with MIME type detection |   High   | DocxTextExtractor |
| Add unit tests                     |   High   |   Test DOCX files |

**Implementation Location:** `services/docproc/src/machina/docproc/extractor/`

### Phase 2: Pipeline Integration

**Goal:** Support DOCX alongside PDF in extraction pipeline

| Task                                 | Priority | Dependencies |
|:-------------------------------------|:--------:|-------------:|
| Update `guess_mime()` for DOCX       |   High   |      Phase 1 |
| Add DOCX branch in `Pipeline.run()`  |   High   |      Phase 1 |
| Create DOCX-specific extraction prompt | Medium |  POC learnings |
| Handle tables/formatting markers     |  Medium  |      Phase 1 |

**Key Decision:** Processing Strategy Selection

| Strategy                   |               When to Use |                             Pros |                          Cons |
|:---------------------------|-------------------------:|---------------------------------:|------------------------------:|
| **Text-only extraction**   |    Text-heavy documents |                    Fast, simple |         Misses embedded images |
| **Image mode extraction**  | Complex layouts, charts | Preserves context, handles visuals | Slower, external dependency |
| **Interleaved text+image** | Mixed content documents | Best of both, preserves context | Most complex extraction |

### Phase 3: Image Mode Support

**Goal:** Add image-based extraction for complex DOCX layouts

| Task                                    | Priority |    Dependencies |
|:----------------------------------------|:--------:|----------------:|
| Add LibreOffice/Spire.Doc for PDF conversion | High |         Phase 2 |
| Implement PDF to image rendering        |   High   |  pdf2image/Pillow |
| Integrate with Gemini vision API        |   High   | Image rendering |
| Add automatic mode selection heuristics |  Medium  |         Phase 2 |

**DOCX to Image Conversion Options:**

| Library          |               Type |                          Pros |                           Cons |
|:-----------------|-------------------:|------------------------------:|-------------------------------:|
| **LibreOffice**  | System dependency |  High fidelity, free | Large install, headless mode |
| **Spire.Doc**    |       Pure Python |  No system deps, simple API | Commercial, free tier limits |
| **pdf2image**    |       PDF → Image | Well-tested, Poppler backend | Requires intermediate PDF |

### Phase 4: Interleaved Content Extraction

**Goal:** Handle DOCX files with mixed text and images while preserving document order

**Critical Requirement:** Text and images must be interleaved in their original document order to preserve context. A chart appearing after a paragraph about "cholesterol levels" must remain associated with that context.

| Task                                         | Priority |         Dependencies |
|:---------------------------------------------|:--------:|---------------------:|
| Implement ordered content extraction         |   High   |              Phase 3 |
| Build interleaved content representation     |   High   |   Ordered extraction |
| Integrate images with Gemini multimodal API  |  Medium  | Content representation |
| Add content ratio analysis for strategy selection | Medium |              Phase 3 |

**Interleaved Extraction Approach:**

DOCX files store content as a sequence of block-level elements (paragraphs, tables, images). The extraction must walk this sequence in order:

```python
from docx import Document
from docx.document import Document as DocType
from docx.oxml.ns import qn

def extract_interleaved_content(doc: DocType) -> list[dict]:
    """Extract text and images in document order."""
    content = []

    for element in doc.element.body:
        if element.tag == qn('w:p'):  # Paragraph
            # Check for inline images within paragraph
            for drawing in element.findall('.//' + qn('w:drawing')):
                # Extract image from relationship
                content.append({"type": "image", "data": extract_image(drawing)})

            text = element.text_content()
            if text.strip():
                content.append({"type": "text", "content": text})

        elif element.tag == qn('w:tbl'):  # Table
            content.append({"type": "table", "content": extract_table(element)})

    return content
```

**Multimodal Prompt Construction:**

For Gemini, interleaved content becomes a multimodal prompt:

```python
parts = []
for item in interleaved_content:
    if item["type"] == "text":
        parts.append(types.Part.from_text(text=item["content"]))
    elif item["type"] == "image":
        parts.append(types.Part.from_bytes(data=item["data"], mime_type="image/png"))
    elif item["type"] == "table":
        parts.append(types.Part.from_text(text=f"[TABLE]\n{item['content']}\n[/TABLE]"))

parts.append(types.Part.from_text(text=EXTRACTION_PROMPT))
response = client.models.generate_content(model=model, contents=parts)
```

**Content Analysis for Strategy Selection:**

| Text Length  | Image Count |       Recommended Strategy |
|:-------------|:------------|---------------------------:|
| > 1000 chars |           0 |        Text-only extraction |
| > 500 chars  |         > 0 |       Interleaved text+image |
| < 500 chars  |         > 0 | Image mode (likely image-heavy) |
| < 100 chars  |           0 | Skip or flag as empty/placeholder |

### Phase 5: Format-Specific Processors

**Goal:** Optimize extraction for common DOCX document types

| Task                                          | Priority | Dependencies |
|:----------------------------------------------|:--------:|-------------:|
| Identify common DOCX document formats         |  Medium  |      Phase 4 |
| Create specialized extraction prompts         |  Medium  | Format analysis |
| Add format detection based on content patterns |  Medium  |      Phase 4 |

### Phase 6: Production Hardening

**Goal:** Production-ready DOCX support

| Task                               | Priority | Dependencies |
|:-----------------------------------|:--------:|-------------:|
| Add comprehensive error handling   |   High   |      Phase 4 |
| Implement file size limits         |   High   |      Phase 4 |
| Add metrics/logging                |  Medium  |      Phase 4 |
| Update API documentation           |  Medium  |   All phases |
| Load testing with large DOCX files |  Medium  |      Phase 5 |

### Dependencies to Add

```toml
# pyproject.toml (services/docproc)
dependencies = [
    # ... existing ...
    "python-docx>=1.1.0",      # Text extraction
    "pdf2image>=1.16.0",       # PDF to image (for image mode)
    "Pillow>=10.0.0",          # Image handling
    # Optional: "spire-doc>=12.1.0",  # Alternative DOCX to image (commercial)
]
```

**System Dependencies (for image mode):**
- LibreOffice (DOCX → PDF): `nix-shell -p libreoffice` or `apt install libreoffice`
- Poppler (PDF → Image): `nix-shell -p poppler_utils` or `apt install poppler-utils`

### API Changes

No API changes required. Existing endpoints will accept DOCX files:

- `POST /api/v1/files/upload` - Already accepts any file type
- `POST /api/v1/medical-data-engine/process` - Will process DOCX after implementation

### Configuration

```toml
# config.toml (services/docproc)
[extractor]
supported_mime_types = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  # .doc (legacy)
]

[extractor.docx]
default_mode = "text"  # "text", "image", or "auto"
image_dpi = 200
auto_mode_image_threshold = 3  # Switch to image mode if > N images detected
```

## References

- [Gemini Document Processing](https://ai.google.dev/gemini-api/docs/document-processing)
- [Gemini Files API](https://ai.google.dev/api/files)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [Spire.Doc for Python](https://github.com/eiceblue/Spire.Doc-for-Python) - Commercial DOCX library
- [Spire.Doc Image Conversion Tutorial](https://www.e-iceblue.com/Tutorials/Python/Spire.Doc-for-Python/Program-Guide/Conversion/Python-Convert-Word-to-Images.html)
- POC Script: `scripts/gemini_docx_poc.py`
