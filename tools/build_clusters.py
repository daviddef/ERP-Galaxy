#!/usr/bin/env python3
"""Embed data/cluster_tables.json into the explorer as CLUSTER_TABLES.

Cluster tables get their own class in the app because the app was quietly
lying about them: it offered joins and key fields as though you could SELECT
the data. You cannot. The payload is one compressed binary field.
"""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src  = root / 'sap-table-explorer.html'
data = json.load(open(root / 'data' / 'cluster_tables.json'))

payload = {'common': data['_common'], 'tables': data['tables'], 's4': data['_s4'],
           'source': data['_source']['primary'],
           'areasCaveat': data['_source']['areasCaveat']}
blob = 'const CLUSTER_TABLES=' + json.dumps(payload, separators=(',', ':'), ensure_ascii=False) + ';'

h = src.read_text()
new, n = re.subn(r'const CLUSTER_TABLES=\{.*?\};(?=\s*//)', blob + '   //', h, count=1, flags=re.S)
if n != 1:
    raise SystemExit('CLUSTER_TABLES anchor not found — did the declaration move?')
src.write_text(new)
print(f'embedded {len(data["tables"])} cluster tables, {len(blob):,} bytes')
