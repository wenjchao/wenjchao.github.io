#!/usr/bin/env python3
"""Build manifest_patches[] from repair intents by reading canonical old_values.

Repair agent provides intents (equation_id, crop_id, field, new_value). This tool
reads canonical equations.json and equation_decisions.json, looks up the current
value of each field, and produces paired patches for both manifests.

Usage:
    python build_manifest_patches.py \
        --canonical <canonical_dir> \
        --intents <intents_json_path>

    # or pipe intents via stdin:
    echo '[{"equation_id": "F1", "crop_id": "F1", "field": "crop_px", "new_value": [0,0,100,100]}]' \
        | python build_manifest_patches.py --canonical <canonical_dir>

Exit codes:
    0  success (patches written to stdout)
    1  some intents could not be resolved (errors on stderr, valid patches still on stdout)
    2  input error (cannot read canonical or intents)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MANIFEST_FILES = ("equations.json",)

ALLOWED_FIELDS = {
    "crop_px",
    "image_file",
    "preview",
    "boundary_preview",
    "top_band",
    "left_band",
    "right_band",
    "bottom_band",
    "bottom_micro",
    "role",
}


def load_manifest(canonical: Path, filename: str) -> dict | None:
    path = canonical / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_crop_unit(
    data: dict, equation_id: str, crop_id: str
) -> dict | None:
    fig = next(
        (f for f in data.get("equations", []) if f.get("equation_id") == equation_id),
        None,
    )
    if fig is None:
        return None
    return next(
        (c for c in fig.get("crop_units", []) if c.get("crop_id") == crop_id),
        None,
    )


def build_patches(
    intents: list[dict],
    manifests: dict[str, dict],
) -> tuple[list[dict], list[str]]:
    patches: list[dict] = []
    errors: list[str] = []

    for intent in intents:
        equation_id = intent.get("equation_id")
        crop_id = intent.get("crop_id")
        field = intent.get("field")
        new_value = intent.get("new_value")

        if not equation_id or not crop_id or not field:
            errors.append(
                f"incomplete intent: equation_id={equation_id}, "
                f"crop_id={crop_id}, field={field}"
            )
            continue

        if field not in ALLOWED_FIELDS:
            errors.append(
                f"{equation_id}/{crop_id}: field '{field}' not in allowed list "
                f"({', '.join(sorted(ALLOWED_FIELDS))})"
            )
            continue

        for manifest_file, data in manifests.items():
            cu = find_crop_unit(data, equation_id, crop_id)
            if cu is None:
                errors.append(
                    f"{equation_id}/{crop_id} not found in {manifest_file}"
                )
                continue

            old_value = cu.get(field)

            if old_value == new_value:
                continue

            if old_value is None:
                patches.append({
                    "target_file": manifest_file,
                    "operation": "add_if_missing",
                    "scope": "crop_unit",
                    "selector": {
                        "equation_id": equation_id,
                        "crop_id": crop_id,
                    },
                    "path": f"crop_units[].{field}",
                    "old_value": None,
                    "new_value": new_value,
                })
            else:
                patches.append({
                    "target_file": manifest_file,
                    "operation": "replace",
                    "scope": "crop_unit",
                    "selector": {
                        "equation_id": equation_id,
                        "crop_id": crop_id,
                    },
                    "path": f"crop_units[].{field}",
                    "old_value": old_value,
                    "new_value": new_value,
                })

    return patches, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build manifest patches from repair intents"
    )
    parser.add_argument(
        "--canonical", required=True,
        help="Path to canonical directory containing equations.json and "
             "equation_decisions.json",
    )
    parser.add_argument(
        "--intents",
        help="Path to intents JSON file (default: read from stdin)",
    )
    args = parser.parse_args()

    canonical = Path(args.canonical)

    manifests: dict[str, dict] = {}
    for filename in MANIFEST_FILES:
        data = load_manifest(canonical, filename)
        if data is None:
            print(
                json.dumps({
                    "status": "error",
                    "reason": f"cannot read {canonical / filename}",
                }, indent=2),
                file=sys.stderr,
            )
            return 2
        manifests[filename] = data

    try:
        if args.intents:
            with open(args.intents, "r", encoding="utf-8") as f:
                intents = json.load(f)
        else:
            intents = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as exc:
        print(
            json.dumps({"status": "error", "reason": str(exc)}, indent=2),
            file=sys.stderr,
        )
        return 2

    if not isinstance(intents, list):
        print(
            json.dumps({
                "status": "error",
                "reason": "intents must be a JSON array",
            }, indent=2),
            file=sys.stderr,
        )
        return 2

    patches, errors = build_patches(intents, manifests)

    print(json.dumps(patches, indent=2, ensure_ascii=False))

    if errors:
        print(
            json.dumps({"errors": errors}, indent=2, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
