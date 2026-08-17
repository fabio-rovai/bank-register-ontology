# An open ontology for US bank registers, tested against the FDIC, the Federal Reserve, and the Global LEI System

*Draft for gov.tesseract.academy/research/bank-register-ontology. NOT PUBLISHED. Every figure is from a build of 16 August 2026 and is reproducible from https://github.com/fabio-rovai/bank-register-ontology.*

On 1 October 2026 a rule takes effect that makes this a live problem rather than a curiosity.

The Financial Data Transparency Act Joint Data Standards final rule (91 FR 38246, published 25 June 2026) commits nine federal financial regulators, the FDIC and the Federal Reserve among them, to a single answer for how a legal entity is identified. In its codified text:

> the legal entity identifier is established to be ISO 17442, Financial Services, the Legal Entity Identifier (LEI).

The LEI is twenty characters. Four identify the issuing operating unit, two are reserved, twelve identify the entity, and the last two are check digits computed under ISO 7064 MOD 97-10. Those last two are the reason the LEI exists in the form it does. They let any system, anywhere, decide whether a value it has just been handed could possibly be real, without asking anyone.

I pulled all 27,836 institution records from the FDIC's BankFind register and measured the length of every LEI in it. The histogram has exactly one bucket:

```
{16: 2252}
```

Every LEI the FDIC publishes is sixteen characters. Not most of them, not the old ones, not a bad batch from one year. All 2,252, without a single exception, truncated by four characters from the twenty the standard requires.

You can check it in one request. JPMorgan Chase Bank, National Association appears in BankFind as `7H6GLXDRUGQFU57R`. Its actual LEI is `7H6GLXDRUGQFU57RNE97`. Citibank is `E57ODZWZ7FF32TWE` against a real `E57ODZWZ7FF32TWEFA76`. Wells Fargo, Goldman Sachs Bank USA and U.S. Bank all show the same clean sixteen-character prefix. This is a field-width defect, almost certainly a column defined as sixteen characters somewhere upstream a long time ago, quietly amputating the same four characters ever since.

## Being precise about what this is and is not

The FDTA rule binds the agencies, not banks, and it changes no reporting obligation. Its own DATES section says so: the joint rule "will not change any reporting requirements without further action by the agencies." The agency-specific rules that will have teeth are due around mid-2028 and, as of today, **not one has been proposed**.

So nobody is in breach of anything. What follows is a baseline measurement taken before the implementing rules are written. That framing matters, because the rule's preamble expressly preserves the practices that let identifier quality rot: a reporting entity "need only report an LEI if the entity has one", lapsed LEIs may still be reported, and agencies may adopt other standards entirely. Those tolerances are the mechanism by which today's defects survive into the post-2028 regime unless somebody measures them first.

There is also a sharp irony sitting in existing law. Under 12 CFR 1003.4(a)(1)(i), every HMDA Universal Loan Identifier *begins with the reporting institution's LEI* and ends with a check digit computed under ISO 7064 MOD 97-10. HMDA cannot function on a truncated LEI. The same federal government requires twenty characters in one collection and publishes sixteen in another.

## Why the missing four characters are the four that matter

Two of the discarded characters are check digits, and two are part of the entity portion.

Losing the check digits means the value can no longer be validated in isolation. The cheapest control in the entire identifier system, one modulo operation, no network call, no licence, no lookup table, has been removed from every record.

Losing two entity characters means the damage cannot be undone by arithmetic. Given sixteen characters there are thirty-six possibilities for character seventeen and thirty-six for character eighteen, so 1,296 candidates, and only then do the check digits become determined. You cannot repair a truncated LEI by recomputing anything. You can only look it up.

So I looked all of them up, against the entire Global LEI System.

## Sixteen characters is not enough, and this is measurable

I took the GLEIF golden copy published at 08:00 on 16 August 2026, all 3,403,760 LEI records, and truncated every one to sixteen characters to see how often the result still identifies something unique.

It collapses 3,403,760 identifiers into 3,220,636 distinct prefixes. **33,841 of those prefixes are shared by more than one legal entity, putting 216,965 LEIs, 6.37 per cent of the entire global population, into a collision.** The worst single prefix is shared by one hundred distinct entities.

That is a census, not a projection. Six per cent of the world's legal entity identifiers are not uniquely recoverable from sixteen characters.

Nine of the FDIC's own values fall into exactly that hole. Every one was issued under the LOU prefix `894500`, which allocates sequentially, so consecutive registrations differ only in their final characters. The result is that `894500C8YTS0IB1B`, as published in a United States federal banking register, denotes any of the following:

- Waterfall Bank, in the United States
- АГРАРХАФЕН РУСЕ, in Bulgaria
- SOCIETE DU PASSAGE AGARD, in France
- GRISHVA INFRAPROJECT LLP, in India
- UMANG CURE PRIVATE LIMITED, in India
- BSL PLACEMENT PRIVATE LIMITED, in India

Madison County Bank shares its published identifier with a Canadian bond fund and a Guernsey limited partnership. Cherokee State Bank shares its own with a Danish holding company and a Luxembourg estate agency. The community banks that used the cheapest registrar are precisely the ones whose federally published identifier now points at half a dozen unrelated companies.

A further sixteen values match no LEI in the global system at all. Twelve more contain lowercase characters, which ISO 17442 does not permit, so any case-sensitive join fails silently on them. Those twelve all resolve once uppercased, which makes them the cheapest fix in this article.

## The one that made me stop

Once each value resolves to a real LEI you can ask a better question than "is this well formed". You can ask whether it identifies the right company.

Mostly it does. On 2,173 institutions the resolved name matches the bank. On two, GLEIF's own consolidation records prove it does not, and one of those two is worth the whole exercise.

FDIC certificate 5296 is **Associated Bank, National Association**, of Green Bay, Wisconsin. Its record carries the LEI value `549300N3CIN473IW`, which completes to exactly one real identifier, `549300N3CIN473IW5094`.

That identifier belongs to **ASSOCIATED BANC-CORP**, of Madison. The holding company. The parent.

The bank's own LEI is `ZF85QS7OXKPBG52R7N18`, registered in Green Bay, status ACTIVE. It appears nowhere in the FDIC's register. GLEIF's Level 2 relationship file confirms the parent-child link independently, which is how this was detected rather than guessed.

Fifteen further institutions resolve to names ending in BANCORP, BANCSHARES or HOLDING, including SoFi Bank resolving to GOLDEN PACIFIC BANCORP. GLEIF publishes no active consolidation edge for those fifteen, so I do not count them as confirmed. They are the same shape.

This is not a clerical curiosity. A bank and its holding company file different reports on different consolidation bases. FR Y-9C is the holding company consolidated. FFIEC 041 is the bank alone. If the identifier meant to distinguish them points at the same entity, then consolidated and unconsolidated positions are attributed to one legal person by any system that trusts the register.

And the Federal Reserve gets it right, which is what turns this from a fact of life into a defect. The FFIEC National Information Center's own bulk file records RSSD 917742, Associated Bank, National Association, FDIC certificate 5296, carrying `ZF85QS7OXKPBG52R7N18`, the bank's own LEI. It separately records RSSD 1199563, Associated Banc-Corp, carrying `549300N3CIN473IW5094`, the parent's. Two identifiers, correctly assigned, in the other federal register describing the same bank. Across all 61,308 NIC entity records, every populated LEI is a correct twenty characters. The truncation belongs to the FDIC's publication alone.

The same record shows a second kind of drift. The FDIC reports Associated Bank at $45.5bn with a reporting date of 31 March 2026. Associated Banc-Corp's acquisition of American National Corporation closed on 1 April 2026, the next day, and the company now reports roughly $52 billion. One record, carrying the parent's identifier and a balance sheet one acquisition out of date.

One further case needs no name judgement at all. CBI Bank & Trust, an Iowa institution, resolves to Herausgebergemeinschaft Wertpapier-Mitteilungen, a German company. The country code settles it.

I should be fair about one number. 283 active insured institutions hold a lapsed, retired or duplicate LEI, including Santander Bank, N.A. That sounds worse than it is: GLEIF's July 2026 report puts **35.0 per cent of all LEIs worldwide in a lapsed state**, so 16.5 per cent among FDIC-insured banks is materially better than the global population.

## Where the responsibility actually sits, and where it doesn't

It would be easy and wrong to make this a story about GLEIF failing. GLEIF's July 2026 data quality report gives an average Total Data Quality Score of 99.99 across 3,390,204 records, and its conformance check on ISO 17442 structure is scoped to what LEI issuers submit.

That is the whole point. **GLEIF polices what issuers put in. Nothing in the Global LEI System constrains what a regulator publishes back out.** No check anywhere measures the length of an LEI as republished downstream. That gap is not anyone's fault in particular, and it is exactly where 2,252 truncated identifiers have been sitting.

Which makes one open GitHub issue worth reading. On 25 January 2022, Pete Rivett filed issue #218 against GLEIF's own RDF repository, proposing SHACL for constraints rather than OWL restrictions, on the grounds that closed-world constraint execution suits the GLEIF dataset. It has zero comments, four and a half years later. Issue #91, asking for invalid sample data for validation testing, has been open since January 2019.

Had either been actioned, a shape enforcing twenty characters and the check digits would have caught this on any ingest.

## The same failure, one layer up

While I had the registers open I pulled the Federal Reserve's MDRM, the published dictionary of regulatory reporting items: 87,702 rows, 47,305 item codes, 181 reporting forms. It is the closest thing American banking has to an official business glossary, and its mnemonics are the element-naming backbone of the FFIEC Call Report XBRL taxonomy, so whatever is true of it is inherited by every Call Report filed.

I expected the classic glossary pathology, one code carrying different definitions on different forms. I was wrong, and the truth is more interesting.

**The Item Name and the Description are pure functions of the four-digit item code.** Byte for byte identical, on every form, in every period. Zero divergence across all 47,305 codes. Item code 2170, TOTAL ASSETS, carries one definition across 117 mnemonics and 64 reporting forms.

The dictionary achieves perfect consistency by being unable to represent the difference. Total assets on FR Y-9C is a consolidated holding company figure. On FFIEC 041 it is the bank alone. On FR Y-14A it is a projection under stress. The MDRM says the same sentence for all three, and where it does acknowledge that forms differ it does so in free text inside the definition, under a heading marked `COMPARABILITY:`. 1,278 concepts carry their scope that way, as prose.

Meanwhile 27,445 of the 47,305 item codes carry no definition anywhere at all. They are labels. (Keyed instead on the full eight-character MDRM identifier the figure is 33,281 of 75,264; both are worth stating, because the denominator moves the headline.)

And where meaning cannot vary, the facets do. **1,816 item codes are confidential on one form and public on another.** More pointedly, 1,342 MDRM identifiers change their confidentiality across their own date ranges. Disclosure status is scoped by form and by period, and is not derivable from the item code, which is exactly what a metadata layer keyed on the item code would assume.

## One problem, twice

Put the two halves together and they are the same sentence.

In the entity fabric, scope was thrown away when the identifier was truncated, then attached to the wrong level of the corporate hierarchy. In the concept fabric, scope was never encoded, because the dictionary attaches meaning to a code spanning sixty-four forms with different consolidation bases.

**Scope is never in the identifier.** Both public registers embody it.

So the ontology I built is shaped by that rather than around it. Identifiers are reified assertions, not designators, which is the only way to state that a published value is truncated, ambiguous, or belongs to somebody else. Resolution is data: an assertion records what it resolved to and how many candidates it resolved to. The insured institution and the legal entity are separate classes, which is what makes the Associated Bank case statable rather than merely wrong. On the reporting side, confidentiality and item type hang off a reified usage of a concept on a form in a period, because that is where the source data shows them varying.

The result is 1,123,634 triples gated by SHACL. The shapes are the interesting part: each encodes a defect class found in the sources, so the shape file doubles as the specification of what went wrong. Running pyshacl over the graph rediscovers, from the recorded state alone, all 1,733 truncations, 283 lapsed registrations, 9 ambiguities, 3 unresolvable values and 2 wrong-entity assertions. The governance report computes every headline twice, once set-based from source and once through the shipped SPARQL, and refuses to write itself if the two disagree.

## What I am not claiming

I am not the first person to put US bank regulatory data into OWL. Jürgen Ziemer's FinRegOnt has published the FFIEC 031 Call Report transliterated into OWL, in FIBO namespaces with real filings keyed on FDIC certificate number, since 2017. The Office of Financial Research modelled NIC ownership and control in OWL 2 in 2018 (Fan and Flood, Staff Discussion Paper 18-01), though no artifact was ever released.

Nor does FIBO ignore this territory. It declares the RSSD identifier, the FDIC certificate number, the bank holding company, the LEI, registry lifecycle states, and the complete 43-code NIC entity-type vocabulary. Anyone claiming otherwise has not looked.

What none of them do is validate anything. Measured against FIBO's current master: zero SHACL shapes across 295 files, zero `xsd:pattern` on the LEI class, zero SKOS concept schemes. FIBO asserts ISO 17442 conformance in prose and carries no length or check-digit constraint, so a FIBO graph cannot detect that a sixteen-character string is not an LEI. Neither can FinRegOnt, whose own documentation notes that "all joins are simple text label comparisons as in the original source".

That is the narrow, defensible contribution: the first SHACL validation in this domain, the first SKOS registries carrying scheme rules as data, the first RDF rendering of MDRM and of BankFind, and the first computed disagreement between a US banking register and the Global LEI System.

On novelty of the findings themselves I will say only what I can defend: no prior report of either the truncation or the collision census was found in a targeted search of GLEIF's publications, the LEI Regulatory Oversight Committee, FSB progress reports, OFR working papers, arXiv and GitHub. SSRN and Google Scholar were not searched.

Two gaps are worth naming. The FFIEC's National Information Center bulk download, which holds the Federal Reserve's own view of who owns whom, sits behind a CAPTCHA and could not be fetched, so the comparison I most wanted to make is not in this build. The HMDA panel file, a genuine published crosswalk between LEIs and RSSDs, sits on a host that is edge-blocked. Both are recorded in the build report rather than papered over.

## None of this is evidence of incompetence

A sixteen-character column is an ordinary engineering decision that became wrong when an external standard specified twenty, and it survived because nothing downstream ever failed loudly. That is how identifier defects always survive. They produce values that still look like identifiers.

The fixes are correspondingly ordinary. Widen the field to twenty characters. Uppercase on ingest, which repairs twelve records immediately. Validate the check digits at the point of entry, one modulo operation. Record the identifier of the insured institution rather than of whichever entity in the group was to hand.

I am sending these findings to the FDIC's Chief Data Officer and to GLEIF, because a coverage result about the Global LEI System belongs with the people who run it, and a defect in a federal register belongs with its publisher. The repository, pipeline, shapes and queries are open, so anyone can re-run the census on tomorrow's golden copy and get tomorrow's numbers.

---

**The artifact:** https://github.com/fabio-rovai/bank-register-ontology, code MIT, ontology and shapes CC BY 4.0.

If your organisation runs on bank entity data, regulatory reporting lineage, counterparty resolution, holding-company hierarchies, or a business glossary that has to reconcile to what the regulator actually publishes, this repository is the open baseline of that discipline. For the applied version on your own data: **fabio@thetesseractacademy.com**.
