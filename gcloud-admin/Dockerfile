# GCloud Admin Container
# Full-featured administrative container for managing GKE deployments
# Base: Debian Bookworm (stable)

FROM debian:bookworm-slim

LABEL maintainer="NumberOne-AI"
LABEL description="GCP/GKE administrative container with full Kubernetes tooling"

# Docker automatic platform ARGs (provided by BuildKit)
# Docker containers always run Linux, so we only need architecture
ARG TARGETARCH

# Convert ARG to ENV for use in all RUN commands
ENV TARGETARCH=${TARGETARCH}

# Versions - update these as needed
ENV KUBECTL_VERSION=1.31.4
ENV HELM_VERSION=3.16.3
ENV KUSTOMIZE_VERSION=5.5.0
ENV K9S_VERSION=0.32.7
ENV KUBECTX_VERSION=0.9.5
ENV STERN_VERSION=1.31.0
ENV ARGOCD_VERSION=2.13.2
ENV YQ_VERSION=4.44.6

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install base system packages and network debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential utilities
    ca-certificates \
    curl \
    wget \
    gnupg \
    lsb-release \
    apt-transport-https \
    software-properties-common \
    unzip \
    git \
    vim \
    nano \
    less \
    tree \
    htop \
    jq \
    bash-completion \
    openssh-client \
    # Network debugging tools
    dnsutils \
    bind9-dnsutils \
    net-tools \
    iputils-ping \
    iputils-tracepath \
    traceroute \
    mtr-tiny \
    netcat-openbsd \
    tcpdump \
    nmap \
    iperf3 \
    iproute2 \
    telnet \
    whois \
    host \
    socat \
    # TLS/SSL debugging
    openssl \
    # Process debugging
    procps \
    psmisc \
    strace \
    # File transfer
    rsync \
    # Text processing
    gawk \
    sed \
    grep \
    # Python for scripting (minimal)
    python3-minimal \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Platform Architecture Variables
# =============================================================================
# Docker containers always run Linux, so OS is constant.
# Only architecture varies: amd64 (Intel) or arm64 (Apple Silicon/ARM).
# Some packages use x86_64 instead of amd64, so we define ARCH_ALT for those.
#
#   TARGETARCH    - Architecture (amd64, arm64) - from Docker BuildKit
#   ARCH_ALT      - Alternative arch name (x86_64, arm64) - for kubectx/kubens
# =============================================================================

# Create platform variables script for use in all RUN commands
RUN echo '#!/bin/bash' > /usr/local/bin/platform-vars.sh && \
    echo "export TARGETARCH=${TARGETARCH}" >> /usr/local/bin/platform-vars.sh && \
    echo "export ARCH_ALT=\$(echo \${TARGETARCH} | sed 's/amd64/x86_64/')" >> /usr/local/bin/platform-vars.sh && \
    chmod +x /usr/local/bin/platform-vars.sh && \
    /usr/local/bin/platform-vars.sh && \
    cat /usr/local/bin/platform-vars.sh

# Install Google Cloud SDK with gke-gcloud-auth-plugin
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y --no-install-recommends \
    google-cloud-cli \
    google-cloud-cli-gke-gcloud-auth-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Install Helm
RUN curl -fsSL "https://get.helm.sh/helm-v${HELM_VERSION}-linux-${TARGETARCH}.tar.gz" | \
    tar -xzf - --strip-components=1 -C /usr/local/bin linux-${TARGETARCH}/helm

# Install Kustomize
RUN curl -fsSL "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv${KUSTOMIZE_VERSION}/kustomize_v${KUSTOMIZE_VERSION}_linux_${TARGETARCH}.tar.gz" | \
    tar -xzf - -C /usr/local/bin

# Install k9s (Kubernetes TUI)
RUN curl -fsSL "https://github.com/derailed/k9s/releases/download/v${K9S_VERSION}/k9s_Linux_${TARGETARCH}.tar.gz" | \
    tar -xzf - -C /usr/local/bin k9s

# Install kubectx and kubens
RUN . /usr/local/bin/platform-vars.sh && \
    curl -fsSL "https://github.com/ahmetb/kubectx/releases/download/v${KUBECTX_VERSION}/kubectx_v${KUBECTX_VERSION}_linux_${ARCH_ALT}.tar.gz" | \
    tar -xzf - -C /usr/local/bin kubectx && \
    curl -fsSL "https://github.com/ahmetb/kubectx/releases/download/v${KUBECTX_VERSION}/kubens_v${KUBECTX_VERSION}_linux_${ARCH_ALT}.tar.gz" | \
    tar -xzf - -C /usr/local/bin kubens

# Install stern (multi-pod log tailing)
RUN curl -fsSL "https://github.com/stern/stern/releases/download/v${STERN_VERSION}/stern_${STERN_VERSION}_linux_${TARGETARCH}.tar.gz" | \
    tar -xzf - -C /usr/local/bin stern

# Install ArgoCD CLI
RUN curl -fsSL "https://github.com/argoproj/argo-cd/releases/download/v${ARGOCD_VERSION}/argocd-linux-${TARGETARCH}" -o /usr/local/bin/argocd && \
    chmod +x /usr/local/bin/argocd

# Install yq (YAML processor)
RUN curl -fsSL "https://github.com/mikefarah/yq/releases/download/v${YQ_VERSION}/yq_linux_${TARGETARCH}" -o /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# Install Docker CLI (for building images, not running containers)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=${TARGETARCH} signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bookworm stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    docker-buildx-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install additional Kubernetes tools via krew (kubectl plugin manager)
RUN set -x && \
    KREW="krew-linux_${TARGETARCH}" && \
    curl -fsSL "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" | \
    tar -xzf - -C /tmp && \
    /tmp/${KREW} install krew && \
    rm -rf /tmp/krew-*

# Add krew to PATH
ENV PATH="${PATH}:/root/.krew/bin"

# Install useful kubectl plugins via krew
# Note: Some plugins may not be available for all architectures
RUN kubectl krew install \
    ctx \
    ns \
    neat \
    tree \
    images \
    get-all \
    resource-capacity \
    whoami \
    node-shell \
    view-secret || true && \
    kubectl krew install access-matrix || echo "access-matrix not available for this platform"

# Setup bash completion for all tools
RUN echo 'source /usr/share/bash-completion/bash_completion' >> /root/.bashrc && \
    echo 'source <(kubectl completion bash)' >> /root/.bashrc && \
    echo 'source <(helm completion bash)' >> /root/.bashrc && \
    echo 'source <(k9s completion bash)' >> /root/.bashrc && \
    echo 'source <(stern --completion bash)' >> /root/.bashrc && \
    echo 'source <(argocd completion bash)' >> /root/.bashrc && \
    echo 'alias k=kubectl' >> /root/.bashrc && \
    echo 'complete -F __start_kubectl k' >> /root/.bashrc && \
    echo 'alias kx=kubectx' >> /root/.bashrc && \
    echo 'alias kn=kubens' >> /root/.bashrc

# Create workspace directory
WORKDIR /workspace

# Add a helpful MOTD
RUN echo '#!/bin/bash' > /etc/profile.d/motd.sh && \
    echo 'echo ""' >> /etc/profile.d/motd.sh && \
    echo 'echo "╔══════════════════════════════════════════════════════════════════╗"' >> /etc/profile.d/motd.sh && \
    echo 'echo "║  GCloud Admin Container - NumberOne-AI                           ║"' >> /etc/profile.d/motd.sh && \
    echo 'echo "╠══════════════════════════════════════════════════════════════════╣"' >> /etc/profile.d/motd.sh && \
    echo 'echo "║  GCP Tools:     gcloud, gsutil, bq                               ║"' >> /etc/profile.d/motd.sh && \
    echo 'echo "║  K8s Tools:     kubectl, helm, kustomize, k9s, stern, argocd     ║"' >> /etc/profile.d/motd.sh && \
    echo 'echo "║  Navigation:    kubectx (kx), kubens (kn)                        ║"' >> /etc/profile.d/motd.sh && \
    echo 'echo "║  Network:       dig, nslookup, traceroute, mtr, tcpdump, nmap    ║"' >> /etc/profile.d/motd.sh && \
    echo 'echo "║  Aliases:       k=kubectl, kx=kubectx, kn=kubens                 ║"' >> /etc/profile.d/motd.sh && \
    echo 'echo "╚══════════════════════════════════════════════════════════════════╝"' >> /etc/profile.d/motd.sh && \
    echo 'echo ""' >> /etc/profile.d/motd.sh && \
    chmod +x /etc/profile.d/motd.sh

# Default command
CMD ["/bin/bash", "-l"]
