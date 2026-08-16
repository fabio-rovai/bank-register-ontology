# Bank Register Ontology (BRO)

An open OWL 2 ontology, SKOS registries, and SHACL governance layer for the **entity fabric and the regulatory-reporting concept fabric of US banking**, built and validated against the whole of three public sources on the same day:

- the **FDIC BankFind** register of insured depository institutions (4,250 active, 27,836 all-time),
- the **GLEIF golden copy**, all 3,403,760 LEI records plus 484,565 Level 2 relationship records,
- the **Federal Reserve's MDRM**, the published data dictionary of regulatory reporting items (87,702 rows, 47,305 item codes, 181 reporting forms),

joined into a **1,123,634-triple knowledge graph**, gated by SHACL, and reported on automatically.

This is not a toy schema. It is the US banking system's own registers, joined against the global identifier system that is supposed to bind them together, with the disagreements computed, graded, and queryable.

## Findings from the first full build (16 August 2026)

All figures from the 16 August 2026 FDIC fetch, the GLEIF golden copy published 08:00 that day, and the MDRM file rebuilt at 04:00 that day. All three are living systems, so a re-fetch moves the totals. Counts below are per institution unless stated.

### The identifier fabric

| # | Finding | Number |
|---|---|---|
| 1 | LEI values published in the FDIC register that are **truncated to 16 of the 20 characters ISO 17442 requires**. The length histogram is `{16: 2252}` with no exceptions. The four discarded characters include **both ISO 7064 check digits**, so the LEI's entire self-validation mechanism is thrown away and every value the FDIC publishes is, as published, not a valid LEI | **all 2,252 (100%)** |
| 2 | Because two of the discarded characters are entity-identifying, a truncated value has **1,296 arithmetically possible completions** before the check digits are pinned. Truncation is not repairable by arithmetic, only by lookup | 36<sup>2</sup> |
| 3 | Across all 3,403,760 LEIs in the Global LEI System, truncating to 16 characters puts **216,965 LEIs (6.37%) into a collision**: 33,841 prefixes are shared by more than one legal entity, and the worst single prefix covers **100** of them. Sixteen characters is not merely lossy in principle, it is demonstrably insufficient | **216,965 (6.37%)** |
| 4 | FDIC values that are consequently **ambiguous**, compatible with more than one real LEI. Every one was issued under LOU prefix `894500`, which allocates sequentially, so consecutive registrations share prefixes. `894500C8YTS0IB1B` is Waterfall Bank (US), a Bulgarian agricultural firm, a French property company, and three Indian companies | **9** |
| 5 | Institutions whose published identifier resolves to a **different legal entity than the institution itself**, confirmed against GLEIF's own consolidation records. **Associated Bank, National Association** ($45.5bn, cert 5296) carries `549300N3CIN473IW`, which completes to `549300N3CIN473IW5094`, which is **ASSOCIATED BANC-CORP, its parent holding company**. The bank's own LEI, `ZF85QS7OXKPBG52R7N18`, appears nowhere in the FDIC register | **2 confirmed, 15 more parent-shaped** |
| 6 | Values containing **lowercase characters**, which ISO 17442 forbids. Ten are entirely lowercase, two are mixed case (`5493003OSi5cd032`, Denali State Bank). All resolve once uppercased, so these are pure formatting defects that nonetheless break any case-sensitive join | **12 across the register, 11 on active banks** |
| 7 | Values for which **no LEI in the Global LEI System is compatible at all**, after case normalisation. The institution carries an identifier that refers to nothing. Three are at currently active banks, including Independence Bank of Kentucky ($3.79bn) | **16 across the register, 3 on active banks** |
| 8 | Active insured institutions whose LEI registration is **LAPSED, RETIRED or DUPLICATE** in GLEIF: taking insured deposits, not maintaining the global identifier. They include **Santander Bank, N.A. ($106.1bn)**, SoFi Bank ($49.7bn), Texas Capital Bank ($33.2bn) and Sallie Mae Bank ($29.5bn). Context matters here: GLEIF's July 2026 data quality report puts **35.0% of all LEIs worldwide in a lapsed state**, so 16.5% among FDIC-insured banks is materially *better* than the global population, not worse | **283** |
| 9 | LEI coverage is **40.8% of active institutions but 92.20% of assets** ($24.13tn of $26.18tn). Coverage tracks size almost perfectly: 8.8% below $100m, 35.9% to $1bn, 66.3% to $10bn, 89.4% to $100bn, 93.8% above. The register omits an LEI for **Ally Bank ($185.7bn), Regions Bank ($159.4bn) and City National Bank ($99.9bn)** | **1,733 of 4,250** |
| 10 | One US community bank, **CBI Bank & Trust** (Iowa, $1.66bn), resolves to a **German** entity, Herausgebergemeinschaft Wertpapier-Mitteilungen. The country code alone proves the identifier wrong, with no name judgement required | **1** |

The FDIC's own hierarchy fields are, separately, unusable: `PARCERT` is populated on **4 of 4,250** active institutions, and `ULTCERT` equals the institution's own certificate for all **4,245** that carry it. The holding-company link that does work is `RSSDHCR`, present on **3,560 (83.8%)** across **3,340** distinct holding companies.

The same record also illustrates how far a register can lag the thing it describes. The FDIC reports Associated Bank at $45,537,550k with a reporting date of **31 March 2026**. Associated Banc-Corp's acquisition of American National Corporation **closed on 1 April 2026**, the very next day, and the company now reports total assets of approximately **$52 billion**. So a single record carries an identifier belonging to the parent company and a balance sheet that predates the group's most recent acquisition by one day. Neither is a scandal. Both are the ordinary condition of register data, and both are why anything built on it needs to model provenance and time rather than assume them.

### The reporting concept fabric

| # | Finding | Number |
|---|---|---|
| 11 | The MDRM's **Item Name and Description are pure functions of the four-digit item code**, identical byte for byte across every form and every date range that uses them. Item code **2170, TOTAL ASSETS, carries one definition across 117 mnemonics and 64 reporting forms**. The dictionary therefore cannot express that total assets on FR Y-9C (consolidated holding company) has different scope from FFIEC 041 (bank only) or FR Y-14A (projected) | **0 divergent definitions, 0 divergent names** |
| 12 | Item codes carrying **no definition anywhere in the dictionary**. More than half the regulatory glossary is a label with nothing behind it. Keyed on the four-digit item code alone; keyed instead on the eight-character MDRM identifier (mnemonic plus code) the figure is 33,281 of 75,264, or 44.2%. Both are stated because the denominator changes the headline and a reader is entitled to know which one is in use | **27,445 of 47,305 (58.0%)** |
| 13 | Where meaning cannot vary, the facets do. Item codes marked **confidential on one form and public on another** | **1,816** |
| 14 | The same, **within a single MDRM identifier across its own date ranges**: an item whose disclosure status changes over time. Disclosure is form-scoped and period-scoped, and is never derivable from the item code alone | **1,342** |
| 15 | Item codes whose **item type** conflicts across forms (2170 is both Derived and Financial depending on the collection); and within one identifier across periods | **1,746 / 637** |
| 16 | Rows naming **no reporting form at all**, so nothing says which collection imposes them. Dominated by the Uniform Bank Performance Report series (UBPR 3,239, UBPK, UBPS) | **7,171** |
| 17 | Item type **`E`, Examination/supervision, is documented in the Federal Reserve's own README and used on zero rows**. Used values are F 75,537, D 9,128, S 1,098, P 980, R 924, J 35 | **0** |
| 18 | Exactly one row carries a **lowercase `n`** where the confidentiality flag is otherwise `Y`/`N` (SVGL K072, OTS 1313, 2011) | **1** |

Where the dictionary does record form-specific scope, it does so in **free text inside the single definition**, typically under a `COMPARABILITY:` heading, rather than as structure. 1,278 concepts carry scope that way. That is precisely the content this ontology exists to make queryable.

No prior report of either the FDIC truncation or the prefix-collision census was found in a targeted search of GLEIF's own publications, the LEI Regulatory Oversight Committee, FSB progress reports, OFR working papers, arXiv and GitHub. That is a scoped negative, not a claim of priority: SSRN, Google Scholar and the ROC's unpublished work on LEI coverage of US banking organisations were not searched.

Full numbers, method and caveats: [BUILD_REPORT.md](BUILD_REPORT.md) and [reports/GOVERNANCE_REPORT.md](reports/GOVERNANCE_REPORT.md).

## Why this matters now

On **25 June 2026** nine federal financial regulators published the **Financial Data Transparency Act Joint Data Standards** final rule (**91 FR 38246**, document 2026-12787), effective **1 October 2026**. It establishes, in codified text, that

> the legal entity identifier is established to be ISO 17442, Financial Services, the Legal Entity Identifier (LEI).

and it requires that a data transmission or schema and taxonomy format must, to the extent practicable,

> enable high quality data through schemas, with accompanying metadata documented in **machine-readable taxonomy or ontology models**, which clearly define the semantic meaning of the data.

Two things follow, and the second is the one that is usually got wrong.

First, this is a real and dated federal commitment to the LEI and to machine-readable semantics. The agencies deliberately established **no format and no taxonomy**, expressly declining to adopt even the FFIEC Call Report Taxonomy, so what "ontology models" means in practice is still open. The FIGI was dropped between proposal and final rule, leaving **no common financial instrument identifier at all**.

Second, and this repository is careful about it: **the joint rule binds the agencies, not banks, and changes no reporting obligation today.** Its own DATES section says the rule "will not change any reporting requirements without further action by the agencies." The agency-specific rules that will have teeth are due around mid-2028 and, as of August 2026, **not one has been proposed**. The preamble also expressly preserves the practices that degrade identifier quality: a reporting entity "need only report an LEI if the entity has one", lapsed LEIs may still be reported, and agencies may adopt standards other than these.

So nothing measured here is evidence of anybody's non-compliance. It is a **baseline for the transition**, taken before the implementing rules are written, and the tolerances quoted above are precisely the mechanism by which today's defects will survive into the post-2028 regime unless someone measures and names them.

There is one sharp irony worth stating plainly. The same federal government already depends on a **valid, complete** LEI elsewhere: under **12 CFR 1003.4(a)(1)(i)**, every HMDA Universal Loan Identifier *begins with the institution's LEI* and ends with a check digit computed under ISO/IEC 7064 MOD 97-10. HMDA cannot function on a truncated LEI. BankFind publishes nothing but truncated LEIs. Separately, in both the FFIEC Central Data Repository (keyed on RSSD) and BankFind (keyed on FDIC certificate), **the LEI is an attribute and the join key in neither**, which is exactly why it has been allowed to rot.

## Why this exists

The US has no operational, government-published semantic layer for bank regulatory data, and the gap is verifiable rather than rhetorical:

- **FIBO** (EDM Council, MIT-licensed) already owns more of this territory than is usually acknowledged, and this repository does not pretend otherwise. Verified against commit `119fa8c` of 17 July 2026: FIBO declares the RSSD identifier (`usjrga:ResearchStatisticsSupervisionDiscountIdentifier`), the FDIC certificate number (`usjrga:FDICCertificateNumber`), the bank holding company (`fse:BankHoldingCompany`), the LEI (`be-le-lei:LegalEntityIdentifier`), registry lifecycle states including `breg:LapsedStatus`, and the complete 43-code FFIEC National Information Center entity-type vocabulary in its `usnic:` development module. What FIBO does **not** have, measured in the same commit, is the part that matters here: **zero `sh:NodeShape` across all 295 files, zero `xsd:pattern` on the LEI class, and zero `skos:ConceptScheme`.** FIBO asserts ISO 17442 conformance in prose while carrying no length, character-set or check-digit constraint, so a FIBO graph cannot detect that a 16-character string is not an LEI. It also has no vocabulary for an identifier being wrong, for two systems disagreeing, or for a value resolving ambiguously. See [`ontology/bro-fibo-alignment.ttl`](ontology/bro-fibo-alignment.ttl), which maps into FIBO with `closeMatch` and `relatedMatch` and asserts no equivalences.
- The **Office of Financial Research** built prototype OWL ontologies over National Information Center data and published them as *An Ontology of Ownership and Control Relations of Bank Holding Companies* (Liju Fan and Mark D. Flood, Staff Discussion Paper 18-01, 27 June 2018). It was research; no ontology artifact was ever released alongside it.
- **Earlier work exists and is cited rather than ignored.** Jayzed Data Models (Jürgen Ziemer) has published the FFIEC 031 Call Report transliterated from XBRL into OWL, in FIBO namespaces and with FDIC-certificate-keyed instance data, at bankontology.com and finregont.com since 2017 under MIT and GPL. It is substantial, roughly 1.4 million statements, and it is real prior art. What it does not do, and what this repository does, is validate anything: it contains no SHACL, no SKOS registries, no GLEIF join and no computed cross-source disagreement, and its own documentation notes that "all joins are simple text label comparisons as in the original source". Its content is frozen at 2017 and its `owl:imports` IRIs do not dereference.
- **MDRM** is a flat CSV code list. It is the closest thing the US has to a regulatory business glossary, and findings 11 to 18 above are what it actually contains. It is not decorative: MDRM mnemonics are the element-naming backbone of the FFIEC Call Report XBRL taxonomy, so the flatness described above is inherited directly by every Call Report filed through the Central Data Repository.
- The European comparison is often overstated and worth stating accurately. **BIRD is SQL plus VTL, not RDF**, and the EBA's **DPM 2.0** is a relational database feeding XBRL taxonomies; the EBA's "semantic glossary" means conceptual harmonisation inside that relational model, not a published ontology. Neither side of the Atlantic operates an RDF reporting-semantics standard. Europe's is relational and unified, the US's is relational and fragmented. The unification layer that would have changed that, the ECB's **IReF**, slipped hard: per the ECB's press release of 8 June 2026, consultation is in H2 2027, the pilot begins **Q2 2030**, and first official reporting is **Q2 2031**.

So the definitive open artifact starts where the data actually is. BRO's design commitments, two of which are forced by the defects above and appear in neither sibling ontology:

1. **Identifiers are reified assertions**, carrying scheme, source system, and computed conformance. Cross-system disagreement is a query, not an audit project.
2. **A value may fail its own scheme, and resolution is data.** An assertion records what it resolves to and **how many candidates it resolved to**. A model in which an identifier *is* its referent cannot represent a truncated LEI at all.
3. **The insured institution and the legal entity are different things.** That distinction is what makes "this bank's record carries its parent's LEI" a statable fact rather than merely a wrong one.
4. **Scope lives on usage, not on the code.** The concept is the item code; confidentiality, item type and validity hang off a reified `ItemUsage`, because that is where the source data shows them actually varying.
5. **Arithmetic in code, policy in shapes.** ISO 7064 and the truncation analysis run in the pipeline and assert their results; SHACL requires the recorded state. pyshacl independently re-finds all 1,733 truncations, 283 lapsed registrations, 9 ambiguities, 3 unresolvable values and 2 wrong-entity assertions from the graph alone.

## Related work

| Work | What it is | What it does not do |
|---|---|---|
| **FIBO** (EDM Council, MIT) | Production OWL covering the RSSD identifier, FDIC certificate number, bank holding company, LEI and registry lifecycle states, plus the 43-code FFIEC NIC entity-type vocabulary in its development branch | No SHACL, no `xsd:pattern` on the LEI, no SKOS registries, no instance data over BankFind, and no way to state that an identifier assertion is wrong |
| **OFR SDP 18-01** (Fan and Flood, 2018) | OWL 2 prototype over NIC ownership and control data; documented real NIC metadata defects, the same rhetorical move made here | Paper only. No artifact was released; the `financialresearch` GitHub organisation holds zero public repositories |
| **Jayzed / FinRegOnt** (Ziemer, 2016 to 2017) | FFIEC 031 Call Report transliterated from XBRL into OWL in FIBO namespaces, with real filings keyed on FDIC certificate number, roughly 1.4M statements, MIT and GPL | No SHACL, no SKOS, no GLEIF join, no cross-source disagreement. Frozen at 2017, `owl:imports` IRIs do not dereference, no repository, no endpoint |
| **GLEIF-IT/lei-rdf** (GLEIF, MIT) | GLEIF's own official RDF rendering of the LEI model, refreshed weekly | Publishes the LEI data; does not touch US bank registers. Its open issue #218, proposing SHACL for constraints, has stood unanswered since January 2022 |
| **andenick/bank-data-dictionary** | Active CSV crosswalks over MDRM, NIC and identifiers, updated through 2026 | No semantic-web content at all: no Turtle, OWL or RDF |

The specific contribution here is therefore narrow and stated precisely: the first SHACL validation in this domain, the first SKOS registries carrying scheme rules as data, the first RDF rendering of MDRM and of FDIC BankFind, and the first computed cross-register disagreement between a US banking register and the Global LEI System.

## Repository layout

```
ontology/bro-fibo-alignment.ttl    Verified mapping into FIBO (closeMatch/relatedMatch
                                   only), plus the measured list of what FIBO lacks
ontology/bro-core.ttl              Core OWL: institutions, legal entities, control
                                   assertions, the reified identifier fabric with
                                   conformance and resolution, the concept fabric
skos/identifier-schemes.ttl        SKOS: 8 identifier schemes declaring their own
                                   length, character set, case and check-digit rules
                                   as DATA; non-conformance reasons; resolution
                                   methods; control types; MDRM item types
shapes/bro-shapes.ttl              SHACL layers 1-2: structure, then one shape per
                                   defect class found in the sources
pipeline/checksums.py              ISO 7064 MOD 97-10 and ABA routing arithmetic,
                                   with embedded test vectors
pipeline/fetch_fdic.py             FDIC BankFind institutions register (keyless API)
pipeline/resolve_identifiers.py    Streams the GLEIF golden copy: global collision
                                   measurement, prefix resolution, parent detection
pipeline/build_graph.py            Turtle emitter, 1.12M triples in under 2 seconds
pipeline/validate.py               Parses every artifact, runs the SHACL gate
pipeline/governance_report.py      Set-based recomputation, cross-checked against
                                   the shipped SPARQL queries
queries/                           6 verified SPARQL queries
reports/GOVERNANCE_REPORT.md       The generated findings report
```

## Reproduce

```bash
pip install rdflib pyshacl
python pipeline/fetch_fdic.py            # ~28k institutions, keyless
# MDRM:  https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip  -> data/
# GLEIF: goldencopy.gleif.org/api/v2/golden-copies/publishes    -> data/
python pipeline/resolve_identifiers.py   # streams 3.4M LEIs, ~38 s
python pipeline/build_graph.py           # 1,123,634 triples, ~2 s
python pipeline/validate.py              # SHACL gate, ~30 s
python pipeline/governance_report.py     # report + SPARQL cross-check, ~70 s
```

The golden copy is a 4.9 GB CSV and the MDRM file is 91 MB, so neither is committed. `data/resolution.json` is the small, committed, regenerable join result.

## Licence

Code MIT; ontology, SKOS registries, shapes and reports CC BY 4.0. Source data: FDIC BankFind (US Government public data), GLEIF golden copy (CC0 1.0), Federal Reserve MDRM (US Government public data).

## Working with this

If your organisation runs on bank entity data, regulatory reporting lineage, counterparty resolution, holding-company hierarchies, or a business glossary that has to reconcile to what the regulator actually publishes, this repository is the open baseline of exactly that discipline. For the applied version on your own data: **fabio@thetesseractacademy.com**.
