#!/usr/bin/env python3
"""Validate table extraction artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image


REQUIRED_CHECKS = {
    "source_compared",
    "title_complete",
    "structure_complete",
    "text_symbols_preserved",
    "footnotes_complete",
    "crop_clean",
    "rendered_output_matches_source",
}
PREVIEW_FIELDS = {
    "source_previews_read",
    "crop_previews_read",
    "rendered_table_previews_read",
}
REVIEW_PREVIEW_FIELDS = PREVIEW_FIELDS | {
    "source_edge_previews_read",
    "crop_edge_previews_read",
}
EDGE_KEYS = {"top", "bottom", "left", "right"}
MAX_IMAGE_DIM = 1600


def tables_dir(path: Path) -> Path:
    return path if path.name == "tables" else path / "tables"


def infer_run_dir(tdir: Path) -> Path:
    if tdir.name == "canonical" and tdir.parent.name == "tables":
        return tdir.parents[2]
    return tdir.parent


def load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid json: {path}: {exc}")
        return None


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(raw_path: str, bases: list[Path]) -> Path | None:
    path = Path(raw_path)
    if path.is_absolute():
        return path if path.exists() else None
    if path.exists():
        return path
    for base in bases:
        candidate = base / path
        if candidate.exists():
            return candidate
    return None


def check_image_path(label: str, raw_path: Any, bases: list[Path], errors: list[str]) -> None:
    if not is_nonempty_string(raw_path):
        errors.append(f"{label} must be a non-empty string path")
        return
    resolved = resolve_path(raw_path, bases)
    if resolved is None:
        errors.append(f"{label} missing: {raw_path}")
        return
    try:
        with Image.open(resolved) as img:
            width, height = img.size
    except Exception as exc:
        errors.append(f"{label} is not a readable image: {raw_path}: {exc}")
        return
    if width > MAX_IMAGE_DIM or height > MAX_IMAGE_DIM:
        errors.append(f"{label} exceeds {MAX_IMAGE_DIM}px dimension limit: {raw_path} is {width}x{height}")


def check_path_list(label: str, value: Any, bases: list[Path], errors: list[str], image: bool = False) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return
    for index, raw_path in enumerate(value):
        if image:
            check_image_path(f"{label}[{index}]", raw_path, bases, errors)
        elif not is_nonempty_string(raw_path) or resolve_path(raw_path, bases) is None:
            errors.append(f"{label}[{index}] missing: {raw_path}")


def column_count(table_id: str, data: dict[str, Any], label: str, errors: list[str]) -> int | None:
    headers = data.get("headers")
    header_levels = data.get("header_levels")
    if headers is not None and header_levels is not None:
        errors.append(f"{table_id}: {label} cannot have both headers and header_levels")
        return None
    if isinstance(headers, list):
        expected = len(headers)
    elif isinstance(header_levels, list) and header_levels and all(isinstance(row, list) for row in header_levels):
        expected = len(header_levels[-1])
    else:
        errors.append(f"{table_id}: {label} must have headers or header_levels")
        return None
    if expected == 0:
        errors.append(f"{table_id}: {label} has zero columns")
        return None
    return expected


def row_width(table_id: str, data: dict[str, Any], label: str, errors: list[str]) -> None:
    expected = column_count(table_id, data, label, errors)
    if expected is None:
        return
    rows = data.get("rows")
    if not isinstance(rows, list):
        errors.append(f"{table_id}: {label}.rows must be a list")
        return
    for r_index, row in enumerate(rows):
        if not isinstance(row, list):
            errors.append(f"{table_id}: {label}.rows[{r_index}] must be a list")
            continue
        if len(row) != expected:
            errors.append(f"{table_id}: {label}.rows[{r_index}] has {len(row)} cells, expected {expected}")
        for c_index, cell in enumerate(row):
            if cell is None:
                errors.append(f"{table_id}: {label}.rows[{r_index}][{c_index}] must be empty string, not null")
            elif not isinstance(cell, str):
                errors.append(f"{table_id}: {label}.rows[{r_index}][{c_index}] must be a string")
            elif "\n" in cell:
                errors.append(f"{table_id}: {label}.rows[{r_index}][{c_index}] contains raw newline")


def structure(data: dict[str, Any]) -> dict[str, int] | None:
    rows = data.get("rows")
    if not isinstance(rows, list):
        return None
    headers = data.get("headers")
    header_levels = data.get("header_levels")
    if isinstance(headers, list):
        cols = len(headers)
        header_count = 1
    elif isinstance(header_levels, list) and header_levels and all(isinstance(row, list) for row in header_levels):
        cols = len(header_levels[-1])
        header_count = len(header_levels)
    else:
        return None
    footnotes = data.get("footnotes")
    return {
        "row_count": len(rows),
        "column_count": cols,
        "header_level_count": header_count,
        "footnote_count": len(footnotes) if isinstance(footnotes, list) else 0,
    }


def check_crop_px(label: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict) or not value:
        errors.append(f"{label}.crop_px must be a non-empty page-keyed object")
        return
    for page_key, box in value.items():
        if not isinstance(page_key, str) or not page_key.startswith("page_"):
            errors.append(f"{label}.crop_px key must look like page_N, got {page_key!r}")
        if not (isinstance(box, list) and len(box) == 4 and all(isinstance(v, int) for v in box)):
            errors.append(f"{label}.crop_px.{page_key} must be [x1, y1, x2, y2]")


def compare_table_payload(table_id: str, decision: dict[str, Any], table_data: dict[str, Any], filename: str, errors: list[str]) -> None:
    for key in ["table_label", "table_number", "title", "pages", "headers", "header_levels", "rows", "footnotes"]:
        if decision.get(key) != table_data.get(key):
            errors.append(f"{table_id}: {filename}.{key} differs from table_decisions.json")
    expected = decision.get("expected_structure")
    actual = structure(table_data)
    if isinstance(expected, dict) and actual is not None and expected != actual:
        errors.append(f"{table_id}: expected_structure {expected} does not match final table structure {actual}")


def validate_edge_checks(table_id: str, item: dict[str, Any], errors: list[str]) -> None:
    edge_checks = item.get("edge_checks")
    if not isinstance(edge_checks, dict):
        errors.append(f"{table_id}: edge_checks must be an object")
        return
    missing = EDGE_KEYS - set(edge_checks)
    if missing:
        errors.append(f"{table_id}: edge_checks missing {sorted(missing)}")
    for edge in sorted(EDGE_KEYS):
        check = edge_checks.get(edge)
        if not isinstance(check, dict):
            errors.append(f"{table_id}: edge_checks.{edge} must be an object")
            continue
        if check.get("status") != "pass":
            errors.append(f"{table_id}: edge_checks.{edge}.status must be pass")
        if not is_nonempty_string(check.get("evidence")):
            errors.append(f"{table_id}: edge_checks.{edge}.evidence must be non-empty")


def keyed_items(data: Any, key: str, id_key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(data, dict):
        return {}
    items = data.get(key)
    if not isinstance(items, list):
        errors.append(f"{label}.{key} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}.{key}[{index}] must be an object")
            continue
        item_id = item.get(id_key)
        if not is_nonempty_string(item_id):
            errors.append(f"{label}.{key}[{index}].{id_key} must be non-empty")
            continue
        if item_id in result:
            errors.append(f"{label}: duplicate {id_key}: {item_id}")
        result[item_id] = item
    return result


def validate_visual_review(data: Any, final_by_id: dict[str, dict[str, Any]], tdir: Path, run_dir: Path, errors: list[str]) -> None:
    if not isinstance(data, dict):
        errors.append("table_visual_review.json must be an object")
        return
    if data.get("status") != "pass":
        errors.append("table_visual_review.json status must be pass for final acceptance")
    tables = data.get("tables")
    if not isinstance(tables, list):
        errors.append("table_visual_review.json.tables must be a list")
        return
    summary = data.get("summary")
    decisions = [item.get("decision") for item in tables if isinstance(item, dict)]
    expected_summary = {
        "table_count": len(decisions),
        "pass_count": sum(1 for item in decisions if item == "pass"),
        "fail_count": sum(1 for item in decisions if item == "fail"),
    }
    if not isinstance(summary, dict):
        errors.append("table_visual_review.json.summary must be an object")
    else:
        for key, expected in expected_summary.items():
            if summary.get(key) != expected:
                errors.append(f"table_visual_review.json.summary.{key} must be {expected}")

    reviewed_ids: set[str] = set()
    bases = [tdir, run_dir, Path.cwd()]
    for index, item in enumerate(tables):
        if not isinstance(item, dict):
            errors.append(f"table_visual_review.tables[{index}] must be an object")
            continue
        table_id = item.get("table_id")
        if not is_nonempty_string(table_id):
            errors.append(f"table_visual_review.tables[{index}].table_id must be non-empty")
            continue
        if table_id in reviewed_ids:
            errors.append(f"duplicate table_id in table_visual_review: {table_id}")
        reviewed_ids.add(table_id)
        final = final_by_id.get(table_id)
        if final is None:
            errors.append(f"{table_id}: visual review has no matching final table")
        for field in REVIEW_PREVIEW_FIELDS:
            check_path_list(f"{table_id}: {field}", item.get(field), bases, errors, image=True)
            if field in {"source_edge_previews_read", "crop_edge_previews_read"}:
                paths = item.get(field)
                if isinstance(paths, list) and len(paths) < 4:
                    errors.append(f"{table_id}: {field} must include top, bottom, left, and right edge evidence")
        hashes = item.get("crop_hashes")
        if not isinstance(hashes, dict):
            errors.append(f"{table_id}: crop_hashes must be an object")
        elif final is not None:
            for filename in final.get("image_files", []):
                if not isinstance(filename, str):
                    continue
                crop_path = tdir / filename
                if not crop_path.exists():
                    errors.append(f"{table_id}: crop missing for hash check: {filename}")
                    continue
                if hashes.get(filename) != file_sha256(crop_path):
                    errors.append(f"{table_id}: stale visual review hash for {filename}")
        checks = item.get("checks")
        if not isinstance(checks, dict):
            errors.append(f"{table_id}: checks must be an object")
        else:
            for key in REQUIRED_CHECKS:
                if checks.get(key) != "pass":
                    errors.append(f"{table_id}: checks.{key} must be pass")
        if item.get("decision") != "pass":
            errors.append(f"{table_id}: decision must be pass")
        if item.get("defects") not in ([], None):
            errors.append(f"{table_id}: defects must be empty for passing review")
        expected_structure = item.get("expected_structure")
        observed_structure = item.get("observed_structure")
        if not isinstance(expected_structure, dict) or not isinstance(observed_structure, dict):
            errors.append(f"{table_id}: expected_structure and observed_structure must be objects")
        elif expected_structure != observed_structure:
            errors.append(f"{table_id}: observed_structure does not match expected_structure")
        elif final is not None:
            table_files = final.get("table_files")
            if isinstance(table_files, list) and table_files:
                table_path = tdir / table_files[0]
                table_data = load_json(table_path, errors)
                if isinstance(table_data, dict):
                    actual = structure(table_data)
                    if actual is not None and expected_structure != actual:
                        errors.append(f"{table_id}: review expected_structure does not match final table structure")
        validate_edge_checks(table_id, item, errors)
        notes = item.get("notes")
        if not isinstance(notes, list) or not any(is_nonempty_string(note) for note in notes):
            errors.append(f"{table_id}: notes must describe the passing evidence")
    if reviewed_ids != set(final_by_id):
        errors.append(f"table/final id mismatch: visual={sorted(reviewed_ids)} final={sorted(final_by_id)}")


def validate(path: Path, require_visual_review: bool = True, canonical_dir: Path | None = None, review_json: Path | None = None) -> dict[str, Any]:
    tdir = canonical_dir or tables_dir(path)
    run_dir = infer_run_dir(tdir)
    errors: list[str] = []
    warnings: list[str] = []
    index = load_json(tdir / "table_index.json", errors)
    decisions = load_json(tdir / "table_decisions.json", errors)
    manifest = load_json(tdir / "tables.json", errors)
    if index is None or decisions is None or manifest is None:
        return {"tables_dir": str(tdir), "status": "fail", "table_count": 0, "errors": errors, "warnings": warnings}
    index_by_id = keyed_items(index, "tables", "table_id", "table_index.json", errors)
    decisions_by_id = keyed_items(decisions, "tables", "table_id", "table_decisions.json", errors)
    final_by_id = keyed_items(manifest, "tables", "table_id", "tables.json", errors)
    if set(index_by_id) != set(decisions_by_id):
        errors.append(f"index/decision table_id mismatch: index={sorted(index_by_id)} decisions={sorted(decisions_by_id)}")
    if set(decisions_by_id) != set(final_by_id):
        errors.append(f"decision/final table_id mismatch: decisions={sorted(decisions_by_id)} final={sorted(final_by_id)}")
    bases = [tdir, run_dir, Path.cwd()]
    for table_id, item in final_by_id.items():
        check_crop_px(f"{table_id}: tables.json", item.get("crop_px"), errors)
        for filename in item.get("image_files", []):
            if not isinstance(filename, str) or not (tdir / filename).exists():
                errors.append(f"{table_id}: missing image file {filename}")
        table_files = item.get("table_files")
        if not isinstance(table_files, list) or not table_files:
            errors.append(f"{table_id}: table_files must be a non-empty list")
        else:
            for filename in table_files:
                if not isinstance(filename, str):
                    errors.append(f"{table_id}: table_files contains non-string path")
                    continue
                table_path = tdir / filename
                table_data = load_json(table_path, errors)
                if isinstance(table_data, dict):
                    row_width(table_id, table_data, filename, errors)
                    decision = decisions_by_id.get(table_id)
                    if decision is not None:
                        compare_table_payload(table_id, decision, table_data, filename, errors)
        for field in PREVIEW_FIELDS:
            if field in item:
                check_path_list(f"{table_id}: {field}", item.get(field), bases, errors, image=True)
        verification = item.get("verification")
        if isinstance(verification, dict):
            if verification.get("result") != "pass":
                errors.append(f"{table_id}: verification.result must be pass")
        else:
            errors.append(f"{table_id}: verification must be an object")
    for table_id, item in decisions_by_id.items():
        row_width(table_id, item, "table_decisions.json", errors)
        check_crop_px(f"{table_id}: table_decisions.json", item.get("crop_px"), errors)
        indexed = index_by_id.get(table_id)
        if indexed is not None:
            for key in ["table_label", "table_number", "title", "pages", "candidate_ids"]:
                if indexed.get(key) != item.get(key):
                    errors.append(f"{table_id}: table_index.json.{key} differs from table_decisions.json")
    # CSV is optional during mechanical validation but required for final acceptance.
    for table_id, item in final_by_id.items():
        csv_files = item.get("csv_files")
        csv_issues = errors if require_visual_review else warnings
        if not isinstance(csv_files, list) or not csv_files:
            csv_issues.append(f"{table_id}: csv_files is empty or missing")
        elif isinstance(csv_files, list):
            for csv_file in csv_files:
                if isinstance(csv_file, str) and not (tdir / csv_file).exists():
                    csv_issues.append(f"{table_id}: csv file missing: {csv_file}")
    # Footnote marker consistency
    MARKER_CHARS = set("ᵃᵇᶜᵈᵉ*†‡§‖¶#")
    for table_id, item in final_by_id.items():
        table_files = item.get("table_files")
        if not isinstance(table_files, list) or not table_files:
            continue
        table_path = tdir / table_files[0]
        table_data = load_json(table_path, [])
        if not isinstance(table_data, dict):
            continue
        cell_has_markers = False
        for row in table_data.get("rows", []):
            if isinstance(row, list):
                for cell in row:
                    if isinstance(cell, str) and any(c in cell for c in MARKER_CHARS):
                        cell_has_markers = True
                        break
            if cell_has_markers:
                break
        if not cell_has_markers:
            headers = table_data.get("headers") or []
            header_levels = table_data.get("header_levels") or []
            all_headers = headers if headers else [c for level in header_levels for c in (level if isinstance(level, list) else [])]
            for h in all_headers:
                if isinstance(h, str) and any(c in h for c in MARKER_CHARS):
                    cell_has_markers = True
                    break
        if cell_has_markers:
            footnotes = table_data.get("footnotes", [])
            if isinstance(footnotes, list) and footnotes:
                has_marker_footnote = any(
                    isinstance(fn, str) and fn and fn[0] in MARKER_CHARS
                    for fn in footnotes
                )
                if not has_marker_footnote:
                    warnings.append(f"{table_id}: cells contain marker characters but no footnote starts with a marker")

    if require_visual_review:
        review = load_json(review_json or tdir / "table_visual_review.json", errors)
        if review is not None:
            validate_visual_review(review, final_by_id, tdir, run_dir, errors)
    return {
        "tables_dir": str(tdir),
        "status": "pass" if not errors else "fail",
        "table_count": len(final_by_id),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", nargs="?", help="Deprecated legacy run directory or tables directory")
    parser.add_argument("--canonical-dir", help="Explicit canonical tables directory")
    parser.add_argument("--review-json", help="Explicit merged review JSON path for final validation")
    parser.add_argument("--mechanical-only", action="store_true", help="Skip table_visual_review.json checks")
    parser.add_argument("--write", help="Optional path to write validation JSON")
    args = parser.parse_args()
    if args.canonical_dir:
        output_dir = Path(args.output_dir) if args.output_dir else Path(args.canonical_dir)
        result = validate(output_dir, require_visual_review=not args.mechanical_only, canonical_dir=Path(args.canonical_dir), review_json=Path(args.review_json) if args.review_json else None)
    else:
        if not args.output_dir:
            parser.error("provide --canonical-dir or legacy output_dir")
        print("warning: positional output_dir mode is deprecated; use --canonical-dir", file=sys.stderr)
        result = validate(Path(args.output_dir), require_visual_review=not args.mechanical_only)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    if result["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
