# Attribution and baseline

JudgeMeter is a derived work of [Braintrust AutoEvals](https://github.com/braintrustdata/autoevals), MIT licensed. The full upstream history, LICENSE, Python `autoevals` scorers, TypeScript library and evaluation templates are retained. Baseline immutable commit: `586cc167eb625d84b11581936b1e11619ec0d15a`. Original README is preserved as `docs/AUTOEVALS-README.md`.

JudgeMeter additions are the `judgemeter` Python package, CLI, offline reports, consistency fixtures/tests, evidence and campaign. Repetition/trialCount is existing Braintrust capability; cross-trial analysis is the focused addition. Motivation: upstream issue #219. No affiliation or endorsement by Braintrust is implied.

The fork wheel installs `autoevals` as well as `judgemeter` to retain useful scorers. Install in a fresh environment: do not co-install the PyPI autoevals distribution because both distributions own the autoevals namespace. Upstream's JavaScript package remains named autoevals and is not published by this project.
