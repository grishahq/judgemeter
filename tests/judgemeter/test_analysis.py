"""Independent, offline contract tests for repeated fixed-answer judging."""

import copy
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

from judgemeter import analyze, compare


ROOT = Path(__file__).resolve().parents[2]


def records(scores, case_id="case", judge="judge", trials=None):
    if trials is None:
        trials = range(len(scores))
    return [
        {
            "case_id": case_id,
            "judge": judge,
            "trial": trial,
            "input": {"question": case_id},
            "output": {"answer": "fixed"},
            "score": score,
        }
        for trial, score in zip(trials, scores)
    ]


def case(report, case_id="case", judge="judge"):
    return next(item for item in report["judges"][judge]["cases"] if item["case_id"] == case_id)


def summary(report, judge="judge"):
    return report["judges"][judge]["summary"]


def run_cli(*arguments):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "py") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "judgemeter", *map(str, arguments)],
        text=True,
        capture_output=True,
        env=env,
        cwd=ROOT,
    )


def test_pairwise_agreement_is_all_unordered_pairs_and_threshold_is_inclusive():
    # Pass, pass, fail, fail: two matching pairs out of choose(4, 2) = 6.
    report = analyze(records([0.5, 1.0, 0.0, 0.49]))
    result = case(report)
    assert result["n_valid"] == 4
    assert result["mean_score"] == pytest.approx(0.4975)
    assert result["pairwise_agreement"] == pytest.approx(1 / 3)
    assert result["verdict_flips"] == 1
    assert result["adjacent_pairs"] == 3


def test_macro_and_pair_weighting_are_distinct_and_insufficient_cases_are_excluded():
    # A contributes six pairs with agreement 1/3, B one matching pair.
    # C contributes no pairs. Macro = (1/3 + 1)/2; pooled = (2 + 1)/(6 + 1).
    data = records([1, 1, 0, 0], "a") + records([1, 1], "b") + records([0.2], "c")
    report = analyze(data)
    result = summary(report)
    assert result["macro_agreement"] == pytest.approx(2 / 3)
    assert result["pairwise_agreement"] == pytest.approx(3 / 7)
    assert result["mean_score"] == pytest.approx(4.2 / 7)
    assert result["cases_insufficient"] == 1
    assert case(report, "c")["pairwise_agreement"] is None


def test_flip_order_uses_trial_id_and_missing_or_invalid_breaks_adjacency():
    data = records([1, None, 0, 1, "bad", 0, 1], trials=[0, 1, 2, 3, 4, 5, 6])
    report = analyze(list(reversed(data)))
    result = case(report)
    assert result["missing"] == 1
    assert result["invalid"] == 1
    assert result["n_valid"] == 5
    assert result["adjacent_pairs"] == 2
    assert result["verdict_flips"] == 2
    assert result["pairwise_agreement"] == pytest.approx(4 / 10)


def test_gaps_in_integer_trial_ids_break_adjacency_without_imputing_missing_rows():
    result = case(analyze(records([1, 0, 1, 0], trials=[2, 3, 7, 8])))
    assert result["adjacent_pairs"] == 2
    assert result["verdict_flips"] == 2
    assert result["missing"] == 0


def test_missing_score_and_null_are_missing_but_bad_scores_are_invalid():
    data = records([None, None, True, False, "0.9", math.nan, math.inf, -math.inf, -0.1, 1.1, 0, 1])
    del data[0]["score"]
    result = case(analyze(data))
    assert result["missing"] == 2
    assert result["invalid"] == 8
    assert result["n_valid"] == 2
    assert result["mean_score"] == pytest.approx(0.5)
    assert result["pairwise_agreement"] == 0


def test_report_is_json_safe_even_with_nonfinite_invalid_scores():
    report = analyze(records([math.nan, math.inf, -math.inf, None, 0.2]))
    json.dumps(report, allow_nan=False)


def test_fleiss_kappa_hand_calculation():
    # 3 passes, 2 passes/1 fail, 3 fails. Pbar=7/9; pass marginal=5/9.
    # Pe=41/81; kappa=(63-41)/(81-41)=11/20.
    data = records([1, 1, 1], "a") + records([1, 1, 0], "b") + records([0, 0, 0], "c")
    result = summary(analyze(data))["fleiss_kappa"]
    assert result["value"] == pytest.approx(0.55)
    assert result["reason"] is None


@pytest.mark.parametrize(
    "data",
    [
        records([1, 0], "a"),
        records([1], "a") + records([0], "b"),
        records([1, 0], "a") + records([0, 1, 1], "b"),
        records([1, None, 0], "a") + records([1, 0], "b"),
        records([1, "invalid", 0], "a") + records([1, 0], "b"),
        records([1, 1], "a") + records([1, 1], "b"),
    ],
)
def test_kappa_explains_ineligible_or_undefined_data(data):
    result = summary(analyze(data))["fleiss_kappa"]
    assert result["value"] is None
    assert isinstance(result["reason"], str) and result["reason"]


def test_case_identity_is_checked_across_judges_with_json_object_order_ignored():
    data = records([1], judge="a") + records([0], judge="b")
    data[0]["input"] = {"one": 1, "two": 2}
    data[1]["input"] = {"two": 2, "one": 1}
    analyze(data)
    for field in ("input", "output"):
        changed = copy.deepcopy(data)
        changed[1][field] = {"changed": True}
        with pytest.raises(ValueError):
            analyze(changed)


def test_json_identity_does_not_conflate_booleans_and_numbers():
    data = records([1, 0])
    data[0]["output"] = True
    data[1]["output"] = 1
    with pytest.raises(ValueError):
        analyze(data)


def test_duplicate_trial_is_rejected_but_trial_can_repeat_across_judges():
    data = records([1])
    with pytest.raises(ValueError):
        analyze(data + copy.deepcopy(data))
    analyze(data + records([1], judge="other"))


@pytest.mark.parametrize("replacement", [None, [], "record", 1])
def test_nonobject_record_is_rejected(replacement):
    with pytest.raises(ValueError):
        analyze([replacement])


@pytest.mark.parametrize(
    "field,value",
    [
        ("case_id", ""),
        ("case_id", 1),
        ("judge", ""),
        ("judge", None),
        ("trial", -1),
        ("trial", True),
        ("trial", 0.5),
        ("trial", "0"),
        ("input", {"bad": math.nan}),
        ("output", {"bad": object()}),
        ("input", (1, 2)),
        ("output", {1: "not a JSON key"}),
    ],
)
def test_malformed_fields_are_rejected(field, value):
    data = records([1])
    data[0][field] = value
    with pytest.raises(ValueError):
        analyze(data)


@pytest.mark.parametrize("field", ["case_id", "judge", "trial", "input", "output"])
def test_required_fields_are_rejected_when_missing(field):
    data = records([1])
    del data[0][field]
    with pytest.raises(ValueError):
        analyze(data)


@pytest.mark.parametrize("threshold", [True, "0.5", math.nan, math.inf, -0.1, 1.1, 10**400])
def test_bad_threshold_is_rejected(threshold):
    with pytest.raises(ValueError):
        analyze(records([1, 0]), threshold=threshold)


def test_analysis_does_not_mutate_input_records():
    data = records([1, None, 0])
    before = copy.deepcopy(data)
    analyze(data)
    assert data == before


def test_cli_writes_valid_json_and_escaped_self_contained_html(tmp_path):
    data = records([1, 0], case_id="<script>alert('case')</script>")
    data[0]["output"] = data[1]["output"] = "</script><img src=x onerror=alert(1)>"
    source, json_path, html_path = (tmp_path / name for name in ("scores.json", "report.json", "report.html"))
    source.write_text(json.dumps(data))
    result = run_cli("analyze", source, "--json", json_path, "--html", html_path)
    assert result.returncode == 0, result.stderr
    report = json.loads(json_path.read_text())
    assert report["judges"]["judge"]["cases"][0]["n_valid"] == 2
    rendered = html_path.read_text()
    assert "<script>alert('case')</script>" not in rendered
    assert "<img src=x onerror=alert(1)>" not in rendered
    assert "&lt;" in rendered or "\\u003c" in rendered
    assert 'src="http' not in rendered and 'href="http' not in rendered


def test_cli_agreement_and_invalid_rate_gates_and_input_errors(tmp_path):
    source = tmp_path / "scores.json"
    source.write_text(json.dumps(records([1, 0])))
    result = run_cli("analyze", source, "--min-agreement", "0.8")
    assert result.returncode == 1, result.stderr
    source.write_text(json.dumps(records([1, "invalid"])))
    result = run_cli("analyze", source, "--max-invalid-rate", "0")
    assert result.returncode == 1, result.stderr
    source.write_text("{broken json")
    assert run_cli("analyze", source).returncode == 2
    source.write_text(json.dumps(records([1, 1])))
    assert run_cli("analyze", source, "--min-agreement", "1.1").returncode == 2
    assert run_cli("analyze", tmp_path / "missing.json").returncode == 2


def test_paired_comparison_uses_common_eligible_cases_with_equal_case_weights():
    data = (
        records([1, 1], "a", "baseline")
        + records([1, 0], "a", "candidate")
        + records([1, 0, 1, 0], "b", "baseline")
        + records([1, 1], "b", "candidate")
        + records([1], "insufficient", "baseline")
        + records([1, 1], "insufficient", "candidate")
        + records([1, 1], "baseline-only", "baseline")
        + records([1, 1], "candidate-only", "candidate")
    )
    result = compare(analyze(data), "baseline", "candidate")
    # Deltas: a = -1, b = +2/3. Their macro delta is -1/6.
    assert result["paired_cases"] == 2
    assert result["agreement_delta"] == pytest.approx(-1 / 6)
    assert result["mean_score_delta"] == pytest.approx(0)
    assert result["baseline_only"] == ["baseline-only"]
    assert result["candidate_only"] == ["candidate-only"]
    assert result["insufficient_cases"] == ["insufficient"]
    assert [row["case_id"] for row in result["cases"]] == ["a", "b"]


def test_comparison_no_eligible_pair_has_undefined_deltas():
    report = analyze(records([1], judge="a") + records([0, 1], judge="b"))
    result = compare(report, "a", "b")
    assert result["paired_cases"] == 0
    assert result["agreement_delta"] is None
    assert result["mean_score_delta"] is None
    with pytest.raises(ValueError):
        compare(report, "a", "a")
    with pytest.raises(ValueError):
        compare(report, "a", "unknown")


def test_cli_paired_regression_gate_and_configuration_failures(tmp_path):
    source = tmp_path / "scores.json"
    source.write_text(json.dumps(records([1, 1], judge="baseline") + records([1, 0], judge="candidate")))
    arguments = ["analyze", source, "--baseline", "baseline", "--candidate", "candidate"]
    result = run_cli(*arguments, "--max-agreement-drop", "0.1")
    assert result.returncode == 1, result.stderr
    result = run_cli(*arguments, "--max-agreement-drop", "1")
    assert result.returncode == 0, result.stderr
    assert run_cli("analyze", source, "--baseline", "baseline").returncode == 2
    assert run_cli("analyze", source, "--max-agreement-drop", "0.1").returncode == 2


def test_arbitrarily_large_integer_score_is_invalid_without_overflow():
    result = case(analyze(records([10**400, 1])))
    assert result["invalid"] == 1
    assert result["n_valid"] == 1


def test_no_usable_scores_produces_undefined_metrics():
    report = analyze(records([None, "invalid", None]))
    result = case(report)
    assert result["n_valid"] == 0
    assert result["mean_score"] is None
    assert result["pairwise_agreement"] is None
    assert result["verdict_flips"] == result["adjacent_pairs"] == 0
    totals = summary(report)
    assert totals["mean_score"] is totals["macro_agreement"] is totals["pairwise_agreement"] is None
    assert totals["cases_insufficient"] == 1
    json.dumps(report, allow_nan=False)


def test_negative_kappa_is_preserved_instead_of_clamped():
    # Every case splits its two votes. Observed agreement=0, chance=1/2.
    report = analyze(records([0, 1], "a") + records([0, 1], "b"))
    assert summary(report)["fleiss_kappa"]["value"] == pytest.approx(-1)


def test_cli_keeps_failed_gate_reports_and_honors_equal_boundary(tmp_path):
    source, target = tmp_path / "scores.json", tmp_path / "report.json"
    source.write_text(json.dumps(records([1, 0])))
    result = run_cli("analyze", source, "--json", target, "--min-agreement", "0.1")
    assert result.returncode == 1, result.stderr
    assert json.loads(target.read_text())["gate"]["passed"] is False
    result = run_cli("analyze", source, "--min-agreement", "0")
    assert result.returncode == 0, result.stderr


def test_cli_refuses_to_overwrite_records_or_overlap_outputs(tmp_path):
    source = tmp_path / "scores.json"
    original = json.dumps(records([1, 1]))
    source.write_text(original)
    assert run_cli("analyze", source, "--json", source).returncode == 2
    assert source.read_text() == original
    target = tmp_path / "report.json"
    assert run_cli("analyze", source, "--json", target, "--html", target).returncode == 2
    assert not target.exists()
