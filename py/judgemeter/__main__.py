import argparse
import json
import math
import sys
from pathlib import Path

from . import __version__, analyze, compare
from .demo import demo_records
from .report import render_html


def _fraction(value):
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("must be a finite number in [0,1]")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="judgemeter", description="Analyze repeated fixed-answer judge scores offline."
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    analysis = sub.add_parser("analyze")
    analysis.add_argument("records", type=Path)
    demo = sub.add_parser("demo", help="Generate explicitly synthetic seeded records and a report")
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--records-out", type=Path)
    for cmd in (analysis, demo):
        cmd.add_argument("--threshold", type=_fraction, default=0.5)
        cmd.add_argument("--json", type=Path)
        cmd.add_argument("--html", type=Path)
        cmd.add_argument("--min-agreement", type=_fraction)
        cmd.add_argument("--max-invalid-rate", type=_fraction)
        cmd.add_argument("--max-unusable-rate", type=_fraction)
        cmd.add_argument("--baseline")
        cmd.add_argument("--candidate")
        cmd.add_argument("--max-agreement-drop", type=_fraction)
    args = parser.parse_args(argv)
    try:
        if bool(args.baseline) != bool(args.candidate):
            raise ValueError("--baseline and --candidate must be provided together")
        if args.max_agreement_drop is not None and not args.baseline:
            raise ValueError("--max-agreement-drop requires baseline and candidate")
        if args.command == "demo":
            records = demo_records(args.seed)
        else:
            records = json.loads(
                args.records.read_text(),
                parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"invalid JSON constant: {x}")),
            )
        report = analyze(records, args.threshold)
        if args.command == "demo":
            report["data_kind"] = "synthetic_demo; seeded; no model API calls"
        if args.baseline:
            report["comparison"] = compare(report, args.baseline, args.candidate)
        failures = []
        # With a pair, gates evaluate candidate; otherwise every judge is gated.
        targets = {args.candidate: report["judges"][args.candidate]} if args.candidate else report["judges"]
        for name, judge in targets.items():
            s = judge["summary"]
            if args.min_agreement is not None:
                if (
                    s["macro_agreement"] is None
                    or s["cases_insufficient"]
                    or s["macro_agreement"] < args.min_agreement
                ):
                    failures.append(f"{name}: insufficient case evidence or macro agreement below minimum")
            if args.max_invalid_rate is not None and s["invalid_rate"] > args.max_invalid_rate:
                failures.append(f"{name}: invalid score rate exceeds maximum")
            if args.max_unusable_rate is not None and s["unusable_rate"] > args.max_unusable_rate:
                failures.append(f"{name}: missing + invalid score rate exceeds maximum")
        if args.max_agreement_drop is not None:
            comp = report["comparison"]
            if (
                comp["agreement_delta"] is None
                or comp["baseline_only"]
                or comp["candidate_only"]
                or comp["insufficient_cases"]
            ):
                failures.append("comparison: incomplete matched evidence")
            elif comp["agreement_delta"] < -args.max_agreement_drop:
                failures.append("comparison: candidate agreement drop exceeds maximum")
        report["gate"] = {
            "passed": not failures,
            "failures": failures,
            "policy": {
                k: getattr(args, k)
                for k in ("min_agreement", "max_invalid_rate", "max_unusable_rate", "max_agreement_drop")
            },
        }
        outputs = [(args.json, json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n")]
        if args.html:
            outputs.append((args.html, render_html(report)))
        if args.command == "demo" and args.records_out:
            outputs.append((args.records_out, json.dumps(records, indent=2) + "\n"))
        paths = [path.resolve() for path, _ in outputs if path]
        if len(paths) != len(set(paths)) or (args.command == "analyze" and args.records.resolve() in paths):
            raise ValueError("output paths must be distinct and must not overwrite input records")
        for path, content in outputs:
            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        if not args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
        else:
            print(f"JudgeMeter: {len(records)} records; gate {'PASS' if not failures else 'FAIL'}; JSON {args.json}")
        for failure in failures:
            print(f"Gate failure: {failure}", file=sys.stderr)
        return 1 if failures else 0
    except (ValueError, OSError) as exc:
        print(f"JudgeMeter input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
