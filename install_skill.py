#!/usr/bin/env python3
"""Universal cross-platform installer for ClaudeMark agent skill into Antigravity, Cursor, Claude Desktop, Grok, and Codex."""

import argparse
import filecmp
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


def _trees_match(source: Path, destination: Path) -> bool:
    """Return whether two skill trees have the same relative files and bytes."""
    if not source.is_dir() or not destination.is_dir():
        return False
    source_files = {p.relative_to(source) for p in source.rglob("*") if p.is_file()}
    destination_files = {p.relative_to(destination) for p in destination.rglob("*") if p.is_file()}
    if source_files != destination_files:
        return False
    return all(filecmp.cmp(source / rel, destination / rel, shallow=False) for rel in source_files)


def install_single_target(skill_src: Path, dest_dir: Path, force: bool = False, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"[Dry Run] Would stage skill from {skill_src.name} to {dest_dir}")
        return True

    if dest_dir.exists():
        if skill_src.resolve() == dest_dir.resolve():
            print(f"Skill source and destination are the same: {dest_dir} (skipping)")
            return True
        if _trees_match(skill_src, dest_dir):
            print(f"Skill already up to date at: {dest_dir} (skipping)")
            return True
        if not force:
            print(f"Skill already present at: {dest_dir} (skipping, use --force to overwrite)")
            return True
        shutil.rmtree(dest_dir)

    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_src, dest_dir)
    print(f"Successfully installed ClaudeMark skill to: {dest_dir}")
    return True


def install_skill(force: bool = False, target_env: str = "all", scope: str = "all", dry_run: bool = False) -> int:
    repo_root = Path(__file__).resolve().parent
    skill_src = repo_root / "skills" / "ai-forensics"

    if not skill_src.is_dir():
        print(f"Error: Skill source directory not found: {skill_src}", file=sys.stderr)
        return 1

    targets = list(TARGET_MAP.keys()) if target_env == "all" else [target_env]
    roots = []
    if scope in ("workspace", "all"):
        roots.append(repo_root)
    if scope in ("user", "all"):
        roots.append(Path.home())

    success = True
    for root in roots:
        for t in targets:
            if t in TARGET_MAP:
                dest = root / TARGET_MAP[t]
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
    parser.add_argument(
        "--scope",
        "-s",
        choices=["all", "workspace", "user"],
        default="all",
        help="Installation scope: workspace (project local), user (~/), or all (default: all)",
    )
    args = parser.parse_args()
    sys.exit(install_skill(force=args.force, target_env=args.target, scope=args.scope, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
