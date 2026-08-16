# Contributing

Contributions are welcome, particularly corrections. If a finding in this
repository is wrong, the most useful thing you can do is prove it.

## Data policy

This project uses **open data only**, and that constraint is deliberate.

Permitted sources include: FDIC BankFind (US Government public data), the GLEIF
golden copy and API (CC0 1.0), Federal Reserve MDRM (US Government public data),
SEC EDGAR, and other government or CC0/CC-BY published registers.

**Do not contribute data, mappings or derived files that originate from a
licensed commercial identifier or reference-data product.** That includes
CUSIP, SEDOL, RIC, and any vendor entity hierarchy or cross-reference file.
A pull request carrying licensed content will be rejected regardless of merit.
The point of the artifact is that it can be rebuilt from scratch by anyone,
for nothing, without signing anything.

Large source files are not committed. `data/resolution.json` is the small,
regenerable join result and is the exception.

## Reproducing before you report

Findings are timestamped against living registers. Before reporting that a
number is wrong, re-run the pipeline, because the number may simply have moved:

```bash
pip install -r requirements-dev.txt
python pipeline/fetch_fdic.py
# then fetch MDRM and the GLEIF golden copy into data/ (see README)
python pipeline/resolve_identifiers.py
python pipeline/build_graph.py
python pipeline/validate.py
python pipeline/governance_report.py
```

`governance_report.py` computes every headline number twice, once set-based
from source and once through the shipped SPARQL, and exits non-zero if the two
disagree. If you can make it exit non-zero, that is a bug worth an issue.

## Standards for a change

- Offline tests must pass: `python -m pytest tests/ -q`.
- New findings need a query in `queries/` that returns exactly the claimed count.
- New defect classes need a SHACL shape, so the shape file stays a complete
  specification of what is known to go wrong.
- Arithmetic belongs in `pipeline/`, policy belongs in `shapes/`. Do not encode
  a check-digit rule in a shape or a policy threshold in Python.
- No em dashes in prose. CI enforces this.

## Reporting a defect to the source

If you find a defect in a public register, please consider reporting it to the
publisher as well as opening an issue here. An open finding that nobody tells
the data owner about is a blog post, not a contribution.
