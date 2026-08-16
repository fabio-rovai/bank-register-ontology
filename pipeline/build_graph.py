"""Build the BRO knowledge graph from the fetched sources.

Emits Turtle directly (the graph is large enough that constructing it in an
in-memory rdflib Graph first is the slow path), then the validate step parses
what was written, so nothing is asserted that has not been read back.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checksums import lei_checksum_valid, lei_is_well_formed  # noqa: E402

csv.field_size_limit(10_000_000)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

NS = "https://gov.tesseract.academy/def/banking#"
SCH = "https://gov.tesseract.academy/def/banking/scheme#"
ID = "https://gov.tesseract.academy/id/banking/"

LEI_LEN = 20
PREFIX_LEN = 16
OPEN_SENTINEL = "12/31/9999"

PREAMBLE = f"""@prefix bank:    <{NS}> .
@prefix banksch: <{SCH}> .
@prefix id:      <{ID}> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

"""


def esc(s) -> str:
    s = "" if s is None else str(s)
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    return s


def lit(s) -> str:
    return f'"{esc(s)}"'


def slug(s) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(s))


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s.split(" ")[0], "%m/%d/%Y").date().isoformat()
    except ValueError:
        return None


class Writer:
    def __init__(self, path):
        self.fh = open(path, "w", encoding="utf-8")
        self.fh.write(PREAMBLE)
        self.n = 0

    def t(self, s, p, o):
        self.fh.write(f"{s} {p} {o} .\n")
        self.n += 1

    def close(self):
        self.fh.close()


# ---------------------------------------------------------------- entity layer
def build_entities(w: Writer) -> dict:
    fdic = [json.loads(l) for l in open(os.path.join(DATA, "fdic_all.jsonl"),
                                        encoding="utf-8") if l.strip()]
    active = [r for r in fdic if r.get("ACTIVE") == 1]
    res = json.load(open(os.path.join(DATA, "resolution.json"), encoding="utf-8"))
    resolution = res["resolution"]

    stats = {
        "institutions": 0, "lei_assertions": 0, "nonconformant": 0,
        "ambiguous": 0, "unresolvable": 0, "parent_cases": 0,
        "control_assertions": 0, "lapsed": 0, "resolved_entities": 0,
    }
    seen_entities = set()

    for r in active:
        cert = r.get("CERT")
        inst = f"id:inst-cert-{slug(cert)}"
        stats["institutions"] += 1
        w.t(inst, "a", "bank:InsuredDepositoryInstitution")
        w.t(inst, "bank:legalName", lit(r.get("NAME")))
        w.t(inst, "bank:isActive", "true")
        if r.get("ASSET") is not None:
            w.t(inst, "bank:totalAssets", f'"{r["ASSET"]}"^^xsd:decimal')
        if r.get("OFFDOM") is not None:
            w.t(inst, "bank:domesticOffices", f'"{r["OFFDOM"]}"^^xsd:integer')
        if r.get("STALP"):
            w.t(inst, "rdfs:comment", lit(f"{r.get('CITY','')}, {r.get('STALP','')}"))

        # --- FDIC certificate assertion
        a = f"id:idassert-cert-{slug(cert)}"
        w.t(inst, "bank:identifiedBy", a)
        w.t(a, "a", "bank:FDICCertAssertion")
        w.t(a, "bank:assertedValue", lit(cert))
        w.t(a, "bank:identifierScheme", "banksch:FDICCert")
        w.t(a, "bank:sourceSystem", "banksch:FDICBankFind")
        w.t(a, "bank:schemeConformant", "true")

        # --- RSSD assertion (no check digit exists for this scheme)
        rssd = str(r.get("FED_RSSD") or "").strip()
        if rssd and rssd != "0":
            a = f"id:idassert-rssd-{slug(cert)}"
            w.t(inst, "bank:identifiedBy", a)
            w.t(a, "a", "bank:RSSDAssertion")
            w.t(a, "bank:assertedValue", lit(rssd))
            w.t(a, "bank:identifierScheme", "banksch:RSSD")
            w.t(a, "bank:sourceSystem", "banksch:FDICBankFind")
            w.t(a, "bank:schemeConformant", "true")

        # --- LEI assertion, the interesting one
        raw = (r.get("LEI") or "").strip()
        if raw:
            stats["lei_assertions"] += 1
            a = f"id:idassert-lei-{slug(cert)}"
            w.t(inst, "bank:identifiedBy", a)
            w.t(a, "a", "bank:LEIAssertion")
            w.t(a, "bank:assertedValue", lit(raw))
            w.t(a, "bank:identifierScheme", "banksch:LEI")
            w.t(a, "bank:sourceSystem", "banksch:FDICBankFind")

            conformant = lei_is_well_formed(raw)
            w.t(a, "bank:schemeConformant", "true" if conformant else "false")
            if not conformant:
                stats["nonconformant"] += 1
                if len(raw) < LEI_LEN:
                    w.t(a, "bank:nonConformanceReason", "banksch:Truncated")
                if raw != raw.upper():
                    w.t(a, "bank:nonConformanceReason", "banksch:WrongCase")
            else:
                w.t(a, "bank:checksumValid",
                    "true" if lei_checksum_valid(raw) else "false")

            entry = resolution.get(raw.upper())
            if entry:
                card = entry["cardinality"]
                w.t(a, "bank:resolutionCardinality", f'"{card}"^^xsd:integer')
                w.t(a, "bank:resolutionMethod",
                    "banksch:PrefixJoin" if card else "banksch:Unresolved")
                if card == 0:
                    stats["unresolvable"] += 1
                elif card > 1:
                    stats["ambiguous"] += 1
                else:
                    lei = entry["resolved"]
                    ent = f"id:entity-lei-{slug(lei)}"
                    w.t(a, "bank:resolvesTo", ent)
                    w.t(a, "bank:gleifLegalName", lit(entry["resolved_name"]))
                    w.t(a, "bank:gleifCountry", lit(entry["resolved_country"]))
                    w.t(a, "bank:gleifEntityStatus", lit(entry["entity_status"]))
                    w.t(a, "bank:gleifRegistrationStatus",
                        lit(entry["registration_status"]))
                    if entry["registration_status"] in (
                            "LAPSED", "RETIRED", "ANNULLED", "DUPLICATE"):
                        stats["lapsed"] += 1
                    if lei not in seen_entities:
                        seen_entities.add(lei)
                        stats["resolved_entities"] += 1
                        w.t(ent, "a", "bank:LegalEntity")
                        w.t(ent, "bank:legalName", lit(entry["resolved_name"]))
                    for pc in entry.get("parent_of_bank", []):
                        if pc.get("cert") == cert:
                            stats["parent_cases"] += 1
                            w.t(a, "bank:denotesDifferentEntity", "true")
                            own = f"id:entity-lei-{slug(pc['bank_own_lei'])}"
                            w.t(own, "a", "bank:LegalEntity")
                            w.t(own, "bank:legalName", lit(pc["bank_own_name"]))
                            w.t(inst, "rdfs:seeAlso", own)

        # --- control assertion from the FDIC high holder field
        hcr = str(r.get("RSSDHCR") or "").strip()
        if hcr and hcr != "0":
            hc = f"id:entity-rssd-{slug(hcr)}"
            w.t(hc, "a", "bank:BankHoldingCompany")
            if r.get("NAMEHCR"):
                w.t(hc, "bank:legalName", lit(r.get("NAMEHCR")))
            ca = f"id:control-fdic-{slug(cert)}"
            w.t(ca, "a", "bank:ControlAssertion")
            w.t(ca, "bank:controlled", inst)
            w.t(ca, "bank:controller", hc)
            w.t(ca, "bank:controlType", "banksch:FDICHighHolder")
            w.t(ca, "bank:sourceSystem", "banksch:FDICBankFind")
            stats["control_assertions"] += 1

    return stats


# --------------------------------------------------------------- concept layer
def build_concepts(w: Writer) -> dict:
    path = os.path.join(DATA, "MDRM_CSV.csv")
    stats = {"concepts": 0, "usages": 0, "forms": 0, "series": 0,
             "open_ended": 0, "no_definition": 0, "prose_scope": 0}
    concepts: dict[str, dict] = {}
    forms: set[str] = set()
    series: set[str] = set()
    rows = []

    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        fh.readline()                      # classification banner
        for r in csv.DictReader(fh):
            rows.append(r)
            code = (r.get("Item Code") or "").strip()
            if not code:
                continue
            name = (r.get("Item Name") or "").strip()
            desc = r.get("Description") or ""
            c = concepts.setdefault(code, {"name": name, "desc": ""})
            if desc.strip() and not c["desc"]:
                c["desc"] = desc

    for code, c in concepts.items():
        u = f"id:concept-mdrm-{slug(code)}"
        stats["concepts"] += 1
        w.t(u, "a", "bank:ReportingConcept")
        w.t(u, "a", "skos:Concept")
        w.t(u, "skos:prefLabel", lit(c["name"]))
        w.t(u, "bank:itemCode", lit(code))
        if c["desc"].strip():
            w.t(u, "bank:hasDefinition", lit(c["desc"]))
            if "COMPARABILITY" in c["desc"].upper():
                w.t(u, "bank:definedOnlyInProse", "true")
                stats["prose_scope"] += 1
        else:
            stats["no_definition"] += 1

    ITEMTYPE = {"F": "banksch:Financial", "D": "banksch:Derived",
                "S": "banksch:Structure", "P": "banksch:Percentage",
                "R": "banksch:Rate", "J": "banksch:Projected",
                "E": "banksch:Examination"}

    for i, r in enumerate(rows):
        code = (r.get("Item Code") or "").strip()
        mn = (r.get("Mnemonic") or "").strip()
        if not code or not mn:
            continue
        form = (r.get("Reporting Form") or "").strip()
        start = parse_date(r.get("Start Date"))
        end_raw = (r.get("End Date") or "").strip()
        end = parse_date(end_raw)
        u = f"id:usage-{slug(mn)}-{slug(code)}-{i}"
        stats["usages"] += 1
        w.t(u, "a", "bank:ItemUsage")
        w.t(u, "bank:usageOf", f"id:concept-mdrm-{slug(code)}")
        w.t(u, "bank:mdrmIdentifier", lit(f"{mn}{code}"))

        s = f"id:series-{slug(mn)}"
        if mn not in series:
            series.add(mn)
            stats["series"] += 1
            w.t(s, "a", "bank:ReportingSeries")
            w.t(s, "skos:notation", lit(mn))
        w.t(u, "bank:inSeries", s)

        if form:
            f = f"id:form-{slug(form)}"
            if form not in forms:
                forms.add(form)
                stats["forms"] += 1
                w.t(f, "a", "bank:ReportingForm")
                w.t(f, "rdfs:label", lit(form))
            w.t(u, "bank:onForm", f)

        if start:
            w.t(u, "bank:validFrom", f'"{start}"^^xsd:date')
        if end_raw.startswith(OPEN_SENTINEL):
            w.t(u, "bank:isOpenEnded", "true")
            stats["open_ended"] += 1
        elif end:
            w.t(u, "bank:validTo", f'"{end}"^^xsd:date')

        conf = (r.get("Confidentiality") or "").strip().upper()
        if conf in ("Y", "N"):
            w.t(u, "bank:confidentiality", "true" if conf == "Y" else "false")
        it = (r.get("ItemType") or "").strip().upper()
        if it in ITEMTYPE:
            w.t(u, "bank:itemType", ITEMTYPE[it])

    return stats


def main() -> None:
    out = os.path.join(BUILD, "bro.ttl")
    w = Writer(out)
    print("building entity layer...")
    e = build_entities(w)
    n_after_entities = w.n
    print("building concept layer...")
    c = build_concepts(w)
    w.close()

    print(f"\nentity layer  : {n_after_entities:,} triples")
    for k, v in e.items():
        print(f"   {k:<22} {v:,}")
    print(f"concept layer : {w.n - n_after_entities:,} triples")
    for k, v in c.items():
        print(f"   {k:<22} {v:,}")
    print(f"\nTOTAL         : {w.n:,} triples -> {out}")
    print(f"file size     : {os.path.getsize(out)/1e6:.1f} MB")

    json.dump({"entity": e, "concept": c, "triples": w.n},
              open(os.path.join(BUILD, "build_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
