#!/usr/bin/env python3
"""Merge N per-worker repair_report.json files into one combined report.

Rewrites repair_output paths to include the worker subdirectory prefix so
merge_repair.py can resolve them from the common parent directory.

Usage:
    python merge_repair_reports.py \
        repair_01/repair_report.json repair_02/repair_report.json \
        --repair-round round_01 \
        --output repairs/round_01/merged_repair_report.json

Exit codes:
    0  success
    1  integrity error (duplicate request_id, patch conflict, round mismatch)
    2  input error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def prefix_path(value: str, prefix: str) -> str:
    """Prepend worker subdirectory to a repair-root-relative path."""
    return f"{prefix}/{value}"


def rewrite_output_map(mapping: dict[str, Any], prefix: str) -> dict[str, Any]:
    """Rewrite all paths in a repair_output / canonical_target map."""
    result = dict(mapping)
    for key in ("image_file", "preview", "boundary_preview"):
        if key in result and isinstance(result[key], str):
            result[key] = prefix_path(result[key], prefix)
    for key in ("top_band", "left_band", "right_band",
                 "bottom_band", "bottom_micro"):
        if key in result and isinstance(result[key], list):
            result[key] = [prefix_path(p, prefix) for p in result[key]]
    return result


def rewrite_evidence_read(evidence: dict[str, Any], prefix: str) -> dict[str, Any]:
    """Rewrite all path arrays in evidence_read."""
    result = dict(evidence)
    for key in (
        "repaired_crop_previews",
        "repaired_boundary_previews",
        "repaired_bottom_band_previews",
        "repaired_bottom_micro_previews",
    ):
        if key in result and isinstance(result[key], list):
            result[key] = [prefix_path(p, prefix) for p in result[key]]
    return result


def rewrite_repair(repair: dict, prefix: str) -> dict:
    """Deep-rewrite all repair-root-relative paths in a repair entry."""
    repair = dict(repair)

    if "updated_crop_units" in repair and isinstance(repair["updated_crop_units"], list):
        new_units = []
        for unit in repair["updated_crop_units"]:
            unit = dict(unit)
            if "repair_output" in unit and isinstance(unit["repair_output"], dict):
                unit["repair_output"] = rewrite_output_map(unit["repair_output"], prefix)
            new_units.append(unit)
        repair["updated_crop_units"] = new_units

    if "evidence_read" in repair and isinstance(repair["evidence_read"], dict):
        repair["evidence_read"] = rewrite_evidence_read(repair["evidence_read"], prefix)

    return repair


def rewrite_file_copy(entry: dict, prefix: str) -> dict:
    """Rewrite repair_output path in a file_copies entry."""
    entry = dict(entry)
    if "repair_output" in entry and isinstance(entry["repair_output"], str):
        entry["repair_output"] = prefix_path(entry["repair_output"], prefix)
    return entry


def patch_conflict_key(patch: dict) -> tuple:
    selector = patch.get("selector", {})
    return (
        patch.get("target_file", ""),
        selector.get("figure_id", ""),
        selector.get("crop_id", ""),
        patch.get("path", ""),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge per-worker repair reports"
    )
    parser.add_argument("reports", nargs="+", help="Paths to repair_report.json files")
    parser.add_argument("--repair-round", required=True, help="Expected repair round")
    parser.add_argument("--source-request-file",
                        help="Original full repair_requests_merged.json path "
                             "(canonical-relative, for the merged report)")
    parser.add_argument("--output", required=True, help="Output path for merged report")
    args = parser.parse_args()

    all_repairs: list[dict] = []
    all_file_copies: list[dict] = []
    all_manifest_patches: list[dict] = []
    seen_request_ids: set[str] = set()
    seen_patch_keys: dict[tuple, str] = {}
    errors: list[str] = []

    any_needs_merge = False
    all_complete = True
    all_validation_pass = True
    source_request_file = args.source_request_file or ""

    for report_path in args.reports:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(json.dumps({"status": "error", "reason": f"{report_path}: {exc}"},
                             indent=2), file=sys.stderr)
            return 2

        if report.get("schema_version") != "figure_repair.v3":
            errors.append(f"{report_path}: schema_version is not figure_repair.v3")

        if report.get("repair_round") != args.repair_round:
            errors.append(
                f"{report_path}: repair_round is '{report.get('repair_round')}', "
                f"expected '{args.repair_round}'"
            )

        repair_id = report.get("repair_id", "")
        if not repair_id:
            errors.append(f"{report_path}: missing repair_id")
            continue

        if not source_request_file:
            source_request_file = report.get("source_request_file", "")

        if report.get("status") != "complete":
            all_complete = False

        validation = report.get("validation", {})
        if validation.get("repair_self_check_status") != "pass":
            all_validation_pass = False

        merge = report.get("merge", {})
        if merge.get("needs_parent_merge"):
            any_needs_merge = True

        for repair in report.get("repairs", []):
            request_id = repair.get("request_id", "")
            if request_id in seen_request_ids:
                errors.append(f"duplicate request_id '{request_id}' across reports")
            seen_request_ids.add(request_id)
            all_repairs.append(rewrite_repair(repair, repair_id))

        for entry in merge.get("file_copies", []):
            all_file_copies.append(rewrite_file_copy(entry, repair_id))

        for patch in merge.get("manifest_patches", []):
            key = patch_conflict_key(patch)
            if key in seen_patch_keys:
                errors.append(
                    f"patch conflict: {key} appears in both "
                    f"'{seen_patch_keys[key]}' and '{report_path}'"
                )
            seen_patch_keys[key] = report_path
            all_manifest_patches.append(patch)

    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2,
                         ensure_ascii=False), file=sys.stderr)
        return 1

    results = [r.get("result", "") for r in all_repairs]

    merged = {
        "schema_version": "figure_repair.v3",
        "repair_round": args.repair_round,
        "repair_id": "merged",
        "status": "complete" if all_complete else "incomplete",
        "source_request_file": source_request_file,
        "repairs": all_repairs,
        "merge": {
            "needs_parent_merge": any_needs_merge,
            "file_copies": all_file_copies,
            "manifest_patches": all_manifest_patches,
            "review_required_after_merge": True,
        },
        "validation": {
            "repair_self_check_status": "pass" if all_validation_pass else "fail",
            "notes": [],
        },
        "summary": {
            "request_count": len(all_repairs),
            "repaired_count": sum(1 for r in results if r == "repaired"),
            "preview_regenerated_count": sum(1 for r in results if r == "preview_regenerated"),
            "unresolved_count": sum(1 for r in results if r == "unresolved"),
            "blocked_count": sum(1 for r in results if r == "blocked"),
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    result = {
        "status": "ok",
        "repair_round": args.repair_round,
        "source_reports": args.reports,
        "request_count": len(all_repairs),
        "repaired_count": merged["summary"]["repaired_count"],
        "file_copies_count": len(all_file_copies),
        "manifest_patches_count": len(all_manifest_patches),
        "merged_status": merged["status"],
        "written": str(output_path),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
