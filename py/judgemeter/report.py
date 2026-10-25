"""Self-contained HTML, with every user-supplied string escaped."""

import html
import json


def render_html(report):
    esc = lambda value: html.escape(str(value))
    cards = []
    for name, judge in report["judges"].items():
        s = judge["summary"]
        pct = lambda value: "insufficient" if value is None else f"{value:.1%}"
        rows = "".join(
            f'<tr><td>{esc(c["case_id"])}</td><td>{c["n_valid"]}/{c["n_records"]}</td>'
            f'<td>{pct(c["pairwise_agreement"])}</td><td>{c["verdict_flips"]}/{c["adjacent_pairs"]}</td>'
            f'<td>{c["missing"]}</td><td>{c["invalid"]}</td></tr>'
            for c in judge["cases"]
        )
        cards.append(
            f"""<section><h2>{esc(name)}</h2><div class="metrics">
        <div><b>{pct(s['macro_agreement'])}</b><span>Macro pair agreement</span></div>
        <div><b>{esc(round(s['mean_score'], 4) if s['mean_score'] is not None else 'insufficient')}</b><span>Mean numeric score</span></div>
        <div><b>{s['missing']} / {s['invalid']}</b><span>Missing / invalid</span></div></div>
        <p>Fleiss’ kappa: {esc(s['fleiss_kappa']['value'] if s['fleiss_kappa']['value'] is not None else s['fleiss_kappa']['reason'])}</p>
        <table><thead><tr><th>Fixed case</th><th>Valid/total</th><th>Pair agreement</th><th>Flips/adjacent</th><th>Missing</th><th>Invalid</th></tr></thead><tbody>{rows}</tbody></table></section>"""
        )
    comparison = ""
    if "comparison" in report:
        comparison = (
            "<section><h2>Matched comparison</h2><pre>"
            + esc(json.dumps(report["comparison"], indent=2))
            + "</pre></section>"
        )
    assumptions = "".join("<li>" + esc(x) + "</li>" for x in report["assumptions"])
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JudgeMeter consistency report</title><style>
    body{{font:16px/1.6 system-ui,sans-serif;background:#101827;color:#e7edf7;margin:0;padding:40px;max-width:1200px}}
    h1{{font-size:38px;margin:0}}h2{{color:#64dcc0}}section{{background:#1a2639;padding:24px;border-radius:14px;margin:24px 0}}
    .eyebrow{{color:#64dcc0;letter-spacing:2px}}.metrics{{display:flex;gap:48px;flex-wrap:wrap}}b{{display:block;font-size:30px}}
    span{{color:#b1bed0}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{text-align:left;padding:9px;border-bottom:1px solid #3b4b62}}
    pre{{white-space:pre-wrap;overflow-wrap:anywhere}}summary{{cursor:pointer}}.notice{{border-left:4px solid #e4b660;padding-left:16px}}
    </style><header><p class="eyebrow">JUDGEMETER / v0.1.0 EXPERIMENTAL</p><h1>Same answer. Consistent judgment?</h1>
    <p>Repeated evaluations of fixed inputs and outputs · pass threshold ≥ {report['threshold']}</p>
    <p class="notice">Data: {esc(report.get('data_kind', 'user_supplied'))}. Consistency is not correctness. No human-label accuracy claim.</p></header>
    {''.join(cards)}{comparison}<section><h2>Method and limits</h2><ul>{assumptions}</ul>
    <p>Pairs compare all unordered valid trials. Flips count consecutive integer trial IDs with two valid scores. Missing/invalid scores break adjacency. See FORMAT.md for denominators and kappa assumptions.</p></section>
    <details><summary>Full report and preserved raw records</summary><pre>{esc(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))}</pre></details></html>"""
