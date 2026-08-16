# Build report

Build date **16 August 2026**. This file records exactly what was fetched, what was computed, what was verified, and what could not be obtained. Where a claim is weaker than it might look, it is weakened here rather than in the README.

## Sources actually fetched

| Source | Endpoint | Result |
|---|---|---|
| FDIC BankFind institutions | `https://api.fdic.gov/banks/institutions` | Fetched. Keyless, no registration. 4,250 active and 27,836 all-time records, 134 fields. Note the host moved: `banks.data.fdic.gov` now issues a 301 to `api.fdic.gov`. |
| GLEIF golden copy, Level 1 | `goldencopy.gleif.org/api/v2/golden-copies/publishes` | Fetched. Publication stamped 2026-08-16 08:00, 3,403,760 records, 476 MB zipped, 4.94 GB as CSV, CDF version LEI_3.1. |
| GLEIF golden copy, Level 2 (relationships) | same API | Fetched. 484,565 records. Active relationship types present: `IS_FUND-MANAGED_BY` 149,242, `IS_ULTIMATELY_CONSOLIDATED_BY` 132,526, `IS_DIRECTLY_CONSOLIDATED_BY` 126,366, `IS_SUBFUND_OF` 73,103, `IS_INTERNATIONAL_BRANCH_OF` 1,943, `IS_FEEDER_TO` 1,385. |
| Federal Reserve MDRM | `https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip` | Fetched. 7.7 MB zip containing `MDRM_CSV.csv` (91,178,734 bytes, stamped 2026-08-16 04:00) and a README last updated 2017-05-11. Line 1 of the CSV is a `PUBLIC` classification banner; the real header is line 2. |

## Sources that could NOT be obtained

These are real gaps and they constrain what this build can claim.

- **FFIEC National Information Center bulk data** (`ffiec.gov/npw/FinancialReport/DataDownload`). Returns HTTP 403 with a page titled "CAPTCHA Error | FFIEC". This is a bot challenge, not a login or a licence restriction; the data is public but is not reachable by script from this environment. **Consequence:** the Federal Reserve's own holding-company hierarchy, with percentage equity and relationship levels, is absent from this build. The FDIC's `RSSDHCR` high-holder field is used instead, which gives one edge per insured institution and no ownership percentages. The comparison this build would most like to make, the Fed's view of who owns whom against GLEIF's, is therefore **not** made here.
- **HMDA / FFIEC CFPB platform** (`ffiec.cfpb.gov`). Not used in this build. **This entry originally recorded the host as edge-blocked, and that was wrong**: see the addendum below. The host serves normally to an honest `curl` User-Agent, and the 2023 HMDA panel (5,113 rows carrying `lei` and `respondent_rssd`, though no FDIC certificate number, which that file has never contained) is openly downloadable. It is queued for the next build rather than claimed in this one. Note also that the panel has been discontinued: 2023 is the final edition, and from 2024 the CFPB publishes only a transmittal sheet, which carries no RSSD at all.
- **FFIEC Central Data Repository** Call Report bulk downloads were not exercised in this build.
- **NMLS Consumer Access** offers no bulk download that was found.

## Addendum, 16 August 2026: the NIC cross-check

The FFIEC National Information Center bulk files were obtained after the first build, not from the live endpoint, which remains behind a CAPTCHA, but from **Internet Archive captures**: `CSV_ATTRIBUTES_ACTIVE.CSV` and `CSV_RELATIONSHIPS.CSV` from a **23 May 2025** snapshot. These are therefore **stale by roughly fifteen months** and are used only for corroboration, never as a primary source for any headline number. No CAPTCHA was solved, bypassed or attacked, and no credentials were used.

What they corroborate, verified directly: NIC records RSSD 917742 (Associated Bank, National Association, FDIC certificate 5296) with `ID_LEI = ZF85QS7OXKPBG52R7N18`, and RSSD 1199563 (Associated Banc-Corp) with `ID_LEI = 549300N3CIN473IW5094`. Across all 61,308 NIC entity records the `ID_LEI` length histogram is `{1: 53067, 20: 8241}`, so every populated value is a well-formed 20-character LEI. This independently confirms both that the bank's own LEI exists and that the value the FDIC publishes belongs to its parent, from a source with no dependency on the GLEIF join used elsewhere in this build.

A separate correction worth recording for anyone reproducing this work: `ffiec.cfpb.gov`, which serves the HMDA files, is **not** edge-blocked. It returns HTTP 403 only when a browser User-Agent is spoofed over a non-browser TLS stack, and returns 200 to an honest `curl` User-Agent. An earlier attempt failed because it tried to look like a browser.

## What was computed, and how

- **Truncation.** Every LEI value in the FDIC register was measured. The length histogram is `{16: 2252}`. No value has any other length, which is why this is described as a systematic schema truncation rather than data entry error.
- **Collision measurement.** All 3,403,760 LEIs were reduced to their first 16 characters and counted. This is a direct census, not a sample or an estimate.
- **Resolution.** Each FDIC value was matched as a prefix against every LEI in the golden copy. Resolution is therefore a property of the register *on 16 August 2026*; a value unique today can become ambiguous when a new LEI is issued under the same prefix. `bank:resolutionCardinality` records what was true at build time and the SKOS registry says so explicitly under `banksch:PrefixJoin`.
- **Case.** Resolution is performed on uppercased values. 12 values contain lowercase characters; all 12 resolve once uppercased, so they are formatting defects rather than information loss. Without case normalisation, 28 values fail to resolve rather than 16.
- **Parent detection.** For each uniquely resolved value, GLEIF Level 2 active consolidation edges were used to find the resolved entity's children, and a child was accepted as "the bank" only if its legal name matched the FDIC institution name under a conservative key that removes legal-form words (`n.a.`, `inc`, `llc`, `the`) but **deliberately retains** `bancorp`, `bancshares`, `holding` and `financial`, because those are exactly the tokens that distinguish a parent from its subsidiary. An earlier version of this test stripped those tokens too and returned zero cases, including for Associated Bank, where the answer is known; the conservative key is the corrected one.

## Claims deliberately weakened

- **"2 confirmed, 15 more parent-shaped."** Only **2** cases (Associated Bank, National Association; First Southwest Bank) are proven by an active GLEIF consolidation edge linking the resolved entity to a name-matching child. A further **15** resolve to names containing `BANCORP`, `BANCSHARES`, `BANKSHARES` or `HOLDING`, including SoFi Bank to GOLDEN PACIFIC BANCORP and First NBC Bank to First NBC Bank Holding Company. Those are strongly parent-shaped but GLEIF publishes no active edge proving the link, so they are reported separately and are **not** counted as confirmed.
- **Wrong-country resolutions.** Six resolved LEIs sit outside the US. Five are Puerto Rico institutions correctly registered under `PR` (Banco Popular de Puerto Rico, FirstBank Puerto Rico, Oriental Bank, Banco Santander Puerto Rico, Scotiabank de Puerto Rico) and are **not** errors. Only **one**, CBI Bank & Trust resolving to a German entity, is a genuine wrong-entity resolution provable from the country code.
- **Per-institution versus per-value counts.** The graph contains active institutions only, and counts institutions. Set-based analyses over distinct asserted values give slightly different totals where two certificates share a value: 283 lapsed institutions correspond to 282 distinct values. Neither number is wrong; the unit differs and is stated each time.
- **All-register versus active-only.** 12 lowercase values and 16 unresolvable values exist across all 27,836 records; the graph and the SHACL gate see 11 and 3 respectively because they cover active institutions only.
- **"The MDRM is definitionally flat"** is a claim about the **published machine-readable file**. Description and Item Name are byte-for-byte identical per item code across every row. It is possible that the interactive MDRM web dictionary presents form-specific instruction text that the CSV export does not carry; this build cannot speak to that, and the claim is scoped to the distributed artifact.
- **Missing LEI in the FDIC register does not mean the bank has no LEI.** Ally Bank, Regions Bank and City National Bank have no LEI value in BankFind. This is a register completeness gap. It was not tested whether those institutions hold LEIs in GLEIF under their own names.

## Verification performed

- `pipeline/checksums.py` self-test passes on known-valid LEIs verified against the GLEIF API in prior work in this series, and on known-invalid vectors including an all-zero value and a letter-O transposition.
- Every Turtle artifact was parsed by rdflib: `bro-core.ttl` 194 triples, `identifier-schemes.ttl` 179, `bro-shapes.ttl` 114. The built graph is 1,123,634 triples and `build/bro-entity.ttl` re-parses at 128,617.
- The SHACL gate over the entity layer independently re-derives, from the recorded graph state alone, 1,733 truncations, 283 lapsed or retired registrations, 11 case violations, 9 ambiguities, 3 unresolvable values and 2 wrong-entity assertions.
- `pipeline/governance_report.py` recomputes four headline findings set-based from the source data and runs the shipped SPARQL queries against the graph. All four agree exactly: truncated 1,733/1,733, ambiguous 9/9, wrong entity 2/2, lapsed 283/283. The script exits non-zero on disagreement.

## Not yet done

- The concept layer is not gated by default because its shapes are `FILTER NOT EXISTS` constraints over 47,305 concepts and 87,702 usages, which takes minutes rather than seconds; pass `--full` to `pipeline/validate.py` to run it. It **was** run for this build: `build/bro-concept.ttl` parsed at 994,577 triples in 28.6 s and validated in 317.3 s, independently re-deriving 27,445 concepts with no definition, 7,171 usages naming no reporting form, and 1,278 concepts carrying scope only in prose. All three match the set-based counts exactly.
- No FIBO alignment is asserted. Whether FIBO models US bank register concepts such as RSSD or FDIC certificate numbers was not verified in this build, so this repository makes **no claim** about a FIBO gap.
- **Financial Data Transparency Act.** The currency check was completed after the first build and the README now cites it. Every FDTA statement was verified against the primary text of **91 FR 38246** (document 2026-12787, published 25 June 2026, effective 1 October 2026) retrieved from govinfo.gov, not from secondary commentary, because federalregister.gov blocks automated fetches. The quoted phrases, "the legal entity identifier is established to be ISO 17442" and "machine-readable taxonomy or ontology models", were read from that text directly. The scoping caveats in the README, that the joint rule binds the agencies rather than banks, that it changes no reporting obligation at its effective date, that no agency-specific implementing rule had been proposed as of August 2026, and that the preamble tolerates unreported and lapsed LEIs, are all from the same source. **No finding in this repository depends on the FDTA**; the rule is context for why the measurement is timely, not evidence for any number.
- **Associated Bank asset figure.** The FDIC reports $45,537,550k with `REPDTE` 31 March 2026. Associated Banc-Corp's Q2 2026 earnings release states the acquisition of American National Corporation "closed on April 1, 2026" and reports total assets of approximately $52 billion. Both were read from source. The README quotes the FDIC figure where it is describing the FDIC record, and says explicitly where the company's own figure differs and why.
- Entity resolution against SEC EDGAR CIK, OCC charter numbers and NMLS identifiers is modelled in the SKOS registry but not populated.
