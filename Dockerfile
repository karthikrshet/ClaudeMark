# ClaudeMark — Multi-AI Watermark & Provenance Forensics Toolkit
# Container build for ClaudeMark service and CLI
FROM python:3.11-slim

LABEL maintainer="Karthik R Shet <https://github.com/karthikrshet>"
LABEL org.opencontainers.image.source="https://github.com/karthikrshet/ClaudeMark"
LABEL org.opencontainers.image.title="ClaudeMark"
LABEL org.opencontainers.image.description="Multi-AI Watermark & Provenance Forensics Toolkit"

WORKDIR /app

# Install optional system forensic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    exiftool \
    qpdf \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged application user
RUN groupadd --system --gid 1001 cmuser \
    && useradd --system --uid 1001 --gid cmuser --shell /usr/sbin/nologin --home /app cmuser

COPY claudemark /app/claudemark
COPY claudemark.py /app/claudemark.py

# Ensure correct non-root permissions
RUN chown -R cmuser:cmuser /app

USER cmuser

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/health')" || exit 1

ENTRYPOINT ["python3", "claudemark.py"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8765"]
