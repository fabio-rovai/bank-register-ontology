# BRO governance report
Generated 2026-08-16 from the FDIC BankFind register, the GLEIF golden copy of 3,403,760 LEI records, and the Federal Reserve MDRM.
All three sources are living systems; a re-fetch moves the totals. Every number below is reproduced by `pipeline/governance_report.py` and cross-checked against the shipped SPARQL queries.

## 1. The identifier fabric
- Active insured institutions: **4,250**
- Carrying an LEI value: **1,733 (40.8%)**, covering **92.20%** of total assets ($24,133,361,787k of $26,175,007,272k)
- LEI values that are **truncated** below the 20 characters ISO 17442 requires: **1,733** (every single one)
- Values containing **lowercase** characters: **11**
- Values that are **ambiguous** (compatible with more than one real LEI): **9**
- Values that resolve to **no LEI at all**: **3**
- Values that resolve to a **different legal entity** than the institution, confirmed against GLEIF consolidation records: **2**
- Active institutions whose LEI is **LAPSED / RETIRED / DUPLICATE**: **283**

### LEI coverage by asset band
| Asset band | With LEI | Institutions | Coverage |
|---|---:|---:|---:|
| <$100m | 48 | 544 | 8.8% |
| $100m-$1bn | 957 | 2,664 | 35.9% |
| $1bn-$10bn | 588 | 887 | 66.3% |
| $10bn-$100bn | 110 | 123 | 89.4% |
| >$100bn | 30 | 32 | 93.8% |

### Why 16 characters is not enough
Across all **3,403,760** LEIs in the Global LEI System, truncating to 16 characters collapses them into **3,220,636** distinct prefixes. **33,841** of those prefixes are shared by more than one LEI, putting **216,965 LEIs (6.37%)** into a collision. The worst single prefix covers **100** distinct legal entities.

## 2. The reporting concept fabric
- Dictionary rows: **87,702**
- Distinct item codes: **47,305**; distinct MDRM identifiers (mnemonic + code): **75,264**
- Reporting forms: **181**; series (mnemonics): **855**
- Rows still open (end date 12/31/9999): **52,255**
- Item codes carrying **no definition anywhere**: **27,445 of 47,305 (58.0%)**
- Item codes whose published **definition** differs across forms or periods: **0**
- Item codes whose published **name** differs across forms or periods: **0**
- Widest-reaching item code: **9999** (*REPORTING DATE (CC;YR;MO;DA)*) on **84** forms, with one definition
- Item codes whose **confidentiality** differs across forms: **1,816**; across periods within one MDRM identifier: **1,342**
- Item codes whose **item type** differs across forms: **1,746**; within one identifier: **637**
- Rows naming **no reporting form**: **7,171**
- Item type usage: F=75,537, D=9,128, S=1,098, P=980, R=924, J=35

The definition and the name are pure functions of the four-digit item code: identical, byte for byte, on every form and in every period that uses it. The facets that vary are exactly the ones the code cannot carry, which is why this ontology reifies item usage.

## 3. Cross-check
| Finding | Set-based | SPARQL | Agree |
|---|---:|---:|:--:|
| truncated | 1,733 | 1,733 | yes |
| ambiguous | 9 | 9 | yes |
| wrong entity | 2 | 2 | yes |
| lapsed | 283 | 283 | yes |
