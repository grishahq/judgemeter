# Contributing to JudgeMeter

JudgeMeter is experimental. Reproducible correctness issues and concrete export examples are welcome. Never attach credentials or private evaluation records to a public issue.

For a bug, provide the version, operating system/Python version, minimal redacted JSON records, exact CLI flags, expected calculation and actual JSON report. Explain whether the data is measured or synthetic. For statistical changes, include a hand-calculated example and an independent implementation comparison; define missing-data and insufficient-sample behavior.

Start with README.md and PLAN.md. Keep JudgeMeter analysis isolated from retained AutoEvals modules. Preserve MIT credits and upstream history. Run the documented offline tests and package checks. Model-API tests need separate credentials and must be reported separately from offline results. Do not assume repeated trials are independent or stability implies accuracy.

v0.2 prioritizes real Braintrust export compatibility; please include a minimal, shareable export sample before proposing a schema adapter. Human-label calibration is v0.3 work and needs independent label provenance. Issues are reviewed weekly during active maintenance; there is no support SLA.
