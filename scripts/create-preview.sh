#!/usr/bin/env bash
# Create preview environment by tagging repositories
#
# Usage:
#   create-preview.sh <preview-id> [options]
#
# Options:
#   --repos <repos>    Comma-separated list of repos to tag (default: dem2,dem2-webui)
#   --branch <branch>  Branch to tag (default: current branch)
#   --no-push          Don't push tags (dry-run)
#   --force            Force overwrite existing tags
#
# Examples:
#   create-preview.sh my-feature
#   create-preview.sh my-feature --repos dem2,dem2-webui,medical-catalog
#   create-preview.sh my-feature --branch feature/my-branch --no-push

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
REPOS="dem2,dem2-webui"
BRANCH=""
DRY_RUN=false
FORCE=false

# Parse arguments
if [[ $# -eq 0 ]]; then
    fatal "Preview ID is required" "Usage: create-preview.sh <preview-id> [options]"
fi

PREVIEW_ID="$1"
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repos)
            REPOS="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --no-push)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            fatal "Unknown option: $1"
            ;;
    esac
done

# Validate preview ID
if [[ ! "$PREVIEW_ID" =~ ^[a-z0-9-]+$ ]]; then
    fatal "Preview ID must contain only lowercase letters, numbers, and hyphens: $PREVIEW_ID"
fi

TAG_NAME="preview-${PREVIEW_ID}"

info "Creating preview environment: $PREVIEW_ID"
info "Repositories: $REPOS"
info "Tag name: $TAG_NAME"

# Convert comma-separated repos to array
IFS=',' read -ra REPO_ARRAY <<< "$REPOS"

# Track success/failure
declare -a TAGGED_REPOS=()
declare -a FAILED_REPOS=()

# Tag each repository
for repo in "${REPO_ARRAY[@]}"; do
    repo_path="$WORKSPACE_ROOT/repos/$repo"

    if [[ ! -d "$repo_path" ]]; then
        err "Repository not found: $repo_path"
        FAILED_REPOS+=("$repo")
        continue
    fi

    info "Processing $repo..."

    cd "$repo_path"

    # Get current branch if not specified
    current_branch="${BRANCH:-$(git branch --show-current)}"

    if [[ -z "$current_branch" ]]; then
        err "Could not determine current branch for $repo"
        FAILED_REPOS+=("$repo")
        continue
    fi

    # Check if branch exists
    if ! git rev-parse --verify "$current_branch" &>/dev/null; then
        err "Branch does not exist: $current_branch"
        FAILED_REPOS+=("$repo")
        continue
    fi

    # Create tag
    if [[ "$FORCE" == "true" ]]; then
        git tag -f "$TAG_NAME" "$current_branch"
    else
        if git rev-parse "$TAG_NAME" &>/dev/null; then
            err "Tag already exists: $TAG_NAME (use --force to overwrite)"
            FAILED_REPOS+=("$repo")
            continue
        fi
        git tag "$TAG_NAME" "$current_branch"
    fi

    # Push tag
    if [[ "$DRY_RUN" == "false" ]]; then
        if [[ "$FORCE" == "true" ]]; then
            git push origin "$TAG_NAME" --force
        else
            git push origin "$TAG_NAME"
        fi
        success "Tagged and pushed $repo: $TAG_NAME"
    else
        info "DRY-RUN: Would push tag $TAG_NAME for $repo"
    fi

    TAGGED_REPOS+=("$repo")
done

# Summary
echo ""
echo "========================================"
echo "Preview Environment Summary"
echo "========================================"
echo "Preview ID: $PREVIEW_ID"
echo "Tag: $TAG_NAME"
echo ""
echo "Tagged repositories (${#TAGGED_REPOS[@]}):"
for repo in "${TAGGED_REPOS[@]}"; do
    echo "  ✅ $repo"
done

if [[ ${#FAILED_REPOS[@]} -gt 0 ]]; then
    echo ""
    echo "Failed repositories (${#FAILED_REPOS[@]}):"
    for repo in "${FAILED_REPOS[@]}"; do
        echo "  ❌ $repo"
    done
fi

echo ""
if [[ "$DRY_RUN" == "false" ]]; then
    echo "Preview environment will be created in a few minutes."
    echo ""
    echo "Monitor deployment:"
    echo "  ArgoCD UI: https://argo.n1-machina.dev/applications"
    echo "  Track progress: $SCRIPT_DIR/track-preview.sh $PREVIEW_ID"
    echo ""
    echo "Preview URL (once deployed):"
    echo "  https://${PREVIEW_ID}.preview.n1-machina.dev"
else
    echo "DRY-RUN: No tags were pushed"
fi

# Exit with error if any repos failed
if [[ ${#FAILED_REPOS[@]} -gt 0 ]]; then
    exit 1
fi
