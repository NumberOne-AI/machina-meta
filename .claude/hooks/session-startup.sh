#!/usr/bin/env bash

# Session startup hook for machina-meta workspace
# Sets working directory to project root for all bash commands
# Exports $WS variable for convenient reference to workspace root

# Critical dependency check
if [ -z "$CLAUDE_ENV_FILE" ]; then
    echo "❌ FATAL: CLAUDE_ENV_FILE is not set." >&2
    echo "   This script must run within a Claude Code session environment." >&2
    exit 1
fi

export WS="$PWD"

# Export WS variable pointing to workspace root
declare -p WS >> "$CLAUDE_ENV_FILE"

# Every bash command will start from the session root
echo 'cd "$WS"' >> "$CLAUDE_ENV_FILE"

echo "✓ Session working directory: $WS"
echo "✓ \$WS variable set to workspace root"

exit 0
