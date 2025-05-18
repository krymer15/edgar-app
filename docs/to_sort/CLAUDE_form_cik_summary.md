# SEC Form Filing CIK and Entity Extraction Summary

This document outlines the best methods, sources, and implementation guidance for extracting filer and issuer CIKs from various SEC form types used in the Safe Harbor EDGAR AI Platform.

---

## 1. Form Metadata Extraction Overview

| Form     | Structured Format | Filer CIK Source        | Issuer CIK Present? | Other Entities | XML Available? | Machine-Readable Holdings/Targets? |
|----------|--------------------|--------------------------|---------------------|----------------|----------------|-------------------------------------|
| 10-K     | SGML `.txt`        | Regex (`CIK:` line)      | ✅ Yes              | ❌ No          | ❌ No          | ❌ No                                |
| 10-Q     | SGML `.txt`        | Regex (`CIK:` line)      | ✅ Yes              | ❌ No          | ❌ No          | ❌ No                                |
| 8-K      | SGML `.txt`        | Regex (`CIK:` line)      | ✅ Yes              | ❌ No          | ❌ No          | ❌ No                                |
| Form 4   | XML                | `<issuerCik>` + `<rptOwnerCik>` | ✅ Yes | ✅ Yes         | ✅ Yes         | ❌ (but structured)                  |
| 13F-HR   | XML + SGML         | `<cik>` (XML) or regex    | ❌ No               | Holdings only  | ✅ Yes         | ✅ `infoTable[]`                     |
| 13D/G    | SGML `.txt`        | Regex (`CIK:` line)      | ❌ No               | Target company name only | ❌ No | ❌ No                                |
| 14A      | SGML `.txt`        | Regex (`CIK:` line)      | ✅ Yes              | ❌ No          | ❌ No          | ❌ No                                |
| 425      | SGML `.txt`        | Regex (`CIK:` line)      | ✅ Yes              | ❌ No          | ❌ No          | ❌ No                                |
| 424B*    | SGML `.txt`        | Regex (`CIK:` line)      | ✅ Yes              | ❌ No          | ❌ No          | ❌ No                                |

---

## 2. CIK & Entity Role Summary

| Form      | Filer CIK | Issuer CIK | Reporting Entities | Target Company (Name only) | Notes |
|-----------|-----------|------------|---------------------|-----------------------------|-------|
| 10-K/Q/8-K/14A/425/424B | ✅ | ✅ (same) | ❌ | ❌ | One entity (issuer is filer) |
| Form 4     | ✅ | ✅         | ✅ (e.g. insiders)   | ❌ | Multiple CIKs per filing |
| 13F-HR     | ✅ | ❌        | ❌ | ✅ via `nameOfIssuer` | Holdings only; CUSIP and name |
| 13D/G      | ✅ | ❌        | ❌ | ✅ (text narrative) | Must infer issuer |

---

## 3. CIK Extraction Methods

| Form      | CIK Extraction Method | Tag or Pattern | Implementation Logic |
|-----------|------------------------|----------------|-----------------------|
| 10-K/Q/8-K/14A/425/424B | Regex from `.txt` | `^CIK:\s+(\d+)` | Extract from metadata |
| Form 4     | Parse XML             | `<issuerCik>`, `<rptOwnerCik>` | Structured parse |
| 13F-HR     | XML or regex fallback | `<cik>` or `^CIK:` line | Prefer XML |
| 13D/G      | Regex from `.txt`     | `^CIK:\s+(\d+)` | Plaintext regex |
| 13F Issuer | XML                   | `<nameOfIssuer>` | Requires external mapping |

---

## 4. Implementation Notes

| Form Group | Logic Needed | Implementation Tips |
|------------|--------------|----------------------|
| 10-K/Q/8-K/14A/425/424B | Simple regex | Use universal SGML regex parser |
| Form 4     | Multi-entity | Use XML for issuer + reporters |
| 13F-HR     | Holdings logic | Extract from `infoTable[]`, map CUSIP |
| 13D/G      | Narrative logic | Use regex or GPT/NER on `Item 1` |
| Exhibits   | Optional      | Extract exhibit metadata if needed |

---

## 5. Suggested SQL Schema Models

| Model/Table         | Fields |
|---------------------|--------|
| filings             | accession_number, form_type, filer_cik, file_date, issuer_name (optional) |
| form4_entities      | filing_id, entity_cik, role (issuer, reporter) |
| form13f_holdings    | filing_id, name_of_issuer, cusip, value, shares |
| exhibit_metadata    | filing_id, exhibit_number, filename, accessible_flag |

---

## Notes

- The `CIK:` line is reliably present in SGML forms, even when tags are missing.
- Form 4 and 13F are the only ones with rich structured XML.
- Issuer CIKs must often be inferred from text (13D/G) or mapped from CUSIP (13F).