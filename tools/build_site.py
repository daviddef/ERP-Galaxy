#!/usr/bin/env python3
"""Generate the companion static site into docs/.

Why this exists: searches for "ERP Galaxy" return nothing, while every
competitor is discovered through the web because they ARE the web. An App Store
listing will never rank for "what happened to KONV in S/4HANA" -- a page titled
exactly that will. It is also where advertising belongs, so the app itself can
keep saying no ads, no tracking, no network, and have every word be true.

LICENSING DISCIPLINE, and it differs from the app on purpose.
The app quotes SAP's required-action text with attribution, which is fair for a
reference tool. Republishing that prose across 248 indexed public pages is a
different act, and it is the exact exposure flagged in the licence review: SAP's
terms forbid bulk reproduction, and the EU database right protects substantial
extraction regardless of whether the individual items are copyrightable.

So this site publishes FACTS -- table name, our verdict classification,
successor table, SAP Note number -- plus prose we wrote. It never emits the
`action` or `evidence` fields. Those stay in the app.
"""
import json, re, pathlib, html, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs'
SITE = OUT / 's4'
BASE = 'https://daviddef.github.io/ERP-Galaxy'
APP = 'https://apps.apple.com/app/id6791550922'
# AdSense publisher id. The `ca-` prefix is what the tag expects; the id shown
# in the AdSense dashboard omits it.
ADSENSE_CLIENT = 'ca-pub-4156851882993001'
# Manual ad units, keyed by the slot name used in the page templates. These are
# the numeric ids AdSense gives you when you create an ad unit -- they are NOT
# invented. Leave empty and the pages carry only the publisher script, which is
# what Auto ads and account review need; a made-up slot id never fills and
# renders as a blank reserved box.
AD_SLOTS = {}

lifecycle = json.load(open(ROOT / 'data' / 's4_lifecycle.json'))
index = json.load(open(ROOT / 'data' / 'tables.json'))
htmlsrc = (ROOT / 'sap-table-explorer.html').read_text()
curated = {}
for m in re.finditer(r'\{id:"([A-Z0-9_/]+)",module:"([A-Z0-9_/]+)"(.*?)\n\s*relations:', htmlsrc, re.S):
    d = re.search(r'shortDesc:"((?:[^"\\]|\\.)*)"', m.group(3))
    p = re.search(r'plainEnglish:"((?:[^"\\]|\\.)*)"', m.group(3))
    curated[m.group(1)] = {
        'module': m.group(2),
        'short': (d.group(1).replace('\\"', '"') if d else ''),
        'plain': (p.group(1).replace('\\"', '"') if p else ''),
    }

# Our own words for each outcome. Deliberately not SAP's.
VERDICT = {
    'deprecated': ('Gone', '#d0342c',
                   'Not present in S/4HANA. Reads and writes both fail, so anything referring to it '
                   'has to be rewritten before you convert.'),
    'replaced':   ('Replaced — your code must change', '#c2410c',
                   'The table may still exist, but it is no longer where the data lives, and there is '
                   'no same-named view standing in for it. Existing SELECTs either fail or quietly '
                   'return stale and partial answers, which is the more dangerous outcome.'),
    'compat_view':('Compatibility view — reads still work', '#1d4ed8',
                   'Survives as a compatibility view rather than a real table. Existing reports keep '
                   'running, which is exactly why this one gets missed; writes are not supported and '
                   'the failure surfaces later.'),
    'changed':    ('Changed', '#a16207',
                   'Still present, but its structure, semantics or content are different. Code that '
                   'compiles against it can still be wrong.'),
    'unchanged':  ('Unchanged', '#15803d',
                   'SAP states this table is unaffected by the move to S/4HANA.'),
}
NICE = {'deprecated': 'disappears', 'replaced': 'is replaced', 'compat_view': 'becomes a compatibility view',
        'changed': 'changes', 'unchanged': 'is unchanged'}

def esc(s): return html.escape(str(s or ''))

CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--card:#f5f5f7;--line:#e5e5ea;--acc:#4f9cf9}
@media(prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--mut:#8b949e;--card:#161b22;--line:#30363d}}
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;max-width:760px;
 margin:0 auto;padding:28px 20px 64px;line-height:1.65;color:var(--fg);background:var(--bg)}
a{color:var(--acc)}
header.site{display:flex;justify-content:space-between;align-items:center;gap:12px;
 border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:26px;flex-wrap:wrap}
header.site a{font-weight:700;text-decoration:none;color:var(--fg)}
h1{font-size:1.75rem;line-height:1.25;margin:.2em 0 .4em}
h2{font-size:1.15rem;margin-top:2em}
.verdict{border-left:4px solid var(--v);background:var(--card);padding:16px 18px;border-radius:10px;margin:18px 0}
.verdict .label{font-weight:700;color:var(--v);font-size:1.05rem}
.facts{width:100%;border-collapse:collapse;margin:14px 0}
.facts th,.facts td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.facts th{width:38%;color:var(--mut);font-weight:600;font-size:.9rem}
code{background:var(--card);padding:1px 6px;border-radius:4px;font-size:.92em;
 font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:14px 0;padding:0;list-style:none}
.grid a{display:block;padding:9px 11px;background:var(--card);border-radius:8px;text-decoration:none;
 font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:600}
.grid small{display:block;color:var(--mut);font-weight:400;font-family:-apple-system,system-ui,sans-serif;font-size:.76rem}
.cta{background:var(--card);border-radius:12px;padding:18px 20px;margin:30px 0}
.ad{margin:26px 0;min-height:90px}
footer{margin-top:3.5em;font-size:.85rem;color:var(--mut);border-top:1px solid var(--line);padding-top:1.2em}
.tag{display:inline-block;font-size:.72rem;padding:2px 8px;border-radius:99px;background:var(--card);color:var(--mut)}
"""

def ad_slot(slot):
    """Emit a manual unit only when a REAL slot id exists for it.

    Until then the page carries the publisher script and nothing else, which is
    what Auto ads use and what account review needs to see.
    """
    sid = AD_SLOTS.get(slot)
    if not (ADSENSE_CLIENT and sid):
        return f'<!-- ad slot {slot}: add its AdSense unit id to AD_SLOTS -->'
    return (f'<div class="ad"><ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{sid}" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')

AD_HEAD = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" '
           f'crossorigin="anonymous"></script>') if ADSENSE_CLIENT else ''

def page(path, title, desc, body, canonical, jsonld=None):
    doc = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<style>{CSS}</style>{AD_HEAD}
{f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ''}
</head><body>
<header class="site">
  <a href="{BASE}/">ERP Galaxy</a>
  <span class="tag">Independent SAP reference</span>
</header>
{body}
<footer>
<p>Not affiliated with, sponsored by, or endorsed by SAP SE. SAP, S/4HANA, ABAP and Fiori are
trademarks of SAP SE. Verdicts here are our own summaries of SAP's publicly published
Simplification List, written in our own words &mdash; they are not reproductions of SAP
documentation, and they describe SAP's intended architecture rather than any particular system.
Confirm against your own system before planning work.</p>
<p><a href="{BASE}/">Home</a> &middot; <a href="{BASE}/privacy.html">Privacy</a> &middot;
<a href="{APP}">iOS app</a></p>
</footer>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc)

def table_page(tid, e):
    label, colour, blurb = VERDICT[e['s4status']]
    cur = curated.get(tid, {})
    idx = index.get(tid, {})
    module = cur.get('module') or idx.get('module') or ''
    what = cur.get('short') or idx.get('desc') or ''
    plain = cur.get('plain') or ''
    by = e.get('replacedBy')
    note = e.get('sapNote')

    title = f"What happened to {tid} in S/4HANA?"
    desc = f"{tid} {NICE[e['s4status']]} in SAP S/4HANA." + (f" Data now lives in {by}." if by else '') + \
           (f" SAP Note {note}." if note else '')

    rows = [('Table', f'<code>{esc(tid)}</code>')]
    if what:   rows.append(('What it is', esc(what)))
    if module: rows.append(('Module', esc(module)))
    rows.append(('Fate in S/4HANA', f'<strong style="color:{colour}">{esc(label)}</strong>'))
    if by:     rows.append(('Data now lives in', f'<a href="{by}.html"><code>{esc(by)}</code></a>'
                            if by in lifecycle else f'<code>{esc(by)}</code>'))
    if note:   rows.append(('SAP Note', esc(note)))

    # Alphabetical neighbours are useless to a reader and weak internal linking.
    # Prefer the same module -- that is who else the same team has to worry about.
    # The heading only claims a module when the list actually delivers one,
    # because "Other SD tables" above a list of FI tables is simply untrue.
    def mod_of(x):
        return curated.get(x, {}).get('module') or index.get(x, {}).get('module') or ''
    pool = [k for k, v in lifecycle.items() if v['s4status'] == e['s4status'] and k != tid]
    kin = [k for k in pool if module and mod_of(k) == module][:12]
    OUTCOME = {'deprecated': 'disappear', 'replaced': 'are replaced',
               'compat_view': 'survive only as compatibility views',
               'changed': 'change', 'unchanged': 'are unchanged'}
    # Claim the module ONLY when every entry is that module. Padding a short
    # list out to twelve with other modules is what made the heading wrong.
    if len(kin) >= 4:
        same, heading = kin, f'Other {esc(module)} tables that {OUTCOME[e["s4status"]]}'
    else:
        same = kin + [k for k in pool if k not in kin][:12 - len(kin)]
        heading = f'Other tables that {OUTCOME[e["s4status"]]}'
    body = f"""
<h1>{esc(title)}</h1>
<p><strong>{esc(tid)}</strong> {esc(NICE[e['s4status']])} in SAP S/4HANA.</p>
<div class="verdict" style="--v:{colour}">
  <div class="label">{esc(label)}</div>
  <p style="margin:.4em 0 0">{esc(blurb)}</p>
</div>
{f'<p>{esc(plain)}</p>' if plain else ''}
<table class="facts">{''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in rows)}</table>
{ad_slot('1')}
<div class="cta">
  <strong>Check this against the whole picture.</strong>
  <p style="margin:.5em 0 0">ERP Galaxy is a free iOS app holding 2,273 SAP tables, 248 published
  S/4HANA verdicts, their key fields and how they join &mdash; entirely offline, with no account and
  no data collection. <a href="{APP}">Get it on the App&nbsp;Store</a>.</p>
</div>
<h2>{heading}</h2>
<ul class="grid">{''.join(f'<li><a href="{k}.html">{esc(k)}</a></li>' for k in same)}</ul>
<p><a href="{BASE}/s4/">All {len(lifecycle)} verdicts</a></p>
"""
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{
        "@type": "Question", "name": title,
        "acceptedAnswer": {"@type": "Answer", "text": f"{tid} {NICE[e['s4status']]} in SAP S/4HANA. {blurb}"
                           + (f" Data now lives in {by}." if by else '')}}]}
    page(SITE / f'{tid}.html', title, desc, body, f'{BASE}/s4/{tid}.html', jsonld)

def group_page(fname, title, desc, ids, intro):
    items = ''.join(
        f'<li><a href="{i}.html">{esc(i)}'
        f'<small>{esc((curated.get(i, {}).get("short") or index.get(i, {}).get("desc") or "")[:58])}</small></a></li>'
        for i in sorted(ids))
    body = f"<h1>{esc(title)}</h1><p>{intro}</p>{ad_slot('2')}<ul class=\"grid\">{items}</ul>"
    page(SITE / fname, title, desc, body, f'{BASE}/s4/{fname}')

def build():
    SITE.mkdir(parents=True, exist_ok=True)
    for tid, e in lifecycle.items():
        if e['s4status'] in VERDICT:
            table_page(tid, e)

    breaks = [k for k, v in lifecycle.items() if v['s4status'] in ('replaced', 'deprecated')]
    reads = [k for k, v in lifecycle.items() if v['s4status'] == 'compat_view']

    group_page('index.html', f'SAP ECC to S/4HANA: {len(lifecycle)} table verdicts',
               f'What happens to {len(lifecycle)} SAP tables in S/4HANA — which disappear, which are '
               f'replaced, and which survive only as compatibility views.',
               lifecycle.keys(),
               f'Every table SAP has published a Simplification List verdict for. '
               f'<strong>{len(breaks)}</strong> of them require code changes; '
               f'<strong>{len(reads)}</strong> keep working for reads through a compatibility view.')

    group_page('code-must-change.html',
               f'{len(breaks)} SAP tables that will break your ABAP in S/4HANA',
               'The SAP tables with no compatibility view — every SELECT against them either fails or '
               'returns stale data after conversion.',
               breaks,
               'These have no same-named compatibility view. Existing code either fails outright or '
               'quietly returns partial answers &mdash; the second being far more dangerous, because '
               'it compiles and runs. This is the list worth checking your custom code against first.')

    group_page('reads-still-work.html',
               f'{len(reads)} SAP tables that survive as compatibility views',
               'SAP tables that still return data in S/4HANA through a compatibility view — reads work, '
               'writes do not.',
               reads,
               'These still answer a SELECT, which is exactly why they get missed. They are no longer '
               'real tables, writes are not supported, and the failure surfaces late.')

    # Home
    top = ['KONV', 'VBUK', 'MKPF', 'MSEG', 'BSIS', 'COSP', 'MARD', 'VBUP']
    top = [t for t in top if t in lifecycle]
    body = f"""
<h1>What happens to your SAP tables in S/4HANA?</h1>
<p>SAP publishes the answer in a Simplification List that runs to well over a thousand pages, and the
interactive version needs an S-user login. This is the same information as plain pages, one table at
a time, free and without an account.</p>
<h2>Most looked up</h2>
<ul class="grid">{''.join(f'<li><a href="s4/{t}.html">{esc(t)}<small>{esc(VERDICT[lifecycle[t]["s4status"]][0])}</small></a></li>' for t in top)}</ul>
{ad_slot('3')}
<h2>Start here</h2>
<ul>
<li><a href="s4/code-must-change.html"><strong>{len(breaks)} tables that will break your ABAP</strong></a> — no compatibility view, code must change.</li>
<li><a href="s4/reads-still-work.html"><strong>{len(reads)} tables that survive as compatibility views</strong></a> — reads work, writes do not.</li>
<li><a href="s4/">All {len(lifecycle)} published verdicts</a></li>
</ul>
<div class="cta">
  <strong>The full thing, offline, on your phone.</strong>
  <p style="margin:.5em 0 0">ERP Galaxy holds 2,273 tables with key fields, how they join, BAPIs,
  movement types and migration playbooks — no account, no network, no data collection.
  <a href="{APP}">Free on the App&nbsp;Store</a>.</p>
</div>
"""
    page(OUT / 'index.html', 'ERP Galaxy — what happens to your SAP tables in S/4HANA',
         f'{len(lifecycle)} published SAP ECC to S/4HANA table verdicts: which disappear, which are '
         f'replaced, and which survive only as compatibility views. Free, no login.',
         body, f'{BASE}/')

    urls = [f'{BASE}/', f'{BASE}/s4/', f'{BASE}/s4/code-must-change.html', f'{BASE}/s4/reads-still-work.html']
    urls += [f'{BASE}/s4/{t}.html' for t in sorted(lifecycle)]
    today = datetime.date.today().isoformat()
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls)
        + '</urlset>\n')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    (OUT / '.nojekyll').write_text('')

    print(f'{len(lifecycle)} table pages + 4 index pages')
    print(f'  code-must-change : {len(breaks)}')
    print(f'  reads-still-work : {len(reads)}')
    print(f'  sitemap urls     : {len(urls)}')
    print(f'  adsense          : {"configured" if ADSENSE_CLIENT else "NOT SET — slots emit comments only"}')

if __name__ == '__main__':
    build()
