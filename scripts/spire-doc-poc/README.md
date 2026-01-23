# Spire.Doc POC Container

Docker container for testing DOCX → Image conversion using Spire.Doc (pure Python, no LibreOffice system dependency).

## Build

```bash
docker build -t spire-doc-poc scripts/spire-doc-poc/
```

## Run

```bash
# Text extraction mode (default)
docker run --rm -v $(pwd):/workspace -e GOOGLE_API_KEY spire-doc-poc path/to/file.docx

# Image extraction mode (uses Spire.Doc)
docker run --rm -v $(pwd):/workspace -e GOOGLE_API_KEY spire-doc-poc path/to/file.docx --mode=image

# Compare both modes
docker run --rm -v $(pwd):/workspace -e GOOGLE_API_KEY spire-doc-poc path/to/file.docx --mode=compare
```

## Why Docker?

Spire.Doc requires:
- ICU libraries (libicu72) for .NET globalization
- System fonts for document rendering
- Proper locale configuration

The container provides all these dependencies pre-configured.

## Container Contents

- Python 3.13 + uv
- Spire.Doc (spire-doc-free)
- ICU libraries
- Liberation + DejaVu fonts
- LibreOffice + Poppler (fallback)
