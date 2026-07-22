#!/usr/bin/env python3
"""Embed data/foreign_keys.json into the explorer as FK.

The shipped FK const is a DERIVED shape -- [outbound, inbound] per table --
built from the outbound-only source file. That transform had no build step, so
like CODEX it could only be reproduced by hand. It is deterministic; this
captures it.
"""
import json, re, collections, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src  = root / 'sap-table-explorer.html'
fk   = json.load(open(root / 'data' / 'foreign_keys.json'))

inbound = collections.defaultdict(dict)
for s, m in fk.items():
    for tgt, fld in m.items():
        inbound[tgt][s] = fld

out = {t: [fk.get(t, {}), dict(inbound.get(t, {}))]
       for t in sorted(set(fk) | set(inbound))}
blob = 'const FK=' + json.dumps(out, separators=(',', ':'), ensure_ascii=False) + ';'

h = src.read_text()
new, n = re.subn(r'const FK=\{.*?\};', blob, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit('FK anchor not found')
src.write_text(new)
print(f'embedded FK for {len(out):,} tables '
      f'({sum(len(v[0]) for v in out.values()):,} outbound edges)')
