#!/usr/bin/env bash
# Track preview environment deployment progress in ArgoCD
#
# Usage:
#   track-preview.sh <preview-id> [options]
#
# Options:
#   --watch           Watch deployment progress (poll every 5s)
#   --timeout <secs>  Max time to wait in watch mode (default: 600)
#
# Examples:
#   track-preview.sh my-feature
#   track-preview.sh my-feature --watch
#   track-preview.sh my-feature --watch --timeout 300

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source bashutils if available
if [[ -f "$WORKSPACE_ROOT/repos/dem2/scripts/bashutils.sh" ]]; then
    source "$WORKSPACE_ROOT/repos/dem2/scripts/bashutils.sh"
else
    # Fallback implementations
    err() { echo "ERROR: $*" >&2; }
    fatal() { echo "FATAL: $*" >&2; exit 1; }
    info() { echo "INFO: $*"; }
    success() { echo "SUCCESS: $*"; }
fi

# Default values
WATCH_MODE=false
TIMEOUT=600
POLL_INTERVAL=5

# Parse arguments
if [[ $# -eq 0 ]]; then
    fatal "Preview ID is required" "Usage: track-preview.sh <preview-id> [options]"
fi

PREVIEW_ID="$1"
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --watch)
            WATCH_MODE=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        *)
            fatal "Unknown option: $1"
            ;;
    esac
done

# ArgoCD configuration
ARGOCD_SERVER="argo.n1-machina.dev"
ARGOCD_URL="https://${ARGOCD_SERVER}"
APP_NAME="preview-${PREVIEW_ID}"

# Function to check if ArgoCD application exists
check_app_exists() {
    local app_name="$1"

    # Try to get app info (ArgoCD API is typically accessible without auth for read operations)
    if curl -sf "${ARGOCD_URL}/api/v1/applications/${app_name}" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to get application status
get_app_status() {
    local app_name="$1"

    # Get application info from ArgoCD API
    local response
    response=$(curl -sf "${ARGOCD_URL}/api/v1/applications/${app_name}" 2>/dev/null)

    if [[ -z "$response" ]]; then
        echo "UNKNOWN"
        return 1
    fi

    # Parse status fields using basic text processing (no jq dependency)
    local health_status
    local sync_status

    health_status=$(echo "$response" | grep -o '"health":{"status":"[^"]*"' | grep -o 'status":"[^"]*' | cut -d'"' -f3 || echo "Unknown")
    sync_status=$(echo "$response" | grep -o '"sync":{"status":"[^"]*"' | grep -o 'status":"[^"]*' | cut -d'"' -f3 || echo "Unknown")

    echo "$health_status|$sync_status"
}

# Function to display application status
display_status() {
    local health_status="$1"
    local sync_status="$2"

    echo ""
    echo "========================================"
    echo "Preview Environment Status"
    echo "========================================"
    echo "Preview ID: ${PREVIEW_ID}"
    echo "Application: ${APP_NAME}"
    echo ""
    echo "Health Status: ${health_status}"
    echo "Sync Status: ${sync_status}"
    echo ""

    # Health status indicators
    case "$health_status" in
        Healthy)
            success "Application is healthy ✓"
            ;;
        Progressing)
            info "Application is deploying..."
            ;;
        Degraded)
            err "Application is degraded ✗"
            ;;
        Suspended)
            info "Application is suspended"
            ;;
        Missing)
            err "Application resources are missing ✗"
            ;;
        Unknown)
            err "Health status unknown"
            ;;
        *)
            info "Health status: ${health_status}"
            ;;
    esac

    # Sync status indicators
    case "$sync_status" in
        Synced)
            success "Application is synced ✓"
            ;;
        OutOfSync)
            info "Application is out of sync (pending changes)"
            ;;
        Unknown)
            err "Sync status unknown"
            ;;
        *)
            info "Sync status: ${sync_status}"
            ;;
    esac

    echo ""
    echo "Preview URL (once deployed):"
    echo "  https://${PREVIEW_ID}.preview.n1-machina.dev"
    echo ""
    echo "ArgoCD UI:"
    echo "  ${ARGOCD_URL}/applications/${APP_NAME}"
    echo ""
}

# Function to check if deployment is complete
is_deployment_complete() {
    local health_status="$1"
    local sync_status="$2"

    if [[ "$health_status" == "Healthy" && "$sync_status" == "Synced" ]]; then
        return 0
    else
        return 1
    fi
}

# Check if application exists
info "Checking ArgoCD for preview environment: ${APP_NAME}"

if ! check_app_exists "$APP_NAME"; then
    fatal "Preview environment not found in ArgoCD" \
        "Application '${APP_NAME}' does not exist." \
        "Make sure the preview has been created with: just preview-create ${PREVIEW_ID}" \
        "It may take a few minutes for ArgoCD to detect the new environment."
fi

# Get initial status
status_output=$(get_app_status "$APP_NAME")
IFS='|' read -r health_status sync_status <<< "$status_output"

display_status "$health_status" "$sync_status"

# Watch mode - poll for status changes
if [[ "$WATCH_MODE" == "true" ]]; then
    info "Watching deployment progress (polling every ${POLL_INTERVAL}s, timeout: ${TIMEOUT}s)..."
    info "Press Ctrl+C to stop watching"
    echo ""

    elapsed=0
    while [[ $elapsed -lt $TIMEOUT ]]; do
        sleep "$POLL_INTERVAL"
        elapsed=$((elapsed + POLL_INTERVAL))

        # Get current status
        status_output=$(get_app_status "$APP_NAME")
        IFS='|' read -r health_status sync_status <<< "$status_output"

        # Display status update
        echo "[${elapsed}s] Health: ${health_status} | Sync: ${sync_status}"

        # Check if deployment is complete
        if is_deployment_complete "$health_status" "$sync_status"; then
            echo ""
            success "Deployment complete! 🎉"
            display_status "$health_status" "$sync_status"
            exit 0
        fi

        # Check for failure states
        if [[ "$health_status" == "Degraded" || "$health_status" == "Missing" ]]; then
            echo ""
            err "Deployment failed or degraded"
            display_status "$health_status" "$sync_status"
            exit 1
        fi
    done

    echo ""
    err "Timeout reached (${TIMEOUT}s) - deployment still in progress"
    display_status "$health_status" "$sync_status"
    exit 1
fi
