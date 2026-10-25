#!/usr/bin/env python3
"""Cross-check public JudgeMeter kappa against statsmodels, independently.

Run from a checkout with Python, statsmodels and JudgeMeter available:
    PYTHONPATH=py python evidence/verify_statistics.py --output evidence/statistics-check.json
statsmodels is verification tooling, never a JudgeMeter runtime dependency.
"""

import argparse
import json
import math
import platform
import random
import sys
from pathlib import Path

# Permit execution directly from the source checkout as well as an installed wheel.
if str(Path(__file__).resolve().parents[1] / "py") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "py"))

import numpy as np
import statsmodels
from statsmodels.stats.inter_rater import fleiss_kappa

from judgemeter import analyze


SEED = 20261025
TOLERANCE = 1e-12


def check_counts(name, counts):
    """Build scores from the independently provided [fail, pass] table."""
    data = []
    for case_index, (failures, passes) in enumerate(counts):
        # All input/output fields remain constant within a case.
        for trial, verdict in enumerate([0] * failures + [1] * passes):
            data.append(
                {
                    "case_id": f"case-{case_index}",
                    "judge": "verification",
                    "trial": trial,
                    "input": {"id": case_index},
                    "output": "fixed answer",
                    "score": 0.9 if verdict else 0.1,
                }
            )
    actual = analyze(data)["judges"]["verification"]["summary"]["fleiss_kappa"]["value"]
    expected = float(fleiss_kappa(np.asarray(counts), method="fleiss"))
    if actual is None or not math.isfinite(actual) or abs(actual - expected) > TOLERANCE:
        raise AssertionError(f"{name}: JudgeMeter={actual!r}; statsmodels={expected!r}")
    return {
        "name": name,
        "cases": len(counts),
        "trials_per_case": sum(counts[0]),
        "category_counts": [list(row) for row in counts],
        "judgemeter_kappa": actual,
        "statsmodels_kappa": expected,
        "absolute_error": abs(actual - expected),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(SEED)
    checks = [check_counts("hand-calculated kappa 0.55", [[0, 3], [1, 2], [3, 0]])]
    # Every seeded table has exactly balanced binary marginals, >=2 cases,
    # and the same >=2 trial count in each case. No production helper creates
    # the reference counts; statsmodels sees this independently built table.
    for index in range(20):
        n_cases, n_trials = 10 + 2 * index, 2 + 2 * (index % 4)
        verdicts = [0] * (n_cases * n_trials // 2) + [1] * (n_cases * n_trials // 2)
        rng.shuffle(verdicts)
        counts = []
        for offset in range(0, len(verdicts), n_trials):
            block = verdicts[offset : offset + n_trials]
            passes = sum(block)
            counts.append([n_trials - passes, passes])
        checks.append(check_counts(f"seeded-balanced-{index:02d}", counts))
    result = {
        "status": "passed",
        "seed": SEED,
        "tolerance": TOLERANCE,
        "python_version": platform.python_version(),
        "statsmodels_version": statsmodels.__version__,
        "checks": checks,
        "max_absolute_error": max(row["absolute_error"] for row in checks),
        "scope": "Fixed-rater-count Fleiss kappa only; does not establish score accuracy or trial independence.",
    }
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
