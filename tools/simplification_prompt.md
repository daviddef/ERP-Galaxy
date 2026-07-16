# Task: extract table lifecycle facts from SAP Simplification List items

Input: a JSON array of items `{id, title, text}` from SAP's official Simplification List for
S/4HANA 2023. Each is one "S4TWL" (S/4 Transition Worklist) entry describing something that
changed in S/4HANA.

Extract, for **each SAP table explicitly named in the item's text**, what happens to it in S/4HANA.

## Hard rules

1. **Only report tables the text actually names.** Do not add tables you know are related.
   Do not infer from the title alone.
2. **Only report a status the text actually supports.** If the item mentions a table but does not
   say what happens to it (e.g. it's just named in passing as a selection criterion), use
   `"mentioned"` — do NOT upgrade that to `"deprecated"`.
3. **`replacedBy` only if the text names the successor.** Otherwise `null`.
4. **Never guess.** An empty array for an item is a valid, correct answer.
5. `evidence` must be a SHORT verbatim quote (<=25 words) from the item text that supports your
   status. If you cannot quote it, you cannot claim it.

## Status values (use exactly one)

- `"deprecated"` — table is no longer available / not supported / must not be used in S/4.
- `"replaced"`   — its function moved to another table (set `replacedBy`).
- `"compat_view"`— the table now exists only as a compatibility view, not a real table.
- `"changed"`    — still exists but its structure/semantics/content changed.
- `"unchanged"`  — text explicitly says it is unaffected/still available.
- `"mentioned"`  — named, but the text does not state what happens to it.

## Output

Write STRICT JSON to the given output path: an array of objects.

```json
[
  {"item": "2.33", "table": "BSEG", "status": "changed",
   "replacedBy": null,
   "evidence": "line items are now stored in ACDOCA"}
]
```

One object per (item, table) pair. No markdown fences, no commentary.
If an item yields nothing, simply contribute no objects for it.
