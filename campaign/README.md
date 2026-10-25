# JudgeMeter campaign handoff

Copy: [CAMPAIGN.md](CAMPAIGN.md). Structured items: [campaign.json](campaign.json). Each of five distinct story beats includes audience, hook, evidence paths, a substantive LinkedIn post, a four-part X thread, CTA, image and alt text. Copy uses verified repository/release links. LinkedIn lengths are <=3000 characters; each X post is <=280 both raw and with URLs weighted to 23 characters. Run `python campaign/prepare_campaign.py` to regenerate prepared copy and length checks; do not use this to overwrite scheduling readback.

Assets:

- `assets/same-answer-concept.png`: original built-in imagegen illustration for problem beat.
- `assets/consistency-not-correctness.png`: original built-in imagegen illustration for tradeoff beat.
- `assets/real-report-screenshot.png`: actual rendered JudgeMeter demo report for demo/quickstart beats.
- `assets/demo-consistency-chart.png`: matplotlib chart derived from exported demo JSON for methodology beat.

Prompts, source provenance, visual direction and inspections: ART-PROVENANCE.json. Concept art is never presented as UI, empirical data or a result chart. The software-generated screenshot/chart visibly disclose the synthetic dataset and correctness limitation.

Preparation, slot reservation, native scheduling and actual publication are distinct states. Read publishing-readback.json and STATUS.json for authoritative outcomes. No future delivery is guaranteed by a reservation. Shared cadence: at most three primary items per week per platform across the five-project portfolio, including already queued unrelated posts when choosing availability. Matching X threads count as one item. The shared lock must be acquired before touching native composers or modifying shared slot reservations. Existing posts must be preserved.
