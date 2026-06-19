#!/usr/bin/env python3
"""Validate figure extractor worker output contract.

This validator is intentionally mechanical. It checks JSON structure, path
resolution, crop-unit handoff consistency, and basic coordinate sanity. It does
not judge visual quality.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCHEMA = "figure_extraction.v3"
STATUS = {"complete", "incomplete"}
VERIFICATION_STATUS = {"pass", "fail"}
FIGURE_TYPES = {"main", "extended", "supplementary", "other"}
FORBIDDEN_DERIVED_FIGURE_KEYS = {"pages", "image_files", "crop_count"}
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
    except Exception as exc:  # noqa: BLE001 - validator should report plainly.
        add(errors, label, f"JSON parse/read error: {exc}")
        return None


def infer_paper_dir(artifact_root: Path) -> Path | None:
    parts = artifact_root.resolve().parts
    for idx in range(len(parts)):
        if parts[idx] == "figures":
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


def validate_shared_path(
    value: Any,
    path: str,
    paper_dir: Path | None,
    errors: list[str],
    *,
    must_exist: bool = True,
) -> None:
    if not is_nonempty_string(value):
        add(errors, path, "must be a non-empty string")
        return
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        add(errors, path, "must be paper-dir-relative, not absolute or parent-relative")
        return
    if must_exist and paper_dir is not None and not (paper_dir / rel).exists():
        add(errors, path, f"does not exist under paper_dir: {value}")


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
            add(errors, path, f"cannot verify page bounds because {page_image} is missing")
            return
        size = read_png_size(page_image)
        if size is None:
            add(errors, path, f"cannot read PNG size for {page_image}")
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
            unit.get(key),
            f"{path}.{key}",
            artifact_root,
            errors,
            must_exist=must_exist,
        )
    for field in ("top_band", "left_band", "right_band",
                   "bottom_band", "bottom_micro"):
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
            isinstance(crop_px, list)
            and len(crop_px) == 4
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
                        add(
                            errors,
                            f"{path}.image_file",
                            f"crop image is {size[0]}x{size[1]} but crop_px expects {expected_w}x{expected_h}",
                        )

    return unit


def validate_figure_identity(value: dict[str, Any], path: str, errors: list[str]) -> None:
    for key in ("figure_id", "figure_label"):
        require_nonempty_string(value, key, path, errors)
    if "figure_type" in value and value["figure_type"] not in FIGURE_TYPES:
        add(errors, f"{path}.figure_type", "must be main, extended, supplementary, or other")


def validate_candidates(data: Any, artifact_root: Path, errors: list[str]) -> None:
    root = require_object(data, "$.figure_candidates.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.figure_candidates.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.figure_candidates.json", errors)

    pages = require_array(root.get("pages"), "$.figure_candidates.json.pages", errors)
    if pages is not None:
        for page_idx, page_obj in enumerate(pages):
            page_path = f"$.figure_candidates.json.pages[{page_idx}]"
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
                                source_obj.get(key),
                                f"{source_path}.{key}",
                                artifact_root,
                                errors,
                            )

    if not isinstance(root.get("unexpected_labeled_figures"), list):
        add(errors, "$.figure_candidates.json.unexpected_labeled_figures", "must be an array")


def validate_index(data: Any, errors: list[str]) -> None:
    root = require_object(data, "$.figure_index.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.figure_index.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.figure_index.json", errors)
    figures = require_array(root.get("figures"), "$.figure_index.json.figures", errors)
    if figures is not None:
        seen: set[str] = set()
        for idx, figure in enumerate(figures):
            path = f"$.figure_index.json.figures[{idx}]"
            obj = require_object(figure, path, errors)
            if obj is None:
                continue
            validate_figure_identity(obj, path, errors)
            figure_id = obj.get("figure_id")
            if is_nonempty_string(figure_id):
                if figure_id in seen:
                    add(errors, f"{path}.figure_id", "must be unique")
                seen.add(figure_id)
            if not isinstance(obj.get("pages"), list):
                add(errors, f"{path}.pages", "must be an array in figure_index.json")
            for key in ("candidate_ids", "source_region_ids"):
                if not isinstance(obj.get(key), list):
                    add(errors, f"{path}.{key}", "must be an array")
    if not isinstance(root.get("omitted_candidates"), list):
        add(errors, "$.figure_index.json.omitted_candidates", "must be an array")


def validate_decisions(
    data: Any,
    artifact_root: Path,
    paper_dir: Path | None,
    errors: list[str],
) -> dict[str, list[dict[str, Any]]]:
    root = require_object(data, "$.figure_decisions.json", errors)
    decision_units: dict[str, list[dict[str, Any]]] = {}
    if root is None:
        return decision_units
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.figure_decisions.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.figure_decisions.json", errors)
    figures = require_array(root.get("figures"), "$.figure_decisions.json.figures", errors)
    if figures is not None:
        seen: set[str] = set()
        for idx, figure in enumerate(figures):
            path = f"$.figure_decisions.json.figures[{idx}]"
            obj = require_object(figure, path, errors)
            if obj is None:
                continue
            validate_figure_identity(obj, path, errors)
            for key in FORBIDDEN_DERIVED_FIGURE_KEYS:
                if key in obj:
                    add(errors, f"{path}.{key}", "is derived from crop_units and must be omitted")
            figure_id = obj.get("figure_id")
            if is_nonempty_string(figure_id):
                if figure_id in seen:
                    add(errors, f"{path}.figure_id", "must be unique")
                seen.add(figure_id)
            units = require_array(obj.get("crop_units"), f"{path}.crop_units", errors)
            decision_units[str(figure_id)] = []
            if units is not None:
                crop_ids: set[str] = set()
                for unit_idx, unit in enumerate(units):
                    unit_obj = validate_crop_unit(
                        unit,
                        f"{path}.crop_units[{unit_idx}]",
                        artifact_root,
                        paper_dir,
                        errors,
                    )
                    if unit_obj is None:
                        continue
                    crop_id = unit_obj.get("crop_id")
                    if is_nonempty_string(crop_id):
                        if crop_id in crop_ids:
                            add(errors, f"{path}.crop_units[{unit_idx}].crop_id", "must be unique")
                        crop_ids.add(crop_id)
                    decision_units[str(figure_id)].append(unit_obj)
    return decision_units


def validate_evidence_for_pass_figure(
    figure: dict[str, Any],
    path: str,
    errors: list[str],
) -> None:
    evidence = require_object(figure.get("evidence_read"), f"{path}.evidence_read", errors)
    if evidence is None:
        return
    final_previews = evidence.get("final_crop_previews")
    boundary_previews = evidence.get("boundary_previews")
    bottom_band_previews = evidence.get("bottom_band_previews")
    bottom_micro_previews = evidence.get("bottom_micro_previews")
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

    units = figure.get("crop_units", [])
    if not isinstance(units, list):
        return
    for unit_idx, unit in enumerate(units):
        if not isinstance(unit, dict):
            continue
        if unit.get("preview") not in final_previews:
            add(errors, f"{path}.crop_units[{unit_idx}].preview", "pass figure must list preview in evidence_read")
        if unit.get("boundary_preview") not in boundary_previews:
            add(
                errors,
                f"{path}.crop_units[{unit_idx}].boundary_preview",
                "pass figure must list boundary_preview in evidence_read",
            )
        unit_bottom_band = unit.get("bottom_band")
        if isinstance(unit_bottom_band, list):
            for bp in unit_bottom_band:
                if bp not in bottom_band_previews:
                    add(
                        errors,
                        f"{path}.crop_units[{unit_idx}].bottom_band",
                        "pass figure must list bottom_band preview in evidence_read",
                    )
        unit_bottom_micro = unit.get("bottom_micro")
        if isinstance(unit_bottom_micro, list):
            for bm in unit_bottom_micro:
                if bm not in bottom_micro_previews:
                    add(
                        errors,
                        f"{path}.crop_units[{unit_idx}].bottom_micro",
                        "pass figure must list bottom_micro preview in evidence_read",
                    )


def validate_figures(
    data: Any,
    artifact_root: Path,
    paper_dir: Path | None,
    errors: list[str],
) -> None:
    root = require_object(data, "$.figures.json", errors)
    if root is None:
        return
    if root.get("schema_version") != SCHEMA:
        add(errors, "$.figures.json.schema_version", f'must be "{SCHEMA}"')
    require_nonempty_string(root, "worker_id", "$.figures.json", errors)
    if root.get("status") not in STATUS:
        add(errors, "$.figures.json.status", 'must be "complete" or "incomplete"')

    figures = require_array(root.get("figures"), "$.figures.json.figures", errors)
    verification_results: list[str] = []
    if figures is not None:
        seen: set[str] = set()
        for idx, figure in enumerate(figures):
            path = f"$.figures.json.figures[{idx}]"
            obj = require_object(figure, path, errors)
            if obj is None:
                continue
            validate_figure_identity(obj, path, errors)
            for key in FORBIDDEN_DERIVED_FIGURE_KEYS:
                if key in obj:
                    add(errors, f"{path}.{key}", "is derived from crop_units and must be omitted")
            figure_id = obj.get("figure_id")
            if is_nonempty_string(figure_id):
                if figure_id in seen:
                    add(errors, f"{path}.figure_id", "must be unique")
                seen.add(figure_id)

            units = require_array(obj.get("crop_units"), f"{path}.crop_units", errors)
            figure_units: list[dict[str, Any]] = []
            if units is not None:
                crop_ids: set[str] = set()
                for unit_idx, unit in enumerate(units):
                    unit_obj = validate_crop_unit(
                        unit,
                        f"{path}.crop_units[{unit_idx}]",
                        artifact_root,
                        paper_dir,
                        errors,
                        check_dimensions=True,
                    )
                    if unit_obj is None:
                        continue
                    crop_id = unit_obj.get("crop_id")
                    if is_nonempty_string(crop_id):
                        if crop_id in crop_ids:
                            add(errors, f"{path}.crop_units[{unit_idx}].crop_id", "must be unique")
                        crop_ids.add(crop_id)
                    figure_units.append(unit_obj)

            verification = require_object(obj.get("verification"), f"{path}.verification", errors)
            result = None
            if verification is not None:
                result = verification.get("result")
                if result not in VERIFICATION_STATUS:
                    add(errors, f"{path}.verification.result", 'must be "pass" or "fail"')
                else:
                    verification_results.append(result)
                for key, value in verification.items():
                    if value not in VERIFICATION_STATUS:
                        add(errors, f"{path}.verification.{key}", 'must be "pass" or "fail"')
            if result == "pass":
                validate_evidence_for_pass_figure(obj, path, errors)

    expected_status = "incomplete" if any(result == "fail" for result in verification_results) else "complete"
    if root.get("status") in STATUS and root["status"] != expected_status:
        add(errors, "$.figures.json.status", f"must be {expected_status} from verification results")


def validate_extraction(artifact_root: Path, paper_dir: Path | None) -> list[str]:
    errors: list[str] = []
    artifact_root = artifact_root.resolve()
    if paper_dir is None:
        paper_dir = infer_paper_dir(artifact_root)

    if not artifact_root.exists():
        add(errors, "$.artifact_root", f"does not exist: {artifact_root}")
        return errors

    required_files = {
        "figure_candidates.json": artifact_root / "figure_candidates.json",
        "figure_index.json": artifact_root / "figure_index.json",
        "figure_decisions.json": artifact_root / "figure_decisions.json",
        "figures.json": artifact_root / "figures.json",
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

    if loaded["figure_candidates.json"] is not None:
        validate_candidates(loaded["figure_candidates.json"], artifact_root, errors)
    if loaded["figure_index.json"] is not None:
        validate_index(loaded["figure_index.json"], errors)

    decision_units: dict[str, list[dict[str, Any]]] = {}
    if loaded["figure_decisions.json"] is not None:
        decision_units = validate_decisions(
            loaded["figure_decisions.json"],
            artifact_root,
            paper_dir,
            errors,
        )
    if loaded["figures.json"] is not None:
        validate_figures(
            loaded["figures.json"],
            artifact_root,
            paper_dir,
            errors,
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate figure extractor worker output.")
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
