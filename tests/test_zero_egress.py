"""Zero-egress verification tests proving core operations make 0 outbound network requests."""

import socket
import pytest
from claudemark import analyze_text, compute_forensic_diff, normalize_text
from claudemark.core.unicode_forensics import analyze_unicode_forensics, visualize_unicode_markers
from claudemark.detectors.registry import detector_registry
from claudemark.rewrite.paraphrase import disrupt_watermark
from claudemark.security.scanner import check_path_security, scan_file_security


class BlockedNetworkCall(Exception):
    pass


@pytest.fixture(autouse=True)
def block_outbound_sockets(monkeypatch):
    """Intercept and block any attempt to create outbound network sockets."""
    orig_connect = socket.socket.connect

    def guarded_connect(self, *args, **kwargs):
        raise BlockedNetworkCall(f"Outbound network call blocked during offline execution: {args}")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)


def test_zero_egress_text_analysis():
    # Analyze text with all detectors - must execute 100% locally
    for det_name in detector_registry.list_detectors():
        res = analyze_text("In conclusion, comprehensive frameworks are essential.", detector_name=det_name)
        assert res["watermark_result"].signal_score >= 0.0


def test_zero_egress_unicode_forensics():
    rep = analyze_unicode_forensics("Secret\u200bData\u00a0Hidden")
    assert rep.zero_width_count == 1
    vis = visualize_unicode_markers("Secret\u200bData")
    assert "<ZWSP>" in vis


def test_zero_egress_disrupt_watermark():
    res = disrupt_watermark("Furthermore, it is crucial to implement this.")
    assert res.success is True
    assert res.rewritten_text != ""


def test_zero_egress_security_scan(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Clean file content", encoding="utf-8")
    rep = scan_file_security(f)
    assert rep.is_safe is True
