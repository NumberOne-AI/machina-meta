#!/bin/bash
# Entrypoint for Spire.Doc POC container
# Runs the gemini_docx_poc.py script (which uses uv shebang)
#
# To run with correct file ownership, use:
#   docker run --rm --user "$(id -u):$(id -g)" -v "$(pwd):/workspace" spire-doc-poc ...

set -e

# Check for arguments
if [ $# -eq 0 ]; then
    echo "Spire.Doc POC Container"
    echo ""
    echo "Usage: docker run --rm -v \$(pwd):/workspace spire-doc-poc <docx-file-or-dir> [options]"
    echo ""
    echo "Extraction-Only Modes (no API key required):"
    echo "  --mode=extract-text    Extract text only, save to .txt"
    echo "  --mode=extract-images  Convert to PNG images only"
    echo "  --mode=extract-all     Extract both text and images"
    echo ""
    echo "LLM Modes (require GOOGLE_API_KEY):"
    echo "  --mode=text    Extract text and send to Gemini"
    echo "  --mode=image   Convert to images and send to Gemini vision"
    echo "  --mode=compare Run both LLM modes and compare"
    echo ""
    echo "Examples:"
    echo "  # Extract images only (no API key needed)"
    echo "  docker run --rm -v \$(pwd):/workspace spire-doc-poc docs/ --mode=extract-images -o output/"
    echo ""
    echo "  # LLM extraction (requires API key)"
    echo "  docker run --rm -v \$(pwd):/workspace -e GOOGLE_API_KEY spire-doc-poc test.docx --mode=image"
    exit 0
fi

# Check if mode requires API key
MODE=""
for arg in "$@"; do
    if [[ "$arg" == --mode=* ]]; then
        MODE="${arg#--mode=}"
    elif [[ "$arg" == "-m" ]]; then
        # Next arg will be mode, but we'll just check in the script
        :
    fi
done

# Only require API key for LLM modes
if [[ "$MODE" != extract-* ]] && [[ "$MODE" != "" ]]; then
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "ERROR: GOOGLE_API_KEY environment variable is required for LLM modes"
        echo "Use --mode=extract-images or --mode=extract-all for extraction without LLM"
        exit 1
    fi
fi

# Run the POC script (uses uv shebang for dependency management)
exec /workspace/scripts/gemini_docx_poc.py "$@"
