#!/usr/bin/env python3
"""Check review gate: read visual_review.json and report pass/fail/blocked.

Usage:
    python check_review_gate.py <visual_review_json>

Exit codes:
    0  all equations pass → lane can close
    1  has required findings → needs repair
    2  blocked (no actionable findings, or structural issues)
    3  input error

Stdout JSON includes the gate decision and, if failing, the equation IDs
and finding count that need repair.
"""

from __future__ import annotations

import argparse
import json
import sys


def check_gate(review: dict) -> dict:
    status = review.get("status")
    equations = review.get("equations", [])

    if not equations:
        return {"gate": "blocked", "reason": "equations array is empty"}

    if status == "pass":
        for fig in equations:
            if fig.get("decision") != "pass":
                return {
                    "gate": "blocked",
                    "reason": f"top-level status is pass but {fig.get('equation_id')} decision is {fig.get('decision')}",
                }
        return {"gate": "pass", "equation_count": len(equations)}

    if status != "fail":
        return {"gate": "blocked", "reason": f"unexpected status: {status}"}

    required_findings = []
    advisory_findings = []
    failed_equations = []

    for fig in review.get("equations", []):
        if fig.get("decision") != "fail":
            continue
        failed_equations.append(fig.get("equation_id"))
        for finding in fig.get("findings", []):
            if finding.get("severity") == "required":
                required_findings.append(finding.get("finding_id"))
            elif finding.get("severity") == "advisory":
                advisory_findings.append(finding.get("finding_id"))

    if not failed_equations:
        return {"gate": "blocked", "reason": "status is fail but no failed equations"}

    if not required_findings:
        return {
            "gate": "blocked",
            "reason": "failed equations exist but no required findings — cannot build repair request",
            "failed_equations": failed_equations,
        }

    return {
        "gate": "needs_repair",
        "failed_equations": failed_equations,
        "required_finding_count": len(required_findings),
        "advisory_finding_count": len(advisory_findings),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check review gate")
    parser.add_argument("visual_review_json", help="Path to visual_review.json")
    args = parser.parse_args()

    try:
        with open(args.visual_review_json, "r", encoding="utf-8") as f:
            review = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"gate": "error", "reason": str(exc)}, indent=2),
              file=sys.stderr)
        return 3

    result = check_gate(review)
    print(json.dumps(result, indent=2))

    gate = result["gate"]
    if gate == "pass":
        return 0
    elif gate == "needs_repair":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
