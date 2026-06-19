#!/usr/bin/env python3
"""Promote files from a source directory to canonical.

Supports two modes:
  --mode extraction  : promote workers → canonical (equations.json, crops/, previews/, rendered_latex/)
  --mode review      : promote visual_review.json → canonical/visual_review.json

Usage:
    python promote_to_canonical.py \
        --source <workers_dir> \
        --canonical <canonical_dir> \
        --mode extraction

    python promote_to_canonical.py \
        --source <review_dir> \
        --canonical <canonical_dir> \
        --mode review
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

EXTRACTION_FILES = [
    "equations.json",
]
EXTRACTION_DIRS = [
    "crops",
    "previews",
    "rendered_latex",
]


def promote_extraction(source: Path, canonical: Path) -> list[str]:
    copied = []
    for fname in EXTRACTION_FILES:
        src = source / fname
        dst = canonical / fname
        if not src.exists():
            print(f"WARNING: {src} does not exist, skipping", file=sys.stderr)
            continue
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(canonical)))

    for dname in EXTRACTION_DIRS:
        src_dir = source / dname
        dst_dir = canonical / dname
        if not src_dir.exists():
            print(f"WARNING: {src_dir} does not exist, skipping", file=sys.stderr)
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        for f in src_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, dst_dir / f.name)
                copied.append(f"{dname}/{f.name}")

    return copied


def promote_review(source: Path, canonical: Path) -> list[str]:
    src = source / "visual_review.json"
    dst = canonical / "visual_review.json"

    if not src.exists():
        print(f"ERROR: {src} does not exist", file=sys.stderr)
        return []

    shutil.copy2(src, dst)
    return ["visual_review.json"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote files to canonical")
    parser.add_argument("--source", required=True, help="Source directory")
    parser.add_argument("--canonical", required=True, help="Canonical directory")
    parser.add_argument("--mode", required=True, choices=["extraction", "review"])
    args = parser.parse_args()

    source = Path(args.source)
    canonical = Path(args.canonical)

    if not source.exists():
        print(f"ERROR: source {source} does not exist", file=sys.stderr)
        return 1

    canonical.mkdir(parents=True, exist_ok=True)

    if args.mode == "extraction":
        copied = promote_extraction(source, canonical)
    else:
        copied = promote_review(source, canonical)

    print(f"Promoted {len(copied)} items to {canonical}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
