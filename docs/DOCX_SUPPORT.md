# DOCX Document Support Analysis

Analysis of DOCX support for MachinaMed, comparing text vs image extraction modes.

**Last Updated:** 2026-01-21

## Current State

| Component        | DOCX Support | Notes                          |
|:-----------------|:------------:|:-------------------------------|
| docproc pipeline |      No      | PDF, PNG, JPEG only            |
| file-storage     |   Partial    | Stores files, no processing    |
| shell.nix        |  Available   | `pandoc` installed             |

**Gemini Limitation:** Document vision only works with PDFs. DOCX files are extracted as plain text, losing formatting and embedded content.

## POC Implementation

`scripts/gemini_docx_poc.py` - Three extraction modes:

| Mode      | Method                                          | Use Case                    |
|:----------|:------------------------------------------------|:----------------------------|
| `text`    | `python-docx` → Gemini text prompt              | Fast, text-heavy documents  |
| `image`   | DOCX → PDF → Images → Gemini vision             | Preserves layout, charts    |
| `compare` | Run both modes, compare results                 | Mode evaluation             |

## Extraction Categories

The POC extracts structured biomedical data into these categories:

| Category          | Description                                          | Example                              |
|:------------------|:-----------------------------------------------------|:-------------------------------------|
| Biomarkers        | Lab values with reference ranges                     | Cholesterol: 180 mg/dL (normal)      |
| Genetic Variants  | SNPs, mutations with clinical significance           | APOE ε4/ε4 (rs429358) - pathogenic   |
| Diagnoses         | Medical conditions with ICD codes                    | Obstructive Sleep Apnea (G47.33)     |
| Medications       | Current drugs and supplements                        | CoQ10 200mg daily                    |
| Recommendations   | Clinical advice with gene associations               | KetoFlex diet (APOE e4)              |

## Comparative Analysis (5 Test Documents)

| Document                              | Text | Image | Winner | Text Time | Image Time | Ratio |
|:--------------------------------------|-----:|------:|:------:|----------:|-----------:|------:|
| 1. Master context and prompt.docx     |    7 |     7 |   Tie  |    17.2s  |     41.7s  |  2.4x |
| 2. Lifestyle and Medical History.docx |   51 |    57 |  Image |    58.7s  |     73.7s  |  1.3x |
| 3. Full Genetics Profile.docx         |    1 |   373 |  Image |    30.5s  |    402.3s  | 13.2x |
| 4. Supplementation Considerations.docx|   34 |    39 |  Image |    48.4s  |     80.7s  |  1.7x |
| RPT - Full Genetics Profile.docx      |   66 |    64 |  Text  |    62.7s  |     67.9s  |  1.1x |
| **TOTAL**                             |**159**|**540**|**Image**|**217s** | **666s**  |**3.1x**|

### Extraction by Category (Aggregate)

| Category          | Text Mode | Image Mode | Winner |
|:------------------|----------:|-----------:|:-------|
| Biomarkers        |        11 |         11 | Tie    |
| Genetic Variants  |        39 |        411 | Image  |
| Diagnoses         |        42 |         38 | Text   |
| Medications       |        45 |         40 | Text   |
| Recommendations   |        19 |         37 | Image  |

**Key Metrics:**
- Image mode extracts **3.4x more data** (540 vs 159 items)
- Image mode takes **3.1x longer** (666s vs 217s)
- Image mode dominates **genetic variant extraction** (411 vs 39)
- Text mode better for **medications/diagnoses** categorization

## When to Use Each Mode

| Document Type                     | Mode  | Reason                                    |
|:----------------------------------|:------|:------------------------------------------|
| Embedded content (links, images)  | Image | Text extraction yields nothing            |
| Genetics reports with tables      | Image | 373 variants only visible when rendered   |
| Medical history narratives        | Image | Captures more diagnoses/recommendations   |
| Structured text lists             | Either| Both perform similarly                    |
| Speed-critical processing         | Text  | 3.1x faster                               |

**Critical:** Document "3. Full Genetics Profile" has only 21 chars of text but 17 pages of rendered content with 373 genetic variants. Image mode is mandatory for such documents.

## Implementation Plan

### Phase 1: Text Extraction
- Add `python-docx` dependency to docproc
- Create `DocxTextExtractor` class
- Update MIME type detection

### Phase 2: Pipeline Integration
- Add DOCX branch in `Pipeline.run()`
- Create DOCX-specific extraction prompt

### Phase 3: Image Mode
- Add LibreOffice or Spire.Doc for conversion
- Integrate with Gemini vision API
- Add automatic mode selection based on text/image ratio

### Phase 4: Production
- Error handling, file size limits, metrics/logging

### Dependencies

```toml
# pyproject.toml (services/docproc)
dependencies = [
    "python-docx>=1.1.0",      # Text extraction
    "pdf2image>=1.16.0",       # PDF to image (image mode)
    "Pillow>=10.0.0",          # Image handling
]
```

**System (image mode):** LibreOffice + Poppler (`nix-shell -p libreoffice poppler_utils`)

## References

- [Gemini Document Processing](https://ai.google.dev/gemini-api/docs/document-processing)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [Spire.Doc for Python](https://github.com/eiceblue/Spire.Doc-for-Python)
- POC Script: `scripts/gemini_docx_poc.py`
