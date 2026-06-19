#!/usr/bin/env python3
"""Validate figure repair repair_report.json contract.

This validator is intentionally mechanical. It checks report shape, merge
instructions, repair-local paths, and summary consistency. It does not judge
whether the repaired crop is visually acceptable.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCHEMA = "figure_repair.v3"
STATUS = {"complete", "incomplete"}
VALIDATION_STATUS = {"pass", "fail"}
RESULTS = {"repaired", "manifest_corrected", "preview_regenerated", "unresolved", "blocked"}
COPY_KINDS = {"crop", "crop_preview", "boundary_preview",
              "top_band", "left_band", "right_band",
              "bottom_band", "bottom_micro"}
PATCH_TARGETS = {"figures.json", "figure_index.json"}
PATCH_OPERATIONS = {"replace", "add_if_missing"}
FORBIDDEN_PATH_PARTS = {
    "workers",
    "canonical",
    "reviewers",
    "repairs",
}
FORBIDDEN_HASH_KEYS = {"hash", "sha256", "crop_hash", "image_hash", "file_hash"}


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


def check_no_hash_keys(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_HASH_KEYS or key.lower().endswith("_hash"):
                add(errors, f"{path}.{key}", "hash fields are not used in this pipeline")
            check_no_hash_keys(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            check_no_hash_keys(child, f"{path}[{idx}]", errors)


def validate_relative_path(
    value: Any,
    path: str,
    errors: list[str],
    *,
    root: Path | None = None,
    must_exist: bool = False,
) -> None:
    if not is_nonempty_string(value):
        add(errors, path, "must be a non-empty relative string")
        return
    rel = Path(value)
    if rel.is_absolute():
        add(errors, path, "must not be absolute")
        return
    if ".." in rel.parts:
        add(errors, path, "must not contain '..'")
        return
    if any(part in FORBIDDEN_PATH_PARTS for part in rel.parts):
        add(errors, path, "must be artifact-root-relative, without lane/stage prefixes")
        return
    if must_exist and root is not None and not (root / rel).exists():
        add(errors, path, f"does not exist under repair root: {value}")


def validate_crop_px(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) != 4 or not all(isinstance(item, int) for item in value):
        add(errors, path, "must be four integer page-pixel coordinates")
        return
    x1, y1, x2, y2 = value
    if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
        add(errors, path, "must satisfy 0 <= x1 < x2 and 0 <= y1 < y2")


def validate_output_map(
    value: Any,
    path: str,
    repair_root: Path,
    errors: list[str],
    *,
    must_exist: bool,
    require_full_crop_set: bool,
) -> None:
    mapping = require_object(value, path, errors)
    if mapping is None:
        return

    required = ("image_file", "preview", "boundary_preview") if require_full_crop_set else ()
    for key in required:
        validate_relative_path(
            mapping.get(key),
            f"{path}.{key}",
            errors,
            root=repair_root,
            must_exist=must_exist,
        )
    for key in ("image_file", "preview", "boundary_preview"):
        if key in mapping and key not in required:
            validate_relative_path(
                mapping[key],
                f"{path}.{key}",
                errors,
                root=repair_root,
                must_exist=must_exist,
            )

    for field in ("bottom_band", "bottom_micro"):
        if require_full_crop_set or field in mapping:
            field_path = f"{path}.{field}"
            paths = mapping.get(field)
            if not isinstance(paths, list) or len(paths) == 0:
                add(errors, field_path, "must be a non-empty array")
                continue
            for idx, p in enumerate(paths):
                validate_relative_path(
                    p,
                    f"{field_path}[{idx}]",
                    errors,
                    root=repair_root,
                    must_exist=must_exist,
                )


def validate_updated_crop_unit(
    value: Any,
    path: str,
    repair_root: Path,
    errors: list[str],
) -> None:
    unit = require_object(value, path, errors)
    if unit is None:
        return
    require_nonempty_string(unit, "crop_id", path, errors)
    if "page" in unit and not isinstance(unit["page"], int):
        add(errors, f"{path}.page", "must be an integer when present")
    validate_crop_px(unit.get("old_crop_px"), f"{path}.old_crop_px", errors)
    validate_crop_px(unit.get("new_crop_px"), f"{path}.new_crop_px", errors)
    require_nonempty_string(unit, "role", path, errors)
    validate_output_map(
        unit.get("repair_output"),
        f"{path}.repair_output",
        repair_root,
        errors,
        must_exist=True,
        require_full_crop_set=True,
    )
    validate_output_map(
        unit.get("canonical_target"),
        f"{path}.canonical_target",
        repair_root,
        errors,
        must_exist=False,
        require_full_crop_set=True,
    )

    new_crop_px = unit.get("new_crop_px")
    repair_output = unit.get("repair_output")
    if (
        isinstance(new_crop_px, list)
        and len(new_crop_px) == 4
        and all(isinstance(v, int) for v in new_crop_px)
        and isinstance(repair_output, dict)
        and is_nonempty_string(repair_output.get("image_file"))
    ):
        img_path = repair_root / repair_output["image_file"]
        if img_path.exists():
            size = read_png_size(img_path)
            if size is not None:
                expected_w = new_crop_px[2] - new_crop_px[0]
                expected_h = new_crop_px[3] - new_crop_px[1]
                if size != (expected_w, expected_h):
                    add(
                        errors,
                        f"{path}.repair_output.image_file",
                        f"crop image is {size[0]}x{size[1]} but new_crop_px expects {expected_w}x{expected_h}",
                    )


def validate_repair(
    value: Any,
    path: str,
    repair_root: Path,
    errors: list[str],
) -> str | None:
    repair = require_object(value, path, errors)
    if repair is None:
        return None
    for key in ("request_id", "figure_id"):
        require_nonempty_string(repair, key, path, errors)
    if "figure_label" in repair and not is_nonempty_string(repair["figure_label"]):
        add(errors, f"{path}.figure_label", "must be a non-empty string when present")

    result = repair.get("result")
    if result not in RESULTS:
        add(errors, f"{path}.result", "must be a valid repair result")
        result = None

    units = require_array(repair.get("updated_crop_units"), f"{path}.updated_crop_units", errors)
    if units is not None:
        for idx, unit in enumerate(units):
            validate_updated_crop_unit(unit, f"{path}.updated_crop_units[{idx}]", repair_root, errors)

    if result == "repaired" and not units:
        add(errors, f"{path}.updated_crop_units", "repaired result must include updated crop units")

    if result in {"repaired", "manifest_corrected", "preview_regenerated"}:
        if repair.get("requires_review") is not True:
            add(errors, f"{path}.requires_review", "modified repairs must require review")
    elif "requires_review" in repair and not isinstance(repair["requires_review"], bool):
        add(errors, f"{path}.requires_review", "must be boolean")

    if not isinstance(repair.get("notes"), list):
        add(errors, f"{path}.notes", "must be an array")

    if result == "repaired":
        evidence = require_object(repair.get("evidence_read"), f"{path}.evidence_read", errors)
        if evidence is not None:
            for key in (
                "source_boundary_previews",
                "repaired_crop_previews",
                "repaired_boundary_previews",
                "repaired_bottom_band_previews",
                "repaired_bottom_micro_previews",
            ):
                values = require_array(evidence.get(key), f"{path}.evidence_read.{key}", errors)
                if values is not None and not values:
                    add(errors, f"{path}.evidence_read.{key}", "must not be empty for repaired result")
                if values is not None:
                    for idx, item in enumerate(values):
                        validate_relative_path(
                            item,
                            f"{path}.evidence_read.{key}[{idx}]",
                            errors,
                            root=repair_root,
                            must_exist=True,
                        )

    return result if isinstance(result, str) else None


def validate_file_copy(
    value: Any,
    path: str,
    repair_root: Path,
    errors: list[str],
) -> None:
    item = require_object(value, path, errors)
    if item is None:
        return
    kind = item.get("kind")
    if kind not in COPY_KINDS:
        add(errors, f"{path}.kind", "must be crop, crop_preview, boundary_preview, bottom_band, or bottom_micro")
    for key in ("figure_id", "crop_id"):
        require_nonempty_string(item, key, path, errors)
    validate_relative_path(
        item.get("repair_output"),
        f"{path}.repair_output",
        errors,
        root=repair_root,
        must_exist=True,
    )
    validate_relative_path(
        item.get("canonical_target"),
        f"{path}.canonical_target",
        errors,
        root=repair_root,
        must_exist=False,
    )


def patch_key(patch: dict[str, Any], target_file: str) -> str:
    selector = json.dumps(patch.get("selector"), sort_keys=True, ensure_ascii=False)
    new_value = json.dumps(patch.get("new_value"), sort_keys=True, ensure_ascii=False)
    return f"{target_file}|{patch.get('operation')}|{patch.get('scope')}|{selector}|{patch.get('path')}|{new_value}"


def validate_patch(value: Any, path: str, errors: list[str]) -> dict[str, Any] | None:
    patch = require_object(value, path, errors)
    if patch is None:
        return None
    if patch.get("target_file") not in PATCH_TARGETS:
        add(errors, f"{path}.target_file", f"must be one of: {', '.join(sorted(PATCH_TARGETS))}")
    if patch.get("operation") not in PATCH_OPERATIONS:
        add(errors, f"{path}.operation", 'must be "replace" or "add_if_missing"')
    for key in ("scope", "path"):
        require_nonempty_string(patch, key, path, errors)
    if not isinstance(patch.get("selector"), dict):
        add(errors, f"{path}.selector", "must be an object")
    if "old_value" not in patch:
        add(errors, f"{path}.old_value", "is required")
    if "new_value" not in patch:
        add(errors, f"{path}.new_value", "is required")
    return patch


def validate_merge(
    value: Any,
    path: str,
    repair_root: Path,
    errors: list[str],
) -> None:
    merge = require_object(value, path, errors)
    if merge is None:
        return
    if not isinstance(merge.get("needs_parent_merge"), bool):
        add(errors, f"{path}.needs_parent_merge", "must be boolean")

    file_copies = require_array(merge.get("file_copies"), f"{path}.file_copies", errors)
    if file_copies is not None:
        for idx, item in enumerate(file_copies):
            validate_file_copy(item, f"{path}.file_copies[{idx}]", repair_root, errors)

    patches = require_array(merge.get("manifest_patches"), f"{path}.manifest_patches", errors)
    valid_patches: list[dict[str, Any]] = []
    if patches is not None:
        for idx, item in enumerate(patches):
            patch = validate_patch(item, f"{path}.manifest_patches[{idx}]", errors)
            if patch is not None:
                valid_patches.append(patch)



def validate_summary(
    value: Any,
    path: str,
    results: list[str],
    errors: list[str],
) -> None:
    summary = require_object(value, path, errors)
    if summary is None:
        return
    expected = {
        "request_count": len(results),
        "repaired_count": sum(1 for result in results if result == "repaired"),
        "preview_regenerated_count": sum(1 for result in results if result == "preview_regenerated"),
        "unresolved_count": sum(1 for result in results if result == "unresolved"),
        "blocked_count": sum(1 for result in results if result == "blocked"),
    }
    for key, expected_value in expected.items():
        if key not in summary:
            add(errors, f"{path}.{key}", "is required")
        elif summary[key] != expected_value:
            add(errors, f"{path}.{key}", f"must be {expected_value}")


def validate_repair_report(report_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with report_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - validator should report plainly.
        return [f"$.repair_report.json: JSON parse/read error: {exc}"]

    repair_root = report_path.resolve().parent
    check_no_hash_keys(data, "$", errors)
    root = require_object(data, "$", errors)
    if root is None:
        return errors

    if root.get("schema_version") != SCHEMA:
        add(errors, "$.schema_version", f'must be "{SCHEMA}"')
    if root.get("status") not in STATUS:
        add(errors, "$.status", 'must be "complete" or "incomplete"')
    for key in ("repair_round", "repair_id", "source_request_file"):
        require_nonempty_string(root, key, "$", errors)

    repairs = require_array(root.get("repairs"), "$.repairs", errors)
    results: list[str] = []
    if repairs is not None:
        seen_request_ids: set[str] = set()
        for idx, repair in enumerate(repairs):
            path = f"$.repairs[{idx}]"
            result = validate_repair(repair, path, repair_root, errors)
            if result is not None:
                results.append(result)
            if isinstance(repair, dict) and is_nonempty_string(repair.get("request_id")):
                request_id = repair["request_id"]
                if request_id in seen_request_ids:
                    add(errors, f"{path}.request_id", "must be unique")
                seen_request_ids.add(request_id)

    validate_merge(root.get("merge"), "$.merge", repair_root, errors)

    validation = require_object(root.get("validation"), "$.validation", errors)
    validation_status = None
    if validation is not None:
        validation_status = validation.get("repair_self_check_status")
        if validation_status not in VALIDATION_STATUS:
            add(errors, "$.validation.repair_self_check_status", 'must be "pass" or "fail"')
        if "notes" in validation and not isinstance(validation["notes"], list):
            add(errors, "$.validation.notes", "must be an array")

    validate_summary(root.get("summary"), "$.summary", results, errors)

    expected_status = "incomplete" if any(result in {"unresolved", "blocked"} for result in results) else "complete"
    if root.get("status") in STATUS and root["status"] != expected_status:
        add(errors, "$.status", f"must be {expected_status} from repair results")
    if root.get("status") == "complete" and validation_status != "pass":
        add(errors, "$.validation.repair_self_check_status", "must be pass when status is complete")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate figure repair report contract.")
    parser.add_argument("repair_report_json", help="Path to repair_report.json")
    args = parser.parse_args()

    errors = validate_repair_report(Path(args.repair_report_json))
    status = "fail" if errors else "pass"
    print(json.dumps({"status": status, "errors": errors}, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
