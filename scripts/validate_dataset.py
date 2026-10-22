"""Validate a CSV and print actionable schema/quality details."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from attrition_app.data_loader import DataValidationError, load_csv, quality_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an employee attrition CSV.")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    args = parser.parse_args()
    try:
        frame = load_csv(args.input, require_target=False)
        report = quality_report(frame)
        print("VALID CSV (readable and structurally non-empty)")
        print(json.dumps(report.to_dict(), indent=2))
        if "Attrition" not in frame.columns:
            print("ACTION: Attrition target is absent; this file can support prediction inputs but not supervised training.")
        elif report.target_counts and all(report.target_counts.values()):
            print("Target check: both normalized classes present.")
        else:
            print("ACTION: Review Attrition labels; training requires both Yes and No classes.")
        return 0
    except (DataValidationError, OSError) as exc:
        print(f"INVALID CSV: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
