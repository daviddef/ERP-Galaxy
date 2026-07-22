#!/usr/bin/env python3
"""Regenerate ERPGalaxy/Resources/Data/tables_native.json from the web catalogue.

Third instance of the same defect class as CODEX and FK: the native copy of the
catalogue -- the ONLY thing Spotlight and the widget can read, because neither
can reach inside the WebView -- had no build step. It had fallen 55 tables
behind, so every table added recently was invisible to iOS search.

Curated records (in the HTML) are authoritative where they exist; the index
(data/tables.json) fills in the rest.
"""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
h = (root / 'sap-table-explorer.html').read_text()
index = json.load(open(root / 'data' / 'tables.json'))

def field(block, name):
    m = re.search(r'\b%s:"((?:[^"\\]|\\.)*)"' % name, block)
    return m.group(1).replace('\\"', '"') if m else None

rows, seen = [], set()
# Curated first -- they carry hand-written descriptions and ECC/S4 flags.
for m in re.finditer(r'\{id:"([A-Z0-9_/]+)",module:"([A-Z0-9_/]+)"(.*?)\n\s*relations:', h, re.S):
    tid, mod, body = m.group(1), m.group(2), m.group(3)
    if tid in seen:
        continue
    seen.add(tid)
    rows.append({'id': tid, 'module': mod,
                 'ecc': 'ecc:true' in body, 's4': 's4:true' in body,
                 's4status': field(body, 's4status'),
                 'desc': field(body, 'shortDesc') or tid, 'tier': 1})

for tid, v in sorted(index.items()):
    if tid in seen:
        continue
    seen.add(tid)
    rows.append({'id': tid, 'module': v.get('module') or 'OTHER',
                 'ecc': True, 's4': True, 's4status': None,
                 'desc': v.get('desc') or tid, 'tier': 2})

# The fate is computed HERE, once, using the same precedence as tableFate() in
# the web app -- SAP's published verdict outranks our coarse ecc/s4 flags.
# TableStore.swift used to re-derive this from the flags alone, so Spotlight
# told people BSIS "Disappears in S/4HANA" when SAP says it survives as a
# compatibility view and their reports keep working. 20 tables were wrong.
# One rule, one place, and Swift just reads the answer.
lifecycle = json.load(open(root / 'data' / 's4_lifecycle.json'))
new_in_s4 = json.load(open(root / 'data' / 'new_in_s4.json'))

VERDICT = {
    'deprecated':  'Disappears in S/4HANA',
    'replaced':    'Replaced in S/4HANA',
    'compat_view': 'Compatibility view — reads work, not writes',
    'changed':     'Changes in S/4HANA',
    'unchanged':   'Unchanged in S/4HANA',
}

def fate_of(r):
    tid = r['id']
    if tid in new_in_s4:
        return 'New in S/4HANA'
    e = lifecycle.get(tid)
    curated = r['tier'] == 1
    if curated and not r['ecc'] and r['s4']:
        return 'New in S/4HANA'
    if e:
        v = VERDICT.get(e['s4status'])
        if v:
            by = e.get('replacedBy')
            # A successor name is the single most useful thing a search result
            # can carry -- it answers "then where is my data?" without a tap.
            if by and e['s4status'] == 'replaced':
                return f'Replaced by {by} in S/4HANA'
            return v
    if not curated:
        return ''
    if r['ecc'] and not r['s4']:
        return 'Disappears in S/4HANA'
    return {'deprecated': 'Disappears in S/4HANA', 'modified': 'Changes in S/4HANA',
            'new': 'New in S/4HANA'}.get(r.get('s4status'), 'Carries over to S/4HANA')

for r in rows:
    r['fate'] = fate_of(r)

rows.sort(key=lambda r: (r['tier'], r['id']))
out = root / 'ERPGalaxy' / 'Resources' / 'Data' / 'tables_native.json'
prev = len(json.load(open(out)))
json.dump(rows, open(out, 'w'), ensure_ascii=False)
import collections
print(f'{prev} -> {len(rows)} tables '
      f'(curated {sum(1 for r in rows if r["tier"]==1)}, index {sum(1 for r in rows if r["tier"]==2)})')
c = collections.Counter(r['fate'].split(' in ')[0].split(' \u2014 ')[0] for r in rows if r['fate'])
print('  fates:', dict(c.most_common()))
