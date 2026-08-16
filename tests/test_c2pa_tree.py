"""Tests for C2PA provenance hierarchy extraction and provenance tree rendering."""

import pytest
from claudemark.provenance.c2pa import inspect_c2pa_bytes


def test_c2pa_absent():
    data = b"clean raw jpeg image bytes without any jumbf boxes"
    rep = inspect_c2pa_bytes(data, asset_name="clean.jpg")
    assert rep["has_c2pa"] is False
    assert rep["status"] == "ABSENT"
    assert "No C2PA manifest found" in rep["provenance_tree"]["tree_text"]


def test_c2pa_present_with_claims():
    fake_jumbf = (
        b"header"
        b"\x63\x32\x70\x61"  # "c2pa"
        b'"claim_generator": "DALL-E 3 / OpenAI"'
        b'"softwareAgent": "ChatGPT Forensics Adapter"'
        b'"action": "c2pa.created"'
        b'"action": "c2pa.edited"'
        b"c2pa.assertions"
        b"c2pa.signature"
    )
    rep = inspect_c2pa_bytes(fake_jumbf, asset_name="ai_sample.png")
    assert rep["has_c2pa"] is True
    assert rep["status"] == "UNVERIFIED"
    assert rep["claim_generator"] == "DALL-E 3 / OpenAI"
    assert rep["software_agent"] == "ChatGPT Forensics Adapter"
    assert "c2pa.created" in rep["actions"]
    assert "c2pa.assertions" in rep["assertions"]
    assert "Claim Generator: DALL-E 3 / OpenAI" in rep["provenance_tree"]["tree_text"]
