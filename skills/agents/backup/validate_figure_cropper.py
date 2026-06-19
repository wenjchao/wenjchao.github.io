#!/usr/bin/env python3
"""Validate figure cropper output (figures.json v4 + crops/ + previews/).

Mechanical checks only: JSON structure, crop coordinates, file existence,
verification consistency. Does not judge visual quality.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCHEMA = "figure_extraction.v4"
STATUS_VALUES = {"complete", "incomplete"}
VERIFICATION_VALUES = {"pass", "fail"}
FIGURE_TYPES = {"main", "extended", "supplementary", "other"}
VERIFICATION_KEYS = {
    "final_crop_checked",
    "boundary_checked",
    "figure_content_complete",
    "caption_excluded",
    "page_chrome_excluded",
    "no_adjacent_content",
    "result",
}
FORBIDDEN_DERIVED_KEYS = {"pages", "image_files", "crop_count"}


def add(errors: list[str], path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def read_png_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as fh:
            header = fh.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
            return None
        width, height = struct.unpack(">II", header[16:24])
        return int(width), int(height)
    except OSError:
        return None


def infer_paper_dir(artifact_root: Path) -> Path | None:
    parts = artifact_root.resolve().parts
    for idx in range(len(parts)):
        if parts[idx] == "figures":
            return Path(*parts[:idx]) if idx > 0 else Path(parts[0])
    return None


def check_crop_file(crop_id: str, artifact_root: Path, path: str, errors: list[str]) -> None:
    """Check that the crop image exists."""
    crop_path = artifact_root / "crops" / f"{crop_id}.png"
    if not crop_path.exists():
        add(errors, path, f"crop image missing: crops/{crop_id}.png")


def check_preview_file(crop_id: str, suffix: str, artifact_root: Path, path: str, errors: list[str]) -> None:
    """Check that a single preview file exists."""
    preview_path = artifact_root / "previews" / f"{crop_id}{suffix}"
    if not preview_path.exists():
        add(errors, path, f"preview missing: previews/{crop_id}{suffix}")


def check_previews(crop_id: str, artifact_root: Path, path: str, errors: list[str]) -> None:
    """Check that required preview files exist for a crop_id."""
    check_preview_file(crop_id, "_preview.png", artifact_root, path, errors)
    check_preview_file(crop_id, "_boundary_preview.png", artifact_root, path, errors)
    check_preview_file(crop_id, "_top_seg1_preview.png", artifact_root, path, errors)
    check_preview_file(crop_id, "_left_seg1_preview.png", artifact_root, path, errors)
    check_preview_file(crop_id, "_right_seg1_preview.png", artifact_root, path, errors)

    # Bottom band: at least one segment
    bottom_pattern = list((artifact_root / "previews").glob(f"{crop_id}_bottom_seg*_preview.png"))
    if not bottom_pattern:
        add(errors, path, f"no bottom band previews found for {crop_id}")

    # Bottom microzoom: at least one segment
    micro_pattern = list((artifact_root / "previews").glob(f"{crop_id}_micro_bottom_seg*_preview.png"))
    if not micro_pattern:
        add(errors, path, f"no bottom microzoom previews found for {crop_id}")


def check_crop_px(crop_px: Any, page: Any, paper_dir: Path | None, path: str, errors: list[str]) -> None:
    """Validate crop_px coordinates."""
    if not isinstance(crop_px, list) or len(crop_px) != 4 or not all(isinstance(v, int) for v in crop_px):
        add(errors, path, "must be [x1, y1, x2, y2] with four integers")
        return

    x1, y1, x2, y2 = crop_px
    if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
        add(errors, path, "must satisfy 0 <= x1 < x2 and 0 <= y1 < y2")
        return

    if isinstance(page, int) and paper_dir is not None:
        page_image = paper_dir / "shared" / "pages" / f"page_{page}.png"
        if page_image.exists():
            size = read_png_size(page_image)
            if size is not None:
                w, h = size
                if x2 > w or y2 > h:
                    add(errors, path, f"exceeds page bounds {w}x{h}")


def check_crop_dimensions(crop_id: str, crop_px: list[int], artifact_root: Path, path: str, errors: list[str]) -> None:
    """Check crop image dimensions match crop_px."""
    crop_path = artifact_root / "crops" / f"{crop_id}.png"
    if not crop_path.exists():
        return
    size = read_png_size(crop_path)
    if size is None:
        return
    expected_w = crop_px[2] - crop_px[0]
    expected_h = crop_px[3] - crop_px[1]
    if size != (expected_w, expected_h):
        add(errors, path, f"crop is {size[0]}x{size[1]} but crop_px expects {expected_w}x{expected_h}")


def validate(artifact_root: Path, paper_dir: Path | None) -> list[str]:
    errors: list[str] = []
    artifact_root = artifact_root.resolve()

    if paper_dir is None:
        paper_dir = infer_paper_dir(artifact_root)

    # --- Load figures.json ---
    figures_path = artifact_root / "figures.json"
    if not figures_path.exists():
        add(errors, "$", "figures.json not found")
        return errors

    try:
        with figures_path.open("r", encoding="utf-8") as fh:
            root = json.load(fh)
    except Exception as exc:
        add(errors, "$", f"JSON parse error: {exc}")
        return errors

    if not isinstance(root, dict):
        add(errors, "$", "root must be an object")
        return errors

    # --- Top-level fields ---
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.schema_version", f'must be "{SCHEMA}"')

    status = root.get("status")
    if status not in STATUS_VALUES:
        add(errors, "$.status", 'must be "complete" or "incomplete"')

    if not isinstance(root.get("excluded"), list):
        add(errors, "$.excluded", "must be an array")

    figures = root.get("figures")
    if not isinstance(figures, list):
        add(errors, "$.figures", "must be an array")
        return errors

    # --- Validate each figure ---
    seen_figure_ids: set[str] = set()
    verification_results: list[str] = []

    for idx, fig in enumerate(figures):
        fp = f"$.figures[{idx}]"

        if not isinstance(fig, dict):
            add(errors, fp, "must be an object")
            continue

        # Identity
        for key in ("figure_id", "figure_label"):
            v = fig.get(key)
            if not isinstance(v, str) or not v.strip():
                add(errors, f"{fp}.{key}", "must be a non-empty string")

        figure_id = fig.get("figure_id", "")
        if figure_id in seen_figure_ids:
            add(errors, f"{fp}.figure_id", "must be unique")
        seen_figure_ids.add(figure_id)

        ft = fig.get("figure_type")
        if ft not in FIGURE_TYPES:
            add(errors, f"{fp}.figure_type", "must be main, extended, supplementary, or other")

        # No derived fields
        for key in FORBIDDEN_DERIVED_KEYS:
            if key in fig:
                add(errors, f"{fp}.{key}", "derived from crop_units; must be omitted")

        # crop_units
        units = fig.get("crop_units")
        if not isinstance(units, list) or len(units) == 0:
            add(errors, f"{fp}.crop_units", "must be a non-empty array")
            continue

        seen_crop_ids: set[str] = set()
        for ui, unit in enumerate(units):
            up = f"{fp}.crop_units[{ui}]"

            if not isinstance(unit, dict):
                add(errors, up, "must be an object")
                continue

            # crop_id
            crop_id = unit.get("crop_id", "")
            if not isinstance(crop_id, str) or not crop_id.strip():
                add(errors, f"{up}.crop_id", "must be a non-empty string")
            if crop_id in seen_crop_ids:
                add(errors, f"{up}.crop_id", "must be unique within figure")
            seen_crop_ids.add(crop_id)

            # page
            page = unit.get("page")
            if not isinstance(page, int):
                add(errors, f"{up}.page", "must be an integer")

            # crop_px
            crop_px = unit.get("crop_px")
            check_crop_px(crop_px, page, paper_dir, f"{up}.crop_px", errors)

            # role
            role = unit.get("role")
            if not isinstance(role, str) or not role.strip():
                add(errors, f"{up}.role", "must be a non-empty string")

            # Files exist
            if isinstance(crop_id, str) and crop_id.strip():
                check_crop_file(crop_id, artifact_root, up, errors)
                check_previews(crop_id, artifact_root, up, errors)

                # Dimensions match
                if isinstance(crop_px, list) and len(crop_px) == 4 and all(isinstance(v, int) for v in crop_px):
                    check_crop_dimensions(crop_id, crop_px, artifact_root, up, errors)

        # Verification
        verif = fig.get("verification")
        if not isinstance(verif, dict):
            add(errors, f"{fp}.verification", "must be an object")
            continue

        for key in VERIFICATION_KEYS:
            v = verif.get(key)
            if v not in VERIFICATION_VALUES:
                add(errors, f"{fp}.verification.{key}", 'must be "pass" or "fail"')

        result = verif.get("result")
        if result in VERIFICATION_VALUES:
            verification_results.append(result)

        # If result is pass, all sub-checks must be pass
        if result == "pass":
            for key in VERIFICATION_KEYS:
                if key == "result":
                    continue
                if verif.get(key) != "pass":
                    add(errors, f"{fp}.verification.{key}", 'must be "pass" when result is "pass"')

    # --- Status consistency ---
    if status in STATUS_VALUES and verification_results:
        expected = "incomplete" if "fail" in verification_results else "complete"
        if status != expected:
            add(errors, "$.status", f'should be "{expected}" based on verification results')

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate figure cropper output (figures.json v4).")
    parser.add_argument("artifact_root", help="Path to cropper output directory")
    parser.add_argument("--paper-dir", help="Paper directory for page bound checks")
    args = parser.parse_args()

    artifact_root = Path(args.artifact_root)
    paper_dir = Path(args.paper_dir).resolve() if args.paper_dir else None
    errors = validate(artifact_root, paper_dir)
    status = "fail" if errors else "pass"
    print(json.dumps({"status": status, "errors": errors}, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
