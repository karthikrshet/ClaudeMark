#!/usr/bin/env python3
"""Convenience root runner for ClaudeMark."""

import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from claudemark.cli import main

if __name__ == "__main__":
    sys.exit(main())
