# ClaudeMark — Multi-AI Watermark & Provenance Forensics Toolkit
# Container build for ClaudeMark service and CLI
FROM python:3.14-slim

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
    && rm -rf /var/lib/apt/lists/*

COPY claudemark /app/claudemark
COPY claudemark.py /app/claudemark.py

EXPOSE 8765

ENTRYPOINT ["python3", "claudemark.py"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8765"]
