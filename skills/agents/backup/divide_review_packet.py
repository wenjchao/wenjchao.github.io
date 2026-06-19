#!/usr/bin/env python3
"""Split a review packet into N sub-packets for parallel reviewers.

Each sub-packet gets a disjoint, consecutive subset of figures and is a valid
figure_review_packet.v1.  The assignment manifest is printed to stdout.

Usage:
    python divide_review_packet.py <review_packet.json> \
        --workers 3 \
        --output-dir <paper_dir>/figures/reviewers/round_00

Exit codes:
    0  success
    2  input error
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def divide(figures: list[dict], n: int) -> list[list[dict]]:
    per_worker = math.ceil(len(figures) / n)
    return [figures[i : i + per_worker] for i in range(0, len(figures), per_worker)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split review packet into N sub-packets"
    )
    parser.add_argument("review_packet_json", help="Path to full review_packet.json")
    parser.add_argument("--workers", type=int, required=True, help="Number of parallel reviewers")
    parser.add_argument("--output-dir", required=True, help="Output directory (e.g. reviewers/round_00)")
    args = parser.parse_args()

    try:
        with open(args.review_packet_json, "r", encoding="utf-8") as f:
            packet = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, indent=2),
              file=sys.stderr)
        return 2

    figures = packet.get("figures", [])
    if not figures:
        print(json.dumps({"status": "error", "reason": "no figures in packet"}, indent=2),
              file=sys.stderr)
        return 2

    workers = min(args.workers, len(figures))
    if workers < args.workers:
        print(f"Warning: reduced workers from {args.workers} to {workers} "
              f"(only {len(figures)} figures)", file=sys.stderr)

    groups = divide(figures, workers)
    output_dir = Path(args.output_dir)
    assignments = []

    for idx, group in enumerate(groups):
        reviewer_id = f"reviewer_{idx + 1:02d}"
        sub_packet = {
            "schema_version": packet.get("schema_version", "figure_review_packet.v1"),
            "review_round": packet.get("review_round"),
            "reviewer_id": reviewer_id,
            "canonical_artifact_root": packet.get("canonical_artifact_root"),
            "figures": group,
        }

        reviewer_dir = output_dir / reviewer_id
        reviewer_dir.mkdir(parents=True, exist_ok=True)
        packet_path = reviewer_dir / "review_packet.json"
        with open(packet_path, "w", encoding="utf-8") as f:
            json.dump(sub_packet, f, indent=2, ensure_ascii=False)

        assignments.append({
            "reviewer_id": reviewer_id,
            "figure_ids": [fig.get("figure_id") for fig in group],
            "packet_path": str(packet_path),
            "figure_count": len(group),
        })

    result = {
        "status": "ok",
        "review_round": packet.get("review_round"),
        "workers": workers,
        "assignments": assignments,
        "total_figures": len(figures),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
