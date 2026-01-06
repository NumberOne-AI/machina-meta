#!/usr/bin/env bash
# Export GKE credentials from gcloud-admin Docker volume to host kubectl config
#
# Usage: ./export-kube-config.sh <context-name>
#   context-name: The GKE context to make current after export
#
# Example:
#   ./export-kube-config.sh gke_n1-machina1_us-central1_tusdi-nonprod-cluster

set -euo pipefail

CONTEXT_NAME="${1:-}"

if [[ -z "$CONTEXT_NAME" ]]; then
    echo "Error: Context name is required"
    echo "Usage: $0 <context-name>"
    exit 1
fi

VOLUME_NAME="gcloud-admin_kube-config"
TEMP_CONFIG="/tmp/gcloud-admin-kube-config.$$"
MERGED_CONFIG="/tmp/merged-kube-config.$$"
HOST_CONFIG="${HOME}/.kube/config"

# Cleanup on exit
cleanup() {
    rm -f "$TEMP_CONFIG" "$MERGED_CONFIG"
}
trap cleanup EXIT

echo "=== Exporting GKE credentials from container to host ==="

# Check if volume exists
if ! docker volume inspect "$VOLUME_NAME" &>/dev/null; then
    echo "Error: Docker volume '$VOLUME_NAME' not found"
    echo "Run 'just get-creds-nonprod' or 'just get-creds-prod' first"
    exit 1
fi

# Extract config from Docker volume
echo "Extracting config from Docker volume..."
docker run --rm -v "${VOLUME_NAME}:/data" alpine cat /data/config > "$TEMP_CONFIG"

# Ensure host config directory exists
mkdir -p ~/.kube

# Merge into host config
echo "Merging with host kubectl config..."
if [[ -f "$HOST_CONFIG" ]]; then
    KUBECONFIG="${HOST_CONFIG}:${TEMP_CONFIG}" kubectl config view --flatten > "$MERGED_CONFIG"
else
    # No existing config, just use the exported one
    cp "$TEMP_CONFIG" "$MERGED_CONFIG"
fi

# Replace host config
cp "$MERGED_CONFIG" "$HOST_CONFIG"
chmod 600 "$HOST_CONFIG"

# Switch to specified context
echo "Switching to context: $CONTEXT_NAME"
if kubectl config use-context "$CONTEXT_NAME" &>/dev/null; then
    echo "=== Done! Context is now active on host ==="
    kubectl config current-context
else
    echo "Warning: Context '$CONTEXT_NAME' not found in config"
    echo "Available contexts:"
    kubectl config get-contexts -o name
    exit 1
fi
