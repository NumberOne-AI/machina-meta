#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["google-genai", "python-docx", "pdf2image", "pillow", "spire-doc-free", "plum-dispatch==1.7.4"]
# ///
"""
Gemini DOCX Processing Proof of Concept

Demonstrates extracting structured biomedical/genetic information from DOCX files
using Google Gemini API with multiple extraction modes.

MODES:
    text    - Extract text from DOCX and send as plain text (fast, no formatting)
    image   - Convert DOCX to images and use Gemini vision (preserves layout)
    compare - Run both modes and compare results

Usage:
    ./scripts/gemini_docx_poc.py <path-to-docx-file>
    ./scripts/gemini_docx_poc.py <path-to-docx-file> --mode=image
    ./scripts/gemini_docx_poc.py <path-to-docx-file> --mode=compare
    ./scripts/gemini_docx_poc.py <path-to-docx-file> --model=gemini-2.5-pro-preview-05-06

Image mode conversion (tries in order):
    1. Spire.Doc (pure Python, no system deps) - included in script dependencies
    2. LibreOffice + Poppler (system deps required):
       - macOS: brew install libreoffice poppler
       - Linux: apt install libreoffice poppler-utils

References:
    - https://ai.google.dev/gemini-api/docs/document-processing
    - https://ai.google.dev/api/files
    - https://github.com/eiceblue/Spire.Doc-for-Python
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

from docx import Document
from google import genai
from google.genai import types
from PIL import Image


def load_env_variable(var_name: str, env_file: str = ".env") -> str | None:
    """Load environment variable from env file or environment.

    Priority:
    1. Environment variable (if set)
    2. .env file in current directory
    3. .env file in workspace root
    """
    # Check environment variable first (highest priority)
    value = os.getenv(var_name)
    if value:
        return value

    # Try .env in current working directory and workspace root
    env_paths = [
        Path.cwd() / env_file,
        Path(__file__).parent.parent / env_file,  # Workspace root
    ]

    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith("#"):
                            continue
                        # Match: VAR_NAME=value
                        match = re.match(rf"^{re.escape(var_name)}=(.*)$", line)
                        if match:
                            return match.group(1).strip().strip('"').strip("'")
            except OSError:
                continue

    return None


# Structured extraction prompt for biomedical/genetic data
EXTRACTION_PROMPT = """
Analyze the following medical/genetic document and extract ALL structured information into JSON format.

Extract the following categories if present:

1. **patient_info**: name, date_of_birth, gender, patient_id, collection_date, report_date
2. **biomarkers**: array of objects with fields: name, value, unit, reference_range, status (normal/high/low/critical), category
3. **genetic_variants**: array of objects with fields: gene, variant, zygosity, classification (pathogenic/benign/VUS), associated_conditions
4. **diagnoses**: array of objects with fields: condition, icd_code, status, onset_date
5. **medications**: array of objects with fields: name, dosage, frequency, route, start_date
6. **lab_panels**: array of objects with fields: panel_name, tests (array of name, value, unit, reference_range, flag)
7. **risk_scores**: array of objects with fields: name, score, interpretation, percentile
8. **recommendations**: array of objects with fields: type, description, priority, follow_up_date

Rules:
- Return ONLY valid JSON, no markdown code blocks
- Use null for missing values, not empty strings
- Preserve exact numeric values and units as written
- Include ALL data found, even if categories overlap
- For ranges, use format "min-max" or "< value" or "> value"
"""

TEXT_MODE_PROMPT = EXTRACTION_PROMPT + """
DOCUMENT TEXT:
---
{document_text}
---

Return the structured JSON:
"""

IMAGE_MODE_PROMPT = EXTRACTION_PROMPT + """
The document pages are provided as images. Analyze ALL pages carefully to extract the information.

Return the structured JSON:
"""


def extract_text_from_docx(docx_path: str) -> str:
    """Extract all text content from a DOCX file."""
    doc = Document(docx_path)

    text_parts = []

    # Extract paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)

    # Extract tables
    for table in doc.tables:
        table_text = []
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells]
            table_text.append(" | ".join(row_text))
        if table_text:
            text_parts.append("\n[TABLE]\n" + "\n".join(table_text) + "\n[/TABLE]")

    return "\n".join(text_parts)


def convert_docx_to_images_spire(docx_path: str) -> list[Image.Image] | None:
    """Convert DOCX to images using Spire.Doc (pure Python, no system dependencies).

    Args:
        docx_path: Path to DOCX file

    Returns:
        List of PIL Image objects, one per page, or None if Spire.Doc unavailable
    """
    try:
        from spire.doc import Document as SpireDocument, ImageType
        from io import BytesIO
    except ImportError:
        return None  # Spire.Doc not available, fall back to other methods

    try:
        doc = SpireDocument()
        doc.LoadFromFile(docx_path)

        # Convert all pages to images
        image_streams = doc.SaveImageToStreams(ImageType.Bitmap)

        images = []
        for stream in image_streams:
            # Convert Spire stream to PIL Image
            image_data = stream.ToArray()
            pil_image = Image.open(BytesIO(bytes(image_data)))
            images.append(pil_image.copy())  # Copy to detach from stream

        doc.Close()
        return images
    except Exception as e:
        print(f"[WARN] Spire.Doc conversion failed: {e}")
        return None


def convert_docx_to_pdf_libreoffice(docx_path: str, output_dir: str) -> str | None:
    """Convert DOCX to PDF using LibreOffice headless mode.

    Args:
        docx_path: Path to DOCX file
        output_dir: Directory for PDF output

    Returns:
        Path to generated PDF file, or None if LibreOffice unavailable
    """
    # Check if LibreOffice is available
    libreoffice_cmd = None
    for cmd in ["libreoffice", "soffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice"]:
        if shutil.which(cmd):
            libreoffice_cmd = cmd
            break

    if not libreoffice_cmd:
        return None  # LibreOffice not available

    # Convert to PDF
    result = subprocess.run(
        [
            libreoffice_cmd,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            docx_path
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"[WARN] LibreOffice conversion failed: {result.stderr}")
        return None

    # Find the generated PDF
    docx_name = Path(docx_path).stem
    pdf_path = Path(output_dir) / f"{docx_name}.pdf"

    if not pdf_path.exists():
        return None

    return str(pdf_path)


def convert_pdf_to_images(pdf_path: str, dpi: int = 200) -> list[Image.Image]:
    """Convert PDF pages to PIL Images.

    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for rendering (higher = better quality but larger)

    Returns:
        List of PIL Image objects, one per page
    """
    from pdf2image import convert_from_path

    images = convert_from_path(pdf_path, dpi=dpi)
    return images


def convert_docx_to_images(docx_path: str, dpi: int = 200) -> tuple[list[Image.Image], str]:
    """Convert DOCX to images using best available method.

    Tries methods in order:
    1. Spire.Doc (pure Python, no system deps)
    2. LibreOffice + pdf2image (system deps required)

    Args:
        docx_path: Path to DOCX file
        dpi: Resolution for rendering (used by LibreOffice method)

    Returns:
        Tuple of (list of PIL Images, method name used)

    Raises:
        RuntimeError: If no conversion method is available
    """
    # Method 1: Try Spire.Doc (pure Python)
    print("[IMAGE MODE] Trying Spire.Doc conversion...")
    images = convert_docx_to_images_spire(docx_path)
    if images:
        return images, "spire-doc"

    # Method 2: Try LibreOffice + pdf2image
    print("[IMAGE MODE] Spire.Doc unavailable, trying LibreOffice...")
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = convert_docx_to_pdf_libreoffice(docx_path, temp_dir)
        if pdf_path:
            try:
                images = convert_pdf_to_images(pdf_path, dpi=dpi)
                return images, "libreoffice"
            except Exception as e:
                print(f"[WARN] pdf2image conversion failed: {e}")

    # No methods available
    raise RuntimeError(
        "No DOCX to image conversion method available.\n"
        "Install one of:\n"
        "  - Spire.Doc: pip install spire-doc-free (pure Python, recommended)\n"
        "  - LibreOffice + Poppler:\n"
        "    - macOS: brew install libreoffice poppler\n"
        "    - Linux: apt install libreoffice poppler-utils"
    )


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string."""
    buffer = BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def extract_with_gemini_text(document_text: str, api_key: str, model: str = "gemini-3-pro-preview") -> dict:
    """
    Send document text to Gemini for structured extraction (text mode).

    Args:
        document_text: Extracted text from DOCX
        api_key: Google API key
        model: Gemini model to use

    Returns:
        Extracted structured data as dict
    """
    client = genai.Client(api_key=api_key)

    prompt = TEXT_MODE_PROMPT.format(document_text=document_text)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,  # Low temperature for consistent extraction
            response_mime_type="application/json",  # Request JSON response
        )
    )

    return _parse_json_response(response.text)


def extract_with_gemini_vision(images: list[Image.Image], api_key: str, model: str = "gemini-3-pro-preview") -> dict:
    """
    Send document images to Gemini for structured extraction (vision mode).

    Args:
        images: List of PIL Images (document pages)
        api_key: Google API key
        model: Gemini model to use

    Returns:
        Extracted structured data as dict
    """
    client = genai.Client(api_key=api_key)

    # Build multimodal content: images + prompt
    parts = []

    # Add each page as an image part
    for i, image in enumerate(images):
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        parts.append(types.Part.from_bytes(
            data=image_bytes.read(),
            mime_type="image/png"
        ))

    # Add the extraction prompt (note: text is a keyword-only argument)
    parts.append(types.Part.from_text(text=IMAGE_MODE_PROMPT))

    response = client.models.generate_content(
        model=model,
        contents=parts,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        )
    )

    return _parse_json_response(response.text)


def _parse_json_response(text: str) -> dict:
    """Parse JSON from Gemini response, handling markdown wrapping."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to extract JSON from response if wrapped in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Return raw response for debugging
            return {"_raw_response": text, "_parse_error": str(e)}


def process_docx_text_mode(docx_path: str, api_key: str, model: str = "gemini-3-pro-preview") -> dict:
    """
    Process DOCX file using text extraction mode.

    Args:
        docx_path: Path to DOCX file
        api_key: Google API key
        model: Gemini model to use

    Returns:
        Dict with extraction results and metadata
    """
    path = Path(docx_path)

    # Extract text from DOCX
    print(f"[TEXT MODE] Extracting text from: {path.name}")
    document_text = extract_text_from_docx(str(path))

    if not document_text.strip():
        raise ValueError("No text content found in document")

    print(f"[TEXT MODE] Extracted {len(document_text)} characters")
    print(f"[TEXT MODE] Sending to Gemini ({model})...")

    # Extract structured data using Gemini
    extracted_data = extract_with_gemini_text(document_text, api_key, model)

    return {
        "mode": "text",
        "source_file": path.name,
        "text_length": len(document_text),
        "model_used": model,
        "extracted_data": extracted_data
    }


def process_docx_image_mode(docx_path: str, api_key: str, model: str = "gemini-3-pro-preview", dpi: int = 200) -> dict:
    """
    Process DOCX file using image/vision mode.

    Converts DOCX → Images → Gemini Vision
    Uses Spire.Doc (pure Python) or LibreOffice + pdf2image as fallback.

    Args:
        docx_path: Path to DOCX file
        api_key: Google API key
        model: Gemini model to use
        dpi: Image resolution (default 200, used by LibreOffice method)

    Returns:
        Dict with extraction results and metadata
    """
    path = Path(docx_path)

    print(f"[IMAGE MODE] Converting: {path.name}")

    # Convert DOCX to images using best available method
    images, conversion_method = convert_docx_to_images(str(path), dpi=dpi)
    print(f"[IMAGE MODE] Converted using: {conversion_method}")
    print(f"[IMAGE MODE] Generated {len(images)} page image(s)")

    # Calculate total image size
    total_pixels = sum(img.width * img.height for img in images)

    print(f"[IMAGE MODE] Sending to Gemini vision ({model})...")

    # Extract using vision
    extracted_data = extract_with_gemini_vision(images, api_key, model)

    return {
        "mode": "image",
        "source_file": path.name,
        "page_count": len(images),
        "total_pixels": total_pixels,
        "dpi": dpi,
        "conversion_method": conversion_method,
        "model_used": model,
        "extracted_data": extracted_data
    }


def compare_results(text_result: dict, image_result: dict) -> dict:
    """
    Compare extraction results between text and image modes.

    Args:
        text_result: Result from text mode
        image_result: Result from image mode

    Returns:
        Comparison analysis
    """
    text_data = text_result.get("extracted_data", {})
    image_data = image_result.get("extracted_data", {})

    comparison = {
        "source_file": text_result.get("source_file"),
        "model_used": text_result.get("model_used"),
        "text_mode": {
            "text_length": text_result.get("text_length"),
        },
        "image_mode": {
            "page_count": image_result.get("page_count"),
            "total_pixels": image_result.get("total_pixels"),
            "dpi": image_result.get("dpi"),
            "conversion_method": image_result.get("conversion_method"),
        },
        "extraction_counts": {},
        "differences": []
    }

    # Compare counts for each category
    categories = ["biomarkers", "genetic_variants", "diagnoses", "medications", "lab_panels", "risk_scores", "recommendations"]

    for cat in categories:
        text_items = text_data.get(cat, [])
        image_items = image_data.get(cat, [])

        text_count = len(text_items) if isinstance(text_items, list) else 0
        image_count = len(image_items) if isinstance(image_items, list) else 0

        comparison["extraction_counts"][cat] = {
            "text_mode": text_count,
            "image_mode": image_count,
            "difference": image_count - text_count
        }

        if text_count != image_count:
            comparison["differences"].append(f"{cat}: text={text_count}, image={image_count}")

    # Summary
    total_text = sum(comparison["extraction_counts"][c]["text_mode"] for c in categories)
    total_image = sum(comparison["extraction_counts"][c]["image_mode"] for c in categories)

    comparison["summary"] = {
        "total_items_text": total_text,
        "total_items_image": total_image,
        "difference": total_image - total_text,
        "winner": "image" if total_image > total_text else ("text" if total_text > total_image else "tie")
    }

    return comparison


def process_docx_file(docx_path: str, api_key: str, model: str = "gemini-3-pro-preview", mode: str = "text") -> dict:
    """
    Main function to process a DOCX file and extract structured data.

    Args:
        docx_path: Path to DOCX file
        api_key: Google API key
        model: Gemini model to use
        mode: Extraction mode ("text", "image", or "compare")

    Returns:
        Dict with extraction results and metadata
    """
    path = Path(docx_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {docx_path}")

    if path.suffix.lower() not in [".docx", ".doc"]:
        raise ValueError(f"Expected DOCX file, got: {path.suffix}")

    if mode == "text":
        return process_docx_text_mode(str(path), api_key, model)
    elif mode == "image":
        return process_docx_image_mode(str(path), api_key, model)
    elif mode == "compare":
        print("=" * 60)
        print("RUNNING TEXT MODE")
        print("=" * 60)
        text_result = process_docx_text_mode(str(path), api_key, model)

        print("\n" + "=" * 60)
        print("RUNNING IMAGE MODE")
        print("=" * 60)
        image_result = process_docx_image_mode(str(path), api_key, model)

        print("\n" + "=" * 60)
        print("COMPARING RESULTS")
        print("=" * 60)
        comparison = compare_results(text_result, image_result)

        return {
            "text_result": text_result,
            "image_result": image_result,
            "comparison": comparison
        }
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'text', 'image', or 'compare'")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract biomedical/genetic data from DOCX files using Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  text    - Extract text from DOCX and send as plain text (fast, no formatting)
  image   - Convert DOCX to images and use Gemini vision (preserves layout)
  compare - Run both modes and compare results

Image mode conversion (tries in order):
  1. Spire.Doc (pure Python, no system deps) - included in script dependencies
  2. LibreOffice + Poppler (system deps, fallback):
     - macOS: brew install libreoffice poppler
     - Linux: apt install libreoffice poppler-utils

Examples:
  ./scripts/gemini_docx_poc.py document.docx
  ./scripts/gemini_docx_poc.py document.docx --mode=image
  ./scripts/gemini_docx_poc.py document.docx --mode=compare
  ./scripts/gemini_docx_poc.py document.docx --model=gemini-2.5-pro-preview-05-06
        """
    )

    parser.add_argument("docx_path", help="Path to DOCX file")
    parser.add_argument("--mode", "-m", choices=["text", "image", "compare"], default="text",
                        help="Extraction mode (default: text)")
    parser.add_argument("--model", default="gemini-3-pro-preview",
                        help="Gemini model to use (default: gemini-3-pro-preview)")
    parser.add_argument("--dpi", type=int, default=200,
                        help="Image resolution for image mode (default: 200)")

    args = parser.parse_args()

    # Get API key from environment or .env file
    api_key = load_env_variable("GOOGLE_API_KEY") or load_env_variable("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY or GEMINI_API_KEY not found in environment or .env")
        sys.exit(1)

    try:
        result = process_docx_file(args.docx_path, api_key, args.model, args.mode)

        print("\n" + "=" * 60)
        print("EXTRACTION RESULT:")
        print("=" * 60)
        print(json.dumps(result, indent=2))

        # Save to file with mode suffix
        docx_path = Path(args.docx_path)
        if args.mode == "compare":
            output_path = docx_path.with_suffix(".compare.json")
        else:
            output_path = docx_path.with_suffix(f".{args.mode}.json")

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved to: {output_path}")

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
