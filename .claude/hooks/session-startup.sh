#!/usr/bin/env bash

# Session startup hook for machina-meta workspace
# Sets working directory to project root for all bash commands

if [ -n "$CLAUDE_ENV_FILE" ]; then
  # Every bash command will start from the project root
  # shellcheck disable=SC2016  # Variable expansion intended in sourced file
  echo 'cd "$CLAUDE_PROJECT_DIR"' >> "$CLAUDE_ENV_FILE"
  echo "✓ Session working directory: \$CLAUDE_PROJECT_DIR"
fi

exit 0
