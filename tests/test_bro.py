"""Offline tests. No network, no large data files required except where marked."""

import os
import subprocess
import sys

import pytest
from rdflib import Graph, Namespace, URIRef

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "pipeline"))

from checksums import (  # noqa: E402
    KNOWN_INVALID_LEI, KNOWN_VALID_LEI, KNOWN_VALID_RTN, KNOWN_INVALID_RTN,
    lei_checksum_valid, lei_is_well_formed, rtn_checksum_valid,
)

BANK = Namespace("https://gov.tesseract.academy/def/banking#")
SCH = Namespace("https://gov.tesseract.academy/def/banking/scheme#")


@pytest.mark.parametrize("lei", KNOWN_VALID_LEI)
def test_valid_leis_pass(lei):
    assert lei_is_well_formed(lei)
    assert lei_checksum_valid(lei)


@pytest.mark.parametrize("lei", KNOWN_INVALID_LEI)
def test_invalid_leis_fail(lei):
    assert not lei_checksum_valid(lei)


@pytest.mark.parametrize("rtn", KNOWN_VALID_RTN)
def test_valid_rtns_pass(rtn):
    assert rtn_checksum_valid(rtn)


@pytest.mark.parametrize("rtn", KNOWN_INVALID_RTN)
def test_invalid_rtns_fail(rtn):
    assert not rtn_checksum_valid(rtn)


def test_truncated_lei_is_not_wellformed():
    """The defect this whole repository is about: a 16-character LEI."""
    assert not lei_is_well_formed("549300N3CIN473IW")
    assert lei_is_well_formed("549300N3CIN473IW5094")


def test_truncation_is_not_checksum_failure():
    """A truncated value is UNTESTABLE, not invalid. Both return False here,
    so the pipeline must distinguish them by reason, which it does."""
    assert not lei_checksum_valid("549300N3CIN473IW")
    assert lei_checksum_valid("549300N3CIN473IW5094")


@pytest.mark.parametrize("rel", [
    "ontology/bro-core.ttl",
    "skos/identifier-schemes.ttl",
    "shapes/bro-shapes.ttl",
    "examples/associated-bank.ttl",
])
def test_artifacts_parse(rel):
    g = Graph()
    g.parse(os.path.join(HERE, rel), format="turtle")
    assert len(g) > 0


def test_scheme_registry_declares_lei_rules_as_data():
    g = Graph()
    g.parse(os.path.join(HERE, "skos/identifier-schemes.ttl"), format="turtle")
    length = g.value(SCH.LEI, BANK.expectedLength)
    assert int(length) == 20, "the registry must state the LEI length as data"
    assert g.value(SCH.LEI, BANK.checkDigitAlgorithm) is not None
    # RSSD deliberately has NO check digit; that absence is meaningful
    assert g.value(SCH.RSSD, BANK.checkDigitAlgorithm) is None


def test_associated_bank_example_holds_the_finding():
    g = Graph()
    g.parse(os.path.join(HERE, "examples/associated-bank.ttl"), format="turtle")
    a = URIRef("https://gov.tesseract.academy/id/banking/idassert-lei-5296")
    assert str(g.value(a, BANK.assertedValue)) == "549300N3CIN473IW"
    assert g.value(a, BANK.schemeConformant).toPython() is False
    assert (a, BANK.nonConformanceReason, SCH.Truncated) in g
    assert g.value(a, BANK.denotesDifferentEntity).toPython() is True
    assert str(g.value(a, BANK.gleifLegalName)) == "ASSOCIATED BANC-CORP"
    assert int(g.value(a, BANK.resolutionCardinality)) == 1


def test_queries_are_syntactically_valid():
    qdir = os.path.join(HERE, "queries")
    g = Graph()
    for fn in sorted(os.listdir(qdir)):
        if fn.endswith(".rq"):
            g.query(open(os.path.join(qdir, fn), encoding="utf-8").read())


def test_checksums_selftest_exits_clean():
    r = subprocess.run([sys.executable, os.path.join(HERE, "pipeline", "checksums.py")],
                       capture_output=True)
    assert r.returncode == 0, r.stdout.decode()
