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

rows.sort(key=lambda r: (r['tier'], r['id']))
out = root / 'ERPGalaxy' / 'Resources' / 'Data' / 'tables_native.json'
prev = len(json.load(open(out)))
json.dump(rows, open(out, 'w'), ensure_ascii=False)
print(f'{prev} -> {len(rows)} tables '
      f'(curated {sum(1 for r in rows if r["tier"]==1)}, index {sum(1 for r in rows if r["tier"]==2)})')
