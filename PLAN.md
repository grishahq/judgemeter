# JudgeMeter implementation plan

JudgeMeter is an attributed fork of Braintrust AutoEvals. Preserve scorer APIs, templates, MIT license and history; add a portable Python analysis layer over repeated scores for fixed inputs/outputs. Upstream baseline: 586cc167eb625d84b11581936b1e11619ec0d15a (2026-10-25 checkout).

## Stages and v0.1 acceptance
1. Inspect upstream and record provenance. Preserve upstream scorer baseline and document distinction from Braintrust trialCount.
2. Implement strict JSON record validation, stable case identity, per-judge/case agreement and ordered verdict flips, missing/invalid accounting, macro/pair-weighted summary, fixed-rater-count Fleiss kappa and baseline/candidate paired comparison. Reject changed answers and duplicate trials.
3. Ship CLI/library and escaped self-contained HTML plus JSON reports with raw records, reproducible seeded synthetic demo and configurable gates (exit 1 for policy failure, 2 for invalid input).
4. Verify hand calculations, statsmodels independent kappa comparison, missing data/edge cases, baseline scorers, meaningful CLI integration and clean wheel/tag install. Review change independently before release.
5. Publish public grishahq/judgemeter v0.1.0 experimental release with immutable annotated tag, wheel/sdist, evidence/demo bundle, checksums, changelog and accurate limits. Verify public release and clean downloaded wheel install.
6. Produce five LinkedIn posts and five X threads (3–5 parts), at least two generated concepts, actual report screenshot and data chart. Preserve prompts, alt text and evidence references. Inspect native publishing access under shared lock and either schedule/read back or document access blocker.

## Statistical contract
Numeric scores must be finite real numbers in [0,1]; missing/null and invalid numeric values are counted and excluded. Scores become categorical verdicts by an explicit threshold (>= threshold passes). Pairwise agreement is the fraction of unordered valid within-case pairs with identical verdicts; macro average excludes insufficient cases. Temporal flips use consecutive integer trial IDs sorted by trial ID (gaps break adjacency), with missing/invalid trials breaking adjacency. Fleiss kappa is offered only for at least two cases with equal valid trial count >=2 and no missing/invalid scores; constant marginals yield undefined kappa. No accuracy claim without independent human labels, no confidence interval or significance claim, no inference from synthetic demonstrations to actual models.

## Roadmap
- v0.2: Braintrust-compatible imports; richer paired CI judge/rubric comparisons; validate schema against real exports.
- v0.3: independently reviewed human labels/calibration and additional integrations driven by usage.

## Maintenance
Keep analysis separate from unchanged upstream modules. Record upstream SHA and review monthly or on security/correctness reports; run offline regression suite and baseline scorers before merging updates. Never overwrite released tags. Patch correctness defects with a new tag and changelog entry. Keep registry publication separate. Review issues weekly when actively maintained; no support SLA.
