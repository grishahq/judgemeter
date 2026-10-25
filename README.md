# JudgeMeter

**Measure how consistently your LLM judge makes decisions.** Experimental v0.1.0; Python 3.10+; offline analysis with no API key.

Your answer did not change, but its grade did. JudgeMeter analyzes repeated evaluations of **fixed inputs and outputs**, preserves the raw records, and reports agreement, verdict flips and unusable scores. It compares two judges or rubric versions on matched cases and can fail CI against a policy you choose.

An attributed fork of [Braintrust AutoEvals](https://github.com/braintrustdata/autoevals), retaining its useful Python/TypeScript scorers, templates, MIT license and full Git history. AutoEvals already scores outputs, and Braintrust already supports repeated trials. JudgeMeter adds offline cross-trial analysis. See [upstream provenance](UPSTREAM.md) and the [original scorer documentation](docs/AUTOEVALS-README.md). No upstream endorsement is implied.

## Install and run

Use a **fresh virtual environment**: this fork includes the `autoevals` namespace and must not be co-installed with the PyPI `autoevals` distribution.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'https://github.com/grishahq/judgemeter/releases/download/v0.1.0/judgemeter-0.1.0-py3-none-any.whl'
judgemeter demo --records-out records.json --json report.json --html report.html --baseline stable --candidate variable
# Open report.html in a browser. All records are synthetic; no model calls.
judgemeter analyze records.json --json checked.json --html checked.html \
  --baseline stable --candidate variable --max-agreement-drop 0.1
# Expected exit 1: candidate macro agreement drops 0.60.
```

The seeded demo has 12 fixed cases, six trials per case per judge, 144 records. Both judges average 0.5. Pair agreement is 1.0 for `stable` and 0.4 for `variable`. This is a constructed illustration, **not evidence that one real judge is better**. No human labels are supplied; accuracy cannot be calculated.

## Analyze your records

A JSON array; each case ID must always refer to the same JSON input and output, across judges too. Trial IDs are unique nonnegative integers within each judge/case. Judge IDs should identify a fixed model + rubric + configuration; the analyzer cannot verify that configuration.

```json
[
  {"case_id":"refund-1","judge":"rubric-v1","trial":0,"input":"Can I return this?","output":"Within 30 days.","score":1},
  {"case_id":"refund-1","judge":"rubric-v1","trial":1,"input":"Can I return this?","output":"Within 30 days.","score":0}
]
```

```sh
judgemeter analyze records.json --json report.json --html report.html \
  --min-agreement 0.8 --max-unusable-rate 0.05
```

Exit codes: **0** analysis/policy passed; **1** policy failed; **2** invalid input/configuration. With baseline/candidate flags, score gates apply to candidate; otherwise to every judge. `--max-agreement-drop` also requires full matched case coverage and sufficient paired evidence. `--min-agreement` fails if any gated case lacks two valid trials. `--max-invalid-rate` excludes missing scores; `--max-unusable-rate` covers both. No gates are enabled by default.

```python
from judgemeter import analyze, compare
report = analyze(records, threshold=0.5)
comparison = compare(report, baseline="rubric-v1", candidate="rubric-v2")
# Retained upstream scorer baseline:
from autoevals.value import ExactMatch
assert ExactMatch()(output="yes", expected="yes").score == 1
```

[Record format, formulas and limitations](docs/judgemeter/FORMAT.md) · [Reproduce evidence](evidence/README.md) · [Plan/roadmap](PLAN.md) · [Changelog](CHANGELOG.md)

## What the numbers mean

Pair agreement compares **all unordered valid trial pairs per case** after the explicit threshold (`score >= threshold` passes). Macro agreement gives each sufficiently sampled case equal weight; pooled agreement weights by valid pairs. Mean numeric score weights valid records equally. Verdict flips count consecutive integer trial IDs with valid scores on both ends; gaps or unusable scores break adjacency.

Missing/null scores and invalid scores are counted separately and excluded from categorical statistics. No imputation. Fleiss’ kappa is emitted only with at least two complete cases, equal valid trial counts >=2 and nonconstant category marginals; otherwise it is `null` with a reason. Kappa assumes exchangeable ratings and common categories, and is sensitive to prevalence. Repeated trials may be correlated. v0.1 offers descriptive statistics, no confidence intervals or significance tests.

**Consistency is not correctness.** A judge can consistently give the wrong answer. Establish accuracy with independently reviewed human labels. Choose thresholds and trial budgets before inspecting results. These reports embed complete raw inputs/outputs; share only records you intend to disclose.

## Development and maintenance

```sh
python -m pip install -e . pytest statsmodels build twine respx pytest-asyncio pytest-mock openai braintrust
pytest -q tests/judgemeter
python evidence/verify_statistics.py
pytest -q py/autoevals/test_values.py py/autoevals/test_json.py py/autoevals/test_serializable_data_class.py
python -m build
python -m twine check dist/*
```

Scorer files and upstream version remain unchanged. JavaScript is retained from upstream; this release changes Python only. Historical registry-publishing workflows are archived under `docs/upstream-workflows/`; JudgeMeter CI runs offline checks and does not publish registry packages. v0.2 targets real Braintrust export imports; v0.3 targets human-label calibration. See PLAN.md for maintenance policy. MIT licensed; preserve LICENSE when redistributing.
