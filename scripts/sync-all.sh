#!/usr/bin/env bash
set -euo pipefail

echo "=== Syncing all submodules to latest ==="
git submodule update --remote --merge

echo ""
echo "✓ All repos synced"
