#!/usr/bin/env bash

# Session startup hook for machina-meta workspace
# Sets working directory to project root for all bash commands
# Exports $WS variable for convenient reference to workspace root

export WS="$PWD"

if [ -n "$CLAUDE_ENV_FILE" ]; then
  # Export WS variable pointing to workspace root
  declare -p WS >> "$CLAUDE_ENV_FILE"

  # Every bash command will start from the project root
  echo "cd \"$WS\"" >> "$CLAUDE_ENV_FILE"

  echo "✓ Session working directory: $WS"
  echo "✓ \$WS variable set to workspace root"
else
  # Fallback: if CLAUDE_ENV_FILE isn't available, just print the info
  echo "✓ Workspace root: $WS (CLAUDE_ENV_FILE not available)"
fi

exit 0
