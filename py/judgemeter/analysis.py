"""Offline consistency statistics for fixed-answer repeated evaluations."""

import json
import math
from collections import Counter, defaultdict
from numbers import Real
from statistics import mean


def _json_value(value):
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    if isinstance(value, list):
        for item in value:
            _json_value(item)
        return
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        for item in value.values():
            _json_value(item)
        return
    raise ValueError("input and output must use strict finite JSON types")


def _canonical(value):
    try:
        _json_value(value)
        return json.dumps(value, sort_keys=True, allow_nan=False, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("input and output must be finite JSON values") from exc


def analyze(records, threshold=0.5):
    """Analyze records without making API calls. See docs/judgemeter/FORMAT.md."""
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, Real)
        or not 0 <= threshold <= 1
        or not math.isfinite(threshold)
    ):
        raise ValueError("threshold must be a finite number in [0,1]")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a nonempty JSON array")
    groups = defaultdict(list)
    identities, seen = {}, set()
    raw = []
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            raise ValueError(f"record {index} must be an object")
        for key in ("case_id", "judge"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"record {index}: {key} must be a nonempty string")
        trial = row.get("trial")
        if isinstance(trial, bool) or not isinstance(trial, int) or trial < 0:
            raise ValueError(f"record {index}: trial must be a nonnegative integer")
        if "input" not in row or "output" not in row:
            raise ValueError(f"record {index}: fixed input and output are required")
        identity = (_canonical(row["input"]), _canonical(row["output"]))
        case = row["case_id"]
        if case in identities and identity != identities[case]:
            raise ValueError(f"case {case}: input/output changed across trials or judges")
        identities[case] = identity
        key = (row["judge"], case, trial)
        if key in seen:
            raise ValueError(f"duplicate judge/case/trial: {key}")
        seen.add(key)
        score = row.get("score")
        state = "valid"
        if score is None:
            state = "missing"
        elif isinstance(score, bool) or not isinstance(score, Real) or not 0 <= score <= 1 or not math.isfinite(score):
            state = "invalid"
        normalized = dict(row)
        # JSON has no NaN/Infinity: preserve original representation explicitly.
        if isinstance(score, float) and not math.isfinite(score):
            normalized["score"] = str(score)
            normalized["score_encoding"] = "nonfinite Python score represented as text"
        try:
            json.dumps(normalized, allow_nan=False)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"record {index} contains non-JSON metadata") from exc
        raw.append(normalized)
        groups[(row["judge"], case)].append((trial, score, state))
    judges = defaultdict(list)
    for (judge, case), trials in sorted(groups.items()):
        trials.sort()
        valid = [score for _, score, state in trials if state == "valid"]
        counts = Counter(score >= threshold for score in valid)
        n = len(valid)
        pairs = n * (n - 1) // 2
        agreements = sum(count * (count - 1) // 2 for count in counts.values())
        adjacent = flips = 0
        for left, right in zip(trials, trials[1:]):
            # Missing records and invalid/missing scores break temporal adjacency.
            if right[0] == left[0] + 1 and left[2] == right[2] == "valid":
                adjacent += 1
                flips += (left[1] >= threshold) != (right[1] >= threshold)
        judges[judge].append(
            {
                "case_id": case,
                "n_records": len(trials),
                "n_valid": n,
                "missing": sum(state == "missing" for _, _, state in trials),
                "invalid": sum(state == "invalid" for _, _, state in trials),
                "mean_score": mean(valid) if valid else None,
                "pass_count": counts[True],
                "fail_count": counts[False],
                "valid_pairs": pairs,
                "agreeing_pairs": agreements,
                "pairwise_agreement": agreements / pairs if pairs else None,
                "verdict_flips": flips,
                "adjacent_pairs": adjacent,
                "flip_rate": flips / adjacent if adjacent else None,
                "majority_fraction": max(counts.values()) / n if n else None,
            }
        )
    result = {}
    for judge, cases in judges.items():
        pair_count = sum(c["valid_pairs"] for c in cases)
        n = sum(c["n_valid"] for c in cases)
        all_scores = [
            score for (j, _), trials in groups.items() if j == judge for _, score, state in trials if state == "valid"
        ]
        kappa = {"value": None, "reason": None}
        if len(cases) < 2 or any(c["n_valid"] < 2 for c in cases):
            kappa["reason"] = "requires at least two cases and two valid trials per case"
        elif any(c["missing"] or c["invalid"] for c in cases) or len({c["n_valid"] for c in cases}) != 1:
            kappa["reason"] = "requires complete cases with equal valid trial counts; no imputation or case deletion"
        else:
            observed = mean(c["pairwise_agreement"] for c in cases)
            p_pass = sum(c["pass_count"] for c in cases) / n
            expected = p_pass**2 + (1 - p_pass) ** 2
            if expected == 1:
                kappa["reason"] = "undefined with constant category marginals"
            else:
                kappa["value"] = (observed - expected) / (1 - expected)
        agreements = [c["pairwise_agreement"] for c in cases if c["pairwise_agreement"] is not None]
        total = sum(c["n_records"] for c in cases)
        missing = sum(c["missing"] for c in cases)
        invalid = sum(c["invalid"] for c in cases)
        result[judge] = {
            "cases": cases,
            "summary": {
                "n_cases": len(cases),
                "n_records": total,
                "n_valid": n,
                "missing": missing,
                "invalid": invalid,
                "invalid_rate": invalid / total,
                "missing_rate": missing / total,
                "unusable_rate": (missing + invalid) / total,
                "cases_insufficient": sum(c["n_valid"] < 2 for c in cases),
                "mean_score": mean(all_scores) if all_scores else None,
                "macro_agreement": mean(agreements) if agreements else None,
                "pairwise_agreement": sum(c["agreeing_pairs"] for c in cases) / pair_count if pair_count else None,
                "fleiss_kappa": kappa,
            },
        }
    return {
        "schema_version": "1.0",
        "threshold": threshold,
        "data_kind": "user_supplied",
        "assumptions": [
            "Fixed input/output verified per case across all judges.",
            "Verdict is pass when score >= threshold; statistics use valid numeric scores only.",
            "Agreement measures consistency, not accuracy. Trials are treated as exchangeable for kappa.",
            "No confidence intervals, independence verification or statistical significance claim.",
            "Absent trial rows cannot be counted as missing; submit explicit null scores.",
        ],
        "judges": result,
        "raw_records": raw,
    }


def compare(report, baseline, candidate):
    """Compare matched cases with >=2 valid scores per judge; report coverage."""
    if baseline == candidate:
        raise ValueError("baseline and candidate must differ")
    if baseline not in report["judges"] or candidate not in report["judges"]:
        raise ValueError("baseline and candidate must name existing judges")
    b = {c["case_id"]: c for c in report["judges"][baseline]["cases"]}
    c = {c["case_id"]: c for c in report["judges"][candidate]["cases"]}
    common = sorted(b.keys() & c.keys())
    paired = [
        key for key in common if b[key]["pairwise_agreement"] is not None and c[key]["pairwise_agreement"] is not None
    ]
    return {
        "baseline": baseline,
        "candidate": candidate,
        "paired_cases": len(paired),
        "baseline_only": sorted(b.keys() - c.keys()),
        "candidate_only": sorted(c.keys() - b.keys()),
        "insufficient_cases": sorted(set(common) - set(paired)),
        "agreement_delta": (
            mean(c[key]["pairwise_agreement"] - b[key]["pairwise_agreement"] for key in paired) if paired else None
        ),
        "mean_score_delta": mean(c[key]["mean_score"] - b[key]["mean_score"] for key in paired) if paired else None,
        "cases": [
            {
                "case_id": key,
                "baseline_agreement": b[key]["pairwise_agreement"],
                "candidate_agreement": c[key]["pairwise_agreement"],
            }
            for key in paired
        ],
        "method": "candidate minus baseline, equal weight per matched case; descriptive, not a significance test",
    }
