# JudgeMeter v0.1.0 — experimental

Your answer did not change, but its grade did. This experimental release adds portable offline consistency analysis to an attributed AutoEvals fork.

## Included

- Python CLI and library; strict fixed-input/output identity checks across trials and judges.
- Per-case threshold verdict agreement, consecutive-trial flips, missing and invalid score counts.
- Macro/pooled summaries, guarded binary Fleiss kappa and matched judge/rubric comparisons.
- Configurable CI policy exits and self-contained escaped HTML/JSON preserving raw records.
- Seeded synthetic example with equal means (0.5) but 100% versus 40% pair agreement; real report screenshot and data-derived chart.
- MIT AutoEvals scorers, templates and full Git history retained. Upstream SHA `586cc167eb625d84b11581936b1e11619ec0d15a`.

## Install without a registry

Use Python 3.10+ and a fresh environment; this wheel includes the `autoevals` namespace, so do not co-install PyPI autoevals.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install https://github.com/grishahq/judgemeter/releases/download/v0.1.0/judgemeter-0.1.0-py3-none-any.whl
judgemeter demo --records-out records.json --json report.json --html report.html --baseline stable --candidate variable
judgemeter analyze records.json --json gated.json --baseline stable --candidate variable --max-agreement-drop 0.1
# Last command deliberately exits 1, demonstrating the synthetic regression gate.
```

## Validation and limits

55 JudgeMeter tests, nine retained offline upstream tests and 21 independent statsmodels kappa tables pass. Maximum kappa difference is 2.22e-16. A broader upstream test attempt is recorded: its live-model partial test failed for missing API credentials and is not claimed as passing. No measured model experiment was performed.

Consistency is not correctness. No human labels, accuracy claims, confidence intervals or significance tests. Kappa requires complete equal-size groups and nonconstant marginals. Missing/invalid scores are counted and excluded; insufficient samples are explicit. Native Braintrust export importing remains v0.2 work. The software is experimental, with no stability or support SLA. This is a fork, without Braintrust endorsement.

Downloads: Python wheel, source distribution, reproducible demo/evidence ZIP and SHA256SUMS. Source snapshots retain the full project; evidence ZIP includes campaign concepts, actual product screenshots/charts and raw demo records. No package-registry publication is required.
