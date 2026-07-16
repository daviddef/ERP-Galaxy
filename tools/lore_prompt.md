# Task: write `lore` — the fun voice — for SAP tables

Input: JSON array of `{id, module, submodule, desc, keys, referenced_by, ref_count, points_to}`.
Write ONE `lore` string per table: the same factual content as `desc`, but in a voice a smart
colleague would use explaining it over coffee.

## The voice (reverse-engineered from the app's existing curated tables)

Real examples already in the product:

> **BKPF** — "The cover sheet for every financial posting. One row per document. Who posted it,
> when, which company code, fiscal year, and document type. If BSEG is the body, BKPF is the envelope."

> **BSEG** — "Every single debit and credit line of every financial posting. This is usually the
> BIGGEST table in any ECC6 system."

> **ACDOCA** — "THE big table of S/4HANA. SAP merged Finance, Controlling, Asset Accounting,
> Material Ledger and Profitability Analysis into ONE line-item table. Primary key includes
> ledger (RLDNR) — always filter by it."

What makes these work:
- **An analogy that teaches** ("envelope / body")
- **Caps for emphasis, sparingly** ("THE big table", "BIGGEST")
- **A practical warning tucked in** ("always filter by RLDNR")
- **Short sentences. Fragments are fine.**
- Speaks to a person doing a job, not to an auditor.

## Hard rules — breaking these makes the output worthless

1. **Never invent.** Everything must be supported by `desc`, `keys`, the table name, the module,
   or the reference data given. You may reason FROM the inputs — e.g. if `referenced_by` has 31
   tables, "31 tables point at this one, so it's a backbone config table" is supported. Inventing
   a field, a transaction, or a behaviour is not.
2. **No invented history, versions, or SAP notes.** Do not say "introduced in ECC 6.0 EhP5" or
   "deprecated in S/4" unless the input says so. You have no migration data here.
3. **`ref_count` is a fact you can use.** A table referenced by 456 others is genuinely central —
   that's worth saying, and it's the kind of insight a lookup site can't give.
4. **Keys are facts you can use.** `MANDT, BUKRS` genuinely means "per client, per company code".
   Do not guess what an unfamiliar key field means — if unsure, don't mention it.
5. **If `desc` is too thin to say anything true and interesting, output `null`.** Padding a
   config-table stub into false colour is the worst outcome. `null` is a correct answer.
6. **No jokes for their own sake. No exclamation marks. No marketing.** Personality comes from
   clarity and a point of view, not from trying to be funny.

## Style

- 1–3 sentences, roughly 25–55 words. Longer than `desc`, but not an essay.
- Say what it holds, why anyone cares, and — where the inputs support it — how it relates to
  its neighbours.
- Prefer concrete nouns over SAP-speak.

## Good examples (built only from the inputs)

| id | desc | ref_count | lore |
|---|---|---|---|
| `T024E` | Records defining purchasing organizations | 31 | `The list of purchasing organisations — the "who is allowed to buy" unit in MM. 31 tables point back at this one, which tells you how much of purchasing hangs off it. Small table, wide blast radius.` |
| `T042Z` | Definitions of payment methods used by the automatic payment program | 23 | `Every payment method your payment run can use — cheque, transfer, direct debit — one row each. When F110 says a method isn't allowed, this is usually where the answer is.` |
| `TTXJ` | Check table listing valid tax jurisdiction codes | 14 | `The valid tax jurisdiction codes. It's a check table, so it exists to stop anyone typing a jurisdiction that doesn't exist. Mostly invisible until someone loads master data and it rejects half the rows.` |

Note `T042Z` mentions F110 — the automatic payment program. Only make a link like that when
you are certain; if not, leave it out.

## Output

Write STRICT JSON to the given path: an object mapping every input id to a string or null.
No markdown fences, no commentary. Include EVERY id from the input.
