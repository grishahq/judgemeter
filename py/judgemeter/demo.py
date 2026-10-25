"""Seeded synthetic demonstration; no model calls or measured accuracy."""

import random


def demo_records(seed=42):
    rng = random.Random(seed)
    records = []
    for case in range(12):
        for judge in ("stable", "variable"):
            scores = [float(case % 2)] * 6 if judge == "stable" else [0.0] * 3 + [1.0] * 3
            if judge == "variable":
                rng.shuffle(scores)
            for trial, score in enumerate(scores):
                records.append(
                    {
                        "case_id": f"fixed-{case:02d}",
                        "judge": judge,
                        "trial": trial,
                        "input": {"question": f"Synthetic fixed prompt {case}"},
                        "output": {"answer": f"Synthetic fixed answer {case}"},
                        "score": score,
                        "provenance": "synthetic_demo",
                        "seed": seed,
                    }
                )
    return records
