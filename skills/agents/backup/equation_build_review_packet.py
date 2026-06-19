#!/usr/bin/env python3
"""Build review_packet.json from canonical equations.json.

Usage:
    python build_review_packet.py \
        <canonical_equations_json> \
        --review-round round_00 \
        --paper-dir <paper_dir> \
        --output <output_path>

--paper-dir is used to verify that referenced preview files exist.

Exit codes:
    0  success
    1  missing canonical files detected
    2  input error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def build_review_packet(
    equations_data: dict,
    review_round: str,
    reviewer_id: str = "reviewer_01",
    canonical_root: Path | None = None,
) -> tuple[dict, list[str]]:
    """Returns (packet, warnings). Warnings list missing preview files."""
    packet = {
        "schema_version": "equation_review_packet.v1",
        "review_round": review_round,
        "reviewer_id": reviewer_id,
        "canonical_artifact_root": "equations/canonical",
        "equations": [],
    }

    warnings = []

    for fig in equations_data.get("equations", []):
        equation_id = fig.get("equation_id", "")
        pf = {
            "equation_id": equation_id,
            "equation_number": fig.get("equation_number", equation_id),
            "latex": fig.get("latex", ""),
            "rendered_latex_preview": fig.get("rendered_latex_preview", ""),
            "crop_units": [],
        }
        for cu in fig.get("crop_units", []):
            page = cu.get("page")
            pcu = {
                "crop_id": cu.get("crop_id", ""),
                "role": cu.get("role", "complete equation"),
                "page": page,
                "crop_px": cu.get("crop_px", []),
                "source_page": f"shared/pages/page_{page}.png",
                "crop_preview": cu.get("preview", ""),
                "boundary_preview": cu.get("boundary_preview", ""),
                "top_band": cu.get("top_band", []),
                "left_band": cu.get("left_band", []),
                "right_band": cu.get("right_band", []),
                "bottom_band": cu.get("bottom_band", []),
                "bottom_micro": cu.get("bottom_micro", []),
            }

            if canonical_root:
                for field in ("crop_preview", "boundary_preview"):
                    path = pcu[field]
                    if path and not (canonical_root / path).exists():
                        warnings.append(f"{equation_id}/{cu.get('crop_id')}.{field}: "
                                        f"missing {path}")
                for field in ("top_band", "left_band", "right_band",
                              "bottom_band", "bottom_micro"):
                    for p in pcu[field]:
                        if not (canonical_root / p).exists():
                            warnings.append(f"{equation_id}/{cu.get('crop_id')}.{field}: "
                                            f"missing {p}")

            pf["crop_units"].append(pcu)
        packet["equations"].append(pf)

    return packet, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build review_packet.json from canonical equations.json"
    )
    parser.add_argument("equations_json", help="Path to canonical equations.json")
    parser.add_argument("--review-round", required=True)
    parser.add_argument("--reviewer-id", default="reviewer_01")
    parser.add_argument("--paper-dir",
                        help="Paper directory (for verifying canonical files exist)")
    parser.add_argument("--output", help="Output path (default: stdout)")
    args = parser.parse_args()

    try:
        with open(args.equations_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, indent=2),
              file=sys.stderr)
        return 2

    canonical_root = None
    if args.paper_dir:
        canonical_root = Path(args.paper_dir) / "equations" / "canonical"

    packet, warnings = build_review_packet(
        data, args.review_round, args.reviewer_id, canonical_root
    )

    if warnings:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)

    output_text = json.dumps(packet, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_text, encoding="utf-8")
        count = len(packet["equations"])
        print(f"Wrote {args.output} ({count} equations)", file=sys.stderr)
    else:
        print(output_text)

    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
