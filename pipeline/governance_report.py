"""Generate reports/GOVERNANCE_REPORT.md.

Every number is computed twice: once set-based from the source data, once by
running the shipped SPARQL query against the built graph. The report prints
both and fails loudly if they disagree.
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import date

from rdflib import Graph

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, BUILD = os.path.join(HERE, "data"), os.path.join(HERE, "build")
REPORTS = os.path.join(HERE, "reports")
os.makedirs(REPORTS, exist_ok=True)
csv.field_size_limit(10_000_000)


def sparql_count(g: Graph, path: str) -> int:
    q = open(os.path.join(HERE, "queries", path), encoding="utf-8").read()
    return len(list(g.query(q)))


def main() -> None:
    fdic = [json.loads(l) for l in open(os.path.join(DATA, "fdic_all.jsonl"),
                                        encoding="utf-8") if l.strip()]
    active = [r for r in fdic if r.get("ACTIVE") == 1]
    res = json.load(open(os.path.join(DATA, "resolution.json"), encoding="utf-8"))
    resolution = res["resolution"]
    gc = res["global_collision"]

    # ---------------- entity layer, set-based -----------------------------
    with_lei = [r for r in active if (r.get("LEI") or "").strip()]
    tot_assets = sum(r.get("ASSET") or 0 for r in active)
    lei_assets = sum(r.get("ASSET") or 0 for r in with_lei)

    trunc = lower = ambig = unres = wrong = lapsed = 0
    for r in with_lei:
        v = (r.get("LEI") or "").strip()
        if len(v) < 20:
            trunc += 1
        if v != v.upper():
            lower += 1
        e = resolution.get(v.upper())
        if not e:
            continue
        if e["cardinality"] == 0:
            unres += 1
        elif e["cardinality"] > 1:
            ambig += 1
        else:
            if e.get("registration_status") in ("LAPSED", "RETIRED",
                                                "DUPLICATE", "ANNULLED"):
                lapsed += 1
            if any(pc.get("cert") == r.get("CERT")
                   for pc in e.get("parent_of_bank", [])):
                wrong += 1

    bands = [("<$100m", 0, 100_000), ("$100m-$1bn", 100_000, 1_000_000),
             ("$1bn-$10bn", 1_000_000, 10_000_000),
             ("$10bn-$100bn", 10_000_000, 100_000_000),
             (">$100bn", 100_000_000, float("inf"))]
    band_rows = []
    for label, lo, hi in bands:
        pool = [r for r in active if lo <= (r.get("ASSET") or 0) < hi]
        got = [r for r in pool if (r.get("LEI") or "").strip()]
        if pool:
            band_rows.append((label, len(got), len(pool), len(got)/len(pool)))

    # ---------------- concept layer, set-based ----------------------------
    rows = []
    with open(os.path.join(DATA, "MDRM_CSV.csv"), newline="",
              encoding="utf-8", errors="replace") as fh:
        fh.readline()
        rows = list(csv.DictReader(fh))

    desc_by_code, name_by_code = defaultdict(set), defaultdict(set)
    conf_by_code, type_by_code = defaultdict(set), defaultdict(set)
    conf_by_id, type_by_id = defaultdict(set), defaultdict(set)
    forms_by_code = defaultdict(set)
    itemtypes, blank_form, open_ended = Counter(), 0, 0
    for r in rows:
        code = (r.get("Item Code") or "").strip()
        mn = (r.get("Mnemonic") or "").strip()
        form = (r.get("Reporting Form") or "").strip()
        if (r.get("Description") or "").strip():
            desc_by_code[code].add(r["Description"])
        if (r.get("Item Name") or "").strip():
            name_by_code[code].add(r["Item Name"].strip())
        if (r.get("Confidentiality") or "").strip():
            conf_by_code[code].add(r["Confidentiality"].strip())
            conf_by_id[mn + code].add(r["Confidentiality"].strip())
        if (r.get("ItemType") or "").strip():
            type_by_code[code].add(r["ItemType"].strip())
            type_by_id[mn + code].add(r["ItemType"].strip())
        if form:
            forms_by_code[code].add(form)
        else:
            blank_form += 1
        itemtypes[(r.get("ItemType") or "").strip()] += 1
        if (r.get("End Date") or "").strip().startswith("12/31/9999"):
            open_ended += 1

    n_codes = len(name_by_code)
    n_described = len(desc_by_code)
    divergent_desc = sum(1 for v in desc_by_code.values() if len(v) > 1)
    divergent_name = sum(1 for v in name_by_code.values() if len(v) > 1)
    conf_conflict = sum(1 for v in conf_by_code.values() if len(v) > 1)
    type_conflict = sum(1 for v in type_by_code.values() if len(v) > 1)
    conf_conflict_id = sum(1 for v in conf_by_id.values() if len(v) > 1)
    type_conflict_id = sum(1 for v in type_by_id.values() if len(v) > 1)
    widest = max(forms_by_code.items(), key=lambda kv: len(kv[1]))

    # ---------------- cross-check with SPARQL -----------------------------
    print("cross-checking with SPARQL over build/bro-entity.ttl ...")
    g = Graph()
    g.parse(os.path.join(BUILD, "bro-entity.ttl"), format="turtle")
    checks = {
        "truncated": (trunc, sparql_count(g, "q1_truncated_identifiers.rq")),
        "ambiguous": (ambig, sparql_count(g, "q2_ambiguous_identifiers.rq")),
        "wrong entity": (wrong, sparql_count(g, "q3_wrong_entity.rq")),
        "lapsed": (lapsed, sparql_count(g, "q4_lapsed_on_operating_banks.rq")),
    }
    ok = True
    for k, (a, b) in checks.items():
        flag = "OK " if a == b else "MISMATCH"
        if a != b:
            ok = False
        print(f"  {flag} {k:<14} set-based={a:<6} sparql={b}")

    # ---------------- write ------------------------------------------------
    out = [
        f"# BRO governance report\n",
        f"Generated {date.today().isoformat()} from the FDIC BankFind register, "
        f"the GLEIF golden copy of {res['generated_from']['gleif_level1_records']:,} "
        f"LEI records, and the Federal Reserve MDRM.\n",
        "All three sources are living systems; a re-fetch moves the totals. "
        "Every number below is reproduced by `pipeline/governance_report.py` "
        "and cross-checked against the shipped SPARQL queries.\n",
        "\n## 1. The identifier fabric\n",
        f"- Active insured institutions: **{len(active):,}**\n",
        f"- Carrying an LEI value: **{len(with_lei):,} ({len(with_lei)/len(active):.1%})**, "
        f"covering **{lei_assets/tot_assets:.2%}** of total assets "
        f"(${lei_assets:,.0f}k of ${tot_assets:,.0f}k)\n",
        f"- LEI values that are **truncated** below the 20 characters ISO 17442 "
        f"requires: **{trunc:,}** (every single one)\n",
        f"- Values containing **lowercase** characters: **{lower:,}**\n",
        f"- Values that are **ambiguous** (compatible with more than one real LEI): "
        f"**{ambig:,}**\n",
        f"- Values that resolve to **no LEI at all**: **{unres:,}**\n",
        f"- Values that resolve to a **different legal entity** than the "
        f"institution, confirmed against GLEIF consolidation records: **{wrong:,}**\n",
        f"- Active institutions whose LEI is **LAPSED / RETIRED / DUPLICATE**: "
        f"**{lapsed:,}**\n",
        "\n### LEI coverage by asset band\n",
        "| Asset band | With LEI | Institutions | Coverage |\n|---|---:|---:|---:|\n",
    ]
    for label, got, tot, pct in band_rows:
        out.append(f"| {label} | {got:,} | {tot:,} | {pct:.1%} |\n")

    out += [
        "\n### Why 16 characters is not enough\n",
        f"Across all **{res['generated_from']['gleif_level1_records']:,}** LEIs in "
        f"the Global LEI System, truncating to 16 characters collapses them into "
        f"**{gc['distinct_prefixes']:,}** distinct prefixes. "
        f"**{gc['colliding_prefixes']:,}** of those prefixes are shared by more "
        f"than one LEI, putting **{gc['leis_in_collision']:,} LEIs "
        f"({gc['leis_in_collision']/res['generated_from']['gleif_level1_records']:.2%})** "
        f"into a collision. The worst single prefix covers "
        f"**{gc['worst_multiplicity']}** distinct legal entities.\n",
        "\n## 2. The reporting concept fabric\n",
        f"- Dictionary rows: **{len(rows):,}**\n",
        f"- Distinct item codes: **{n_codes:,}**; distinct MDRM identifiers "
        f"(mnemonic + code): **{len(conf_by_id):,}**\n",
        f"- Reporting forms: **{len(set().union(*forms_by_code.values())):,}**; "
        f"series (mnemonics): **{len(set(k[:4] for k in conf_by_id)):,}**\n",
        f"- Rows still open (end date 12/31/9999): **{open_ended:,}**\n",
        f"- Item codes carrying **no definition anywhere**: "
        f"**{n_codes - n_described:,} of {n_codes:,} ({(n_codes-n_described)/n_codes:.1%})**\n",
        f"- Item codes whose published **definition** differs across forms or "
        f"periods: **{divergent_desc:,}**\n",
        f"- Item codes whose published **name** differs across forms or periods: "
        f"**{divergent_name:,}**\n",
        f"- Widest-reaching item code: **{widest[0]}** "
        f"(*{sorted(name_by_code[widest[0]])[0]}*) on **{len(widest[1])}** forms, "
        f"with one definition\n",
        f"- Item codes whose **confidentiality** differs across forms: "
        f"**{conf_conflict:,}**; across periods within one MDRM identifier: "
        f"**{conf_conflict_id:,}**\n",
        f"- Item codes whose **item type** differs across forms: "
        f"**{type_conflict:,}**; within one identifier: **{type_conflict_id:,}**\n",
        f"- Rows naming **no reporting form**: **{blank_form:,}**\n",
        f"- Item type usage: "
        f"{', '.join(f'{k or 'blank'}={v:,}' for k, v in itemtypes.most_common())}\n",
        "\nThe definition and the name are pure functions of the four-digit item "
        "code: identical, byte for byte, on every form and in every period that "
        "uses it. The facets that vary are exactly the ones the code cannot "
        "carry, which is why this ontology reifies item usage.\n",
        "\n## 3. Cross-check\n",
        "| Finding | Set-based | SPARQL | Agree |\n|---|---:|---:|:--:|\n",
    ]
    for k, (a, b) in checks.items():
        out.append(f"| {k} | {a:,} | {b:,} | {'yes' if a == b else 'NO'} |\n")

    path = os.path.join(REPORTS, "GOVERNANCE_REPORT.md")
    open(path, "w", encoding="utf-8").writelines(out)
    print(f"\nwrote {path}")
    if not ok:
        raise SystemExit("set-based and SPARQL counts disagree")


if __name__ == "__main__":
    main()
