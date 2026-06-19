#!/usr/bin/env python3
"""Split repair requests into N assignments for parallel repair workers.

Groups requests by table_id (all requests for the same table go to one
worker), then uses greedy balancing to distribute table groups evenly by
request count.

Usage:
    python divide_repair_requests.py <repair_requests_merged.json> \
        --workers 3 \
        --output-dir <paper_dir>/tables/repairs/round_01

Exit codes:
    0  success
    2  input error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def greedy_assign(
    table_groups: list[tuple[str, list[dict]]],
    n: int,
) -> list[list[tuple[str, list[dict]]]]:
    """Assign table groups to workers by greedy load balancing."""
    buckets: list[list[tuple[str, list[dict]]]] = [[] for _ in range(n)]
    loads = [0] * n

    for table_id, requests in sorted(table_groups, key=lambda x: -len(x[1])):
        lightest = min(range(n), key=lambda i: loads[i])
        buckets[lightest].append((table_id, requests))
        loads[lightest] += len(requests)

    return [b for b in buckets if b]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split repair requests into N assignments"
    )
    parser.add_argument("repair_requests_json",
                        help="Path to repair_requests_merged.json")
    parser.add_argument("--workers", type=int, required=True,
                        help="Number of parallel repair workers")
    parser.add_argument("--output-dir", required=True,
                        help="Output directory (e.g. repairs/round_01)")
    args = parser.parse_args()

    try:
        with open(args.repair_requests_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, indent=2),
              file=sys.stderr)
        return 2

    requests = data.get("requests", [])
    if not requests:
        print(json.dumps({"status": "error", "reason": "no requests"}, indent=2),
              file=sys.stderr)
        return 2

    by_table: dict[str, list[dict]] = {}
    for req in requests:
        fig_id = req.get("table_id", "")
        by_table.setdefault(fig_id, []).append(req)

    table_groups = list(by_table.items())
    workers = min(args.workers, len(table_groups))
    if workers < args.workers:
        print(f"Warning: reduced workers from {args.workers} to {workers} "
              f"(only {len(table_groups)} tables with requests)", file=sys.stderr)

    buckets = greedy_assign(table_groups, workers)
    output_dir = Path(args.output_dir)
    assignments = []

    for idx, bucket in enumerate(buckets):
        repair_id = f"repair_{idx + 1:02d}"
        table_ids = [fig_id for fig_id, _ in bucket]
        worker_requests = []
        for _, reqs in bucket:
            for req in reqs:
                req_copy = dict(req)
                req_copy["assigned_repair_id"] = repair_id
                worker_requests.append(req_copy)

        request_ids = [r["request_id"] for r in worker_requests]

        sub_request = {
            "schema_version": data.get("schema_version", "table_repair.v1"),
            "repair_round": data.get("repair_round"),
            "source_reviews": data.get("source_reviews", []),
            "assignments": [
                {
                    "repair_id": repair_id,
                    "table_ids": table_ids,
                    "request_ids": request_ids,
                }
            ],
            "requests": worker_requests,
        }

        repair_dir = output_dir / repair_id
        repair_dir.mkdir(parents=True, exist_ok=True)
        request_path = repair_dir / "repair_requests_assigned.json"
        with open(request_path, "w", encoding="utf-8") as f:
            json.dump(sub_request, f, indent=2, ensure_ascii=False)

        assignments.append({
            "repair_id": repair_id,
            "table_ids": table_ids,
            "request_ids": request_ids,
            "request_count": len(worker_requests),
            "request_file": str(request_path),
        })

    result = {
        "status": "ok",
        "repair_round": data.get("repair_round"),
        "workers": len(buckets),
        "assignments": assignments,
        "total_requests": len(requests),
        "total_tables": len(table_groups),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
