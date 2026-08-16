"""Defensive security scanning and hardening module for ClaudeMark."""

from .scanner import SecurityScanReport, check_path_security, scan_file_security

__all__ = [
    "SecurityScanReport",
    "scan_file_security",
    "check_path_security",
]
