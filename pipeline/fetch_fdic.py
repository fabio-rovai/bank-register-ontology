"""Fetch the full FDIC BankFind institutions register (keyless public API)."""

import json
import time
import urllib.parse
import urllib.request

BASE = "https://api.fdic.gov/banks/institutions"
UA = "Tesseract Academy open research (fabio@thetesseractacademy.com)"

FIELDS = [
    "CERT", "NAME", "ACTIVE", "FED_RSSD", "LEI", "UNINUM",
    "RSSDHCR", "NAMEHCR", "CITYHCR", "STALPHCR", "PARCERT", "ULTCERT",
    "BKCLASS", "CLCODE", "CHARTER", "CHRTAGNT", "REGAGNT", "FDICSUPV",
    "SPECGRP", "SPECGRPN", "CITY", "STALP", "STNAME", "COUNTY", "ZIP",
    "ASSET", "DEP", "OFFDOM", "OFFFOR", "ESTYMD", "INSDATE", "ENDEFYMD",
    "MUTUAL", "TRUST", "IBA", "FEDCHRTR", "STCHRTR", "REPDTE", "WEBADDR",
]


def fetch(active_only, out_path):
    rows, offset, limit = [], 0, 1000
    while True:
        params = {
            "fields": ",".join(FIELDS),
            "limit": str(limit),
            "offset": str(offset),
            "format": "json",
            "sort_by": "CERT",
            "sort_order": "ASC",
        }
        if active_only:
            params["filters"] = "ACTIVE:1"
        url = f"{BASE}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.load(resp)
        total = payload["meta"]["total"]
        batch = [d["data"] for d in payload.get("data", [])]
        rows.extend(batch)
        print(f"  {out_path}: {len(rows):,}/{total:,}", flush=True)
        offset += limit
        if not batch or len(rows) >= total:
            break
        time.sleep(0.4)

    with open(out_path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  wrote {len(rows):,} -> {out_path}")
    return rows


if __name__ == "__main__":
    print("Fetching ACTIVE institutions...")
    fetch(True, "fdic_active.jsonl")
    print("Fetching ALL institutions (incl. inactive)...")
    fetch(False, "fdic_all.jsonl")
