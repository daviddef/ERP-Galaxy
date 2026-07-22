#!/usr/bin/env python3
"""Embed data/sf_mapping.json into the explorer as SF_MAP.

Hand-pasted until now, so the file and the shipped const could drift silently.
"""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src  = root / 'sap-table-explorer.html'
d    = json.load(open(root / 'data' / 'sf_mapping.json'))

payload = {'i': d['infotypes'], 'chain': d['_chain'],
           'ftsd': d['_ftsdEligible'], 'caveat': d['_source']['caveat']}
blob = 'const SF_MAP=' + json.dumps(payload, separators=(',', ':'), ensure_ascii=False) + ';'

h = src.read_text()
new, n = re.subn(r'const SF_MAP=\{.*?\};', blob, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit('SF_MAP anchor not found')
src.write_text(new)
mapped = sum(1 for v in d['infotypes'].values() if v.get('fields'))
print(f"embedded {len(d['infotypes'])} infotypes ({mapped} with field mappings)")
