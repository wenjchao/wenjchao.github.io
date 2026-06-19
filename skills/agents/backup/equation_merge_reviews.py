#!/usr/bin/env python3
"""Merge N per-reviewer visual_review.json files into one combined review.

The merged review has reviewer_id="merged" and recomputed summary.  It is a
valid equation_review.v1 that downstream scripts (check_review_gate.py,
build_repair_request.py) can consume unchanged.

Usage:
    python merge_reviews.py \
        review_01.json review_02.json review_03.json \
        --review-round round_00 \
        --output merged_visual_review.json

Exit codes:
    0  success
    1  integrity error (duplicate equation_id, round mismatch)
    2  input error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge per-reviewer visual_review.json files"
    )
    parser.add_argument("reviews", nargs="+", help="Paths to visual_review.json files")
    parser.add_argument("--review-round", required=True, help="Expected review round")
    parser.add_argument("--output", help="Output path (default: stdout)")
    args = parser.parse_args()

    all_equations: list[dict] = []
    seen_equation_ids: set[str] = set()
    errors: list[str] = []
    source_reviews: list[str] = []

    for review_path in args.reviews:
        try:
            with open(review_path, "r", encoding="utf-8") as f:
                review = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(json.dumps({"status": "error", "reason": f"{review_path}: {exc}"},
                             indent=2), file=sys.stderr)
            return 2

        if review.get("schema_version") != "equation_review.v1":
            errors.append(f"{review_path}: schema_version is not equation_review.v1")

        if review.get("review_round") != args.review_round:
            errors.append(
                f"{review_path}: review_round is '{review.get('review_round')}', "
                f"expected '{args.review_round}'"
            )

        source_reviews.append(review_path)

        for fig in review.get("equations", []):
            equation_id = fig.get("equation_id", "")
            if equation_id in seen_equation_ids:
                errors.append(f"duplicate equation_id '{equation_id}' across input reviews")
            seen_equation_ids.add(equation_id)
            all_equations.append(fig)

    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2,
                         ensure_ascii=False), file=sys.stderr)
        return 1

    all_equations.sort(key=lambda f: f.get("equation_id", ""))

    pass_count = sum(1 for f in all_equations if f.get("decision") == "pass")
    fail_count = sum(1 for f in all_equations if f.get("decision") == "fail")
    finding_count = sum(len(f.get("findings", [])) for f in all_equations)
    status = "fail" if fail_count > 0 else "pass"

    merged = {
        "schema_version": "equation_review.v1",
        "review_round": args.review_round,
        "reviewer_id": "merged",
        "status": status,
        "equations": all_equations,
        "summary": {
            "equation_count": len(all_equations),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "finding_count": finding_count,
        },
    }

    output_text = json.dumps(merged, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output_text, encoding="utf-8")
        result = {
            "status": "ok",
            "review_round": args.review_round,
            "source_reviews": source_reviews,
            "equation_count": len(all_equations),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "finding_count": finding_count,
            "merged_status": status,
            "written": args.output,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
