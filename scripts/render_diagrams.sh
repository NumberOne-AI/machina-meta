#!/usr/bin/env bash
# Render all Graphviz .dot files in docs/ to SVG format
# Usage: ./scripts/render_diagrams.sh

set -euo pipefail

DOCS_DIR="$(cd "$(dirname "$0")/../docs" && pwd)"

echo "Rendering Graphviz diagrams in $DOCS_DIR"
echo "==========================================="

cd "$DOCS_DIR"

# Count files
DOT_COUNT=$(find . -maxdepth 1 -name "DATAFLOW_*.dot" | wc -l)
echo "Found $DOT_COUNT .dot files"
echo ""

# Render each .dot file to SVG
for dotfile in DATAFLOW_*.dot; do
    if [ -f "$dotfile" ]; then
        svgfile="${dotfile%.dot}.svg"
        echo "Rendering: $dotfile → $svgfile"

        if dot -Tsvg "$dotfile" -o "$svgfile" 2>&1 | grep -v "Warning"; then
            size=$(du -h "$svgfile" | cut -f1)
            echo "  ✓ Generated $svgfile ($size)"
        else
            echo "  ✗ Error rendering $dotfile"
            exit 1
        fi
    fi
done

echo ""
echo "==========================================="
echo "✓ Successfully rendered $DOT_COUNT diagrams"

# Show summary
echo ""
echo "SVG files:"
ls -lh DATAFLOW_*.svg | awk '{print "  " $9 " (" $5 ")"}'
