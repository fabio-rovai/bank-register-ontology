"""Parse every artifact and run the SHACL gate.

Nothing in this repository is claimed to be valid RDF unless this script has
read it back. Usage:

    python pipeline/validate.py            # parse everything, validate entity layer
    python pipeline/validate.py --full     # also validate the concept layer
"""

from __future__ import annotations

import os
import sys
import time

from rdflib import Graph
from pyshacl import validate as shacl_validate

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "build")

ARTIFACTS = [
    "ontology/bro-core.ttl",
    "skos/identifier-schemes.ttl",
    "shapes/bro-shapes.ttl",
]


def parse(path: str) -> Graph:
    g = Graph()
    t0 = time.time()
    g.parse(path, format="turtle")
    print(f"  parsed {os.path.relpath(path, HERE):<38} "
          f"{len(g):>10,} triples  {time.time()-t0:6.1f}s")
    return g


def split_layers(src: str):
    """Write the entity layer to its own file so it can be gated on its own."""
    ent = os.path.join(BUILD, "bro-entity.ttl")
    con = os.path.join(BUILD, "bro-concept.ttl")
    if os.path.exists(ent) and os.path.exists(con):
        return ent, con
    header = []
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("@prefix") or not line.strip():
                header.append(line)
            else:
                break
    with open(src, encoding="utf-8") as fh, \
            open(ent, "w", encoding="utf-8") as fe, \
            open(con, "w", encoding="utf-8") as fc:
        fe.writelines(header)
        fc.writelines(header)
        for line in fh:
            if line.startswith("@prefix") or not line.strip():
                continue
            target = fc if ("id:concept-" in line or "id:usage-" in line
                            or "id:form-" in line or "id:series-" in line) else fe
            target.write(line)
    return ent, con


def gate(data_path: str, shapes: Graph, label: str) -> bool:
    print(f"\n--- SHACL gate: {label} ---")
    g = parse(data_path)
    t0 = time.time()
    conforms, results_graph, results_text = shacl_validate(
        g, shacl_graph=shapes, inference="none", abort_on_first=False,
        allow_infos=True, allow_warnings=True, meta_shacl=False,
    )
    took = time.time() - t0
    n = len(list(results_graph.subjects(
        predicate=None, object=None, unique=True))) if results_graph else 0
    print(f"  conforms (violations only): {conforms}   [{took:.1f}s]")
    lines = [l for l in results_text.splitlines() if "Message:" in l]
    from collections import Counter
    for msg, c in Counter(lines).most_common(12):
        print(f"    {c:>7,}  {msg.strip()[9:130]}")
    return conforms


def main() -> None:
    print("=== parsing artifacts ===")
    shapes = Graph()
    for rel in ARTIFACTS:
        g = parse(os.path.join(HERE, rel))
        if "shapes" in rel:
            shapes = g

    src = os.path.join(BUILD, "bro.ttl")
    if not os.path.exists(src):
        raise SystemExit("build/bro.ttl not found - run pipeline/build_graph.py")

    ent, con = split_layers(src)
    ok = gate(ent, shapes, "entity layer (FDIC x GLEIF)")
    if "--full" in sys.argv:
        ok = gate(con, shapes, "concept layer (MDRM)") and ok
    else:
        print("\n(concept layer not gated; pass --full to include it)")
    print("\nSHACL gate finished.")


if __name__ == "__main__":
    main()
