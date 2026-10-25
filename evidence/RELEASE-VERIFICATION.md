# Release verification — 2026-10-25

Public repository: https://github.com/grishahq/judgemeter

Published experimental prerelease: https://github.com/grishahq/judgemeter/releases/tag/v0.1.0

Release source commit: cbfcf591649a42fdec3fdf78e3a136df87b90378. Annotated v0.1.0 tag was pushed once and has not been rewritten. Upstream ancestor: 586cc167eb625d84b11581936b1e11619ec0d15a. The upstream remote is retained locally and only grishahq/judgemeter received pushes.

GitHub API readback confirms `isDraft: false`, `isPrerelease: true`, and publication at 2026-10-25T19:08:13Z (23:08 Asia/Dubai). Wheel, sdist, demo/evidence ZIP, checksums and full campaign ZIP are uploaded. See release-readback.json for IDs and digests. The source tag is distinct from later campaign/readback commits; release code is immutable by maintenance policy.

The public wheel was downloaded from the release, installed into a new virtual environment and used to generate JSON/HTML and run retained ExactMatch. See public-install.txt. A separate verification agent independently checked wheel contents/templates/entry point, source parity, clean install, demo, failed gate and cyclic identity rejection, finding no release-blocking correctness issue.

GitHub offline matrix passed for the release commit and campaign commit (Python 3.10, 3.12, 3.13); workflow URLs and exact commit SHAs are recorded in ci-readback.json. Local checks: 55 JudgeMeter tests, nine retained offline upstream tests, 21 independent statsmodels tables; kappa max absolute error 2.22e-16. No model/API credentials are needed by JudgeMeter. The retained live partial scorer test's credential failure is recorded separately in upstream-tests.txt and not counted as passed.

The synthetic mean-versus-consistency example is not a real-model experiment. There are no accuracy, adoption, measured productivity or production-readiness claims. Publication of social posts is tracked separately from preparation and slot reservations.
