#!/usr/bin/env python3
"""Replace guessed module assignments with SAP's own Application Component.

185 codex tables carry `moduleInferred` -- their module was guessed from the
table-name prefix. SAP's Simplification List states an "Application Component"
per item (FI-AA, CO-PC-ACT, PP-MRP ...), which is a real source for the same
answer.

Conservative on purpose, because a wrong module is a wrong colour and a wrong
filter result:

  * A table must be mentioned as a standalone token in the item body.
  * The component must map cleanly into the module vocabulary the app already
    uses. Components like LO-ELR, CA-GTF or FS-BP have no home in that
    vocabulary, so they are skipped rather than forced -- this is what stops
    DBTABLOG (a Basis change-log table mentioned in passing by a logistics
    item) from being relabelled LO.
  * Where a table matches several items, every one of them must agree on the
    resulting module.

Anything left unresolved keeps `moduleInferred` and is surfaced as inferred in
the app, which is the honest outcome rather than a confident guess.

Usage: python3 tools/fix_inferred_modules.py <path-to-simpl2025.txt>
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Component prefix -> the module vocabulary the app renders and filters on.
# Only unambiguous mappings. Cross-application (CA-), financial services (FS-),
# and generic logistics (LO-) are deliberately absent.
COMPONENT_MODULE = [
    ("FI-", "FI"), ("FIN-", "FI"),
    ("CO-", "CO"),
    ("MM-", "MM"),
    ("SD-", "SD"),
    ("PP-", "PP"),
    ("PM-", "PM"),
    ("QM-", "QM"),
    ("PS-", "PS"),
    ("LE-WM", "WM"),
    ("BC-", "BASIS"),
    ("EHS", "EHS"),
]


def module_for(component):
    for prefix, module in COMPONENT_MODULE:
        if component.startswith(prefix):
            return module
    return None


def parse_items(text):
    """-> {item_number: (title, body)} for every S4TWL item body."""
    lines = text.splitlines()
    heads = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\d+(?:\.\d+)+)\.\s+S4TWL\s*-\s*(.+?)\s*$", line)
        if m:
            heads.append((i, m.group(1), m.group(2)))
    out = {}
    for n, (i, num, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        out[num] = (title, "\n".join(lines[i:end]))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: fix_inferred_modules.py <simpl2025.txt>")
    bodies = parse_items(pathlib.Path(sys.argv[1]).read_text())

    components = {}
    for num, (_title, body) in bodies.items():
        m = re.search(r"^Application Component:\s*([A-Z0-9\-_/]+)\s*$", body, re.M)
        if m:
            components[num] = m.group(1)

    tables = json.loads((ROOT / "data" / "tables.json").read_text())
    inferred = [t for t, v in tables.items() if v.get("moduleInferred")]
    print(f"item bodies {len(bodies)} | with component {len(components)} | "
          f"inferred tables {len(inferred)}\n")

    resolved, conflicted, unmapped = {}, {}, []
    for tid in inferred:
        pat = re.compile(r"(?<![A-Z0-9_/])" + re.escape(tid) + r"(?![A-Z0-9_])")
        mods, comps = set(), set()
        # Keep the components that actually produced a module, so the recorded
        # provenance is the one the answer came from and not just the first
        # component alphabetically.
        deciding = set()
        for num, (_t, body) in bodies.items():
            if num in components and pat.search(body):
                comp = components[num]
                comps.add(comp)
                mod = module_for(comp)
                mods.add(mod)
                if mod:
                    deciding.add(comp)
        if not comps or not deciding:
            unmapped.append(tid)          # no match, or only unmappable components
        elif len(mods - {None}) == 1:
            resolved[tid] = (sorted(mods - {None})[0], sorted(deciding))
        else:
            conflicted[tid] = sorted(comps)

    changed, confirmed = [], []
    for tid, (mod, comps) in sorted(resolved.items()):
        was = tables[tid]["module"]
        (confirmed if was == mod else changed).append((tid, was, mod, comps))
        tables[tid]["module"] = mod
        tables[tid]["moduleSource"] = "sap-application-component:" + comps[0]
        tables[tid].pop("moduleInferred", None)

    print(f"resolved   {len(resolved):3}  (module changed {len(changed)}, "
          f"guess confirmed {len(confirmed)})")
    print(f"conflicted {len(conflicted):3}  (kept as inferred)")
    print(f"unmapped   {len(unmapped):3}  (kept as inferred)\n")

    if changed:
        print("module corrected:")
        for tid, was, now, comps in changed:
            print(f"  {tid:16} {was:6} -> {now:6}  {comps[0]}")

    (ROOT / "data" / "tables.json").write_text(
        json.dumps(tables, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    still = sum(1 for v in tables.values() if v.get("moduleInferred"))
    print(f"\nmoduleInferred remaining: {still} (was {len(inferred)})")


if __name__ == "__main__":
    main()
