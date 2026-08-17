"""Centralized configuration limits and constants for ClaudeMark.

Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
"""

from __future__ import annotations

# Text length limit for API and CLI operations (10 MB)
MAX_TEXT_LENGTH: int = 10 * 1024 * 1024

# Maximum payload size in bytes (100 MB)
MAX_INPUT_BYTES: int = 100 * 1024 * 1024

# Maximum files audited in a single run
MAX_AUDIT_FILES: int = 10_000

# Maximum decompression expansion ratio for defensive security scanner
MAX_ARCHIVE_EXPANSION_RATIO: int = 100
