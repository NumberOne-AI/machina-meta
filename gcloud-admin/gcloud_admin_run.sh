#!/usr/bin/env bash
# Wrapper script for running commands in gcloud-admin container
# Usage: ./gcloud_admin_run.sh <command> [args...]
#
# Examples:
#   ./gcloud_admin_run.sh gh pr view 91 --repo NumberOne-AI/dem2-infra
#   ./gcloud_admin_run.sh kubectl get pods -n argocd
#   ./gcloud_admin_run.sh argocd app list

set -euo pipefail

# Change to the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the command in the container
exec docker compose run --rm gcloud-admin "$@"
