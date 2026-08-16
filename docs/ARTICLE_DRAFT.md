# The FDIC publishes 2,252 Legal Entity Identifiers. Not one of them is a valid LEI.

*Draft for gov.tesseract.academy/research/bank-register-ontology. Not published. All figures from a build of 16 August 2026 and reproducible from https://github.com/fabio-rovai/bank-register-ontology.*

The Legal Entity Identifier is twenty characters long. Four identify the issuing operating unit, two are reserved, twelve identify the entity, and the last two are check digits computed under ISO 7064 MOD 97-10. Those last two characters are the reason the LEI exists in the form it does. They let any system, anywhere, decide whether a value it has just been handed could possibly be a real identifier, without asking anyone.

The FDIC's BankFind register carries an LEI field. I pulled all 27,836 institution records it holds, active and closed, and measured the length of every LEI value in it. The histogram has exactly one bucket:

```
{16: 2252}
```

Every LEI the FDIC publishes is sixteen characters. Not most of them, not the old ones, not a bad batch from one year. All of them, without a single exception, truncated by four characters from the twenty that ISO 17442 requires.

You can check this in one request. JPMorgan Chase Bank, National Association appears in BankFind as `7H6GLXDRUGQFU57R`. Its actual LEI is `7H6GLXDRUGQFU57RNE97`. Citibank is `E57ODZWZ7FF32TWE` against a real `E57ODZWZ7FF32TWEFA76`. Wells Fargo, Goldman Sachs Bank USA and U.S. Bank all show the same clean sixteen-character prefix. This is a field-width defect, almost certainly a column defined as `CHAR(16)` somewhere upstream a long time ago, and it has been quietly amputating the same four characters ever since.

## Why the missing four characters are the four that matter

The four discarded characters are positions seventeen through twenty. Two of them are part of the entity portion, and two of them are the check digits.

Losing the check digits means the value can no longer be validated in isolation. Nothing downstream can compute whether `7H6GLXDRUGQFU57R` is plausible, because there is no longer anything to compute. The cheapest control in the entire identifier system, the one that costs a single modulo operation and needs no network call, no licence and no lookup table, has been removed from every record.

Losing two entity characters means the damage cannot be undone by arithmetic. Given sixteen characters, there are thirty-six possibilities for character seventeen and thirty-six for character eighteen, so 1,296 candidate values, and only then do the check digits become determined. You cannot repair a truncated LEI by recomputing anything. You can only look it up.

So I looked all of them up, against the entire Global LEI System.

## Sixteen characters is not enough, and this is measurable

I took the GLEIF golden copy published at 08:00 on 16 August 2026, all 3,403,760 LEI records, and truncated every one of them to sixteen characters to see how often the result still identifies something unique.

It collapses 3,403,760 identifiers into 3,220,636 distinct prefixes. **33,841 of those prefixes are shared by more than one legal entity, putting 216,965 LEIs, 6.37 percent of the entire global population, into a collision.** The worst single prefix is shared by one hundred distinct entities.

This is not a statistical argument about what might go wrong. It is a census. Six percent of the world's legal entity identifiers are not uniquely recoverable from sixteen characters.

Nine of the FDIC's own values fall into exactly that hole. Every one of the nine was issued under the LOU prefix `894500`, which allocates sequentially, so consecutive registrations differ only in their final characters and share everything before them. The result is that `894500C8YTS0IB1B`, as published in a United States federal banking register, denotes any of the following:

- Waterfall Bank, in the United States,
- АГРАРХАФЕН РУСЕ, in Bulgaria,
- SOCIETE DU PASSAGE AGARD, in France,
- GRISHVA INFRAPROJECT LLP, in India,
- UMANG CURE PRIVATE LIMITED, in India,
- BSL PLACEMENT PRIVATE LIMITED, in India.

Madison County Bank shares its published identifier with a Canadian bond fund and a Guernsey limited partnership. Cherokee State Bank shares its own with a Danish holding company and a Luxembourg estate agency. The community banks that chose the cheapest registrar are precisely the ones whose federally published identifier now points at half a dozen unrelated companies.

A further sixteen values match no LEI in the global system at all. Twelve more contain lowercase characters, which ISO 17442 does not permit, so any case-sensitive join against GLEIF fails silently on them. Those twelve all resolve once uppercased, which makes them the cheapest fix in this entire article.

## The one that made me stop

Once each value resolves to a real LEI, you can ask a better question than "is this well formed". You can ask whether it identifies the right company.

Mostly it does. On 2,173 institutions the resolved name matches the bank. On two, GLEIF's own consolidation records prove that it does not, and one of the two is worth the whole exercise.

FDIC certificate 5296 is **Associated Bank, National Association**, of Green Bay, Wisconsin. Forty-five and a half billion dollars in assets, 187 domestic offices, RSSD 917742. Its record carries the LEI value `549300N3CIN473IW`, which completes to exactly one real identifier, `549300N3CIN473IW5094`.

That identifier belongs to **ASSOCIATED BANC-CORP**, of Madison. The holding company. The parent.

The bank's own LEI is `ZF85QS7OXKPBG52R7N18`, registered in Green Bay, status ACTIVE, registration ISSUED. It appears nowhere in the FDIC's register. The subsidiary insured bank is carrying its parent's identifier, and GLEIF's Level 2 relationship file confirms the parent-child link independently, which is how this was detected rather than guessed.

Fifteen further institutions resolve to names ending in BANCORP, BANCSHARES or HOLDING, including SoFi Bank resolving to GOLDEN PACIFIC BANCORP and First NBC Bank resolving to First NBC Bank Holding Company. GLEIF publishes no active consolidation edge for those fifteen, so I do not count them as confirmed. They are, however, the same shape.

This is not a clerical curiosity. A bank and its holding company file different reports, on different consolidation bases, to different supervisors. FR Y-9C is the holding company consolidated. FFIEC 041 is the bank alone. If the identifier that is supposed to distinguish them points at the same entity, then consolidated and unconsolidated positions are attributed to one legal person by any system that trusts the register.

There is a related finding that needs no name judgement at all. CBI Bank & Trust, an Iowa institution with $1.66bn in assets, resolves to Herausgebergemeinschaft Wertpapier-Mitteilungen, a German company. The country code alone settles it.

## The same failure, one layer up

While I had the registers open I pulled the Federal Reserve's MDRM, the published data dictionary of regulatory reporting items. It is 87,702 rows covering 47,305 item codes across 181 reporting forms, and it is the closest thing American banking has to an official business glossary.

I expected to find the classic glossary pathology, the same code carrying different definitions on different forms. I was wrong, and the truth is more interesting.

**The Item Name and the Description are pure functions of the four-digit item code.** Byte for byte identical, on every form, in every period. Zero divergence across all 47,305 codes. Item code 2170, TOTAL ASSETS, carries one definition across 117 mnemonics and 64 reporting forms.

The dictionary achieves perfect consistency by being unable to represent the difference. Total assets on FR Y-9C is a consolidated holding company figure. On FFIEC 041 it is the bank alone. On FR Y-14A it is a projection under a stress scenario. The MDRM says the same sentence for all three, and where it does acknowledge that forms differ, it does so in free text inside the definition under a heading marked `COMPARABILITY:`. 1,278 concepts carry their scope that way, as prose, unparsed.

Meanwhile 27,445 of the 47,305 item codes, fifty-eight percent of the dictionary, carry no definition anywhere at all. They are labels.

And where meaning cannot vary, the facets do. **1,816 item codes are marked confidential on one form and public on another.** More pointedly, 1,342 MDRM identifiers change their confidentiality across their own date ranges. Disclosure status is scoped by form and by period, and is not derivable from the item code, which is exactly what a metadata layer keyed on the item code would assume.

## One problem, twice

Put the two halves together and they are the same sentence.

In the entity fabric, scope was thrown away when the identifier was truncated, and then the identifier was attached to the wrong level of the corporate hierarchy. In the concept fabric, scope was never encoded, because the dictionary attaches meaning to a code that spans sixty-four forms with different consolidation bases.

**Scope is never in the identifier.** Every serious data problem in a bank comes back to that, and both public registers embody it.

So the ontology I built is shaped by it rather than around it. Identifiers are reified assertions, not designators, which is the only way to state that a published value is truncated, ambiguous, or belongs to somebody else. Resolution is data: an assertion records what it resolved to and how many candidates it resolved to, because "this could be six companies" is a fact worth storing. The insured institution and the legal entity are separate classes, which is what makes the Associated Bank case statable rather than merely wrong. And on the reporting side, confidentiality and item type hang off a reified usage of a concept on a form in a period, because that is where the source data shows them actually varying.

The result is 1,123,634 triples, gated by SHACL. The shapes are the interesting part: each one encodes a defect class found in the sources, so the shape file doubles as the specification of what went wrong. Running pyshacl over the graph rediscovers, from the recorded state alone, all 1,733 truncations, 283 lapsed registrations, 9 ambiguities, 3 unresolvable values and 2 wrong-entity assertions. The governance report computes every headline number twice, once set-based from source and once through the shipped SPARQL, and refuses to write itself if the two disagree.

## What I am not claiming

The FFIEC's National Information Center bulk download, which holds the Federal Reserve's own view of who owns whom, is behind a CAPTCHA and could not be fetched. The comparison I most wanted to make, the Fed's hierarchy against GLEIF's, is not in this build. The HMDA panel file, which is a genuine published crosswalk between LEIs and RSSDs, sits on a host that is edge-blocked from here. Both gaps are recorded in the build report rather than papered over.

Nor is any of this evidence of incompetence. A sixteen-character column is an ordinary engineering decision that became wrong when an external standard specified twenty, and it survived because nothing downstream ever failed loudly. That is how identifier defects always survive. They produce values that still look like identifiers.

The fixes are correspondingly ordinary. Widen the field to twenty characters. Uppercase on ingest, which repairs twelve records immediately. Validate the check digits at the point of entry, which is one modulo operation. And record the identifier of the insured institution rather than of whatever entity in the group happened to be to hand.

I am sending these findings to the FDIC and to GLEIF, because a coverage result about the Global LEI System belongs with the people who run it. The repository, the pipeline, the shapes and the queries are open, so anyone can re-run the census on tomorrow's golden copy and get tomorrow's numbers.

---

**The artifact:** https://github.com/fabio-rovai/bank-register-ontology, code MIT, ontology and shapes CC BY 4.0.

If your organisation runs on bank entity data, regulatory reporting lineage, counterparty resolution, holding-company hierarchies, or a business glossary that has to reconcile to what the regulator actually publishes, this repository is the open baseline of that discipline. For the applied version on your own data: **fabio@thetesseractacademy.com**.
