#!/usr/bin/env bash
# Check GitHub token permissions for cross-repo preview workflows
#
# Usage:
#   check-token-permissions.sh [token]
#
# If no token is provided, will attempt to use CROSS_REPO_DEM2_WEBUI_TOKEN env var
#
# Examples:
#   check-token-permissions.sh
#   check-token-permissions.sh ghp_xxxxxxxxxxxxx
#   CROSS_REPO_DEM2_WEBUI_TOKEN=ghp_xxx check-token-permissions.sh

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
    warn() { echo "WARNING: $*"; }
fi

# Get token from argument or environment
TOKEN="${1:-${CROSS_REPO_DEM2_WEBUI_TOKEN:-}}"

if [[ -z "$TOKEN" ]]; then
    fatal "No token provided" \
        "Usage: $0 [token]" \
        "Or set CROSS_REPO_DEM2_WEBUI_TOKEN environment variable"
fi

# Mask token in logs
TOKEN_PREFIX="${TOKEN:0:7}"
TOKEN_MASKED="${TOKEN_PREFIX}...${TOKEN: -4}"

echo ""
echo "========================================"
echo "GitHub Token Permission Checker"
echo "========================================"
echo "Token: $TOKEN_MASKED"
echo ""

# Required repositories
REPOS=(
    "NumberOne-AI/dem2"
    "NumberOne-AI/dem2-webui"
    "NumberOne-AI/dem2-infra"
)

# Track results
declare -a PASSED_CHECKS=()
declare -a FAILED_CHECKS=()

# Function to make authenticated GitHub API request
gh_api() {
    local endpoint="$1"
    local method="${2:-GET}"

    curl -sf \
        -H "Authorization: token $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -X "$method" \
        "https://api.github.com$endpoint" 2>/dev/null
}

# Function to check repository access
check_repo_access() {
    local repo="$1"

    info "Checking access to $repo..."

    # Try to get repository info
    if response=$(gh_api "/repos/$repo"); then
        # Extract permissions from response
        local can_push=$(echo "$response" | grep -o '"push":\s*true' || echo "")
        local can_pull=$(echo "$response" | grep -o '"pull":\s*true' || echo "")

        if [[ -n "$can_pull" ]]; then
            success "✓ Can read $repo"
            PASSED_CHECKS+=("read:$repo")

            if [[ -n "$can_push" ]]; then
                success "✓ Can write to $repo"
                PASSED_CHECKS+=("write:$repo")
            else
                warn "⚠ Cannot write to $repo (read-only access)"
                FAILED_CHECKS+=("write:$repo")
            fi
        else
            err "✗ Cannot read $repo"
            FAILED_CHECKS+=("read:$repo")
        fi
    else
        err "✗ Cannot access $repo (401/403/404)"
        FAILED_CHECKS+=("access:$repo")
    fi

    echo ""
}

# Function to check if token can dispatch events
check_dispatch_permission() {
    local repo="NumberOne-AI/dem2-infra"

    info "Checking repository_dispatch permission for $repo..."

    # We can't actually test dispatch without triggering a real event
    # But we can check if we have write access to the repo, which is required
    if response=$(gh_api "/repos/$repo"); then
        local can_push=$(echo "$response" | grep -o '"push":\s*true' || echo "")

        if [[ -n "$can_push" ]]; then
            success "✓ Has write access (required for repository_dispatch)"
            PASSED_CHECKS+=("dispatch:$repo")
        else
            err "✗ No write access (repository_dispatch requires write permission)"
            FAILED_CHECKS+=("dispatch:$repo")
        fi
    else
        err "✗ Cannot verify dispatch permission"
        FAILED_CHECKS+=("dispatch:$repo")
    fi

    echo ""
}

# Function to check pull request permissions
check_pr_permission() {
    local repo="NumberOne-AI/dem2-infra"

    info "Checking pull request permissions for $repo..."

    # Try to list PRs (requires read)
    if gh_api "/repos/$repo/pulls?state=open&per_page=1" &>/dev/null; then
        success "✓ Can read pull requests"
        PASSED_CHECKS+=("pr_read:$repo")

        # Check if we can create PRs (requires write)
        if response=$(gh_api "/repos/$repo"); then
            local can_push=$(echo "$response" | grep -o '"push":\s*true' || echo "")

            if [[ -n "$can_push" ]]; then
                success "✓ Can create pull requests"
                PASSED_CHECKS+=("pr_write:$repo")
            else
                err "✗ Cannot create pull requests (no write access)"
                FAILED_CHECKS+=("pr_write:$repo")
            fi
        fi
    else
        err "✗ Cannot read pull requests"
        FAILED_CHECKS+=("pr_read:$repo")
    fi

    echo ""
}

# Function to check token scopes
check_token_scopes() {
    info "Checking token scopes..."

    # GitHub returns scopes in X-OAuth-Scopes header
    if response=$(curl -sf -I \
        -H "Authorization: token $TOKEN" \
        "https://api.github.com/user" 2>/dev/null); then

        # Extract scopes from header
        scopes=$(echo "$response" | grep -i "x-oauth-scopes:" | cut -d: -f2 | tr -d '\r' | xargs)

        if [[ -n "$scopes" ]]; then
            success "✓ Token scopes: $scopes"
            PASSED_CHECKS+=("scopes")

            # Check for required scopes
            if echo "$scopes" | grep -q "repo"; then
                success "✓ Has 'repo' scope (full repository access)"
                PASSED_CHECKS+=("scope:repo")
            else
                err "✗ Missing 'repo' scope (required for repository_dispatch)"
                FAILED_CHECKS+=("scope:repo")
            fi

            if echo "$scopes" | grep -q "workflow"; then
                success "✓ Has 'workflow' scope (can update workflows)"
                PASSED_CHECKS+=("scope:workflow")
            else
                warn "⚠ Missing 'workflow' scope (optional but recommended)"
            fi
        else
            warn "⚠ Could not determine token scopes (may be fine-grained token)"
        fi
    else
        err "✗ Cannot authenticate with token"
        FAILED_CHECKS+=("auth")
    fi

    echo ""
}

# Run checks
echo "Running permission checks..."
echo ""

check_token_scopes

for repo in "${REPOS[@]}"; do
    check_repo_access "$repo"
done

check_dispatch_permission
check_pr_permission

# Summary
echo "========================================"
echo "Summary"
echo "========================================"
echo ""
echo "Passed checks: ${#PASSED_CHECKS[@]}"
echo "Failed checks: ${#FAILED_CHECKS[@]}"
echo ""

if [[ ${#FAILED_CHECKS[@]} -eq 0 ]]; then
    success "✅ All checks passed! Token has correct permissions."
    echo ""
    echo "Token is ready for preview workflows:"
    echo "  - Can access all required repositories"
    echo "  - Can dispatch events to dem2-infra"
    echo "  - Can create and update pull requests"
    exit 0
else
    err "❌ Some checks failed!"
    echo ""
    echo "Failed checks:"
    for check in "${FAILED_CHECKS[@]}"; do
        echo "  - $check"
    done
    echo ""
    echo "Required token permissions:"
    echo "  - Scope: 'repo' (full repository access)"
    echo "  - Access: NumberOne-AI/dem2 (read/write)"
    echo "  - Access: NumberOne-AI/dem2-webui (read/write)"
    echo "  - Access: NumberOne-AI/dem2-infra (read/write)"
    echo ""
    echo "To fix:"
    echo "  1. Go to GitHub Settings → Developer settings → Personal access tokens"
    echo "  2. Create new token with 'repo' scope"
    echo "  3. Grant access to NumberOne-AI organization"
    echo "  4. Update CROSS_REPO_DEM2_WEBUI_TOKEN secret in all repositories"
    exit 1
fi
