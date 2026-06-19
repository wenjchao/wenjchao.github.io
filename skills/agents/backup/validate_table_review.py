#!/usr/bin/env python3
"""Validate table reviewer output contract.

Mechanical checks: required sections present, field names correct, enum values
valid, summary counts consistent. Does not judge visual or structural accuracy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA = "table_review.v1"
VALID_DECISIONS = {"pass", "fail"}
VALID_STATUSES = {"pass", "fail"}
VALID_SEVERITIES = {"required", "advisory"}
EDGE_KEYS = {"top", "bottom", "left", "right"}
EDGE_STATUSES = {"pass", "fail"}


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


def read_json(path: Path, label: str, errors: list[str]) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        add(errors, label, f"JSON parse/read error: {exc}")
        return None


def validate_reviewed_crop_units(value: Any, path: str, errors: list[str]) -> None:
    units = require_array(value, f"{path}.reviewed_crop_units", errors)
    if units is None:
        return
    if not units:
        add(errors, f"{path}.reviewed_crop_units", "must not be empty")
        return
    for idx, unit in enumerate(units):
        unit_path = f"{path}.reviewed_crop_units[{idx}]"
        obj = require_object(unit, unit_path, errors)
        if obj is None:
            continue
        if not is_nonempty_string(obj.get("crop_id")):
            add(errors, f"{unit_path}.crop_id", "must be a non-empty string")
        for key in ("crop_preview", "boundary_preview"):
            if not is_nonempty_string(obj.get(key)):
                add(errors, f"{unit_path}.{key}", "must be a non-empty string")


def validate_structural_inventory(value: Any, path: str, errors: list[str]) -> None:
    inv = require_object(value, f"{path}.structural_inventory", errors)
    if inv is None:
        return
    for key in ("source_row_count", "source_column_count"):
        if not isinstance(inv.get(key), int):
            add(errors, f"{path}.structural_inventory.{key}", "must be an integer")
    for key in ("json_row_count", "json_column_count"):
        if not isinstance(inv.get(key), int):
            add(errors, f"{path}.structural_inventory.{key}", "must be an integer")


def validate_edge_checks(value: Any, path: str, errors: list[str]) -> None:
    ec = require_object(value, f"{path}.edge_checks", errors)
    if ec is None:
        return
    crop_units = require_array(ec.get("crop_units"), f"{path}.edge_checks.crop_units", errors)
    if crop_units is None:
        return
    for idx, cu in enumerate(crop_units):
        cu_path = f"{path}.edge_checks.crop_units[{idx}]"
        obj = require_object(cu, cu_path, errors)
        if obj is None:
            continue
        if not is_nonempty_string(obj.get("crop_id")):
            add(errors, f"{cu_path}.crop_id", "must be a non-empty string")
        edges = require_object(obj.get("edges"), f"{cu_path}.edges", errors)
        if edges is None:
            continue
        missing = EDGE_KEYS - set(edges)
        if missing:
            add(errors, f"{cu_path}.edges", f"missing edges: {sorted(missing)}")
        for edge_name in sorted(EDGE_KEYS & set(edges)):
            edge = require_object(edges[edge_name], f"{cu_path}.edges.{edge_name}", errors)
            if edge is None:
                continue
            if edge.get("status") not in EDGE_STATUSES:
                add(errors, f"{cu_path}.edges.{edge_name}.status", "must be pass or fail")


def validate_structure_check(value: Any, path: str, errors: list[str]) -> None:
    sc = require_object(value, f"{path}.structure_check", errors)
    if sc is None:
        return
    for key in ("row_count_matches", "column_count_matches", "header_structure_correct",
                 "cell_text_accurate", "footnotes_complete", "rendered_preview_matches"):
        if key in sc and sc[key] not in VALID_DECISIONS:
            add(errors, f"{path}.structure_check.{key}", "must be pass or fail")


def validate_findings(findings: Any, table_id: str, decision: str, path: str, errors: list[str]) -> int:
    arr = require_array(findings, f"{path}.findings", errors)
    if arr is None:
        return 0
    if decision == "pass" and len(arr) > 0:
        add(errors, f"{path}.findings", "pass table must have empty findings")
    if decision == "fail" and len(arr) == 0:
        add(errors, f"{path}.findings", "fail table must have at least one finding")
    ids_seen: set[str] = set()
    for idx, finding in enumerate(arr):
        fp = f"{path}.findings[{idx}]"
        obj = require_object(finding, fp, errors)
        if obj is None:
            continue
        fid = obj.get("finding_id")
        if not is_nonempty_string(fid):
            add(errors, f"{fp}.finding_id", "must be a non-empty string")
        elif fid in ids_seen:
            add(errors, f"{fp}.finding_id", "must be unique")
        else:
            ids_seen.add(fid)
        if not is_nonempty_string(obj.get("table_id")):
            add(errors, f"{fp}.table_id", "must be a non-empty string")
        elif obj["table_id"] != table_id:
            add(errors, f"{fp}.table_id", f"must match parent table_id ({table_id})")
        if "crop_id" not in obj:
            add(errors, f"{fp}.crop_id", "is required (use null for single-crop tables)")
        if not is_nonempty_string(obj.get("problem")):
            add(errors, f"{fp}.problem", "must be a non-empty string")
        if not is_nonempty_string(obj.get("repair_hint")):
            add(errors, f"{fp}.repair_hint", "must be a non-empty string")
        if obj.get("severity") not in VALID_SEVERITIES:
            add(errors, f"{fp}.severity", "must be required or advisory")
        if not is_nonempty_string(obj.get("notes")):
            add(errors, f"{fp}.notes", "must be a non-empty string")
    return len(arr)


def validate_review(review_path: Path) -> list[str]:
    errors: list[str] = []
    data = read_json(review_path, str(review_path), errors)
    if data is None:
        return errors
    root = require_object(data, "$", errors)
    if root is None:
        return errors

    if root.get("schema_version") != SCHEMA:
        add(errors, "$.schema_version", f'must be "{SCHEMA}"')
    if not is_nonempty_string(root.get("review_round")):
        add(errors, "$.review_round", "must be a non-empty string")
    if not is_nonempty_string(root.get("reviewer_id")):
        add(errors, "$.reviewer_id", "must be a non-empty string")
    if root.get("status") not in VALID_STATUSES:
        add(errors, "$.status", "must be pass or fail")

    tables = require_array(root.get("tables"), "$.tables", errors)
    if tables is None:
        return errors

    pass_count = 0
    fail_count = 0
    total_findings = 0

    for idx, table in enumerate(tables):
        tp = f"$.tables[{idx}]"
        obj = require_object(table, tp, errors)
        if obj is None:
            continue

        table_id = obj.get("table_id", f"<missing_{idx}>")
        if not is_nonempty_string(obj.get("table_id")):
            add(errors, f"{tp}.table_id", "must be a non-empty string")

        decision = obj.get("decision")
        if decision not in VALID_DECISIONS:
            add(errors, f"{tp}.decision", "must be pass or fail")
        elif decision == "pass":
            pass_count += 1
        else:
            fail_count += 1

        validate_reviewed_crop_units(obj.get("reviewed_crop_units"), tp, errors)
        validate_structural_inventory(obj.get("structural_inventory"), tp, errors)
        validate_edge_checks(obj.get("edge_checks"), tp, errors)
        validate_structure_check(obj.get("structure_check"), tp, errors)
        total_findings += validate_findings(obj.get("findings"), str(table_id), str(decision), tp, errors)

    summary = require_object(root.get("summary"), "$.summary", errors)
    if summary is not None:
        expected = {
            "table_count": len(tables),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "finding_count": total_findings,
        }
        for key, val in expected.items():
            if summary.get(key) != val:
                add(errors, f"$.summary.{key}", f"expected {val}, got {summary.get(key)}")

    expected_status = "pass" if fail_count == 0 else "fail"
    if root.get("status") in VALID_STATUSES and root["status"] != expected_status:
        add(errors, "$.status", f"must be {expected_status} (fail_count={fail_count})")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate table reviewer output.")
    parser.add_argument("review_json", help="Path to table_visual_review.json")
    args = parser.parse_args()

    errors = validate_review(Path(args.review_json))
    status = "fail" if errors else "pass"
    print(json.dumps({"status": status, "errors": errors}, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
