.PHONY: test lint run serve build help

help:
	@echo "ClaudeMark — Multi-AI Watermark & Provenance Forensics Toolkit"
	@echo "  make test      Run test suite"
	@echo "  make serve     Start local Web UI & REST API server"
	@echo "  make build     Build container image"

test:
	python -m pytest tests/

serve:
	python claudemark.py serve --port 8765

build:
	docker build -t ghcr.io/karthikrshet/claudemark:latest .
