"""Render chart directly from exported statistics and capture local generated HTML."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / 'evidence/demo-report.json').read_text())
labels = ['stable', 'variable']
fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor='#101827')
for axis, key, title in zip(axes, ['mean_score', 'macro_agreement'], ['Mean numeric score', 'Macro pairwise verdict agreement']):
    values = [report['judges'][name]['summary'][key] for name in labels]
    axis.set_facecolor('#101827')
    bars = axis.bar(labels, values, color=['#64dcc0','#e4b660'], width=.5)
    axis.set_ylim(0, 1.15)
    axis.set_yticks([0,.25,.5,.75,1])
    axis.tick_params(colors='white')
    axis.set_title(title, color='white', fontsize=14)
    for bar, value in zip(bars, values):
        axis.text(bar.get_x()+bar.get_width()/2, value+.035, f'{value:.0%}', ha='center', color='white', fontsize=17)
    for spine in axis.spines.values():
        spine.set_color('#42506a')
fig.suptitle('Same average. Different consistency.', color='white', fontsize=23)
fig.text(.5,.04,'SYNTHETIC DEMO · 12 fixed cases × 6 trials × 2 judges · seed 42 · threshold 0.5\nDescriptive illustration. No measured model comparison or human-label accuracy.',ha='center',color='#c1ccdb',fontsize=10)
fig.subplots_adjust(bottom=.22,top=.8,wspace=.26)
fig.savefig(ROOT/'campaign/assets/demo-consistency-chart.png',dpi=180,facecolor=fig.get_facecolor())
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1400,'height':1100}, device_scale_factor=1)
    page.goto((ROOT/'evidence/demo-report.html').as_uri())
    assert page.title() == 'JudgeMeter consistency report'
    assert page.locator('h2').all_text_contents()[:2] == labels
    assert page.get_by_text('synthetic_demo; seeded; no model API calls', exact=False).count() >= 1
    page.screenshot(path=str(ROOT/'campaign/assets/real-report-screenshot.png'), full_page=False)
    browser.close()
print('Chart derived from demo-report.json; real local HTML report rendered and assertions passed.')
