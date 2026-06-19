#!/usr/bin/env python3
"""Convert Table_<N>.json artifacts to CSV files.

Usage:
    convert_to_csv.py <tables_dir>           # batch: converts all Table_*.json
    convert_to_csv.py <Table_N.json> <out>   # single file
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def convert_one(json_path: Path, csv_path: Path) -> dict:
    table = json.loads(json_path.read_text(encoding="utf-8"))

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if table.get("header_levels"):
            for level in table["header_levels"]:
                writer.writerow(level)
        elif table.get("headers"):
            writer.writerow(table["headers"])

        for row in table.get("rows", []):
            writer.writerow(row)

        if table.get("footnotes"):
            writer.writerow([])
            for fn in table["footnotes"]:
                writer.writerow([fn])

    return {
        "input": str(json_path),
        "output": str(csv_path),
        "table_id": table.get("table_id") or json_path.stem,
    }


def _manifest_csv_path(csv_path: Path, tables_dir: Path) -> str:
    try:
        return csv_path.relative_to(tables_dir).as_posix()
    except ValueError:
        return str(csv_path)


def update_manifest_csv_refs(tables_dir: Path, results: list[dict]) -> list[str]:
    csv_by_id = {}
    for result in results:
        table_id = result.get("table_id")
        output = result.get("output")
        if isinstance(table_id, str) and isinstance(output, str):
            csv_by_id[table_id] = [_manifest_csv_path(Path(output), tables_dir)]

    updated = []
    for manifest_name in ["tables.json", "table_decisions.json"]:
        manifest_path = tables_dir / manifest_name
        if not manifest_path.exists():
            continue
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        tables = data.get("tables")
        if not isinstance(tables, list):
            continue
        changed = False
        for item in tables:
            if not isinstance(item, dict):
                continue
            csv_files = csv_by_id.get(item.get("table_id"))
            if csv_files is not None and item.get("csv_files") != csv_files:
                item["csv_files"] = csv_files
                changed = True
        if changed:
            manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            updated.append(str(manifest_path))
    return updated


def convert_dir(tables_dir: Path) -> list[dict]:
    results = []
    for json_path in sorted(tables_dir.glob("Table_*.json")):
        csv_path = json_path.with_suffix(".csv")
        results.append(convert_one(json_path, csv_path))
    updated = update_manifest_csv_refs(tables_dir, results)
    for result in results:
        result["manifests_updated"] = updated
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Table_N.json file or tables directory")
    parser.add_argument("output", nargs="?", help="Output CSV path (single-file mode only)")
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        csv_path = Path(args.output) if args.output else input_path.with_suffix(".csv")
        results = [convert_one(input_path, csv_path)]
        updated = update_manifest_csv_refs(input_path.parent, results)
        for result in results:
            result["manifests_updated"] = updated
    elif input_path.is_dir():
        results = convert_dir(input_path)
    else:
        raise SystemExit(f"Not found: {input_path}")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
