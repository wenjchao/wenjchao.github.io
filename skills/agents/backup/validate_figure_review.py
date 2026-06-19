#!/usr/bin/env python3
"""Validate figure reviewer visual_review.json contract.

This validator is intentionally mechanical. It checks only JSON structure and
handoff consistency, not visual quality.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EDGES = ("top", "bottom", "left", "right")
STATUS = {"pass", "fail"}
SEVERITY = {"required", "advisory"}
REPAIR_HINTS = {
    "expand_top", "expand_bottom", "expand_left", "expand_right",
    "shrink_top", "shrink_bottom", "shrink_left", "shrink_right",
    "recrop", "split_crop", "merge_crop",
    "regenerate_preview", "manifest_check", "human_check",
}
FORBIDDEN_COORD_KEYS = {
    "current_crop_px",
    "proposed_crop_px",
    "crop_px",
    "bbox",
    "bbox_px",
    "crop_bbox",
    "crop_region",
}


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def add(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def require_object(value: Any, path: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        add(errors, path, "must be an object")
        return None
    return value


def require_array(value: Any, path: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        add(errors, path, "must be an array")
        return None
    return value


def require_nonempty_string(obj: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key not in obj:
        add(errors, f"{path}.{key}", "is required")
    elif not is_nonempty_string(obj[key]):
        add(errors, f"{path}.{key}", "must be a non-empty string")


def validate_reviewed_crop_unit(value: Any, path: str, errors: list[str]) -> str | None:
    unit = require_object(value, path, errors)
    if unit is None:
        return None

    for key in ("crop_id", "crop_preview", "boundary_preview"):
        require_nonempty_string(unit, key, path, errors)

    for field in ("bottom_band", "bottom_micro"):
        paths = unit.get(field)
        if not isinstance(paths, list) or len(paths) == 0:
            add(errors, f"{path}.{field}", "must be a non-empty array")
            continue
        for idx, p in enumerate(paths):
            if not is_nonempty_string(p):
                add(errors, f"{path}.{field}[{idx}]", "must be a non-empty string")

    return unit.get("crop_id") if is_nonempty_string(unit.get("crop_id")) else None


def validate_visual_inventory(value: Any, path: str, errors: list[str]) -> tuple[int, int]:
    inventory = require_object(value, path, errors)
    if inventory is None:
        return 0, 0

    counts = []
    for key in ("source_units", "missing_from_crop"):
        items = require_array(inventory.get(key), f"{path}.{key}", errors)
        if items is None:
            counts.append(0)
            continue
        for idx, item in enumerate(items):
            if not is_nonempty_string(item):
                add(errors, f"{path}.{key}[{idx}]", "must be a non-empty string")
        counts.append(len(items))
    return counts[0], counts[1]


def validate_edge_check_unit(
    value: Any,
    path: str,
    errors: list[str],
) -> tuple[str | None, bool]:
    unit = require_object(value, path, errors)
    if unit is None:
        return None, False

    require_nonempty_string(unit, "crop_id", path, errors)
    crop_id = unit.get("crop_id") if is_nonempty_string(unit.get("crop_id")) else None

    edges = require_object(unit.get("edges"), f"{path}.edges", errors)
    has_fail = False
    if edges is None:
        return crop_id, has_fail

    for edge in EDGES:
        edge_obj = require_object(edges.get(edge), f"{path}.edges.{edge}", errors)
        if edge_obj is None:
            continue

        ep = f"{path}.edges.{edge}"

        bc = edge_obj.get("boundary_content")
        if bc is None or not isinstance(bc, dict):
            add(errors, f"{ep}.boundary_content", "is required and must be an object with seg1, seg2, ... keys")
        elif len(bc) == 0:
            add(errors, f"{ep}.boundary_content", "must have at least one segment entry")
        else:
            for seg_key, seg_val in bc.items():
                seg_obj = require_object(seg_val, f"{ep}.boundary_content.{seg_key}", errors)
                if seg_obj is None:
                    continue
                for field in ("last_inside", "first_outside"):
                    if not is_nonempty_string(seg_obj.get(field)):
                        add(errors, f"{ep}.boundary_content.{seg_key}.{field}", "must be a non-empty string")

        if edge_obj.get("status") not in STATUS:
            add(errors, f"{ep}.status", 'must be "pass" or "fail"')
        elif edge_obj["status"] == "fail":
            has_fail = True

        if "verdict" in edge_obj:
            add(errors, f"{ep}.verdict", 'use "status" instead')
        if "detail" in edge_obj:
            add(errors, f"{ep}.detail", 'use "notes" instead')

        require_nonempty_string(edge_obj, "condition", ep, errors)
        require_nonempty_string(edge_obj, "notes", ep, errors)

    return crop_id, has_fail


def validate_finding(
    value: Any,
    path: str,
    errors: list[str],
    seen_finding_ids: set[str],
) -> None:
    finding = require_object(value, path, errors)
    if finding is None:
        return

    if "type" in finding:
        add(errors, f"{path}.type", 'use "problem" instead')
    if "description" in finding:
        add(errors, f"{path}.description", 'use "notes" instead')

    for key in ("finding_id", "problem", "repair_hint", "notes"):
        require_nonempty_string(finding, key, path, errors)

    hint = finding.get("repair_hint")
    if is_nonempty_string(hint) and hint not in REPAIR_HINTS:
        add(errors, f"{path}.repair_hint",
            f'must be one of: {", ".join(sorted(REPAIR_HINTS))}. Got: "{hint}"')

    if "finding_id" in finding and is_nonempty_string(finding["finding_id"]):
        if finding["finding_id"] in seen_finding_ids:
            add(errors, f"{path}.finding_id", "must be unique within the review")
        seen_finding_ids.add(finding["finding_id"])

    if "crop_id" not in finding:
        add(errors, f"{path}.crop_id", "is required")
    elif finding["crop_id"] is not None and not is_nonempty_string(finding["crop_id"]):
        add(errors, f"{path}.crop_id", "must be null or a non-empty string")

    if "edge" not in finding:
        add(errors, f"{path}.edge", "is required")
    elif finding["edge"] is not None and finding["edge"] not in (*EDGES, "interior", "all"):
        add(errors, f"{path}.edge", 'must be top, bottom, left, right, interior, all, or null')

    if finding.get("severity") not in SEVERITY:
        add(errors, f"{path}.severity", 'must be "required" or "advisory"')

    for key in FORBIDDEN_COORD_KEYS:
        if key in finding:
            add(errors, f"{path}.{key}", "repair findings must not contain coordinates")


def validate_figure(
    value: Any,
    path: str,
    errors: list[str],
    seen_finding_ids: set[str],
) -> tuple[str | None, int]:
    figure = require_object(value, path, errors)
    if figure is None:
        return None, 0

    for key in ("figure_id", "figure_label"):
        require_nonempty_string(figure, key, path, errors)

    decision = figure.get("decision")
    if decision not in STATUS:
        add(errors, f"{path}.decision", 'must be "pass" or "fail"')

    reviewed = require_array(figure.get("reviewed_crop_units"), f"{path}.reviewed_crop_units", errors)
    reviewed_ids: list[str] = []
    if reviewed is not None:
        for idx, unit in enumerate(reviewed):
            crop_id = validate_reviewed_crop_unit(unit, f"{path}.reviewed_crop_units[{idx}]", errors)
            if crop_id is not None:
                reviewed_ids.append(crop_id)

    _, missing_count = validate_visual_inventory(
        figure.get("visual_inventory"),
        f"{path}.visual_inventory",
        errors,
    )

    edge_checks = require_object(figure.get("edge_checks"), f"{path}.edge_checks", errors)
    edge_fail = False
    edge_ids: list[str] = []
    if edge_checks is not None:
        crop_units = require_array(
            edge_checks.get("crop_units"),
            f"{path}.edge_checks.crop_units",
            errors,
        )
        if crop_units is not None:
            for idx, unit in enumerate(crop_units):
                crop_id, has_fail = validate_edge_check_unit(
                    unit,
                    f"{path}.edge_checks.crop_units[{idx}]",
                    errors,
                )
                if crop_id is not None:
                    edge_ids.append(crop_id)
                edge_fail = edge_fail or has_fail

    if reviewed_ids and edge_ids and set(reviewed_ids) != set(edge_ids):
        add(
            errors,
            f"{path}.edge_checks.crop_units",
            "crop ids must match reviewed_crop_units crop ids exactly",
        )

    findings = require_array(figure.get("findings"), f"{path}.findings", errors)
    finding_count = 0
    required_findings = 0
    if findings is not None:
        finding_count = len(findings)
        for idx, finding in enumerate(findings):
            validate_finding(finding, f"{path}.findings[{idx}]", errors, seen_finding_ids)
            if isinstance(finding, dict) and finding.get("severity") == "required":
                required_findings += 1

    if decision == "pass":
        if findings:
            add(errors, f"{path}.findings", "pass figure must have an empty findings array")
        if missing_count:
            add(errors, f"{path}.visual_inventory.missing_from_crop", "pass figure must be empty")
        if edge_fail:
            add(errors, f"{path}.edge_checks", "pass figure cannot contain failed edges")

    if decision == "fail":
        if not findings:
            add(errors, f"{path}.findings", "fail figure must have at least one finding")
        if (edge_fail or missing_count) and not required_findings:
            add(errors, f"{path}.findings", "failed evidence requires at least one required finding")

    if edge_fail and decision != "fail":
        add(errors, f"{path}.decision", "must be fail when any edge status is fail")

    return decision if decision in STATUS else None, finding_count


def validate_review(data: Any) -> list[str]:
    errors: list[str] = []
    root = require_object(data, "$", errors)
    if root is None:
        return errors

    if root.get("schema_version") != "figure_review.v3":
        add(errors, "$.schema_version", 'must be "figure_review.v3"')

    if root.get("status") not in STATUS:
        add(errors, "$.status", 'must be "pass" or "fail"')

    for key in ("review_round", "reviewer_id"):
        require_nonempty_string(root, key, "$", errors)

    figures = require_array(root.get("figures"), "$.figures", errors)
    decisions: list[str] = []
    finding_count = 0
    seen_finding_ids: set[str] = set()
    any_edge_fail = False
    if figures is not None:
        for idx, figure in enumerate(figures):
            decision, count = validate_figure(
                figure,
                f"$.figures[{idx}]",
                errors,
                seen_finding_ids,
            )
            if decision:
                decisions.append(decision)
            finding_count += count
            if isinstance(figure, dict):
                crop_units = (
                    figure.get("edge_checks", {})
                    if isinstance(figure.get("edge_checks"), dict)
                    else {}
                ).get("crop_units", [])
                if isinstance(crop_units, list):
                    for unit in crop_units:
                        if not isinstance(unit, dict):
                            continue
                        edges = unit.get("edges", {})
                        if not isinstance(edges, dict):
                            continue
                        any_edge_fail = any(
                            isinstance(edges.get(edge), dict)
                            and edges[edge].get("status") == "fail"
                            for edge in EDGES
                        ) or any_edge_fail

    summary = require_object(root.get("summary"), "$.summary", errors)
    if summary is not None:
        expected = {
            "figure_count": len(figures or []),
            "pass_count": sum(1 for d in decisions if d == "pass"),
            "fail_count": sum(1 for d in decisions if d == "fail"),
            "finding_count": finding_count,
        }
        for key, expected_value in expected.items():
            if key not in summary:
                add(errors, f"$.summary.{key}", "is required")
            elif summary[key] != expected_value:
                add(errors, f"$.summary.{key}", f"must be {expected_value}")

    expected_status = "fail" if any(d == "fail" for d in decisions) or any_edge_fail else "pass"
    if root.get("status") in STATUS and root["status"] != expected_status:
        add(errors, "$.status", f"must be {expected_status} from figure decisions and edge checks")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate figure review JSON contract.")
    parser.add_argument("visual_review_json", help="Path to visual_review.json")
    args = parser.parse_args()

    path = Path(args.visual_review_json)
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - validator should report parse errors plainly.
        print(json.dumps({"status": "fail", "errors": [f"JSON parse/read error: {exc}"]}, indent=2))
        return 1

    errors = validate_review(data)
    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({"status": "pass", "errors": []}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
