"""Resolve the FDIC's truncated LEI values against the GLEIF golden copy.

Streams the Level 1 file once to (a) measure how ambiguous a 16-character
prefix is across the whole LEI population and (b) find every real LEI
compatible with each value the FDIC publishes. Streams Level 2 once to load
active consolidation edges, which is what lets us prove that a given value
belongs to the bank's PARENT rather than the bank.

Writes data/resolution.json, which is small enough to commit and is the input
to build_graph.py.
"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict

csv.field_size_limit(10_000_000)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")

# GLEIF Level 1 golden copy column positions (CDF 3.1 CSV layout)
C_LEI, C_NAME = 0, 1
C_CITY, C_REGION, C_COUNTRY = 41, 42, 43
C_JURIS, C_CATEGORY = 190, 191
C_ESTATUS, C_RSTATUS = 199, 315

PREFIX_LEN = 16          # the length the FDIC actually publishes
LEI_LEN = 20             # the length ISO 17442 requires

# Strip legal-form noise only. Tokens such as bancorp / holding / bancshares
# are deliberately KEPT, because they are exactly what distinguishes a holding
# company from its subsidiary bank.
LEGAL_FORM = {
    "n", "a", "na", "national", "association", "inc", "incorporated",
    "llc", "ltd", "limited", "the", "co", "company", "corp", "corporation",
    "fsb", "ssb", "sb", "dba",
}


def name_key(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())
    return " ".join(t for t in s.split() if t not in LEGAL_FORM)


def find(pattern: str) -> str:
    hits = glob.glob(os.path.join(DATA, pattern))
    if not hits:
        raise SystemExit(
            f"missing {pattern} in data/ - run pipeline/fetch_gleif.py first")
    return hits[0]


def main() -> None:
    fdic = [json.loads(l) for l in open(os.path.join(DATA, "fdic_all.jsonl"),
                                        encoding="utf-8") if l.strip()]
    targets: dict[str, list] = defaultdict(list)
    raw_values: list[str] = []
    for r in fdic:
        v = (r.get("LEI") or "").strip()
        if v:
            raw_values.append(v)
            targets[v.upper()].append(r)

    lengths = Counter(len(v) for v in raw_values)
    lowercase = [v for v in raw_values if v != v.upper()]
    print(f"FDIC records carrying an LEI value : {len(raw_values):,}")
    print(f"length histogram                   : {dict(sorted(lengths.items()))}")
    print(f"values containing lowercase        : {len(lowercase):,}")
    print(f"distinct values (uppercased)       : {len(targets):,}")

    # ---- Level 1 ---------------------------------------------------------
    prefix_counts: Counter[str] = Counter()
    hits: dict[str, list] = defaultdict(list)
    info: dict[str, dict] = {}
    scanned = 0
    with open(find("*lei2*.csv"), newline="", encoding="utf-8",
              errors="replace") as fh:
        rdr = csv.reader(fh)
        next(rdr)
        for row in rdr:
            scanned += 1
            lei = row[C_LEI]
            prefix_counts[lei[:PREFIX_LEN]] += 1
            rec = {
                "lei": lei, "name": row[C_NAME], "city": row[C_CITY],
                "region": row[C_REGION], "country": row[C_COUNTRY],
                "juris": row[C_JURIS], "category": row[C_CATEGORY],
                "entity_status": row[C_ESTATUS],
                "registration_status": row[C_RSTATUS],
            }
            info[lei] = rec
            if lei[:PREFIX_LEN] in targets:
                hits[lei[:PREFIX_LEN]].append(rec)

    colliding = {p: c for p, c in prefix_counts.items() if c > 1}
    in_collision = sum(colliding.values())
    print(f"\nGLEIF Level 1 records scanned      : {scanned:,}")
    print(f"distinct {PREFIX_LEN}-char prefixes         : {len(prefix_counts):,}")
    print(f"prefixes shared by >1 LEI          : {len(colliding):,}")
    print(f"LEIs sitting in a collision        : {in_collision:,} "
          f"({in_collision / scanned:.4%})")
    print(f"worst prefix multiplicity          : {max(prefix_counts.values())}")

    # ---- Level 2 ---------------------------------------------------------
    children: dict[str, list[str]] = defaultdict(list)
    with open(find("*rr*.csv"), newline="", encoding="utf-8",
              errors="replace") as fh:
        for row in csv.DictReader(fh):
            if row["Relationship.RelationshipStatus"] != "ACTIVE":
                continue
            if row["Relationship.RelationshipType"] not in (
                    "IS_DIRECTLY_CONSOLIDATED_BY",
                    "IS_ULTIMATELY_CONSOLIDATED_BY"):
                continue
            children[row["Relationship.EndNode.NodeID"]].append(
                row["Relationship.StartNode.NodeID"])
    print(f"GLEIF parents with active children : {len(children):,}")

    # ---- classify every asserted value -----------------------------------
    out: dict[str, dict] = {}
    for value, recs in targets.items():
        cands = hits.get(value, [])
        entry: dict = {
            "cardinality": len(cands),
            "candidates": [c["lei"] for c in cands],
            "certs": [r.get("CERT") for r in recs],
        }
        if len(cands) == 1:
            g = cands[0]
            entry["resolved"] = g["lei"]
            entry["resolved_name"] = g["name"]
            entry["resolved_country"] = g["country"]
            entry["entity_status"] = g["entity_status"]
            entry["registration_status"] = g["registration_status"]
            # does the resolved LEI parent an entity named like the bank?
            for r in recs:
                bank = r.get("NAME", "")
                if name_key(bank) == name_key(g["name"]):
                    continue
                for ch in children.get(g["lei"], []):
                    if ch in info and name_key(info[ch]["name"]) == name_key(bank):
                        entry.setdefault("parent_of_bank", []).append({
                            "cert": r.get("CERT"),
                            "bank_name": bank,
                            "bank_own_lei": ch,
                            "bank_own_name": info[ch]["name"],
                        })
                        break
        out[value] = entry

    n_one = sum(1 for e in out.values() if e["cardinality"] == 1)
    n_zero = sum(1 for e in out.values() if e["cardinality"] == 0)
    n_many = sum(1 for e in out.values() if e["cardinality"] > 1)
    n_parent = sum(len(e.get("parent_of_bank", [])) for e in out.values())
    print(f"\nresolve to exactly one real LEI    : {n_one:,}")
    print(f"resolve to no real LEI             : {n_zero:,}")
    print(f"ambiguous (>1 candidate)           : {n_many:,}")
    print(f"confirmed parent-recorded-as-child : {n_parent:,}")

    payload = {
        "generated_from": {
            "gleif_level1_records": scanned,
            "prefix_len": PREFIX_LEN,
            "lei_len": LEI_LEN,
        },
        "global_collision": {
            "distinct_prefixes": len(prefix_counts),
            "colliding_prefixes": len(colliding),
            "leis_in_collision": in_collision,
            "worst_multiplicity": max(prefix_counts.values()),
        },
        "fdic_values": {
            "records_with_value": len(raw_values),
            "length_histogram": dict(sorted(lengths.items())),
            "lowercase_values": sorted(set(lowercase)),
            "distinct_values": len(targets),
            "resolved_one": n_one,
            "resolved_zero": n_zero,
            "ambiguous": n_many,
            "parent_cases": n_parent,
        },
        "resolution": out,
    }
    path = os.path.join(DATA, "resolution.json")
    json.dump(payload, open(path, "w"), indent=1)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
