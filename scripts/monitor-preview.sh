#!/usr/bin/env bash
# Monitor ArgoCD preview environment deployment
#
# Usage:
#   monitor-preview.sh <preview-id> [options]
#
# Options:
#   --timeout <secs>  Max time to wait (default: 600)
#   --pr <number>     PR number (auto-detected if not provided)
#   --poll-only       Use polling instead of argocd app wait
#
# Examples:
#   monitor-preview.sh docproc-extraction-pipeline
#   monitor-preview.sh docproc-extraction-pipeline --timeout 300
#   monitor-preview.sh docproc-extraction-pipeline --pr 91

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source bashutils if available
if [[ -f "$WORKSPACE_ROOT/repos/dem2/scripts/bashutils.sh" ]]; then
    source "$WORKSPACE_ROOT/repos/dem2/scripts/bashutils.sh"
fi

# Fallback implementations if bashutils.sh not sourced
if ! declare -f err &>/dev/null; then
    err() { echo "ERROR: $*" >&2; }
    fatal() { echo "FATAL: $*" >&2; exit 1; }
    info() { echo "INFO: $*" >&2; }
fi

# Default values
TIMEOUT=600
POLL_INTERVAL=5
PR_NUMBER=""
POLL_ONLY=false
ARGOCD_SERVER="argo.n1-machina.dev"

# Parse arguments
if [[ $# -eq 0 ]]; then
    fatal "Preview ID is required" "Usage: monitor-preview.sh <preview-id> [options]"
fi

PREVIEW_ID="$1"
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --pr)
            PR_NUMBER="$2"
            shift 2
            ;;
        --poll-only)
            POLL_ONLY=true
            shift
            ;;
        *)
            fatal "Unknown option: $1"
            ;;
    esac
done

echo ""
echo "========================================"
echo "ArgoCD Preview Environment Monitor"
echo "========================================"
echo "Preview ID: ${PREVIEW_ID}"
echo "Server: ${ARGOCD_SERVER}"
echo ""

# Check if argocd CLI is available
if ! command -v argocd &>/dev/null; then
    fatal "ArgoCD CLI not found" \
        "Install with: curl -sSL https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64 -o /usr/local/bin/argocd && chmod +x /usr/local/bin/argocd"
fi

# Function to check if logged in to ArgoCD
check_argocd_auth() {
    if argocd app list --server "$ARGOCD_SERVER" --grpc-web &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to get PR number from dem2-infra
get_pr_number() {
    local preview_id="$1"

    info "Looking up PR number for preview: $preview_id"

    # Use gh CLI to find the PR
    if command -v gh &>/dev/null; then
        local pr_number
        pr_number=$(gh pr list --repo NumberOne-AI/dem2-infra \
            --label preview \
            --state open \
            --json number,headRefName \
            --jq ".[] | select(.headRefName == \"preview/$preview_id\") | .number" 2>/dev/null)

        if [[ -n "$pr_number" ]]; then
            echo "$pr_number"
            return 0
        fi
    fi

    return 1
}

# Function to get application status using argocd CLI
get_app_status_cli() {
    local app_name="$1"

    argocd app get "$app_name" \
        --server "$ARGOCD_SERVER" \
        --grpc-web \
        --output json 2>/dev/null | \
        jq -r '{health: .status.health.status, sync: .status.sync.status}' 2>/dev/null || echo "{}"
}

# Function to display application status
display_status() {
    local app_name="$1"
    local pr_number="$2"

    echo ""
    echo "========================================"
    echo "Application Status"
    echo "========================================"
    echo "Application: ${app_name}"
    echo "Preview ID: ${PREVIEW_ID}"
    echo "PR: #${pr_number}"
    echo ""

    # Get full app info
    if argocd app get "$app_name" --server "$ARGOCD_SERVER" --grpc-web 2>/dev/null; then
        echo ""
        echo "Preview URL: https://${PREVIEW_ID}.preview.n1-machina.dev"
        echo "ArgoCD UI: https://${ARGOCD_SERVER}/applications/${app_name}"
        echo "PR: https://github.com/NumberOne-AI/dem2-infra/pull/${pr_number}"
        return 0
    else
        return 1
    fi
}

# Function to wait for application to appear
wait_for_app_creation() {
    local app_name="$1"
    local max_wait=60  # Wait up to 60 seconds for app to be created
    local elapsed=0

    info "Waiting for ArgoCD to create application: $app_name"

    while [[ $elapsed -lt $max_wait ]]; do
        if argocd app get "$app_name" --server "$ARGOCD_SERVER" --grpc-web &>/dev/null; then
            info "Application created!"
            return 0
        fi

        echo -n "."
        sleep "$POLL_INTERVAL"
        elapsed=$((elapsed + POLL_INTERVAL))
    done

    echo ""
    err "Application not created after ${max_wait}s"
    return 1
}

# Function to poll application status
poll_app_status() {
    local app_name="$1"
    local timeout="$2"
    local elapsed=0

    info "Polling application status (every ${POLL_INTERVAL}s, timeout: ${timeout}s)..."
    echo ""

    while [[ $elapsed -lt $timeout ]]; do
        local status
        status=$(get_app_status_cli "$app_name")

        local health
        local sync
        health=$(echo "$status" | jq -r '.health // "Unknown"')
        sync=$(echo "$status" | jq -r '.sync // "Unknown"')

        echo "[${elapsed}s] Health: ${health} | Sync: ${sync}"

        # Check if deployment is complete
        if [[ "$health" == "Healthy" && "$sync" == "Synced" ]]; then
            echo ""
            info "Deployment complete! 🎉"
            return 0
        fi

        # Check for failure states
        if [[ "$health" == "Degraded" || "$health" == "Missing" ]]; then
            echo ""
            err "Deployment failed or degraded"
            return 1
        fi

        sleep "$POLL_INTERVAL"
        elapsed=$((elapsed + POLL_INTERVAL))
    done

    echo ""
    err "Timeout reached (${timeout}s) - deployment still in progress"
    return 1
}

# Main execution
info "Checking ArgoCD authentication..."

if ! check_argocd_auth; then
    echo ""
    info "Not logged in to ArgoCD"
    echo ""
    echo "To login, run:"
    echo "  argocd login $ARGOCD_SERVER --grpc-web"
    echo ""
    echo "Or use SSO:"
    echo "  argocd login $ARGOCD_SERVER --grpc-web --sso"
    echo ""
    fatal "Authentication required"
fi

info "Authenticated to ArgoCD"

# Get PR number if not provided
if [[ -z "$PR_NUMBER" ]]; then
    if PR_NUMBER=$(get_pr_number "$PREVIEW_ID"); then
        info "Found PR #${PR_NUMBER} for preview: $PREVIEW_ID"
    else
        fatal "Could not find PR for preview: $PREVIEW_ID" \
            "Make sure the PR exists in dem2-infra with label 'preview'" \
            "Or specify PR number with: --pr <number>"
    fi
fi

APP_NAME="preview-pr-${PR_NUMBER}"
info "Monitoring application: $APP_NAME"

# Wait for application to be created by ApplicationSet
if ! argocd app get "$APP_NAME" --server "$ARGOCD_SERVER" --grpc-web &>/dev/null; then
    info "Application doesn't exist yet (ApplicationSet polls every 30s)"
    if ! wait_for_app_creation "$APP_NAME"; then
        fatal "Application was not created by ArgoCD" \
            "Check ArgoCD UI: https://${ARGOCD_SERVER}/applications" \
            "Check PR has 'preview' label: https://github.com/NumberOne-AI/dem2-infra/pull/${PR_NUMBER}"
    fi
fi

echo ""

# Display initial status
display_status "$APP_NAME" "$PR_NUMBER"

echo ""
echo "========================================"
echo "Waiting for Deployment"
echo "========================================"
echo ""

# Use argocd app wait or poll
if [[ "$POLL_ONLY" == "true" ]]; then
    info "Using polling mode (--poll-only specified)"
    if poll_app_status "$APP_NAME" "$TIMEOUT"; then
        display_status "$APP_NAME" "$PR_NUMBER"
        exit 0
    else
        display_status "$APP_NAME" "$PR_NUMBER"
        exit 1
    fi
else
    info "Using 'argocd app wait' (timeout: ${TIMEOUT}s)..."

    if argocd app wait "$APP_NAME" \
        --server "$ARGOCD_SERVER" \
        --grpc-web \
        --timeout "$TIMEOUT" \
        --health 2>&1; then

        echo ""
        info "Deployment complete! 🎉"
        display_status "$APP_NAME" "$PR_NUMBER"
        exit 0
    else
        echo ""
        err "Deployment did not complete within ${TIMEOUT}s"
        display_status "$APP_NAME" "$PR_NUMBER"
        exit 1
    fi
fi
