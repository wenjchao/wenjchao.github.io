#!/usr/bin/env python3
"""Merge repair output into canonical by executing repair_report.json instructions.

Reads file_copies[] and manifest_patches[] from the repair report, copies files
from the repair directory to canonical, and patches the canonical manifests.

Uses a two-phase approach: validate everything first, then execute. If any
validation fails, canonical is not touched.

Usage:
    python merge_repair.py \
        <repair_report_json> \
        --repair-root <repair_artifact_root> \
        --canonical <canonical_dir>

Exit codes:
    0  success
    1  merge failed (old_value mismatch, missing source file, disallowed target, etc.)
    2  input error or repair status is incomplete
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

ALLOWED_TARGET_FILES = {"tables.json"}


# ---------------------------------------------------------------------------
# Validation (read-only — does not modify canonical)
# ---------------------------------------------------------------------------

def validate_file_copies(
    copies: list[dict],
    repair_root: Path,
) -> list[str]:
    errors = []
    for entry in copies:
        src = repair_root / entry.get("repair_output", "")
        if not src.exists():
            errors.append(f"source missing: {src}")
    return errors


def validate_manifest_patches(
    patches: list[dict],
    canonical: Path,
) -> list[str]:
    errors = []

    by_file: dict[str, list[dict]] = {}
    for patch in patches:
        target_file = patch.get("target_file", "")
        if target_file not in ALLOWED_TARGET_FILES:
            errors.append(f"disallowed target_file: {target_file} "
                          f"(allowed: {', '.join(sorted(ALLOWED_TARGET_FILES))})")
            continue
        by_file.setdefault(target_file, []).append(patch)

    for target_file, file_patches in by_file.items():
        manifest_path = canonical / target_file
        if not manifest_path.exists():
            errors.append(f"manifest not found: {manifest_path}")
            continue

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        trial = copy.deepcopy(data)
        for patch in file_patches:
            err = apply_manifest_patch(trial, patch)
            if err:
                errors.append(f"{target_file}: {err}")

    return errors


# ---------------------------------------------------------------------------
# Execution (modifies canonical — only called after validation passes)
# ---------------------------------------------------------------------------

def execute_file_copies(
    copies: list[dict],
    repair_root: Path,
    canonical: Path,
) -> int:
    copied = 0
    for entry in copies:
        src = repair_root / entry.get("repair_output", "")
        dst = canonical / entry.get("canonical_target", "")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    return copied


def execute_manifest_patches(
    patches: list[dict],
    canonical: Path,
) -> int:
    patched = 0

    by_file: dict[str, list[dict]] = {}
    for patch in patches:
        target_file = patch.get("target_file", "")
        by_file.setdefault(target_file, []).append(patch)

    for target_file, file_patches in by_file.items():
        manifest_path = canonical / target_file

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for patch in file_patches:
            apply_manifest_patch(data, patch)

        patched += len(file_patches)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return patched


# ---------------------------------------------------------------------------
# Patch application (shared by validate and execute)
# ---------------------------------------------------------------------------

def _parse_selector(selector) -> dict:
    """Parse a selector string like 'tables[table_id=X].crop_units[crop_id=Y]'
    into a dict with table_id and crop_id keys."""
    if isinstance(selector, dict):
        return selector
    import re
    result = {}
    m = re.search(r'table_id=([^\]\.\s]+)', str(selector))
    if m:
        result["table_id"] = m.group(1)
    m = re.search(r'crop_id=([^\]\.\s]+)', str(selector))
    if m:
        result["crop_id"] = m.group(1)
    return result


def _extract_field_and_crop(selector_str: str, path: str, scope: str | None) -> tuple:
    """Extract (table_id, crop_id, field) from varied patch formats."""
    import re
    sel = _parse_selector(selector_str)
    table_id = sel.get("table_id") or scope
    crop_id = sel.get("crop_id")

    # Also look for crop_id in the path (e.g. "crop_units[crop_id=X].field")
    m = re.search(r'crop_id=([^\]\.\s]+)', path)
    if m and not crop_id:
        crop_id = m.group(1)

    # Extract the actual field name (last component after any brackets/dots)
    field = re.sub(r'^.*[\.\]]', '', path)
    if not field:
        field = path

    return table_id, crop_id, field


def apply_manifest_patch(
    data: dict,
    patch: dict,
) -> str | None:
    selector_raw = patch.get("selector", {})
    operation = patch.get("operation")
    path = patch.get("path", "")
    old_value = patch.get("old_value")
    new_value = patch.get("new_value")
    scope = patch.get("scope")

    fig_id, crop_id, field = _extract_field_and_crop(
        selector_raw if isinstance(selector_raw, str) else "",
        path, scope)

    if isinstance(selector_raw, dict):
        fig_id = selector_raw.get("table_id") or fig_id
        crop_id = selector_raw.get("crop_id") or crop_id
        if not crop_id and path.startswith("crop_units[]."):
            field = path[len("crop_units[]."):]

    fig = next((f for f in data.get("tables", [])
                if f.get("table_id") == fig_id), None)
    if fig is None:
        return f"table_id {fig_id} not found"

    if crop_id:
        cu = next((c for c in fig.get("crop_units", [])
                   if c.get("crop_id") == crop_id), None)
        if cu is None:
            return f"crop_id {crop_id} not found in {fig_id}"
        target = cu
    else:
        target = fig

    if operation == "replace":
        current = target.get(field)
        if current != old_value:
            return (f"{fig_id}/{crop_id}.{field}: old_value mismatch — "
                    f"expected {json.dumps(old_value)}, got {json.dumps(current)}")
        target[field] = new_value
    elif operation == "add_if_missing":
        if field in target:
            return f"{fig_id}/{crop_id}.{field}: already exists (add_if_missing)"
        target[field] = new_value
    else:
        return f"unknown operation: {operation}"

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge repair output into canonical"
    )
    parser.add_argument("repair_report_json", help="Path to repair_report.json")
    parser.add_argument("--repair-root", required=True,
                        help="Repair artifact root directory")
    parser.add_argument("--canonical", required=True,
                        help="Canonical directory")
    args = parser.parse_args()

    try:
        with open(args.repair_report_json, "r", encoding="utf-8") as f:
            report = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, indent=2),
              file=sys.stderr)
        return 2

    repair_status = report.get("status")
    if repair_status == "incomplete":
        print(json.dumps({
            "status": "error",
            "reason": "repair_report.status is incomplete — cannot merge",
        }, indent=2), file=sys.stderr)
        return 2

    merge = report.get("merge", {})
    if not merge.get("needs_parent_merge"):
        print(json.dumps({"status": "no_merge_needed"}))
        return 0

    repair_root = Path(args.repair_root)
    canonical = Path(args.canonical)

    file_copies = merge.get("file_copies", [])
    manifest_patches = merge.get("manifest_patches", [])

    # --- Phase 1: Validate (read-only) ---
    copy_errors = validate_file_copies(file_copies, repair_root)
    patch_errors = validate_manifest_patches(manifest_patches, canonical)
    all_errors = copy_errors + patch_errors

    if all_errors:
        result = {
            "status": "fail",
            "reason": "validation failed — canonical not modified",
            "copy_errors": len(copy_errors),
            "patch_errors": len(patch_errors),
            "errors": all_errors,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    # --- Phase 2: Execute (canonical modified only here) ---
    copies_count = execute_file_copies(file_copies, repair_root, canonical)
    patches_count = execute_manifest_patches(manifest_patches, canonical)

    result = {
        "status": "ok",
        "files_copied": copies_count,
        "patches_applied": patches_count,
        "errors": [],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
