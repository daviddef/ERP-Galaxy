#!/usr/bin/env python3
"""Find tables SAP explicitly calls NEW in the Simplification List.

Why this exists: "new in S/4" was only derivable from the ecc/s4 flags on the
217 curated tables, so the filter showed 7 and any new table living only in the
index was invisible. Successor targets are NOT a substitute -- KNA1, LFA1, MARA,
MARC and RESB are all named as successors and all predate S/4.

So the only defensible signal is SAP saying the word. Each hit keeps the
surrounding quote, which the app displays, so the claim is checkable rather
than asserted.

The trap this deliberately avoids: "new" usually modifies something other than
the table. "creates new customizing entries in table BUT0ID" and "do not lead to
new entries in the database table IST_TDATA" both match a naive pattern and
both are wrong -- BUT0ID and IST_TDATA are not new tables.

Usage: python3 tools/build_new_in_s4.py <simpl2025.txt>
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PATTERNS = [
    r"new tables?\s+([A-Z][A-Z0-9_]{2,}(?:\s+and\s+[A-Z][A-Z0-9_]{2,})?)",
    r"new (?:planning file|database table|document table)\s+([A-Z][A-Z0-9_]{2,})",
    r"\bnew\b[^.]{0,40}?\btable\s+([A-Z][A-Z0-9_]{2,})",
    r"table\s+([A-Z][A-Z0-9_]{2,})\s+is new\b",
]

# "new entries IN table X" means the entries are new, not the table. The tell is
# the preposition: "entry table ACDOCA" and "Customizing table T130F_C" are both
# genuinely new tables, and a bare noun blocklist wrongly rejected them.
DISQUALIFY = re.compile(r"\b(entries|entry|records?|rows?|values?|fields?)\b\s+in\b", re.I)
# "... in table X" means "new" attaches to whatever preceded the preposition,
# not to X. This is what separates "new database table ACDOCA" (the table is
# new) from "saved in new Asset Accounting in table FAAT_DOC_IT" (the Asset
# Accounting is new; the table's own status is simply not stated here).
IN_TABLE = re.compile(r"\bin\s+(?:the\s+)?table\s", re.I)


def clean_quote(txt, start, end, pad=130):
    """A window trimmed to whole words, and to a sentence start where one is
    close by -- an excerpt beginning mid-word reads like a bug."""
    a, b = max(0, start - pad), min(len(txt), end + pad)
    frag = re.sub(r"\s+", " ", txt[a:b]).strip()
    dot = frag.find(". ")
    if 0 <= dot < 90:
        frag = frag[dot + 2:]
    elif " " in frag:
        frag = frag.split(" ", 1)[1]          # drop a partial leading word
    if " " in frag and not frag.rstrip().endswith("."):
        frag = frag.rsplit(" ", 1)[0]         # and a partial trailing one
    return frag.strip()


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: build_new_in_s4.py <simpl2025.txt>")
    txt = pathlib.Path(sys.argv[1]).read_text()

    found, rejected = {}, {}
    for pat in PATTERNS:
        for m in re.finditer(pat, txt):
            span = m.group(0)
            names = [n.strip() for n in re.split(r"\s+and\s+", m.group(1))]
            quote = clean_quote(txt, m.start(), m.end())
            for name in names:
                if not re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", name):
                    continue
                if DISQUALIFY.search(span) or IN_TABLE.search(span):
                    rejected.setdefault(name, span)
                    continue
                found.setdefault(name, quote)

    for name in rejected:
        found.pop(name, None)

    tables = json.loads((ROOT / "data" / "tables.json").read_text())
    curated = set(json.loads((ROOT / "data" / "curated_ids.json").read_text()))

    out = {}
    for name, quote in sorted(found.items()):
        where = "curated" if name in curated else ("index" if name in tables else "not held")
        out[name] = {"evidence": quote, "held": where}

    path = ROOT / "data" / "new_in_s4.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")

    print(f"accepted {len(out)}   rejected {len(rejected)} (\"new\" modified something else)")
    for n, s in sorted(rejected.items()):
        print(f"  rejected {n:16} {s[:70]}")
    print()
    for n, v in out.items():
        print(f"  {n:18} [{v['held']}]")
    print(f"\nwrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
