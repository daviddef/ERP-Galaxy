# Task: author factual `desc` for SAP tables

You will be given a JSON array of SAP table records: `{id, module, src}` where `src` is a terse
description scraped from a reference site. Produce ONE factual sentence per table in **your own words**.

## Hard rules — violating these makes the output worthless

1. **NEVER invent.** Your sentence must be supported by `src` + the table name + the module.
   You may expand an abbreviation ONLY if you are certain (e.g. `Txt`→text, `Doc.`→document,
   `w/tax`→withholding tax, `Cust.`→customer). If you are not certain, keep the term as-is.
2. **If `src` is too thin to describe** (e.g. "obsolete", "Language dependent", "Structure",
   a bare repeat of the table name, or empty) → output `null` for that id. Do NOT pad it.
   Outputting `null` is CORRECT and expected behaviour, not a failure. Roughly 1-3% should be null.
3. **Do not copy `src` verbatim.** Rephrase it. This is a licensing requirement. But rephrasing
   must not add facts. If `src` is already minimal (e.g. "Document type texts"), a close
   restatement like "Text descriptions for document types, one row per type and language."
   is fine — just don't reproduce the exact string.
4. **Some `src` text is German** (e.g. "Generierte Tabelle zu" = "Generated table for").
   Translate it. If you cannot translate confidently, output `null`.
5. **No personality, no jokes, no marketing.** This is the dry factual field; a separate `lore`
   field handles the fun voice. Plain, useful, neutral.

## Style

- ONE sentence. Under ~20 words. Sentence case, ends with a period.
- Say what the table *holds*, and if `src` supports it, its grain (e.g. "one row per ...").
- Prefer concrete nouns over SAP-speak. "Vendor master data, general section" not "Contains the LFA1 entity".
- Do not start with "This table contains" — go straight to the content.

## Good examples

| id | src | desc |
|---|---|---|
| `T003T` | Document type texts | `Text descriptions for document types, one row per type and language.` |
| `LFB1` | Vendor master (company code) | `Vendor master data specific to one company code, such as reconciliation account and payment terms.` |
| `PA0020` | HR Master Record- Infotype 0020 (DUEVO) | `HR master record infotype 0020, holding DUEVO social insurance notification data.` |
| `/TDAG/CPT_EXEMLI` | CP: Exemption Limits | `Exemption limits used by Compliance for Products in SAP EHS Management.` |
| `/TDAG/RCSA_TPL` | obsolete | `null` |
| `/TDAG/EHXC_DBNAM` | Language dependent | `null` |

## Output

Write STRICT JSON to the output path given — an object mapping every input id to a string or null.
Include EVERY id from the input. No markdown fences, no commentary, no extra keys.

```json
{"T003T": "Text descriptions for document types, one row per type and language.", "/TDAG/RCSA_TPL": null}
```
