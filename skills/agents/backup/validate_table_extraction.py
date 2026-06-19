#!/usr/bin/env python3
"""Validate table extractor worker output contract.

Mechanical checks only: JSON structure, path resolution, crop-unit consistency,
coordinate sanity, structured JSON existence, and edge evidence. Does not judge
visual quality or structural accuracy.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCHEMA = "table_extraction.v1"
STATUS = {"complete", "incomplete"}
VERIFICATION_STATUS = {"pass", "fail"}
FORBIDDEN_DERIVED_KEYS = {"pages", "image_files", "crop_count"}
FORBIDDEN_PATH_PARTS = {
    "workers",
    "canonical",
    "reviewers",
    "repairs",
}
FORBIDDEN_HASH_KEYS = {"hash", "sha256", "crop_hash", "image_hash", "file_hash"}


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


def read_json(path: Path, label: str, errors: list[str]) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        add(errors, label, f"JSON parse/read error: {exc}")
        return None


def infer_paper_dir(artifact_root: Path) -> Path | None:
    parts = artifact_root.resolve().parts
    for idx in range(len(parts)):
        if parts[idx] == "tables":
            if idx == 0:
                return Path(parts[0])
            return Path(*parts[:idx])
    return None


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


def check_no_hash_keys(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_HASH_KEYS or key.lower().endswith("_hash"):
                add(errors, f"{path}.{key}", "hash fields are not used in this pipeline")
            check_no_hash_keys(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            check_no_hash_keys(child, f"{path}[{idx}]", errors)


def validate_relative_artifact_path(
    value: Any,
    path: str,
    artifact_root: Path,
    errors: list[str],
    *,
    must_exist: bool = True,
) -> None:
    if not is_nonempty_string(value):
        add(errors, path, "must be a non-empty artifact-root-relative string")
        return
    rel = Path(value)
    if rel.is_absolute():
        add(errors, path, "must not be absolute")
        return
    if ".." in rel.parts:
        add(errors, path, "must not contain '..'")
        return
    if any(part in FORBIDDEN_PATH_PARTS for part in rel.parts):
        add(errors, path, "must be relative to artifact_root, without lane/stage prefixes")
        return
    resolved = artifact_root / rel
    if must_exist and not resolved.exists():
        add(errors, path, f"does not exist under artifact_root: {value}")


def validate_crop_px(
    value: Any,
    path: str,
    page: Any,
    paper_dir: Path | None,
    errors: list[str],
) -> None:
    coords = require_array(value, path, errors)
    if coords is None:
        return
    if len(coords) != 4 or not all(isinstance(item, int) for item in coords):
        add(errors, path, "must be four integer page-pixel coordinates")
        return
    x1, y1, x2, y2 = coords
    if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
        add(errors, path, "must satisfy 0 <= x1 < x2 and 0 <= y1 < y2")
        return
    if isinstance(page, int) and paper_dir is not None:
        page_image = paper_dir / "shared" / "pages" / f"page_{page}.png"
        if not page_image.exists():
            return
        size = read_png_size(page_image)
        if size is None:
            return
        width, height = size
        if x2 > width or y2 > height:
            add(errors, path, f"must fit within page bounds {width}x{height}")


def validate_crop_unit(
    value: Any,
    path: str,
    artifact_root: Path,
    paper_dir: Path | None,
    errors: list[str],
    *,
    must_exist: bool = True,
    check_dimensions: bool = False,
) -> dict[str, Any] | None:
    unit = require_object(value, path, errors)
    if unit is None:
        return None
    require_nonempty_string(unit, "crop_id", path, errors)
    if not isinstance(unit.get("page"), int):
        add(errors, f"{path}.page", "must be an integer page number")
    validate_crop_px(unit.get("crop_px"), f"{path}.crop_px", unit.get("page"), paper_dir, errors)
    for key in ("image_file", "preview", "boundary_preview"):
        validate_relative_artifact_path(
            unit.get(key), f"{path}.{key}", artifact_root, errors, must_exist=must_exist,
        )
    for field in ("top_band", "left_band", "right_band", "bottom_band", "bottom_micro"):
        paths = unit.get(field)
        if not isinstance(paths, list) or len(paths) == 0:
            add(errors, f"{path}.{field}", "must be a non-empty array")
            continue
        for idx, p in enumerate(paths):
            validate_relative_artifact_path(p, f"{path}.{field}[{idx}]", artifact_root, errors, must_exist=must_exist)
    require_nonempty_string(unit, "role", path, errors)
    if check_dimensions:
        crop_px = unit.get("crop_px")
        image_file = unit.get("image_file")
        if (
            isinstance(crop_px, list) and len(crop_px) == 4
            and all(isinstance(v, int) for v in crop_px)
            and is_nonempty_string(image_file)
        ):
            img_path = artifact_root / image_file
            if img_path.exists():
                size = read_png_size(img_path)
                if size is not None:
                    expected_w = crop_px[2] - crop_px[0]
                    expected_h = crop_px[3] - crop_px[1]
                    if size != (expected_w, expected_h):
                        add(errors, f"{path}.image_file",
                            f"crop image is {size[0]}x{size[1]} but crop_px expects {expected_w}x{expected_h}")
    return unit


def validate_table_identity(value: dict[str, Any], path: str, errors: list[str]) -> None:
    require_nonempty_string(value, "table_id", path, errors)
    require_nonempty_string(value, "table_label", path, errors)


def validate_candidates(data: Any, artifact_root: Path, errors: list[str]) -> None:
    root = require_object(data, "$.table_candidates.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.table_candidates.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.table_candidates.json", errors)
    pages = require_array(root.get("pages"), "$.table_candidates.json.pages", errors)
    if pages is not None:
        for page_idx, page_obj in enumerate(pages):
            page_path = f"$.table_candidates.json.pages[{page_idx}]"
            page = require_object(page_obj, page_path, errors)
            if page is None:
                continue
            if not isinstance(page.get("page"), int):
                add(errors, f"{page_path}.page", "must be an integer")
            source_regions = page.get("source_regions", [])
            if source_regions is not None:
                regions = require_array(source_regions, f"{page_path}.source_regions", errors)
                if regions is not None:
                    for idx, source in enumerate(regions):
                        source_path = f"{page_path}.source_regions[{idx}]"
                        source_obj = require_object(source, source_path, errors)
                        if source_obj is None:
                            continue
                        require_nonempty_string(source_obj, "source_region_id", source_path, errors)
                        for key in ("source_image", "source_preview"):
                            validate_relative_artifact_path(
                                source_obj.get(key), f"{source_path}.{key}", artifact_root, errors,
                            )
    if not isinstance(root.get("unexpected_labeled_tables"), list):
        add(errors, "$.table_candidates.json.unexpected_labeled_tables", "must be an array")


def validate_index(data: Any, errors: list[str]) -> None:
    root = require_object(data, "$.table_index.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.table_index.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.table_index.json", errors)
    tables = require_array(root.get("tables"), "$.table_index.json.tables", errors)
    if tables is not None:
        seen: set[str] = set()
        for idx, table in enumerate(tables):
            path = f"$.table_index.json.tables[{idx}]"
            obj = require_object(table, path, errors)
            if obj is None:
                continue
            validate_table_identity(obj, path, errors)
            table_id = obj.get("table_id")
            if is_nonempty_string(table_id):
                if table_id in seen:
                    add(errors, f"{path}.table_id", "must be unique")
                seen.add(table_id)
            if not isinstance(obj.get("pages"), list):
                add(errors, f"{path}.pages", "must be an array")
            for key in ("candidate_ids", "source_region_ids"):
                if not isinstance(obj.get(key), list):
                    add(errors, f"{path}.{key}", "must be an array")
    if not isinstance(root.get("omitted_candidates"), list):
        add(errors, "$.table_index.json.omitted_candidates", "must be an array")


def validate_decisions(
    data: Any, artifact_root: Path, paper_dir: Path | None, errors: list[str],
) -> None:
    root = require_object(data, "$.table_decisions.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.table_decisions.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.table_decisions.json", errors)
    tables = require_array(root.get("tables"), "$.table_decisions.json.tables", errors)
    if tables is not None:
        seen: set[str] = set()
        for idx, table in enumerate(tables):
            path = f"$.table_decisions.json.tables[{idx}]"
            obj = require_object(table, path, errors)
            if obj is None:
                continue
            validate_table_identity(obj, path, errors)
            for key in FORBIDDEN_DERIVED_KEYS:
                if key in obj:
                    add(errors, f"{path}.{key}", "is derived from crop_units and must be omitted")
            table_id = obj.get("table_id")
            if is_nonempty_string(table_id):
                if table_id in seen:
                    add(errors, f"{path}.table_id", "must be unique")
                seen.add(table_id)
            units = require_array(obj.get("crop_units"), f"{path}.crop_units", errors)
            if units is not None:
                crop_ids: set[str] = set()
                for unit_idx, unit in enumerate(units):
                    unit_obj = validate_crop_unit(
                        unit, f"{path}.crop_units[{unit_idx}]", artifact_root, paper_dir, errors,
                    )
                    if unit_obj is None:
                        continue
                    crop_id = unit_obj.get("crop_id")
                    if is_nonempty_string(crop_id):
                        if crop_id in crop_ids:
                            add(errors, f"{path}.crop_units[{unit_idx}].crop_id", "must be unique")
                        crop_ids.add(crop_id)


def validate_structured_json(
    table_id: str, path_value: Any, parent_path: str, artifact_root: Path, errors: list[str],
) -> None:
    if not is_nonempty_string(path_value):
        add(errors, f"{parent_path}.structured_json", "must be a non-empty string")
        return
    validate_relative_artifact_path(path_value, f"{parent_path}.structured_json", artifact_root, errors)
    resolved = artifact_root / path_value
    if not resolved.exists():
        return
    data = read_json(resolved, f"{parent_path}.structured_json({path_value})", errors)
    if data is None:
        return
    obj = require_object(data, f"{parent_path}.structured_json({path_value})", errors)
    if obj is None:
        return
    if obj.get("table_id") != table_id:
        add(errors, f"{parent_path}.structured_json", f"table_id mismatch: expected {table_id}")
    has_headers = isinstance(obj.get("headers"), list)
    has_header_levels = isinstance(obj.get("header_levels"), list)
    if has_headers and has_header_levels:
        add(errors, f"{parent_path}.structured_json", "headers and header_levels are mutually exclusive")
    if not has_headers and not has_header_levels:
        add(errors, f"{parent_path}.structured_json", "must have either headers or header_levels")
    if not isinstance(obj.get("rows"), list):
        add(errors, f"{parent_path}.structured_json", "rows must be an array")
    else:
        expected_width = None
        if has_headers:
            expected_width = len(obj["headers"])
        elif has_header_levels:
            levels = obj["header_levels"]
            if levels and isinstance(levels[-1], list):
                expected_width = len(levels[-1])
        if expected_width is not None:
            for row_idx, row in enumerate(obj["rows"]):
                if isinstance(row, list) and len(row) != expected_width:
                    add(errors, f"{parent_path}.structured_json.rows[{row_idx}]",
                        f"width {len(row)} != header width {expected_width}")


def validate_evidence_for_pass_table(
    table: dict[str, Any], path: str, errors: list[str],
) -> None:
    evidence = require_object(table.get("evidence_read"), f"{path}.evidence_read", errors)
    if evidence is None:
        return
    final_previews = evidence.get("final_crop_previews")
    boundary_previews = evidence.get("boundary_previews")
    bottom_band_previews = evidence.get("bottom_band_previews")
    bottom_micro_previews = evidence.get("bottom_micro_previews")
    rendered_table_previews = evidence.get("rendered_table_previews")
    if not isinstance(final_previews, list):
        add(errors, f"{path}.evidence_read.final_crop_previews", "must be an array")
        final_previews = []
    if not isinstance(boundary_previews, list):
        add(errors, f"{path}.evidence_read.boundary_previews", "must be an array")
        boundary_previews = []
    if not isinstance(bottom_band_previews, list):
        add(errors, f"{path}.evidence_read.bottom_band_previews", "must be an array")
        bottom_band_previews = []
    if not isinstance(bottom_micro_previews, list):
        add(errors, f"{path}.evidence_read.bottom_micro_previews", "must be an array")
        bottom_micro_previews = []
    if not isinstance(rendered_table_previews, list):
        add(errors, f"{path}.evidence_read.rendered_table_previews", "must be an array")
        rendered_table_previews = []
    units = table.get("crop_units", [])
    if not isinstance(units, list):
        return
    for unit_idx, unit in enumerate(units):
        if not isinstance(unit, dict):
            continue
        if unit.get("preview") not in final_previews:
            add(errors, f"{path}.crop_units[{unit_idx}].preview", "pass table must list preview in evidence_read")
        if unit.get("boundary_preview") not in boundary_previews:
            add(errors, f"{path}.crop_units[{unit_idx}].boundary_preview",
                "pass table must list boundary_preview in evidence_read")
        for bp in (unit.get("bottom_band") or []):
            if bp not in bottom_band_previews:
                add(errors, f"{path}.crop_units[{unit_idx}].bottom_band",
                    "pass table must list bottom_band preview in evidence_read")
        for bm in (unit.get("bottom_micro") or []):
            if bm not in bottom_micro_previews:
                add(errors, f"{path}.crop_units[{unit_idx}].bottom_micro",
                    "pass table must list bottom_micro preview in evidence_read")


def validate_tables(
    data: Any, artifact_root: Path, paper_dir: Path | None, errors: list[str],
) -> None:
    root = require_object(data, "$.tables.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.tables.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.tables.json", errors)
    if root.get("status") not in STATUS:
        add(errors, "$.tables.json.status", 'must be "complete" or "incomplete"')

    tables = require_array(root.get("tables"), "$.tables.json.tables", errors)
    verification_results: list[str] = []
    if tables is not None:
        seen: set[str] = set()
        for idx, table in enumerate(tables):
            path = f"$.tables.json.tables[{idx}]"
            obj = require_object(table, path, errors)
            if obj is None:
                continue
            validate_table_identity(obj, path, errors)
            for key in FORBIDDEN_DERIVED_KEYS:
                if key in obj:
                    add(errors, f"{path}.{key}", "is derived from crop_units and must be omitted")
            table_id = obj.get("table_id")
            if is_nonempty_string(table_id):
                if table_id in seen:
                    add(errors, f"{path}.table_id", "must be unique")
                seen.add(table_id)

            validate_structured_json(str(table_id), obj.get("structured_json"), path, artifact_root, errors)

            rendered_preview = obj.get("rendered_table_preview")
            if is_nonempty_string(rendered_preview):
                validate_relative_artifact_path(rendered_preview, f"{path}.rendered_table_preview", artifact_root, errors)
            else:
                add(errors, f"{path}.rendered_table_preview", "must be a non-empty string")

            units = require_array(obj.get("crop_units"), f"{path}.crop_units", errors)
            if units is not None:
                crop_ids: set[str] = set()
                for unit_idx, unit in enumerate(units):
                    unit_obj = validate_crop_unit(
                        unit, f"{path}.crop_units[{unit_idx}]", artifact_root, paper_dir, errors,
                        check_dimensions=True,
                    )
                    if unit_obj is None:
                        continue
                    crop_id = unit_obj.get("crop_id")
                    if is_nonempty_string(crop_id):
                        if crop_id in crop_ids:
                            add(errors, f"{path}.crop_units[{unit_idx}].crop_id", "must be unique")
                        crop_ids.add(crop_id)

            verification = require_object(obj.get("verification"), f"{path}.verification", errors)
            result = None
            if verification is not None:
                result = verification.get("result")
                if result not in VERIFICATION_STATUS:
                    add(errors, f"{path}.verification.result", 'must be "pass" or "fail"')
                else:
                    verification_results.append(result)
                for key in ("source_context_checked", "final_crop_checked",
                            "boundary_preview_checked", "structure_checked"):
                    if key in verification and verification[key] not in VERIFICATION_STATUS:
                        add(errors, f"{path}.verification.{key}", 'must be "pass" or "fail"')
                if "structure_checked" not in verification:
                    add(errors, f"{path}.verification.structure_checked", "is required for table extraction")
            if result == "pass":
                validate_evidence_for_pass_table(obj, path, errors)

    expected_status = "incomplete" if any(r == "fail" for r in verification_results) else "complete"
    if root.get("status") in STATUS and root["status"] != expected_status:
        add(errors, "$.tables.json.status", f"must be {expected_status} from verification results")


def validate_extraction(artifact_root: Path, paper_dir: Path | None) -> list[str]:
    errors: list[str] = []
    artifact_root = artifact_root.resolve()
    if paper_dir is None:
        paper_dir = infer_paper_dir(artifact_root)
    if not artifact_root.exists():
        add(errors, "$.artifact_root", f"does not exist: {artifact_root}")
        return errors

    required_files = {
        "table_candidates.json": artifact_root / "table_candidates.json",
        "table_index.json": artifact_root / "table_index.json",
        "table_decisions.json": artifact_root / "table_decisions.json",
        "tables.json": artifact_root / "tables.json",
    }
    for label, path in required_files.items():
        if not path.exists():
            add(errors, f"$.{label}", f"missing required file: {path}")

    loaded = {
        label: read_json(path, f"$.{label}", errors) if path.exists() else None
        for label, path in required_files.items()
    }
    for label, data in loaded.items():
        if data is not None:
            check_no_hash_keys(data, f"$.{label}", errors)

    if loaded["table_candidates.json"] is not None:
        validate_candidates(loaded["table_candidates.json"], artifact_root, errors)
    if loaded["table_index.json"] is not None:
        validate_index(loaded["table_index.json"], errors)
    if loaded["table_decisions.json"] is not None:
        validate_decisions(loaded["table_decisions.json"], artifact_root, paper_dir, errors)
    if loaded["tables.json"] is not None:
        validate_tables(loaded["tables.json"], artifact_root, paper_dir, errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate table extractor worker output.")
    parser.add_argument("artifact_root", help="Path to worker output artifact root")
    parser.add_argument("--paper-dir", help="Optional paper directory for shared page checks")
    args = parser.parse_args()

    artifact_root = Path(args.artifact_root)
    paper_dir = Path(args.paper_dir).resolve() if args.paper_dir else None
    errors = validate_extraction(artifact_root, paper_dir)
    status = "fail" if errors else "pass"
    print(json.dumps({"status": status, "errors": errors}, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
