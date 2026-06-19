#!/usr/bin/env python3
"""Build repair_requests_merged.json from a visual_review.json.

Mechanically converts required findings into repair requests. No visual
judgment — just field mapping.

Usage:
    python build_repair_request.py \
        <visual_review_json> \
        --repair-round round_02 \
        --canonical-tables <canonical/tables.json> \
        --output <output_path>

--canonical-tables is needed to resolve null crop_id on multi-crop tables.
If omitted, null crop_id will block unless the table has only one
reviewed_crop_unit.

Exit codes:
    0  success (wrote requests or no required findings)
    1  blocked (human_check, unknown hint, unresolvable null crop_id)
    2  input error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HINT_TO_ACTION = {
    "expand_top": "recrop",
    "expand_bottom": "recrop",
    "expand_left": "recrop",
    "expand_right": "recrop",
    "shrink_top": "recrop",
    "shrink_bottom": "recrop",
    "shrink_left": "recrop",
    "shrink_right": "recrop",
    "recrop": "recrop",
    "split_crop": "recrop",
    "merge_crop": "recrop",
    "regenerate_preview": "regenerate_missing_preview",
    "manifest_check": "manifest_correction",
    "split_header_level": "fix_structure",
    "merge_wrapped_cell": "fix_structure",
    "split_false_row": "fix_structure",
    "correct_cell_text": "fix_structure",
    "add_missing_footnote": "fix_structure",
    "fix_title_separator": "fix_structure",
    "fix_sub_column": "fix_structure",
    "remove_false_footnote": "fix_structure",
}

BLOCKED_HINTS = {"human_check"}


def build_repair_request(
    visual_review: dict,
    repair_round: str,
    repair_id: str = "repair_01",
    canonical_tables: dict | None = None,
) -> dict:
    """Returns {"status": "ok", "result": ...} or {"status": "blocked", ...}
    or {"status": "no_required_findings"}."""

    review_round = visual_review.get("review_round", "")
    reviewer_id = visual_review.get("reviewer_id", "")
    source_review = f"reviews/{review_round}/{reviewer_id}/visual_review.json"

    # Build crop_unit count lookup from canonical tables.json
    canonical_crop_counts: dict[str, list[str]] = {}
    if canonical_tables:
        for fig in canonical_tables.get("tables", []):
            fid = fig.get("table_id", "")
            canonical_crop_counts[fid] = [
                cu.get("crop_id", "") for cu in fig.get("crop_units", [])
            ]

    requests = []
    table_ids = []

    for fig in visual_review.get("tables", []):
        if fig.get("decision") != "fail":
            continue

        table_id = fig.get("table_id")
        if not table_id:
            return {"status": "blocked", "reason": "table missing table_id"}

        for finding in fig.get("findings", []):
            if finding.get("severity") != "required":
                continue

            finding_id = finding.get("finding_id")
            if not finding_id:
                return {"status": "blocked",
                        "reason": f"finding in {table_id} missing finding_id"}

            hint = finding.get("repair_hint", "")

            if hint in BLOCKED_HINTS:
                return {"status": "blocked",
                        "reason": f"{finding_id}: repair_hint is {hint}, "
                                  "requires human intervention"}

            action = HINT_TO_ACTION.get(hint)
            if action is None:
                return {"status": "blocked",
                        "reason": f"{finding_id}: unknown repair_hint '{hint}'"}

            crop_id = finding.get("crop_id")
            if crop_id:
                crop_ids = [crop_id]
            elif action == "fix_structure":
                crop_ids = [None]
            else:
                # Try canonical tables.json first
                canonical_crops = canonical_crop_counts.get(table_id, [])
                if len(canonical_crops) == 1:
                    crop_ids = [canonical_crops[0]]
                else:
                    # Fallback to reviewed_crop_units
                    reviewed = fig.get("reviewed_crop_units", [])
                    if len(reviewed) == 1:
                        crop_ids = [reviewed[0].get("crop_id", "")]
                    else:
                        n = len(canonical_crops) or len(reviewed)
                        return {"status": "blocked",
                                "reason": f"{finding_id}: crop_id is null and "
                                          f"table has {n} crop units, "
                                          "cannot auto-assign"}

            direction = [hint]

            defects = []
            problem = finding.get("problem", "")
            edge = finding.get("edge")
            if problem and edge and edge != "null":
                defects.append(f"{problem}: {edge}")
            elif problem:
                defects.append(problem)

            request = {
                "request_id": finding_id,
                "assigned_repair_id": repair_id,
                "table_id": table_id,
                "table_label": fig.get("table_label", table_id),
                "crop_ids": crop_ids,
                "source_review": source_review,
                "source_finding_id": finding_id,
                "action": action,
                "direction": direction,
                "constraint": finding.get("notes", ""),
                "defects": defects,
            }
            requests.append(request)

            if table_id not in table_ids:
                table_ids.append(table_id)

    if not requests:
        return {"status": "no_required_findings"}

    request_ids = [r["request_id"] for r in requests]

    result = {
        "schema_version": "table_repair.v1",
        "repair_round": repair_round,
        "source_reviews": [source_review],
        "assignments": [
            {
                "repair_id": repair_id,
                "table_ids": table_ids,
                "request_ids": request_ids,
            }
        ],
        "requests": requests,
    }

    return {"status": "ok", "result": result}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build repair_requests_merged.json from visual_review.json"
    )
    parser.add_argument("visual_review_json", help="Path to visual_review.json")
    parser.add_argument("--repair-round", required=True,
                        help="Repair round name, e.g. round_02")
    parser.add_argument("--repair-id", default="repair_01",
                        help="Repair worker ID (default: repair_01)")
    parser.add_argument("--canonical-tables",
                        help="Path to canonical tables.json (for null crop_id resolution)")
    parser.add_argument("--output", help="Output path (default: stdout)")
    args = parser.parse_args()

    try:
        with open(args.visual_review_json, "r", encoding="utf-8") as f:
            review = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, indent=2),
              file=sys.stderr)
        return 2

    canonical_tables = None
    if args.canonical_tables:
        try:
            with open(args.canonical_tables, "r", encoding="utf-8") as f:
                canonical_tables = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(json.dumps({"status": "error",
                              "reason": f"cannot read canonical tables: {exc}"},
                             indent=2), file=sys.stderr)
            return 2

    outcome = build_repair_request(
        review, args.repair_round, args.repair_id, canonical_tables
    )

    if outcome["status"] == "blocked":
        print(json.dumps(outcome, indent=2), file=sys.stderr)
        return 1

    if outcome["status"] == "no_required_findings":
        print(json.dumps(outcome, indent=2))
        return 0

    result = outcome["result"]
    output_text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_text, encoding="utf-8")
        print(f"Wrote {args.output} ({len(result['requests'])} requests)",
              file=sys.stderr)
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
