#!/usr/bin/env python3
"""Assemble repair_report.json from simple repair decisions.

The repair agent writes a small decisions.json with per-request outcomes
(result, new_crop_px, notes).  This tool reads the repair directory, canonical
manifests, and the request file to produce the full repair_report.json that
merge_repair.py and validate_figure_repair.py expect.

Usage:
    python build_repair_report.py \
        --repair-root <repair_artifact_root> \
        --canonical <canonical_dir> \
        --request-file <repair_requests path, canonical-relative> \
        --decisions <decisions.json>

Exit codes:
    0  success
    1  conflict or missing files
    2  input error
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

from build_manifest_patches import build_patches, MANIFEST_FILES, load_manifest


ACTIVE_RESULTS = {"repaired", "manifest_corrected", "preview_regenerated"}
INACTIVE_RESULTS = {"unresolved", "blocked"}


def find_crop_unit_in_manifest(data: dict, figure_id: str, crop_id: str) -> dict | None:
    for fig in data.get("figures", []):
        if fig.get("figure_id") != figure_id:
            continue
        for cu in fig.get("crop_units", []):
            if cu.get("crop_id") == crop_id:
                return cu
    return None


def scan_repair_files(repair_root: Path, crop_id: str) -> dict:
    """Scan repair directory for files belonging to a crop_id."""
    files: dict[str, list[str]] = {
        "crop": [],
        "crop_preview": [],
        "boundary_preview": [],
        "top_band": [],
        "left_band": [],
        "right_band": [],
        "bottom_band": [],
        "bottom_micro": [],
    }

    crop_path = repair_root / "crops" / f"{crop_id}.png"
    if crop_path.exists():
        files["crop"].append(f"crops/{crop_id}.png")

    preview_path = repair_root / "previews" / f"{crop_id}_preview.png"
    if preview_path.exists():
        files["crop_preview"].append(f"previews/{crop_id}_preview.png")

    boundary_path = repair_root / "previews" / f"{crop_id}_boundary_preview.png"
    if boundary_path.exists():
        files["boundary_preview"].append(f"previews/{crop_id}_boundary_preview.png")

    previews_dir = repair_root / "previews"
    if previews_dir.exists():
        edge_patterns = {
            "top_band": re.compile(rf"^{re.escape(crop_id)}_top_seg(\d+)_preview\.png$"),
            "left_band": re.compile(rf"^{re.escape(crop_id)}_left_seg(\d+)_preview\.png$"),
            "right_band": re.compile(rf"^{re.escape(crop_id)}_right_seg(\d+)_preview\.png$"),
            "bottom_band": re.compile(rf"^{re.escape(crop_id)}_bottom_seg(\d+)_preview\.png$"),
            "bottom_micro": re.compile(rf"^{re.escape(crop_id)}_micro_bottom_seg(\d+)_preview\.png$"),
        }

        for p in sorted(previews_dir.iterdir()):
            for kind, pattern in edge_patterns.items():
                if pattern.match(p.name):
                    files[kind].append(f"previews/{p.name}")
                    break

    return files


def build_file_copies(
    crop_id: str, figure_id: str, files: dict[str, list[str]]
) -> list[dict]:
    copies = []
    for kind, paths in files.items():
        for path in paths:
            entry: dict = {
                "kind": kind,
                "figure_id": figure_id,
                "crop_id": crop_id,
                "repair_output": path,
                "canonical_target": path,
            }
            if kind in ("top_band", "left_band", "right_band",
                        "bottom_band", "bottom_micro"):
                seg_match = re.search(r"seg(\d+)", path)
                if seg_match:
                    entry["segment"] = int(seg_match.group(1))
            copies.append(entry)
    return copies


def build_output_map(files: dict[str, list[str]]) -> dict:
    result: dict = {}
    if files["crop"]:
        result["image_file"] = files["crop"][0]
    if files["crop_preview"]:
        result["preview"] = files["crop_preview"][0]
    if files["boundary_preview"]:
        result["boundary_preview"] = files["boundary_preview"][0]
    for field in ("top_band", "left_band", "right_band",
                   "bottom_band", "bottom_micro"):
        if files[field]:
            result[field] = files[field]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble repair_report.json from repair decisions"
    )
    parser.add_argument("--repair-root", required=True,
                        help="Repair artifact root directory")
    parser.add_argument("--canonical", required=True,
                        help="Canonical directory")
    parser.add_argument("--request-file", required=True,
                        help="Path to repair_requests_assigned.json (canonical-relative)")
    parser.add_argument("--decisions", required=True,
                        help="Path to decisions.json")
    args = parser.parse_args()

    repair_root = Path(args.repair_root)
    canonical = Path(args.canonical)

    # Load canonical manifests
    manifests: dict[str, dict] = {}
    for filename in MANIFEST_FILES:
        data = load_manifest(canonical, filename)
        if data is None:
            print(json.dumps({"status": "error",
                              "reason": f"cannot read {canonical / filename}"},
                             indent=2), file=sys.stderr)
            return 2
        manifests[filename] = data

    figures_json = manifests["figures.json"]

    # Load request file
    request_path = Path(args.request_file)
    try:
        with open(request_path, "r", encoding="utf-8") as f:
            request_data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": f"request file: {exc}"},
                         indent=2), file=sys.stderr)
        return 2

    repair_round = request_data.get("repair_round", "")
    repair_id = (request_data.get("assignments", [{}])[0].get("repair_id", "")
                 if request_data.get("assignments") else "repair_01")
    source_request_file = args.request_file

    # Load decisions
    try:
        with open(args.decisions, "r", encoding="utf-8") as f:
            decisions = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": f"decisions: {exc}"},
                         indent=2), file=sys.stderr)
        return 2

    if not isinstance(decisions, list):
        print(json.dumps({"status": "error",
                          "reason": "decisions must be a JSON array"},
                         indent=2), file=sys.stderr)
        return 2

    # Index decisions by request_id, check crop_id consistency
    decision_by_request: dict[str, dict] = {}
    crop_px_by_crop_id: dict[str, list[int]] = {}
    errors: list[str] = []

    for dec in decisions:
        req_id = dec.get("request_id", "")
        crop_id = dec.get("crop_id", "")
        new_crop_px = dec.get("new_crop_px")

        if not req_id:
            errors.append("decision missing request_id")
            continue
        decision_by_request[req_id] = dec

        if new_crop_px and crop_id:
            if crop_id in crop_px_by_crop_id:
                if crop_px_by_crop_id[crop_id] != new_crop_px:
                    errors.append(
                        f"conflicting new_crop_px for crop_id '{crop_id}': "
                        f"{crop_px_by_crop_id[crop_id]} vs {new_crop_px}"
                    )
            else:
                crop_px_by_crop_id[crop_id] = new_crop_px

    if errors:
        print(json.dumps({"status": "error", "errors": errors}, indent=2),
              file=sys.stderr)
        return 1

    # Process all requests (from request file)
    all_requests = request_data.get("requests", [])
    assigned_requests = [r for r in all_requests
                         if r.get("assigned_repair_id") == repair_id]

    repairs: list[dict] = []
    all_file_copies: list[dict] = []
    processed_crop_ids: set[str] = set()
    patch_intents: list[dict] = []
    crop_unit_cache: dict[str, dict] = {}

    for req in assigned_requests:
        req_id = req.get("request_id", "")
        figure_id = req.get("figure_id", "")
        figure_label = req.get("figure_label", figure_id)
        crop_ids = req.get("crop_ids", [])
        crop_id = crop_ids[0] if crop_ids else ""

        dec = decision_by_request.get(req_id)

        if dec is None:
            # Request not addressed in decisions → unresolved
            repairs.append({
                "request_id": req_id,
                "figure_id": figure_id,
                "figure_label": figure_label,
                "result": "unresolved",
                "action_taken": "none",
                "updated_crop_units": [],
                "evidence_read": {
                    "source_boundary_previews": [],
                    "repaired_crop_previews": [],
                    "repaired_boundary_previews": [],
                    "repaired_bottom_band_previews": [],
                    "repaired_bottom_micro_previews": [],
                },
                "requires_review": False,
                "notes": ["Request not addressed in repair decisions"],
            })
            continue

        result = dec.get("result", "repaired")
        action_taken = dec.get("action_taken", "recrop")
        new_crop_px = dec.get("new_crop_px")
        dec_notes = dec.get("notes", [])
        if isinstance(dec_notes, str):
            dec_notes = [dec_notes]

        # For inactive results, skip file scanning
        if result in INACTIVE_RESULTS:
            repairs.append({
                "request_id": req_id,
                "figure_id": figure_id,
                "figure_label": figure_label,
                "result": result,
                "action_taken": action_taken,
                "updated_crop_units": [],
                "evidence_read": {
                    "source_boundary_previews": [],
                    "repaired_crop_previews": [],
                    "repaired_boundary_previews": [],
                    "repaired_bottom_band_previews": [],
                    "repaired_bottom_micro_previews": [],
                },
                "requires_review": False,
                "notes": dec_notes,
            })
            continue

        # Look up canonical crop unit
        canonical_cu = find_crop_unit_in_manifest(
            figures_json, figure_id, crop_id
        )
        if canonical_cu is None:
            errors.append(f"{figure_id}/{crop_id} not found in canonical figures.json")
            repairs.append({
                "request_id": req_id,
                "figure_id": figure_id,
                "figure_label": figure_label,
                "result": "unresolved",
                "action_taken": action_taken,
                "updated_crop_units": [],
                "evidence_read": {
                    "source_boundary_previews": [],
                    "repaired_crop_previews": [],
                    "repaired_boundary_previews": [],
                    "repaired_bottom_band_previews": [],
                    "repaired_bottom_micro_previews": [],
                },
                "requires_review": False,
                "notes": [f"crop_id {crop_id} not found in canonical"],
            })
            continue

        old_crop_px = canonical_cu.get("crop_px")
        page = canonical_cu.get("page")
        role = canonical_cu.get("role", "complete figure")

        # Scan repair directory for files
        files = scan_repair_files(repair_root, crop_id)

        # Validate expected files exist
        if new_crop_px and not files["crop"]:
            errors.append(f"{crop_id}: has new_crop_px but no crop file found")
        if result in ACTIVE_RESULTS and not files["crop_preview"]:
            errors.append(f"{crop_id}: missing crop preview")

        # Build file_copies (dedup per crop_id)
        if crop_id not in processed_crop_ids:
            all_file_copies.extend(build_file_copies(crop_id, figure_id, files))
            processed_crop_ids.add(crop_id)

        # Build output map
        output_map = build_output_map(files)

        # Build updated_crop_units — every repaired entry gets one, but
        # file_copies and patch_intents are only generated once per crop_id
        updated_crop_units: list[dict] = []
        if new_crop_px:
            if crop_id in crop_unit_cache:
                updated_crop_units.append(crop_unit_cache[crop_id])
            else:
                unit = {
                    "crop_id": crop_id,
                    "page": page,
                    "old_crop_px": old_crop_px,
                    "new_crop_px": new_crop_px,
                    "role": role,
                    "repair_output": output_map,
                    "canonical_target": output_map,
                }
                crop_unit_cache[crop_id] = unit
                updated_crop_units.append(unit)

                # Build patch intents (once per crop_id)
                if old_crop_px != new_crop_px:
                    patch_intents.append({
                        "figure_id": figure_id,
                        "crop_id": crop_id,
                        "field": "crop_px",
                        "new_value": new_crop_px,
                    })
                # Check all patchable output_map fields for changes
                field_map = {
                    "image_file": output_map.get("image_file"),
                    "preview": output_map.get("preview"),
                    "boundary_preview": output_map.get("boundary_preview"),
                    "bottom_band": output_map.get("bottom_band"),
                    "bottom_micro": output_map.get("bottom_micro"),
                }
                for field, new_val in field_map.items():
                    if new_val is None:
                        continue
                    canonical_val = canonical_cu.get(field)
                    if canonical_val != new_val:
                        patch_intents.append({
                            "figure_id": figure_id,
                            "crop_id": crop_id,
                            "field": field,
                            "new_value": new_val,
                        })

        # Build evidence_read
        canonical_boundary = canonical_cu.get("boundary_preview", "")
        evidence_read = {
            "source_boundary_previews": [canonical_boundary] if canonical_boundary else [],
            "repaired_crop_previews": files["crop_preview"],
            "repaired_boundary_previews": files["boundary_preview"],
            "repaired_bottom_band_previews": files["bottom_band"],
            "repaired_bottom_micro_previews": files["bottom_micro"],
        }

        repairs.append({
            "request_id": req_id,
            "figure_id": figure_id,
            "figure_label": figure_label,
            "result": result,
            "action_taken": action_taken,
            "updated_crop_units": updated_crop_units,
            "evidence_read": evidence_read,
            "requires_review": result in ACTIVE_RESULTS,
            "notes": dec_notes,
        })

    # Generate manifest patches
    manifest_patches: list[dict] = []
    if patch_intents:
        patches, patch_errors = build_patches(patch_intents, manifests)
        manifest_patches = patches
        if patch_errors:
            errors.extend(patch_errors)

    # Compute summary
    results = [r.get("result", "") for r in repairs]
    summary = {
        "request_count": len(repairs),
        "repaired_count": sum(1 for r in results if r == "repaired"),
        "preview_regenerated_count": sum(1 for r in results if r == "preview_regenerated"),
        "unresolved_count": sum(1 for r in results if r == "unresolved"),
        "blocked_count": sum(1 for r in results if r == "blocked"),
    }

    status = "complete" if not any(r in INACTIVE_RESULTS for r in results) else "incomplete"
    needs_merge = any(r in ACTIVE_RESULTS for r in results)

    report = {
        "schema_version": "figure_repair.v3",
        "repair_round": repair_round,
        "repair_id": repair_id,
        "status": status,
        "source_request_file": source_request_file,
        "repairs": repairs,
        "merge": {
            "needs_parent_merge": needs_merge,
            "file_copies": all_file_copies,
            "manifest_patches": manifest_patches,
            "review_required_after_merge": True,
        },
        "validation": {
            "repair_self_check_status": "pass" if not errors else "fail",
            "notes": errors if errors else [],
        },
        "summary": summary,
    }

    output_path = repair_root / "repair_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    result_msg = {
        "status": "ok" if not errors else "warning",
        "written": str(output_path),
        "repairs": len(repairs),
        "file_copies": len(all_file_copies),
        "manifest_patches": len(manifest_patches),
        "summary": summary,
    }
    if errors:
        result_msg["errors"] = errors

    print(json.dumps(result_msg, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
