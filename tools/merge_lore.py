#!/usr/bin/env python3
"""Merge generated lore into the codex, refusing anything that invented facts.

Lore is written from a table's own `desc`, `module`, `keyFields` and foreign-key
neighbours -- it rephrases and contextualises what we already hold, it does not
add SAP knowledge. This gate enforces that mechanically, because a fluent
sentence stating a wrong SAP fact is worse than no sentence.

An entry is REJECTED if it contains an uppercase identifier-shaped token that
does not appear in the table's own allowed vocabulary (its id, its key fields,
its related tables and their join fields, and the words of its own desc), or a
transaction-code / SAP-Note / release-shaped token, or a digit that isn't in the
source. Rejected entries are reported and simply not merged.

Usage: python3 tools/merge_lore.py <lore-dir>
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Ordinary English/industry abbreviations that are not SAP object names.
ALLOWED_WORDS = {
    "SAP", "ABAP", "SQL", "EDI", "IDOC", "IDOCS", "GUID", "UUID", "API", "APIS",
    "BADI", "BAPI", "CDS", "DDIC", "ERP", "LIS", "MRP", "VAT", "GST", "WBS",
    "FIFO", "LIFO", "PDF", "XML", "JSON", "URL", "UI", "OK", "ID", "IDS",
    "TEMSE", "SD", "MM", "FI", "CO", "PP", "PM", "QM", "PS", "HR", "WM", "EHS",
    "FM", "BASIS", "LO", "LE", "CA", "GL", "AP", "AR", "AA", "IM", "IV", "PUR",
    "CFP", "TDAG", "ATC", "BOM", "BOMS", "ERS", "MIGO", "GR", "GI", "PO", "POS",
    "STO", "UOM", "COGS", "WIP", "SOP", "ATP", "EWM", "CRM", "SRM", "BW",
    # Slash-joined finance abbreviations read as one token by TOKEN.
    "G/L", "P/L", "A/P", "A/R", "B/S", "W/H",
}

TCODE = re.compile(r"\b(?:[A-Z]{2}\d{2}[A-Z0-9]*|SE\d{2}|SM\d{2}|VA\d{2}|ME\d{2})\b")
NOTE = re.compile(r"\b(?:note|oss)\s*\d{5,}\b", re.I)
RELEASE = re.compile(r"\b(?:S/?4\s*HANA|ECC\s*6|EHP\d|1511|1610|1709|1809|1909|20\d\d\s*FPS)\b", re.I)
TOKEN = re.compile(r"\b[A-Z][A-Z0-9_/]{2,}\b")


def allowed_vocab(rec):
    """Every uppercase token the entry is permitted to use."""
    vocab = {rec["id"].upper()}
    vocab |= {k.upper() for k in (rec.get("keyFields") or [])}
    for rel in rec.get("related") or []:
        # "MARA (via MATNR)" -> MARA, MATNR
        vocab |= {t.upper() for t in re.findall(r"[A-Za-z0-9_/]+", rel)}
    vocab |= {t.upper() for t in re.findall(r"[A-Za-z0-9_/]+", rec.get("desc") or "")}
    vocab |= ALLOWED_WORDS
    return vocab


def check(rec, lore):
    """-> list of reasons this entry must be rejected."""
    bad = []
    if not lore or len(lore) < 40:
        bad.append("too short")
    if len(lore) > 420:
        bad.append("too long")
    if TCODE.search(lore):
        bad.append("transaction code: " + TCODE.search(lore).group(0))
    if NOTE.search(lore):
        bad.append("SAP Note reference")
    if RELEASE.search(lore):
        bad.append("release reference: " + RELEASE.search(lore).group(0))

    vocab = allowed_vocab(rec)
    for tok in set(TOKEN.findall(lore)):
        # "EBELN/EBELP/ETENR" and "G/L" are slash-joined lists, not single
        # identifiers -- validate each part so ordinary prose isn't rejected.
        if tok in vocab:
            continue
        parts = [p for p in tok.split("/") if p]
        if parts and all(p in vocab for p in parts):
            continue
        bad.append("unknown identifier: " + tok)

    # Digits inside the table's own name (A148, DD06L) are not invented facts.
    src_digits = set(re.findall(r"\d+", (rec.get("desc") or "")
                                + " ".join(rec.get("related") or [])
                                + " " + rec["id"]
                                + " ".join(rec.get("keyFields") or [])))
    for num in set(re.findall(r"\d+", lore)):
        if num not in src_digits and not any(num in d for d in src_digits):
            bad.append("invented number: " + num)
    return bad


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: merge_lore.py <lore-dir>")
    lore_dir = pathlib.Path(sys.argv[1])

    inputs = {}
    for f in sorted(lore_dir.glob("batch*.json")):
        for rec in json.loads(f.read_text()):
            inputs[rec["id"]] = rec

    generated = {}
    for f in sorted(lore_dir.glob("out*.json")):
        generated.update(json.loads(f.read_text()))
    print(f"inputs {len(inputs)} | generated {len(generated)}")

    accepted, rejected = {}, {}
    for tid, lore in generated.items():
        rec = inputs.get(tid)
        if not rec:
            rejected[tid] = ["not in any input batch"]
            continue
        reasons = check(rec, lore)
        if reasons:
            rejected[tid] = reasons
        else:
            accepted[tid] = lore.strip()

    print(f"accepted {len(accepted)} | rejected {len(rejected)}")
    if rejected:
        print("\nrejected (not merged):")
        for tid, reasons in sorted(rejected.items())[:40]:
            print(f"  {tid:18} {'; '.join(sorted(set(reasons))[:3])}")
        if len(rejected) > 40:
            print(f"  ... and {len(rejected)-40} more")

    path = ROOT / "data" / "tables.json"
    tables = json.loads(path.read_text())
    wrote = 0
    for tid, lore in accepted.items():
        if tid in tables and not tables[tid].get("lore"):
            tables[tid]["lore"] = lore
            wrote += 1
    path.write_text(json.dumps(tables, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

    have = sum(1 for v in tables.values() if v.get("lore"))
    print(f"\nmerged {wrote} | lore coverage now {have}/{len(tables)}")


if __name__ == "__main__":
    main()
