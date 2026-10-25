# JudgeMeter English launch campaign

Verified release: https://github.com/grishahq/judgemeter/releases/tag/v0.1.0

Status: prepared. Scheduling/publication state is tracked separately in publishing-readback.json and STATUS.json. No post is claimed scheduled or published by this document.

Shared portfolio cadence: at most three primary campaign items per week per platform across all five projects. One matching X thread counts as one item. Reserve free slots only under the shared lock after reading native queues. Times use Asia/Dubai.

## 01-problem

Audience: LLM application engineers using judges to select prompts or release candidates
Hook: Your answer did not change. Its grade did.
Evidence: examples/judgemeter/synthetic-records.json, evidence/demo-report.json, evidence/gate-failure-report.json
Image: assets/same-answer-concept.png
Alt text: Conceptual illustration: one fixed answer enters two grading paths, receiving a teal check and amber cross. Text reads Same answer. Different grade. JudgeMeter. This is conceptual art, not a software screenshot.
Call to action: Run the seeded example, then repeat a small set of your own fixed answers.

### LinkedIn

Your answer did not change. Its grade did.

If you use an LLM judge to choose a prompt, model or release candidate, that is a separate failure mode from the answer itself being bad. A plausible average can hide a judge that keeps changing its verdict on the very same answer.

I built JudgeMeter to make that failure reproducible and inspectable. It is an experimental, attributed fork of Braintrust AutoEvals with a Python offline analysis layer. AutoEvals provides the scorer baseline; Braintrust already supports repeated trials. My addition analyzes those repetitions together.

The included synthetic example holds 12 inputs and outputs fixed, then supplies six trials for each of two illustrative judges. Both average 0.5. One has 100% pair agreement; the other has 40%. A configured CI comparison rejects the 0.60 agreement drop.

Those are constructed sequences, not a measured model experiment. They demonstrate exactly what an average cannot tell you. No independent human labels means no accuracy claim.

Run the seeded example, inspect the raw records, then repeat a small fixed-answer set from your own workflow. What would your current release gate miss?

https://github.com/grishahq/judgemeter

### X thread

1/4 Your answer did not change. Its grade did. If an LLM judge helps choose your next prompt or release candidate, repeated disagreement on fixed answers deserves its own check.

2/4 JudgeMeter includes a reproducible synthetic failure: 12 fixed cases, 6 trials per judge. Both illustrative judges average 0.5. Pair agreement: 100% versus 40%. Same average, different consistency.

3/4 This is a constructed counterexample, not a real-model benchmark. No human labels, no accuracy claim. The CLI preserves raw records and can reject the 0.60 agreement drop in CI.

4/4 Experimental, attributed AutoEvals fork. Braintrust already repeats trials; JudgeMeter analyzes them offline. Start with the seeded demo, then try your own fixed answers: https://github.com/grishahq/judgemeter

Length checks: LinkedIn 1208/3000; X [177, 201, 181, 213] raw characters, all <=280 with URL weighting too.

## 02-tradeoff

Audience: Evaluation infrastructure engineers and researchers choosing judge metrics
Hook: Repeating the judge is easy. Choosing what agreement means takes care.
Evidence: docs/judgemeter/FORMAT.md, tests/judgemeter/test_analysis.py, evidence/statistics-check.json
Image: assets/consistency-not-correctness.png
Alt text: Conceptual illustration of a compass drawing repeated circles apart from a target. Text reads Consistent is not always correct. JudgeMeter. This is a metaphor, not an evidence plot.
Call to action: Read the statistical contract and challenge the assumptions against your sampling design.

### LinkedIn

Repeating the judge is easy. Choosing what agreement means takes care.

The straightforward approach is to collect more scores and average them. That gives a useful aggregate, but it does not show whether the same answer repeatedly crosses your pass/fail boundary. Majority voting can hide that variation too.

JudgeMeter reports all-pairs verdict agreement per fixed case, alongside consecutive-trial flips and missing/invalid scores. You choose the numeric threshold. Macro agreement gives cases equal weight; pooled agreement weights by the number of valid pairs. They answer different questions when trial counts vary.

The tradeoff is explicit: thresholding loses variation inside each category. A score moving from 0.51 to 0.99 does not change its verdict at a 0.5 threshold. The raw numeric scores remain in the report so you can inspect that limitation.

Fleiss' kappa is guarded rather than forced onto every dataset. v0.1 requires complete cases with equal trial counts and reports undefined results with a reason. Prevalence and correlated trials still matter; a correct formula cannot rescue a weak sampling design.

And consistency does not establish correctness. A judge can repeat the same wrong decision perfectly. Accuracy needs independently reviewed human labels.

Read the formulas and assumptions before choosing a gate:
https://github.com/grishahq/judgemeter/blob/main/docs/judgemeter/FORMAT.md

### X thread

1/4 More judge trials plus an average still cannot show every fixed-answer verdict flip. JudgeMeter keeps means, but adds per-case pair agreement, ordered flips and missing/invalid counts.

2/4 You choose the pass threshold. That is a tradeoff: scores 0.51 and 0.99 have the same verdict at 0.5. Raw scores remain available. Macro agreement weights cases equally; pooled agreement weights valid pairs.

3/4 Kappa is not always defined. v0.1 requires complete, equal-size groups and nonconstant marginals. It reports insufficient evidence explicitly. Repeated trials may be correlated. Consistency is not correctness.

4/4 Accuracy needs independent human labels. Read the statistical contract, then challenge it against your own trial design: https://github.com/grishahq/judgemeter/blob/main/docs/judgemeter/FORMAT.md

Length checks: LinkedIn 1416/3000; X [188, 211, 213, 199] raw characters, all <=280 with URL weighting too.

## 03-solution

Audience: Engineers who want a local reproducible judge-analysis workflow
Hook: A judge report you can generate without an API key.
Evidence: evidence/demo-report.html, evidence/demo-report.json, evidence/public-install.txt, campaign/assets/real-report-screenshot.png
Image: assets/real-report-screenshot.png
Alt text: Actual JudgeMeter HTML report from the seeded synthetic demo. The stable judge shows 100.0% macro pair agreement, mean score 0.5, no missing or invalid scores and per-case trial details. The report labels the data synthetic and states consistency is not correctness.
Call to action: Install the release in a fresh environment, generate the demo and inspect the JSON beside the HTML.

### LinkedIn

A judge report you can generate without an API key.

JudgeMeter v0.1.0 is available as an experimental GitHub release. The screenshot is the actual HTML report produced by the CLI from the included seeded synthetic records.

The workflow is small: supply a JSON array of repeated evaluations, identify the case and judge configuration, keep the input and answer fixed, and export JSON plus a self-contained HTML report. Changed answers under the same case ID are rejected. Duplicate trials are rejected. Missing and invalid scores are counted separately.

Run this after installing the release wheel in a fresh environment:
judgemeter demo --records-out records.json --json report.json --html report.html --baseline stable --candidate variable

Open report.html, inspect each case, and keep report.json for CI or later analysis. The report contains the complete raw records; use only data you intend to share. The demo is synthetic and makes no model API calls.

The fork retains AutoEvals scorers and templates, including a working deterministic scorer baseline. Native Braintrust export importing is still roadmap work; v0.1 expects the documented portable record format.

Install, reproduce the report, and tell me which export format would remove the most friction in your workflow:
https://github.com/grishahq/judgemeter/releases/tag/v0.1.0

### X thread

1/4 A judge report you can reproduce without an API key. JudgeMeter v0.1.0 accepts repeated fixed-answer JSON records and exports JSON plus self-contained HTML. The attached image is its actual synthetic demo report.

2/4 It rejects changed inputs/answers under the same case ID and duplicate trials. Missing and invalid scores are counted separately. Full raw records stay in the report so you can audit the result.

3/4 After installing the wheel in a fresh environment: judgemeter demo --records-out records.json --json report.json --html report.html. No model calls. Inspect the case table and preserved records.

4/4 Experimental AutoEvals fork; scorers and templates retained. Native Braintrust export importing is planned, not shipped. Install and reproduce the report: https://github.com/grishahq/judgemeter/releases/tag/v0.1.0

Length checks: LinkedIn 1345/3000; X [216, 198, 198, 217] raw characters, all <=280 with URL weighting too.

## 04-experiment

Audience: Engineers evaluating whether judge or rubric changes are usable
Hook: The mean-only check sees a tie. The consistency check sees a 0.60 drop.
Evidence: evidence/README.md, evidence/demo-report.json, evidence/statistics-check.json, evidence/gate-failure.txt, evidence/render_evidence.py
Image: assets/demo-consistency-chart.png
Alt text: Chart calculated from the synthetic JudgeMeter demo JSON. Both stable and variable judges have 50% mean score. Macro pair agreement is 100% for stable and 40% for variable. Caption states 12 fixed cases, six trials, two judges, seed 42, threshold 0.5, and no real-model or human-label accuracy comparison.
Call to action: Reproduce the counterexample, then predeclare your own threshold and compare matched real cases.

### LinkedIn

The mean-only check sees a tie. The consistency check sees a 0.60 drop.

Here is the full methodology behind JudgeMeter's demo chart. Twelve fixed cases. Six trials per case per illustrative judge. Binary scores. Pass threshold 0.5. Seed 42 controls the candidate's trial order. The chart is plotted from the exported JSON, not generated artwork.

The stable baseline gives six cases all 0s and six cases all 1s. The variable candidate gives every case three 0s and three 1s. Both average 0.5 across the same cases and trial budget.

For each variable case, 6 of 15 unordered trial pairs agree, so agreement is 0.4. Baseline agreement is 1.0. Fleiss' kappa is 1.0 versus -0.2. The configured maximum-drop gate exits 1, preserving the failed report for inspection.

That is a fair constructed comparison of what the two analyses expose. It is not a before/after model-quality improvement, a measured production benchmark, or proof that the stable judge is correct.

The implementation was checked against hand-calculated tests and 21 independent statsmodels tables; maximum kappa difference was about 2.22e-16. Those checks validate calculations, not the realism of the synthetic data.

Reproduce it, then predeclare a threshold and compare your own matched cases:
https://github.com/grishahq/judgemeter/blob/main/evidence/README.md

### X thread

1/4 Mean-only check: tie. Consistency check: 0.60 drop. Synthetic methodology: 12 fixed cases, 6 trials per judge, binary scores, threshold 0.5, seed 42. The chart is calculated from exported JSON.

2/4 Baseline: six cases always 0, six always 1. Candidate: three 0s and three 1s on every case. Both mean 0.5. Candidate pair agreement = 6/15 = 0.4; baseline = 1.0. Kappa: -0.2 versus 1.0.

3/4 This is a constructed counterexample, not measured model improvement. The configured gate rejects the drop and preserves the report. Formulas also match 21 statsmodels checks within 2.22e-16; that does not validate real-world judge accuracy.

4/4 Reproduce the records, report, chart and expected CI failure. Then compare your own matched cases with a threshold chosen in advance: https://github.com/grishahq/judgemeter/blob/main/evidence/README.md

Length checks: LinkedIn 1331/3000; X [197, 189, 245, 205] raw characters, all <=280 with URL weighting too.

## 05-release

Audience: LLM evaluation teams and open-source contributors seeking a practical offline tool
Hook: JudgeMeter v0.1.0 is released, with a clean-install check and a reproducible starting point.
Evidence: evidence/release-readback.json, evidence/tag-readback.json, evidence/public-install.txt, evidence/judgemeter-tests.txt, evidence/upstream-offline-tests.txt
Image: assets/real-report-screenshot.png
Alt text: Actual HTML report from JudgeMeter v0.1.0 showing the synthetic stable judge summary and fixed-case table. This illustrates the release quickstart output, not an adoption or production result.
Call to action: Download the wheel, run the demo, then report a concrete integration need or reproducible issue.

### LinkedIn

JudgeMeter v0.1.0 is released, with a clean-install check and a reproducible starting point.

It is an experimental Python CLI/library for analyzing repeated LLM-judge scores on fixed inputs and outputs. The public GitHub release includes a wheel, source distribution, demo/evidence bundle and checksums. I downloaded the public wheel into a fresh environment and ran both the JudgeMeter demo and a retained AutoEvals scorer.

Quickstart: create a fresh Python 3.10+ environment, install the wheel linked in the release, then run:
judgemeter demo --json report.json --html report.html

To analyze your own records, use the documented case/judge/trial/input/output/score format. Choose a pass threshold, inspect agreement and unusable-score counts, then add CI policy only when you understand the denominators and limitations.

Validation: 55 JudgeMeter tests, nine retained offline upstream tests and 21 independent statistical cross-checks. A live-model upstream test could not run successfully without API credentials; that failed attempt is recorded. No measured model experiment or human-label accuracy claim is hidden behind the demo.

Credit belongs to Braintrust AutoEvals for the retained scorer foundation. The fork keeps its history and MIT license. v0.2 targets real Braintrust export imports; v0.3 targets human-label calibration, guided by actual integration needs.

Try the release and share a reproducible issue or the import format you need:
https://github.com/grishahq/judgemeter/releases/tag/v0.1.0

### X thread

1/4 JudgeMeter v0.1.0 is released as experimental. Offline Python CLI/library for fixed-answer judge consistency. Public wheel, source, demo/evidence bundle and checksums; clean public-wheel install verified.

2/4 In a fresh Python 3.10+ environment, install the release wheel. Then run: judgemeter demo --json report.json --html report.html. The example is synthetic, requires no model key and preserves raw records.

3/4 Validation: 55 new tests, 9 retained offline upstream tests, 21 statsmodels checks. A live-model upstream test lacked credentials; its failure is recorded. No real-model benchmark or accuracy claim. Braintrust AutoEvals history and MIT license retained.

4/4 Next: real Braintrust imports, then human-label calibration based on usage. Try it and report an integration need or reproducible issue: https://github.com/grishahq/judgemeter/releases/tag/v0.1.0

Length checks: LinkedIn 1516/3000; X [208, 207, 257, 199] raw characters, all <=280 with URL weighting too.
