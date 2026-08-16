# Outreach pack

Ready-to-send drafts. Nothing here has been sent. Order matters: report the findings to the data owners **before** publishing anything, so the public record shows you told them first. That single sequencing decision is the difference between a contribution and a blog post.

---

## ORDER OF OPERATIONS

1. Report to the FDIC and to GLEIF (items 1 and 2). Same day.
2. Comment on GLEIF issue #218 and open the two FIBO issues (items 3 and 4). Same day, they are public and timestamped.
3. Wait roughly a week for replies, then publish the article (item 8).
4. Only after publishing, do the individual outreach (items 5 to 7).

---

## 1. FDIC Chief Data Officer

**To:** `ChiefDataOfficer@FDIC.gov`
**Why this address:** the FDIC's own CDO page invites "questions on data quality, format, or usability" at exactly this address, which is precisely the category of this finding.
**Subject:** LEI field in the BankFind institutions API is truncated to 16 characters

> Dear FDIC Office of the Chief Data Officer,
>
> I am writing to report what appears to be a systematic data quality defect in the LEI field of the BankFind institutions API, in advance of publishing research that describes it.
>
> Across all 27,836 institution records returned by `api.fdic.gov/banks/institutions`, every non-empty LEI value is exactly 16 characters. The length histogram has a single bucket. ISO 17442 defines the LEI as 20 characters, of which the final two are check digits computed under ISO 7064 MOD 97-10.
>
> Three consequences follow. First, the check digits are absent from every published value, so no consumer can validate an LEI without an external lookup. Second, because two of the four discarded characters are entity-identifying, the truncation is not repairable by arithmetic: each value has 1,296 possible completions. Third, and most seriously, truncation to 16 characters is not always unique. Measured against the full GLEIF golden copy of 16 August 2026, 216,965 of 3,403,760 LEIs share a 16-character prefix with at least one other legal entity. Nine of the FDIC's published values are consequently ambiguous. For example `894500C8YTS0IB1B` is compatible with Waterfall Bank in the United States and with five unrelated companies in Bulgaria, France and India.
>
> Two smaller items in the same field: 12 values contain lowercase characters, which ISO 17442 does not permit and which break case-sensitive joins, though all 12 resolve once uppercased; and certificate 5296, Associated Bank, National Association, carries a value that resolves to the LEI of its parent, ASSOCIATED BANC-CORP, rather than to the bank's own LEI, `ZF85QS7OXKPBG52R7N18`.
>
> I raise this now because the Financial Data Transparency Act joint data standards final rule (91 FR 38246), effective 1 October 2026, establishes ISO 17442 as the legal entity identifier joint standard. I appreciate that the joint rule binds the agencies rather than reporting entities and changes no collection at its effective date, so nothing here is a compliance assertion. It is offered as a measurement taken before the agency-specific rulemakings are drafted.
>
> The full method, code and results are open and reproducible at https://github.com/fabio-rovai/bank-register-ontology. I would be glad to share anything that is useful, in whatever form suits your team, and I am happy to delay publication if that would help you respond.
>
> Kind regards,
> Fabio Rovai
> The Tesseract Academy
> fabio@thetesseractacademy.com

---

## 2. GLEIF, via GODIN

**To:** `godin@gleif.org`
**Why this address:** GODIN, the Global Open Data Integration Network founded by GLEIF and Open Ownership, exists to embed the LEI into open data sources. An LEI defect in a federal open-data product is squarely its remit. The Challenge LEI facility is the wrong instrument, because the LEI records themselves are fine; the defect is downstream republication.
**Subject:** Measured: 6.37% of the Global LEI System is not recoverable from a 16-character prefix

> Dear GODIN team,
>
> I have a coverage and integration result that I think belongs with you rather than in a blog post, and I would value your view before I publish it.
>
> Working on US bank registers, I found that the FDIC's public BankFind API publishes all 2,252 of its LEI values truncated to 16 of the 20 characters ISO 17442 requires, discarding both check digits. That is a defect for the FDIC to fix and I have reported it to them directly.
>
> The result that seems more useful to GLEIF is the general one. I took the golden copy of 16 August 2026, all 3,403,760 records, and truncated every LEI to 16 characters. That collapses them into 3,220,636 distinct prefixes, of which 33,841 are shared by more than one legal entity, putting **216,965 LEIs, 6.37 per cent of the global population, into a collision**. The worst single prefix covers 100 entities. The collisions are structural rather than coincidental: they cluster where an LOU issues sequentially, so consecutive registrations share long prefixes.
>
> The practical implication is that a 16-character LEI field is not merely lossy, it is genuinely ambiguous for roughly one identifier in sixteen, and any downstream system that stores or republishes a truncated LEI may be silently pointing at the wrong entity.
>
> This sits in a gap I do not think anyone is currently watching. GLEIF's data quality framework measures what LEI issuers submit, and does so to a very high standard. Nothing in the system measures the integrity of an LEI as republished by a consumer, which is where these 2,252 values live.
>
> Everything is open and reproducible at https://github.com/fabio-rovai/bank-register-ontology, including the census script, so you can re-run it against any day's golden copy. If it is useful I would be happy to write it up in whatever form GODIN prefers, or to contribute the check as a reusable notebook.
>
> Kind regards,
> Fabio Rovai
> The Tesseract Academy
> fabio@thetesseractacademy.com

---

## 3. Comment on GLEIF issue #218

**Where:** https://github.com/GLEIF-IT/lei-rdf/issues/218 ("Consider use of SHACL for constraints rather than OWL restrictions", filed by Pete Rivett, 25 January 2022, zero comments)
**Why this is the single highest-value action in this pack:** you have implemented, at scale and against real data, the thing this issue asks for. Commenting with a working artifact is a contribution, not a request.

> Four years on, here is a working data point in favour of this.
>
> I have built a SHACL layer over US bank register data (FDIC BankFind joined to the GLEIF golden copy, 1.12M triples) and the closed-world behaviour is exactly what was needed. The specific case: the FDIC publishes all 2,252 of its LEI values truncated to 16 of the 20 characters ISO 17442 requires, discarding both check digits. An OWL restriction cannot express "this value is shorter than its scheme declares"; a SHACL shape can, and it flagged all 2,252 from recorded state alone.
>
> Two things that might be useful here. First, I put the scheme rules in a SKOS registry as data (expected length, character set, case rule, check-digit algorithm) rather than hardcoding them in the shape, so the shape reasons about the declared rule rather than repeating it. Second, the distinction that mattered most in practice was between "fails the check digits" and "cannot be checked at all", which are different governance states with different remediations; a truncated LEI is the latter.
>
> This also speaks to #91. I now have a real corpus of invalid values: 2,252 truncated, 12 containing lowercase characters, 16 matching no LEI in the golden copy, and 9 that are genuinely ambiguous because a 16-character prefix is shared by more than one entity. Measured globally, 216,965 LEIs (6.37%) share a 16-character prefix with at least one other LEI. I am happy to contribute any of it as test fixtures if that would help.
>
> Everything is open at https://github.com/fabio-rovai/bank-register-ontology (shapes under `shapes/`, scheme registry under `skos/`). Glad to turn any of it into a PR here if there is appetite.

---

## 4. Two FIBO issues

**Where:** https://github.com/edmcouncil/fibo/issues
**Note:** the EDM Council became the **EDM Association** in October 2025 after acquiring OMG's assets. Do not use the old name. Contribution needs no membership and no CLA, only a DCO sign-off (`git commit -s`). FIBO ships quarterly; the current release is `master_2026Q2` of 14 July 2026.

### Issue A, trivial and near-certain to land. Open this one first, it earns standing for B.

**Title:** `LEIEntities: adaptedFrom cites withdrawn ISO 17442:2012`

> `fibo-be-le-lei:LegalEntityIdentifier` carries `cmns-av:adaptedFrom` pointing at https://www.iso.org/standard/59771.html, which is ISO 17442:2012. That edition has been superseded. The current standard is ISO 17442-1:2020 (https://www.iso.org/standard/78829.html), with ISO 17442-2:2020 (https://www.iso.org/standard/79917.html) and ISO 17442-3:2024 on verifiable LEIs (https://www.iso.org/standard/85628.html). Parts 1 and 2 were reviewed and confirmed in 2026.
>
> Happy to raise a DCO-signed PR updating the citation if that is welcome.

### Issue B, substantive.

**Title:** `LegalEntityIdentifier has no syntactic constraint, so FIBO cannot detect a malformed LEI`

> `fibo-be-le-lei:LegalEntityIdentifier` asserts conformance to ISO 17442 in its `skos:definition` but carries no `xsd:pattern`, no length restriction and no check-digit rule. Checked against master at commit 119fa8c: `BE/LegalEntities/LEIEntities.rdf` contains zero occurrences of `xsd:pattern`, and there are zero `sh:NodeShape` across all 295 ontology files.
>
> The consequence is that a FIBO graph cannot distinguish a valid LEI from a truncated or malformed one. This is not hypothetical. The FDIC's public BankFind API publishes all 2,252 of its LEI values at 16 characters rather than 20, discarding both ISO 7064 check digits, and 9 of those values are ambiguous because a 16-character prefix is shared by more than one legal entity in the Global LEI System. Loaded into FIBO as it stands, all 2,252 would pass silently.
>
> Two possible routes, and I have no strong view on which fits FIBO's conventions better:
>
> 1. An `owl:withRestrictions` / `xsd:pattern` facet on the identifier's value, catching length and character set but not the check digits.
> 2. A companion SHACL shapes graph, which can express the ISO 7064 MOD 97-10 arithmetic and is the only option that catches a transposition.
>
> I have implemented route 2 over 1.12M triples of US bank register data and would be glad to contribute the shapes, or a reduced version scoped to the LEI, if the working group is interested. Repository: https://github.com/fabio-rovai/bank-register-ontology. Working notes on what FIBO does and does not currently cover are in `ontology/bro-fibo-alignment.ttl`, which maps into FIBO with `closeMatch`/`relatedMatch` only.

---

## 5. Pete Rivett

**Who:** Practice Leader, Knowledge Graph at Intuitive.ai; co-chair EKGF; author of GLEIF issues #218 and #91.
**Why him first among individuals:** you have implemented his unactioned four-year-old proposal against real data. That is the strongest possible opener, and it is a contribution rather than a request.
**Channel:** LinkedIn (`/in/peterivett`) or GitHub (`rivettp`). Send only after item 3 is posted, so the issue comment is there to point at.

> Pete, I have just commented on GLEIF issue #218, the one you filed in January 2022 proposing SHACL over OWL restrictions for the LEI data. Four years and no replies seemed like a shame, so rather than add another opinion I built the thing and brought evidence.
>
> The case that convinced me is that the FDIC publishes all 2,252 LEIs in its public API truncated to 16 of 20 characters, dropping both check digits. An OWL restriction cannot say "shorter than its scheme declares". A SHACL shape can, and did. Globally, 6.37% of all LEIs share a 16-character prefix with another entity, so the truncation is not just lossy, it is ambiguous.
>
> It also produced the invalid-sample corpus your #91 asked for: 2,252 truncated, 12 lowercase, 16 unresolvable, 9 genuinely ambiguous. Happy to contribute any of it upstream.
>
> Repo is open if you want to pull it apart: https://github.com/fabio-rovai/bank-register-ontology. I would genuinely value your view on whether the scheme-rules-as-SKOS-data approach is the right factoring.

---

## 6. Zornitsa Manolova, GLEIF

**Who:** Head of Data Quality Management and Data Science, GLEIF, since 2018.
**Hook:** her "Scaling Interoperability with LEI Mappings" post of 7 August 2026.
**Channel:** LinkedIn. Send after item 2 has had a week to land, and reference it so the two do not read as separate approaches.

> Zornitsa, I sent a note to the GODIN address last week about a downstream LEI integrity result and wanted to flag it to you directly given it touches data quality measurement.
>
> Short version: the FDIC's public API republishes every LEI at 16 of 20 characters, and a census over the 16 August golden copy shows 216,965 LEIs (6.37%) share a 16-character prefix with at least one other entity, so truncated republication is genuinely ambiguous rather than merely lossy.
>
> The part I think is interesting for your programme is where the gap sits. GLEIF's quality framework measures what LEI issuers submit, to a standard your July report puts at 99.99. Nothing measures the integrity of an LEI once a consumer republishes it, which is exactly where these 2,252 values live. Given your work on LEI mappings and interoperability, I wondered whether a downstream-integrity check is something GLEIF would ever consider publishing as guidance.
>
> Method and code are open: https://github.com/fabio-rovai/bank-register-ontology.

---

## 7. Liju Fan

**Who:** lead author of OFR Staff Discussion Paper 18-01, *An Ontology of Ownership and Control Relations of Bank Holding Companies* (2018), with Mark D. Flood. Was OFR's Semantic Architecture Lead for 11 years; left federal service in January 2026 and now runs Ontology Workshop LLC.
**Why:** she built the direct predecessor to this work, inside the agency, and is now free to comment on it. Mark Flood is also reachable via his published University of Maryland address if you would rather approach both.
**Channel:** LinkedIn (`/in/lijufan`).

> Liju, I have just published an open ontology over US bank register data and your 2018 OFR paper with Mark Flood is its most direct predecessor, so I wanted to send it to you rather than have you find it.
>
> You modelled NIC ownership and control in OWL 2 and documented real defects in the regulator's own metadata. I have done something adjacent over the FDIC's BankFind register joined to the GLEIF golden copy, and found that every one of the 2,252 LEIs the FDIC publishes is truncated to 16 of 20 characters, that 6.37% of all LEIs globally are ambiguous under that truncation, and that two banks carry their parent holding company's LEI in their own record.
>
> I could not reach the NIC bulk data itself, which is now behind a CAPTCHA, so the Federal Reserve hierarchy comparison I most wanted to make is missing from this build. If you have a view on whether that data is obtainable any other way I would be grateful for it.
>
> https://github.com/fabio-rovai/bank-register-ontology. Everything is open and reproducible, and I would value your view on the modelling, particularly the decision to reify identifier assertions so that a wrong identifier is representable rather than excluded.

---

## 8. Publication

- Publish the article at `gov.tesseract.academy/research/bank-register-ontology` using the 4-edit recipe, push to origin **and** backup, then ping IndexNow.
- Add the entry to `Research.tsx` and increment the group count.
- Only after items 1 and 2 have been sent.

## 9. Amplification, last

Once the article is live, and in this order: reply to anyone who responded to items 1 to 7 first, then LinkedIn. **Juan Sequeda** (ServiceNow, *Catalog & Cocktails*) is the highest-amplification target and the finding is a gift-wrapped case study for his knowledge-graphs-as-trust thesis; **Tony Seale** has the largest relevant following and has publicly argued that "ontology" is becoming a 2026 buzzword driven by Palantir, for which the demand map is empirical support.

---

## Associated Bank: handle with care

Their Knowledge Engineer requisition (JR105709, posted 10 July 2026) is still open, and their new CDO **Alexander Bush** arrived in February 2026 from 18 years of regulatory reporting at Huntington. He has written publicly about defining terms upstream and about "centralized ontologies", so he is unusually likely to understand why item code 2170 carrying one definition across 64 forms is a defect.

The finding that his own bank's FDIC record carries its parent's LEI is genuine and checkable, and it is the sharpest example in the article.

Two rules for this one. Do not approach him while the article is unpublished, and never frame it as a job application, because it is neither. If you contact him at all, do it after publication, thematically, and lead with the MDRM finding rather than the one about his own bank. The Associated Bank case is the article's evidence, not a conversation opener.
