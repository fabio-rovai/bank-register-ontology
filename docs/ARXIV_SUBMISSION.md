# arXiv submission pack

Ready to paste into the submission form. Nothing submitted.

**Categories.** Primary `cs.DB`. Cross-list `cs.AI`, and optionally `cs.CY` for the regulatory angle. No endorsement is required: you are an established cs-domain author with five prior arXiv papers, one of which already carries cs.DB. Do **not** file under `q-fin` or `econ` as primary, because under the January 2026 endorsement policy those are separate endorsement domains where you are not established, and a company email address no longer satisfies the institutional test on its own.

**Moderation note.** arXiv rejects submissions that read as software announcements. The abstract below deliberately leads with the measurement and mentions the artifact only at the end. Keep it that way.

**License.** CC BY 4.0, matching the repository.

---

## Title

**Truncated at the Source: A Census of Legal Entity Identifier Integrity in US Federal Bank Registers**

## Abstract

The Legal Entity Identifier is a twenty-character code whose final two characters are check digits under ISO 7064 MOD 97-10, and on 1 October 2026 a joint rule of nine US financial regulators establishes it as the federal legal entity identifier standard. We measure what those registers actually publish today. Every one of the 2,252 LEI values in the FDIC's public BankFind register is truncated to sixteen characters, discarding both check digits and two entity-identifying characters, so no published value can be validated in isolation and each admits 1,296 arithmetic completions. We show this loss is not merely lossy but ambiguous: a census over the complete Global LEI System of 3,403,760 records finds 33,841 sixteen-character prefixes shared by more than one legal entity, placing 216,965 identifiers, 6.37 per cent of the global population, in collision, with one prefix covering 100 entities. Nine FDIC values are consequently ambiguous. Resolving the remainder against the golden copy reveals sixteen values matching no LEI, twelve violating the uppercase rule, and two institutions carrying their parent holding company's identifier, confirmed against consolidation records and independently corroborated by the Federal Reserve's National Information Center, whose own LEI values are uniformly well formed. Separately, the Federal Reserve's MDRM data dictionary attaches exactly one name and definition per item code across up to sixty-four reporting forms with differing consolidation bases, and 58 per cent of its item codes carry no definition at all. We release an OWL 2 ontology, SKOS scheme registries and SHACL shapes that make identifier non-conformance, resolution cardinality and cross-register disagreement first-class, queryable state, together with a reproducible pipeline over 1,123,634 triples.

*(1,918 characters including spaces. arXiv's limit is 1,920.)*

## Comments field

> 14 pages. Open artifact, pipeline and SHACL shapes at https://github.com/fabio-rovai/bank-register-ontology. All figures reproducible from public sources: FDIC BankFind API, GLEIF golden copy of 16 August 2026, Federal Reserve MDRM.

## ACM classification (optional)

- Information systems, Data management systems, Data cleaning
- Information systems, World Wide Web, Web data description languages, Semantic web description languages
- Applied computing, Law, social and behavioral sciences

## MSC / PACS

Not applicable.

---

## Paper outline, if you write the full version

1. **Introduction.** The FDTA joint rule, the twenty-character standard, and the question of what federal registers publish today. State plainly that the rule binds agencies rather than banks and that nothing here is a compliance assertion.
2. **Background.** ISO 17442 structure and the role of the check digits; the Global LEI System and GLEIF's quality regime, which measures issuance rather than downstream republication; the US register landscape of FDIC certificate, RSSD, OCC charter.
3. **Method.** Sources and retrieval dates; prefix resolution against the golden copy; the conservative name key for parent detection, including the negative result from the aggressive key, which is worth reporting because it is the failure mode a reader would otherwise repeat.
4. **Results.** Truncation; the collision census with robustness at seventeen and eighteen characters; ambiguity, unresolvability and case; wrong-entity assignment; the NIC corroboration; the MDRM analysis with both denominators.
5. **Modelling.** Why identifier-as-designator cannot represent any of this; reified assertions; resolution cardinality as data; the institution and legal entity split; usage reification for the concept layer.
6. **Validation.** SHACL re-derivation from recorded state; the two-way set-based and SPARQL cross-check that fails the build on disagreement.
7. **Related work.** FIBO, with the measured gap table; OFR SDP 18-01; FinRegOnt; GLEIF's own RDF and the unactioned SHACL proposal.
8. **Limitations.** NIC staleness and the CAPTCHA; the discontinued HMDA panel; prefix uniqueness as a property of the register on a given day; per-institution versus per-value counts.
9. **Discussion.** Where responsibility sits, and the gap between issuance-side and republication-side quality measurement.

## Sequencing

Submit **after** the Zenodo DOI exists, so the artifact can be cited by DOI rather than by a bare repository URL. Some venues, the Semantic Web Journal among them, require a stable archived URL and will not accept GitHub alone.
