#!/usr/bin/env bash
# preview-tool.sh - Utility for managing preview environments, PRs, and deployments
#
# ArgoCD Behavior Note:
# When using the ArgoCD CLI to check if an application has been deleted, the command
# may return "PermissionDenied" error instead of "NotFound", particularly in ArgoCD
# versions 2.6 and later. This is intentional for security reasons to prevent potential
# enumeration of existing applications by attackers. Therefore, "PermissionDenied"
# errors when querying ArgoCD applications may indicate the app doesn't exist or was
# already deleted, not necessarily a permissions issue.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Symbols
CHECK="✅"
CROSS="❌"
CIRCLE="⚪"
WARN="⚠️"

# Repository paths
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEM2_REPO="$WORKSPACE_ROOT/repos/dem2"
WEBUI_REPO="$WORKSPACE_ROOT/repos/dem2-webui"
INFRA_REPO="$WORKSPACE_ROOT/repos/dem2-infra"

# GitHub organization
GITHUB_ORG="NumberOne-AI"

# Print colored output
print_color() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

# Print section header
print_header() {
    echo ""
    print_color "$CYAN" "══════════════════════════════════════════════════════════════"
    print_color "$CYAN" "$1"
    print_color "$CYAN" "══════════════════════════════════════════════════════════════"
}

# Print key-value pair
print_kv() {
    local key="$1"
    local value="$2"
    printf "  %-25s %s\n" "$key:" "$value"
}

# Show usage
show_usage() {
    cat << EOF
Usage: $(basename "$0") <command> [options]

Commands:
  info <id>              Show detailed information about a preview environment
  delete <id>            Delete preview environment (tags, close PR to trigger ArgoCD cleanup)
  delete-argocd <id>     Delete only the ArgoCD application directly
  list                   List all active preview environments (TODO)
  status <id>            Check deployment status of preview environment (TODO)
  cleanup-stale          Find and cleanup stale preview environments (TODO)
  pr-info <repo> <num>   Show PR information for a specific repo (TODO)

Examples:
  $(basename "$0") info pr-70
  $(basename "$0") delete pr-70
  $(basename "$0") delete-argocd pr-70
  $(basename "$0") list
  $(basename "$0") pr-info dem2 70

Options:
  -h, --help             Show this help message

Environment:
  WORKSPACE_ROOT         Root of machina-meta workspace
  DEM2_REPO              Path to dem2 repository
  WEBUI_REPO             Path to dem2-webui repository
  INFRA_REPO             Path to dem2-infra repository
EOF
}

# Get PR info from GitHub using gh CLI
get_pr_info() {
    local repo="$1"
    local pr_number="$2"

    if ! command -v gh &>/dev/null; then
        echo "N/A (gh CLI not installed)"
        return 1
    fi

    gh pr view "$pr_number" --repo "$GITHUB_ORG/$repo" \
        --json number,title,state,headRefName,baseRefName,url,author,createdAt,mergedAt,closedAt \
        2>/dev/null || echo ""
}

# Check if git tag exists in a repo
check_git_tag() {
    local repo_path="$1"
    local tag="$2"

    if [[ ! -d "$repo_path" ]]; then
        echo "REPO_NOT_FOUND"
        return 1
    fi

    if git -C "$repo_path" rev-parse "$tag" &>/dev/null; then
        local tag_commit=$(git -C "$repo_path" rev-parse "$tag" 2>/dev/null)
        local tag_date=$(git -C "$repo_path" log -1 --format=%ai "$tag" 2>/dev/null)
        echo "EXISTS|$tag_commit|$tag_date"
        return 0
    else
        echo "NOT_FOUND"
        return 1
    fi
}

# Check if git branch exists in a repo
check_git_branch() {
    local repo_path="$1"
    local branch="$2"

    if [[ ! -d "$repo_path" ]]; then
        echo "REPO_NOT_FOUND"
        return 1
    fi

    # Check local branches
    if git -C "$repo_path" show-ref --verify --quiet "refs/heads/$branch"; then
        echo "LOCAL"
        return 0
    fi

    # Check remote branches
    if git -C "$repo_path" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        echo "REMOTE"
        return 0
    fi

    echo "NOT_FOUND"
    return 1
}

# Format timestamp
format_timestamp() {
    local timestamp="$1"
    if [[ -n "$timestamp" ]] && [[ "$timestamp" != "null" ]]; then
        date -d "$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$timestamp"
    else
        echo "N/A"
    fi
}

# Show detailed info about a preview environment
cmd_info() {
    local preview_id="$1"

    if [[ -z "$preview_id" ]]; then
        print_color "$RED" "Error: Preview ID required"
        echo "Usage: $(basename "$0") info <preview-id>"
        exit 1
    fi

    print_header "Preview Environment: $preview_id"

    # Extract PR number if the ID is in format "pr-XX"
    local pr_number=""
    if [[ "$preview_id" =~ ^pr-([0-9]+)$ ]]; then
        pr_number="${BASH_REMATCH[1]}"
    fi

    # ============================================================
    # Check dem2 repository
    # ============================================================
    print_header "dem2 (Backend)"

    local dem2_tag_info=$(check_git_tag "$DEM2_REPO" "preview-$preview_id")
    local dem2_tag_status=$(echo "$dem2_tag_info" | cut -d'|' -f1)

    if [[ "$dem2_tag_status" == "EXISTS" ]]; then
        local tag_commit=$(echo "$dem2_tag_info" | cut -d'|' -f2)
        local tag_date=$(echo "$dem2_tag_info" | cut -d'|' -f3)
        print_kv "Preview Tag" "$CHECK preview-$preview_id"
        print_kv "Tag Commit" "${tag_commit:0:8}"
        print_kv "Tag Date" "$tag_date"
    else
        print_kv "Preview Tag" "$CROSS Not found"
    fi

    # Check for PR if we have a number
    if [[ -n "$pr_number" ]]; then
        local dem2_pr_json=$(get_pr_info "dem2" "$pr_number")

        if [[ -n "$dem2_pr_json" ]]; then
            local pr_state=$(echo "$dem2_pr_json" | jq -r '.state')
            local pr_title=$(echo "$dem2_pr_json" | jq -r '.title')
            local pr_branch=$(echo "$dem2_pr_json" | jq -r '.headRefName')
            local pr_url=$(echo "$dem2_pr_json" | jq -r '.url')
            local pr_author=$(echo "$dem2_pr_json" | jq -r '.author.login')
            local pr_created=$(echo "$dem2_pr_json" | jq -r '.createdAt')
            local pr_merged=$(echo "$dem2_pr_json" | jq -r '.mergedAt')
            local pr_closed=$(echo "$dem2_pr_json" | jq -r '.closedAt')

            print_kv "PR #$pr_number" "$pr_title"

            case "$pr_state" in
                "OPEN")
                    print_kv "Status" "$(print_color "$GREEN" "$CHECK OPEN")"
                    ;;
                "MERGED")
                    print_kv "Status" "$(print_color "$BLUE" "$CHECK MERGED") ($(format_timestamp "$pr_merged"))"
                    ;;
                "CLOSED")
                    print_kv "Status" "$(print_color "$RED" "$CROSS CLOSED") ($(format_timestamp "$pr_closed"))"
                    ;;
            esac

            print_kv "Branch" "$pr_branch"
            print_kv "Author" "$pr_author"
            print_kv "Created" "$(format_timestamp "$pr_created")"
            print_kv "URL" "$pr_url"
        else
            print_kv "PR #$pr_number" "$CIRCLE Not found or no access"
        fi
    fi

    # ============================================================
    # Check dem2-webui repository
    # ============================================================
    print_header "dem2-webui (Frontend)"

    local webui_tag_info=$(check_git_tag "$WEBUI_REPO" "preview-$preview_id")
    local webui_tag_status=$(echo "$webui_tag_info" | cut -d'|' -f1)

    if [[ "$webui_tag_status" == "EXISTS" ]]; then
        local tag_commit=$(echo "$webui_tag_info" | cut -d'|' -f2)
        local tag_date=$(echo "$webui_tag_info" | cut -d'|' -f3)
        print_kv "Preview Tag" "$CHECK preview-$preview_id"
        print_kv "Tag Commit" "${tag_commit:0:8}"
        print_kv "Tag Date" "$tag_date"
    else
        print_kv "Preview Tag" "$CROSS Not found"
    fi

    # Check for PR if we have a number
    if [[ -n "$pr_number" ]]; then
        local webui_pr_json=$(get_pr_info "dem2-webui" "$pr_number")

        if [[ -n "$webui_pr_json" ]]; then
            local pr_state=$(echo "$webui_pr_json" | jq -r '.state')
            local pr_title=$(echo "$webui_pr_json" | jq -r '.title')
            local pr_branch=$(echo "$webui_pr_json" | jq -r '.headRefName')
            local pr_url=$(echo "$webui_pr_json" | jq -r '.url')
            local pr_author=$(echo "$webui_pr_json" | jq -r '.author.login')
            local pr_created=$(echo "$webui_pr_json" | jq -r '.createdAt')
            local pr_merged=$(echo "$webui_pr_json" | jq -r '.mergedAt')
            local pr_closed=$(echo "$webui_pr_json" | jq -r '.closedAt')

            print_kv "PR #$pr_number" "$pr_title"

            case "$pr_state" in
                "OPEN")
                    print_kv "Status" "$(print_color "$GREEN" "$CHECK OPEN")"
                    ;;
                "MERGED")
                    print_kv "Status" "$(print_color "$BLUE" "$CHECK MERGED") ($(format_timestamp "$pr_merged"))"
                    ;;
                "CLOSED")
                    print_kv "Status" "$(print_color "$RED" "$CROSS CLOSED") ($(format_timestamp "$pr_closed"))"
                    ;;
            esac

            print_kv "Branch" "$pr_branch"
            print_kv "Author" "$pr_author"
            print_kv "Created" "$(format_timestamp "$pr_created")"
            print_kv "URL" "$pr_url"
        else
            print_kv "PR #$pr_number" "$CIRCLE Not found or no access"
        fi
    fi

    # ============================================================
    # Check dem2-infra repository
    # ============================================================
    print_header "dem2-infra (Infrastructure)"

    local infra_branch_status=$(check_git_branch "$INFRA_REPO" "preview/$preview_id")
    print_kv "Preview Branch" "preview/$preview_id: $infra_branch_status"

    # Look for associated PR in dem2-infra
    if command -v gh &>/dev/null; then
        local infra_pr_json=$(gh pr list --repo "$GITHUB_ORG/dem2-infra" \
            --head "preview/$preview_id" \
            --json number,title,state,url,author,createdAt,mergedAt,closedAt \
            --limit 1 2>/dev/null | jq '.[0]' 2>/dev/null)

        if [[ -n "$infra_pr_json" ]] && [[ "$infra_pr_json" != "null" ]]; then
            local pr_number=$(echo "$infra_pr_json" | jq -r '.number')
            local pr_state=$(echo "$infra_pr_json" | jq -r '.state')
            local pr_title=$(echo "$infra_pr_json" | jq -r '.title')
            local pr_url=$(echo "$infra_pr_json" | jq -r '.url')
            local pr_author=$(echo "$infra_pr_json" | jq -r '.author.login')
            local pr_created=$(echo "$infra_pr_json" | jq -r '.createdAt')
            local pr_merged=$(echo "$infra_pr_json" | jq -r '.mergedAt')
            local pr_closed=$(echo "$infra_pr_json" | jq -r '.closedAt')

            print_kv "PR #$pr_number" "$pr_title"

            case "$pr_state" in
                "OPEN")
                    print_kv "Status" "$(print_color "$GREEN" "$CHECK OPEN")"
                    ;;
                "MERGED")
                    print_kv "Status" "$(print_color "$BLUE" "$CHECK MERGED") ($(format_timestamp "$pr_merged"))"
                    ;;
                "CLOSED")
                    print_kv "Status" "$(print_color "$RED" "$CROSS CLOSED") ($(format_timestamp "$pr_closed"))"
                    ;;
            esac

            print_kv "Author" "$pr_author"
            print_kv "Created" "$(format_timestamp "$pr_created")"
            print_kv "URL" "$pr_url"
        else
            print_kv "Infra PR" "$CIRCLE Not found"
        fi
    fi

    # ============================================================
    # ArgoCD Application Status
    # ============================================================
    print_header "ArgoCD Deployment"

    # ArgoCD app naming convention is preview-pr-{INFRA_PR_NUMBER}
    # So we need to look up the infra PR number first
    local argocd_app=""
    local argocd_url=""

    if command -v gh &>/dev/null; then
        local infra_pr_number=$(gh pr list --repo "$GITHUB_ORG/dem2-infra" \
            --head "preview/$preview_id" \
            --json number \
            --jq '.[0].number' 2>/dev/null || echo "")

        if [[ -n "$infra_pr_number" ]]; then
            argocd_app="preview-pr-$infra_pr_number"
            argocd_url="https://argo.n1-machina.dev/applications/$argocd_app"
            print_kv "Application Name" "$argocd_app (based on infra PR #$infra_pr_number)"
        else
            # Fallback to preview-{id} naming
            argocd_app="preview-$preview_id"
            argocd_url="https://argo.n1-machina.dev/applications/$argocd_app"
            print_kv "Application Name" "$argocd_app (infra PR not found, using fallback)"
        fi
    else
        argocd_app="preview-$preview_id"
        argocd_url="https://argo.n1-machina.dev/applications/$argocd_app"
        print_kv "Application Name" "$argocd_app (gh CLI not available)"
    fi

    print_kv "ArgoCD URL" "$argocd_url"

    # Try to get ArgoCD status if CLI is available
    if command -v argocd &>/dev/null && [[ -n "$argocd_app" ]]; then
        local app_status=$(argocd app get "$argocd_app" -o json 2>/dev/null || echo "")

        if [[ -n "$app_status" ]]; then
            local sync_status=$(echo "$app_status" | jq -r '.status.sync.status')
            local health_status=$(echo "$app_status" | jq -r '.status.health.status')

            print_kv "Sync Status" "$sync_status"
            print_kv "Health Status" "$health_status"
        else
            print_kv "Status" "$CIRCLE Cannot retrieve (app may not exist)"
        fi
    else
        print_kv "Status" "$CIRCLE ArgoCD CLI not available"
    fi

    # ============================================================
    # Summary & Recommendations
    # ============================================================
    print_header "Summary"

    local has_tags=false
    local has_open_prs=false
    local has_infra_branch=false

    if [[ "$dem2_tag_status" == "EXISTS" ]] || [[ "$webui_tag_status" == "EXISTS" ]]; then
        has_tags=true
    fi

    if [[ "$infra_branch_status" != "NOT_FOUND" ]]; then
        has_infra_branch=true
    fi

    # Determine if this is a stale environment
    if [[ "$has_tags" == true ]] || [[ "$has_infra_branch" == true ]]; then
        echo ""
        print_color "$YELLOW" "  $WARN This preview environment has artifacts that may need cleanup:"

        if [[ "$dem2_tag_status" == "EXISTS" ]]; then
            echo "    • dem2 has preview tag: preview-$preview_id"
        fi

        if [[ "$webui_tag_status" == "EXISTS" ]]; then
            echo "    • dem2-webui has preview tag: preview-$preview_id"
        fi

        if [[ "$has_infra_branch" == true ]]; then
            echo "    • dem2-infra has preview branch: preview/$preview_id"
        fi

        echo ""
        print_color "$CYAN" "  To cleanup this preview environment, run:"
        print_color "$GRAY" "    just preview-delete $preview_id"
    else
        print_color "$GREEN" "  $CHECK No preview artifacts found - environment is clean"
    fi

    echo ""
}

# Delete ArgoCD application only
cmd_delete_argocd() {
    local preview_id="$1"

    if [[ -z "$preview_id" ]]; then
        print_color "$RED" "Error: Preview ID required"
        echo "Usage: $(basename "$0") delete-argocd <preview-id>"
        exit 1
    fi

    print_header "Deleting ArgoCD Application for Preview: $preview_id"

    if ! command -v argocd &>/dev/null; then
        print_color "$RED" "$CROSS ArgoCD CLI not available"
        echo ""
        echo "Please install ArgoCD CLI or use 'just preview-delete $preview_id' to close the PR"
        echo "which will trigger ArgoCD to auto-cleanup the application."
        exit 1
    fi

    # Determine ArgoCD app name (preview-pr-{INFRA_PR_NUMBER})
    local argocd_app=""
    if command -v gh &>/dev/null; then
        local infra_pr_number=$(gh pr list --repo "$GITHUB_ORG/dem2-infra" \
            --head "preview/$preview_id" \
            --json number \
            --jq '.[0].number' 2>/dev/null || echo "")

        if [[ -n "$infra_pr_number" ]]; then
            argocd_app="preview-pr-$infra_pr_number"
            echo ""
            print_color "$CYAN" "Found infra PR #$infra_pr_number"
            print_color "$CYAN" "ArgoCD app name: $argocd_app"
        else
            # Fallback to preview-{id} naming
            argocd_app="preview-$preview_id"
            echo ""
            print_color "$YELLOW" "$WARN Could not find infra PR, using fallback name: $argocd_app"
        fi
    else
        argocd_app="preview-$preview_id"
        echo ""
        print_color "$YELLOW" "$WARN gh CLI not available, using fallback name: $argocd_app"
    fi

    # Check if app exists
    # Note: ArgoCD 2.6+ may return PermissionDenied for deleted apps (not NotFound)
    # This is a security feature to prevent app enumeration
    echo ""
    print_color "$CYAN" "Checking if ArgoCD application exists..."
    if ! argocd app get "$argocd_app" &>/dev/null; then
        print_color "$YELLOW" "$WARN Application '$argocd_app' not found in ArgoCD"
        echo ""
        echo "The application may have already been deleted or never existed."
        echo "(Note: ArgoCD 2.6+ returns PermissionDenied for deleted apps)"
        exit 0
    fi

    # Delete the application
    echo ""
    print_color "$CYAN" "Deleting ArgoCD application '$argocd_app'..."
    if argocd app delete "$argocd_app" --yes 2>&1; then
        echo ""
        print_color "$GREEN" "$CHECK Successfully deleted ArgoCD application: $argocd_app"
    else
        echo ""
        print_color "$RED" "$CROSS Failed to delete ArgoCD application"
        exit 1
    fi

    echo ""
    print_color "$YELLOW" "$WARN Note: This only deleted the ArgoCD application"
    echo "  To fully cleanup the preview environment (tags, PRs), run:"
    print_color "$GRAY" "    $(basename "$0") delete $preview_id"

    echo ""
}

# Delete preview environment (tags, close PR, trigger ArgoCD cleanup)
cmd_delete() {
    local preview_id="$1"

    if [[ -z "$preview_id" ]]; then
        print_color "$RED" "Error: Preview ID required"
        echo "Usage: $(basename "$0") delete <preview-id>"
        exit 1
    fi

    print_header "Deleting Preview Environment: $preview_id"

    # ============================================================
    # Close PR in dem2-infra (triggers ArgoCD auto-cleanup)
    # ============================================================
    if command -v gh &>/dev/null; then
        echo ""
        print_color "$CYAN" "Looking up PR for preview/$preview_id branch in dem2-infra..."

        local pr_number=$(gh pr list --repo "$GITHUB_ORG/dem2-infra" \
            --head "preview/$preview_id" \
            --state open \
            --json number \
            --jq '.[0].number' 2>/dev/null || echo "")

        if [[ -n "$pr_number" ]]; then
            print_color "$CYAN" "Found PR #${pr_number}"
            echo ""
            print_color "$CYAN" "Closing PR to remove preview environment..."

            if gh pr close "$pr_number" --repo "$GITHUB_ORG/dem2-infra" \
                --comment "Closing preview environment: $preview_id" 2>/dev/null; then
                print_color "$GREEN" "$CHECK Closed PR #${pr_number}"
            else
                print_color "$YELLOW" "$WARN Could not close PR #${pr_number} (may already be closed)"
            fi
        else
            print_color "$GRAY" "$CIRCLE No open PR found for preview/$preview_id"
        fi
    else
        print_color "$YELLOW" "$WARN gh CLI not available, skipping PR closure"
    fi

    # ============================================================
    # Remove tags from dem2 and dem2-webui repos
    # ============================================================
    echo ""
    print_color "$CYAN" "Removing preview tags from application repositories..."

    local removed_count=0
    local skipped_count=0

    for repo in dem2 dem2-webui; do
        local repo_path="$WORKSPACE_ROOT/repos/$repo"
        echo ""
        print_color "$CYAN" "Processing $repo..."

        if [[ ! -d "$repo_path" ]]; then
            print_color "$YELLOW" "  $WARN Repository not found: $repo_path"
            skipped_count=$((skipped_count + 1))
            continue
        fi

        if git -C "$repo_path" rev-parse "preview-$preview_id" &>/dev/null; then
            # Delete local tag
            git -C "$repo_path" tag -d "preview-$preview_id" 2>&1 | sed 's/^/  /'

            # Delete remote tag
            if git -C "$repo_path" push origin ":refs/tags/preview-$preview_id" 2>&1 | sed 's/^/  /'; then
                print_color "$GREEN" "  $CHECK Removed preview-$preview_id from $repo"
                removed_count=$((removed_count + 1))
            else
                print_color "$YELLOW" "  $WARN Tag not on remote or already deleted"
                removed_count=$((removed_count + 1))
            fi
        else
            print_color "$GRAY" "  $CIRCLE Tag doesn't exist in $repo"
            skipped_count=$((skipped_count + 1))
        fi
    done

    # ============================================================
    # Summary
    # ============================================================
    echo ""
    print_header "Summary"

    # Determine ArgoCD app name for monitoring
    local argocd_app="preview-$preview_id"
    if [[ -n "$pr_number" ]]; then
        argocd_app="preview-pr-$pr_number"
    fi

    echo ""
    print_color "$GREEN" "$CHECK Preview environment deletion completed"
    echo ""
    echo "  Tags removed: $removed_count"
    echo "  Tags skipped: $skipped_count"
    echo ""
    print_color "$CYAN" "Note: ArgoCD application will auto-delete in 30-60 seconds after PR closure"
    echo "Monitor: https://argo.n1-machina.dev/applications/$argocd_app"
    echo ""
    echo "When checking deletion status with 'argocd app get $argocd_app':"
    echo "• PermissionDenied error = app was deleted (ArgoCD 2.6+ security feature)"
    echo "• Application details shown = app still exists"

    echo ""
}

# Main command router
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi

    local command="$1"
    shift

    case "$command" in
        info)
            cmd_info "$@"
            ;;
        delete)
            cmd_delete "$@"
            ;;
        delete-argocd)
            cmd_delete_argocd "$@"
            ;;
        list|status|cleanup-stale|pr-info)
            print_color "$YELLOW" "Command '$command' is not yet implemented"
            exit 1
            ;;
        -h|--help|help)
            show_usage
            exit 0
            ;;
        *)
            print_color "$RED" "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
