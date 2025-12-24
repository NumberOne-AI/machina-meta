#!/usr/bin/env bash
set -euo pipefail

for dir in repos/*/; do
    if [ -d "$dir/.git" ]; then
        echo ""
        echo "=== $(basename "$dir") ==="
        git -C "$dir" status -sb
    fi
done
