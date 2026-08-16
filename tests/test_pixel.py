"""Tests for pixel-domain watermark adapters, registries, and hash evaluations."""

import tempfile
from pathlib import Path
import pytest
from claudemark.pixel.base import PixelAnalysisReport, PixelPurificationResult
from claudemark.pixel.evaluation import compare_image_hashes, compute_pixel_hashes
from claudemark.pixel.registry import pixel_registry


def test_pixel_registry_listing():
    backends = pixel_registry.list_backends()
    assert "synthid-image" in backends
    assert "ctrlregen" in backends
    assert "treering" in backends
    assert len(backends) >= 5


def test_pixel_adapter_inspection(tmp_path):
    dummy_img = tmp_path / "test.png"
    dummy_img.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
    
    synthid_be = pixel_registry.get("synthid-image")
    rep = synthid_be.inspect(dummy_img)
    assert isinstance(rep, PixelAnalysisReport)
    assert rep.backend_name == "synthid-image"
    assert rep.available is False  # Explicit honest reporting when heavy ML weights are not present


def test_image_hashes(tmp_path):
    img1 = tmp_path / "img1.bin"
    img2 = tmp_path / "img2.bin"
    img1.write_bytes(b"image_bytes_version_1")
    img2.write_bytes(b"image_bytes_version_2")

    hashes1 = compute_pixel_hashes(img1)
    assert "md5" in hashes1
    assert "sha256" in hashes1

    comp = compare_image_hashes(img1, img2)
    assert comp["identical_bytes"] is False
