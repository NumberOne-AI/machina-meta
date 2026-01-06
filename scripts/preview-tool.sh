#!/usr/bin/env bash
# preview-tool.sh - Utility for managing preview environments, PRs, and deployments

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
  list                   List all active preview environments (TODO)
  status <id>            Check deployment status of preview environment (TODO)
  cleanup-stale          Find and cleanup stale preview environments (TODO)
  pr-info <repo> <num>   Show PR information for a specific repo (TODO)

Examples:
  $(basename "$0") info pr-70
  $(basename "$0") info my-feature
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

    local argocd_app="preview-$preview_id"
    local argocd_url="https://argo.n1-machina.dev/applications/$argocd_app"

    print_kv "Application Name" "$argocd_app"
    print_kv "ArgoCD URL" "$argocd_url"

    # Try to get ArgoCD status if CLI is available
    if command -v argocd &>/dev/null; then
        local app_status=$(argocd app get "$argocd_app" -o json 2>/dev/null || echo "")

        if [[ -n "$app_status" ]]; then
            local sync_status=$(echo "$app_status" | jq -r '.status.sync.status')
            local health_status=$(echo "$app_status" | jq -r '.status.health.status')

            print_kv "Sync Status" "$sync_status"
            print_kv "Health Status" "$health_status"
        else
            print_kv "Status" "$CIRCLE Cannot retrieve (app may not exist or argocd not configured)"
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
