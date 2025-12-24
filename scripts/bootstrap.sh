#!/usr/bin/env bash
set -euo pipefail

echo "=== Machina Meta Bootstrap ==="
echo ""

# Initialize submodules
echo "Initializing submodules..."
git submodule update --init --recursive

# Check for required tools
echo ""
echo "Checking required tools..."
command -v uv >/dev/null 2>&1 || echo "⚠️  uv not found (needed for Python projects)"
command -v pnpm >/dev/null 2>&1 || echo "⚠️  pnpm not found (needed for dem2-webui)"
command -v docker >/dev/null 2>&1 || echo "⚠️  docker not found (needed for databases)"
command -v just >/dev/null 2>&1 || echo "⚠️  just not found (task runner)"

echo ""
echo "✓ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. just dev-setup    - Install dependencies"
echo "  2. just dev-up       - Start development environment"
