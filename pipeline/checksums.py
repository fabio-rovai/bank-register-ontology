"""Identifier arithmetic for US bank register data.

Every check-digit rule used anywhere in this repository lives here, with its
test vectors alongside it. The pipeline computes; the SHACL shapes assert the
recorded result. Arithmetic in code, policy in shapes.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# LEI: ISO 17442 structure, ISO 7064 MOD 97-10 check digits
# ---------------------------------------------------------------------------

LEI_RE = re.compile(r"^[0-9A-Z]{18}[0-9]{2}$")


def _alpha_to_num(value: str) -> str:
    """A->10 ... Z->35, digits unchanged (ISO 7064 alphabet conversion)."""
    out = []
    for ch in value:
        if ch.isdigit():
            out.append(ch)
        else:
            out.append(str(ord(ch) - 55))
    return "".join(out)


def lei_is_well_formed(lei: str) -> bool:
    """Structural check only: 20 chars, upper alnum, last two digits."""
    return bool(LEI_RE.match(lei or ""))


def lei_checksum_valid(lei: str) -> bool:
    """ISO 7064 MOD 97-10 over the whole 20-character LEI: remainder must be 1.

    A False here means the value cannot exist in the Global LEI System, no
    lookup required. This is the cheapest possible governance control and it
    is the one nobody runs.
    """
    if not lei_is_well_formed(lei):
        return False
    return int(_alpha_to_num(lei)) % 97 == 1


# ---------------------------------------------------------------------------
# ABA routing transit number: 9 digits, weighted mod 10 (3, 7, 1)
# ---------------------------------------------------------------------------

RTN_RE = re.compile(r"^[0-9]{9}$")
_RTN_WEIGHTS = (3, 7, 1, 3, 7, 1, 3, 7, 1)


def rtn_is_well_formed(rtn: str) -> bool:
    return bool(RTN_RE.match(rtn or ""))


def rtn_checksum_valid(rtn: str) -> bool:
    """ABA routing transit number check digit (3-7-1 weighting, mod 10 == 0)."""
    if not rtn_is_well_formed(rtn):
        return False
    total = sum(int(d) * w for d, w in zip(rtn, _RTN_WEIGHTS))
    return total % 10 == 0


# ---------------------------------------------------------------------------
# RSSD and FDIC certificate numbers
#
# Neither carries a check digit. They are opaque sequential keys assigned by
# the Federal Reserve (RSSD) and the FDIC (CERT). That absence is itself a
# governance fact worth modelling: a mistyped RSSD is undetectable without a
# lookup, unlike a mistyped LEI. The registry records the schemes as
# checksum-free so that a consumer of the graph can tell the difference
# between "validated" and "unvalidatable".
# ---------------------------------------------------------------------------

RSSD_RE = re.compile(r"^[0-9]{1,10}$")
CERT_RE = re.compile(r"^[0-9]{1,6}$")
CIK_RE = re.compile(r"^[0-9]{1,10}$")


def rssd_is_well_formed(rssd: str) -> bool:
    return bool(RSSD_RE.match((rssd or "").lstrip("0") or "0"))


def cert_is_well_formed(cert: str) -> bool:
    return bool(CERT_RE.match((cert or "").lstrip("0") or "0"))


def cik_is_well_formed(cik: str) -> bool:
    return bool(CIK_RE.match((cik or "").lstrip("0") or "0"))


# ---------------------------------------------------------------------------
# Test vectors. Run this file directly to check them.
# ---------------------------------------------------------------------------

# LEIs verified against the GLEIF API in prior work in this series.
KNOWN_VALID_LEI = [
    "549300G6KNDK44WUN559",  # Vanguard Index Funds (trust)
    "12WZ1W76P8QD4VJ6OB47",  # Vanguard 500 Index Fund
    "5493000MN7XN3BBKCE67",  # AP Skadesforsikring, DK
]

# The first is the letter-O transposition of the DK LEI above, found sitting in
# an official EU register in the sibling insurance project. The second is the
# all-zero placeholder that turns up in filings.
KNOWN_INVALID_LEI = [
    "5493O00MN7XN3BBKCE67",
    "00000000000000000000",
    "549300G6KNDK44WUN558",
]

KNOWN_VALID_RTN = ["021000021", "011000015", "111000025"]
KNOWN_INVALID_RTN = ["021000022", "12345678", "000000000x"]


def _selftest() -> int:
    failures = 0
    for lei in KNOWN_VALID_LEI:
        if not lei_checksum_valid(lei):
            print(f"FAIL: expected valid LEI rejected: {lei}")
            failures += 1
    for lei in KNOWN_INVALID_LEI:
        if lei_checksum_valid(lei):
            print(f"FAIL: expected invalid LEI accepted: {lei}")
            failures += 1
    for rtn in KNOWN_VALID_RTN:
        if not rtn_checksum_valid(rtn):
            print(f"FAIL: expected valid RTN rejected: {rtn}")
            failures += 1
    for rtn in KNOWN_INVALID_RTN:
        if rtn_checksum_valid(rtn):
            print(f"FAIL: expected invalid RTN accepted: {rtn}")
            failures += 1
    print("checksums selftest:", "OK" if failures == 0 else f"{failures} FAILURES")
    return failures


if __name__ == "__main__":
    raise SystemExit(1 if _selftest() else 0)
