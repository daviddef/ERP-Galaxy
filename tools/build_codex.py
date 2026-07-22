#!/usr/bin/env python3
"""Embed data/tables.json into the explorer as CODEX.

There was no build step for this -- CODEX had been pasted in by hand, so it had
drifted to 2,013 entries while data/tables.json had moved on. Index additions
were silently not reaching the app. This makes it repeatable.

CODEX shape: {id: [module, desc, keyFields, lore]}
"""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src  = root / 'sap-table-explorer.html'
data = json.load(open(root / 'data' / 'tables.json'))

codex = {k: [v.get('module'), v.get('desc'), v.get('keyFields') or [], v.get('lore')]
         for k, v in sorted(data.items())}
blob = 'const CODEX=' + json.dumps(codex, separators=(',', ':'), ensure_ascii=False) + ';'

h = src.read_text()
new, n = re.subn(r'const CODEX=\{.*?\};\n', blob + '\n', h, count=1, flags=re.S)
if n != 1:
    raise SystemExit('CODEX anchor not found')
src.write_text(new)

before = len(re.search(r'const CODEX=(\{.*?\});\n', h, re.S).group(1).split('","')) 
print(f'embedded {len(codex):,} tables ({len(blob):,} bytes)')
missing = [k for k, v in codex.items() if not v[1]]
print(f'  without a description: {len(missing)}')
