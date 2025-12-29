#!/usr/bin/env bash
# Push all repos (submodules first, then parent) when synchronized to a common development branch

set -euo pipefail

# Change to repository root
cd "$(dirname "$0")/.."

echo "Checking branch status across all repos..."
echo ""

# Show current branches
for dir in repos/*/; do
    printf "%-20s %s\n" "$(basename "$dir"):" "$(git -C "$dir" branch --show-current)"
done
echo ""

# Push each submodule
echo "Pushing submodules..."
for dir in repos/*/; do
    repo_name=$(basename "$dir")
    echo ""
    echo "=== Pushing $repo_name ==="

    # Check if there are any local commits
    if ! git -C "$dir" log @{u}.. --oneline 2>/dev/null | grep -q .; then
        echo "✅ $repo_name - no commits to push"
        continue
    fi

    # Try to push, handling cases where remote tracking branch doesn't exist
    if git -C "$dir" push 2>&1; then
        echo "✅ $repo_name - pushed successfully"
    else
        # If push failed due to no upstream, try pushing to origin/current-branch
        current_branch=$(git -C "$dir" branch --show-current)
        echo "⚠️  No upstream branch set, pushing to origin/$current_branch"
        git -C "$dir" push origin HEAD
        echo "✅ $repo_name - pushed successfully"
    fi
done

# Push parent repo
echo ""
echo "=== Pushing machina-meta (parent) ==="
if ! git log @{u}.. --oneline 2>/dev/null | grep -q .; then
    echo "✅ machina-meta - no commits to push"
else
    git push
    echo "✅ machina-meta - pushed successfully"
fi

echo ""
echo "✅ All repos pushed successfully!"
