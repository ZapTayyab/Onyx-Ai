#!/usr/bin/env python3
"""Generate a full backend audit report from the synthetic customer corpus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_services import AuditService
from config import get_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SNT AI backend audit report")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible runs")
    parser.add_argument(
        "--failure-rate",
        type=float,
        help="Failure injection rate between 0.0 and 1.0 (default from config)",
    )
    parser.add_argument("--corpus", type=Path, help="Path to synthetic customer JSON corpus")
    parser.add_argument("--output", type=Path, help="Output report path")
    args = parser.parse_args()

    config = get_config()
    service = AuditService(config)
    seed = args.seed if args.seed is not None else config.default_seed
    failure_rate = (
        args.failure_rate if args.failure_rate is not None else config.default_failure_rate
    )
    corpus_path = args.corpus or config.corpus_path
    output_path = args.output or config.report_output_path

    results, report_text, summary = service.run_audit(
        failure_rate=failure_rate,
        seed=seed,
        corpus_path=corpus_path,
    )
    service.persist_report(report_text, output_path)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(report_text)
    print(f"\nSaved: {output_path.resolve()}")
    print(
        f"Summary — score={summary.score}% sessions={summary.total_sessions} "
        f"flagged={summary.flagged_sessions} turns={summary.total_turns} "
        f"breaches={summary.failed_turns}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
