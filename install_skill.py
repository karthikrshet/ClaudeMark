#!/usr/bin/env python3
"""Cross-platform installer for ClaudeMark agent skill into Cursor, Grok, or Claude Desktop."""

import argparse
import os
import shutil
import sys
from pathlib import Path


def install_skill(force: bool = False, target_env: str = "cursor", dry_run: bool = False) -> int:
    repo_root = Path(__file__).resolve().parent
    skill_src = repo_root / "skills" / "ai-forensics"

    if not skill_src.is_dir():
        print(f"Error: Skill source directory not found: {skill_src}", file=sys.stderr)
        return 1

    home = Path.home()
    if target_env == "cursor":
        dest_dir = home / ".cursor" / "skills" / "ai-forensics"
    elif target_env == "grok":
        dest_dir = home / ".grok" / "skills" / "ai-forensics"
    else:
        dest_dir = home / ".claude" / "skills" / "ai-forensics"

    if dry_run:
        print(f"[Dry Run] Would stage skill from {skill_src} to {dest_dir}")
        return 0

    if dest_dir.exists():
        if not force:
            print(f"Skill already installed at: {dest_dir}")
            print("Use --force to overwrite existing installation.")
            return 0
        shutil.rmtree(dest_dir)

    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_src, dest_dir)
    print(f"Successfully installed ClaudeMark skill to: {dest_dir}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Install ClaudeMark agent skill")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing installation")
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation without writing files")
    parser.add_argument("--target", "-t", choices=["cursor", "grok", "claude"], default="cursor", help="Target agent host")
    args = parser.parse_args()
    sys.exit(install_skill(force=args.force, target_env=args.target, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
