# Spire.Doc POC Container
# Provides working environment for DOCX → Image conversion using Spire.Doc
#
# Build: docker build -t spire-doc-poc scripts/spire-doc-poc/
# Run:   docker run --rm -v $(pwd):/workspace -e GOOGLE_API_KEY spire-doc-poc <docx-file>

FROM python:3.13-slim-bookworm

# Install system dependencies:
# - curl: Required for uv installation
# - libicu72: ICU libraries for .NET globalization (required by Spire.Doc)
# - fonts-liberation: Standard fonts for document rendering
# - fontconfig: Font configuration library
# - libreoffice-writer: Fallback conversion method
# - poppler-utils: PDF to image conversion (pdftoppm)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libicu72 \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    libreoffice-writer \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f -v

# Install uv system-wide (accessible to all users)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
ENV PATH="/usr/local/bin:$PATH"
# Use /tmp for caches to allow non-root users
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV HOME=/tmp

# Set environment variables for .NET/Spire.Doc
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /workspace

# Copy and set up the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
