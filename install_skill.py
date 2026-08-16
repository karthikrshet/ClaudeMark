#!/usr/bin/env python3
"""Universal cross-platform installer for ClaudeMark agent skill into Antigravity, Cursor, Claude Desktop, Grok, and Codex."""

import argparse
import os
import shutil
import sys
from pathlib import Path

TARGET_MAP = {
    "cursor": ".cursor/skills/ai-forensics",
    "antigravity": ".agents/skills/ai-forensics",
    "claude": ".claude/skills/ai-forensics",
    "grok": ".grok/skills/ai-forensics",
    "codex": ".codex/skills/ai-forensics",
}


def install_single_target(skill_src: Path, dest_dir: Path, force: bool = False, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"[Dry Run] Would stage skill from {skill_src.name} to {dest_dir}")
        return True

    if dest_dir.exists():
        if not force:
            print(f"Skill already installed at: {dest_dir} (skipping, use --force to overwrite)")
            return True
        shutil.rmtree(dest_dir)

    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_src, dest_dir)
    print(f"Successfully installed ClaudeMark skill to: {dest_dir}")
    return True


def install_skill(force: bool = False, target_env: str = "all", dry_run: bool = False) -> int:
    repo_root = Path(__file__).resolve().parent
    skill_src = repo_root / "skills" / "ai-forensics"

    if not skill_src.is_dir():
        print(f"Error: Skill source directory not found: {skill_src}", file=sys.stderr)
        return 1

    home = Path.home()
    targets = list(TARGET_MAP.keys()) if target_env == "all" else [target_env]

    success = True
    for t in targets:
        if t in TARGET_MAP:
            dest = home / TARGET_MAP[t]
            if not install_single_target(skill_src, dest, force=force, dry_run=dry_run):
                success = False

    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(description="Universal ClaudeMark agent skill installer")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing installations")
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation without writing files")
    parser.add_argument(
        "--target",
        "-t",
        choices=["all", "antigravity", "cursor", "claude", "grok", "codex"],
        default="all",
        help="Target agent host environment (default: all)",
    )
    args = parser.parse_args()
    sys.exit(install_skill(force=args.force, target_env=args.target, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
