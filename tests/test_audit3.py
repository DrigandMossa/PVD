"""Regression tests for the third audit round: input intake and documented claims.

This round covered the wizard/GUI intake path and the factual claims the docs make
about what the tool builds. Two of the findings are documentation that contradicted
the program - which matters here, because the docs are what a reader uses to
interpret the output.
"""

import os

import pytest

from pvd.design.builder import build_design
from pvd.model import Config
from pvd.parts.enzymes import RESTRICTION_SITES
from pvd.parts.payloads import PAYLOADS
from pvd.parts.programs import REGIMENS
from pvd.patient.parse import looks_like_a_path, read_arg
from pvd.seqops import revcomp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------- finding O
# read_arg fell through to the literal string when a path did not exist, so a
# mistyped filename was cleaned into nucleotides and reported as a malformed CDS.
# Fail-closed, but it sends the user to inspect their sequence instead of their path.

@pytest.mark.parametrize("value", [
    "lamp2a_patient_eligble.fasta",
    "data/patient.fa",
    "/absolute/missing.seq",
    "notes.txt",
])
def test_missing_path_is_an_error_not_a_sequence(value):
    assert looks_like_a_path(value)
    with pytest.raises(ValueError, match="No such file"):
        read_arg(value)


@pytest.mark.parametrize("value", [
    "ATGGCTGCTTAA",
    "atg gct gct taa",
    ">header\nATGGCTGCTTAA",
    "",
])
def test_inline_sequences_are_still_accepted(value):
    assert not looks_like_a_path(value)
    assert read_arg(value) == value


def test_an_existing_file_is_still_read(tmp_path):
    f = tmp_path / "patient.fasta"
    f.write_text(">x\nATGGCTTAA\n")
    assert read_arg(str(f)).startswith(">x")


# --------------------------------------------------------------- finding Y/Z
# The README said the disaggregase pair "spends the whole packaging budget", and
# docs/disaggregase-program.md said pvd implemented option 3, a single-gene
# architecture. Both were wrong: the regimen builds two separate vectors, each
# with ample headroom, and the real constraint is co-transduction.

def test_disaggregase_regimen_is_two_vectors_each_within_capacity():
    assert REGIMENS["disaggregase"]["payloads"] == ["DNAJB1", "HSPH1"]
    sizes = {}
    for payload in REGIMENS["disaggregase"]["payloads"]:
        d = build_design(Config(program="chaperone", payload=payload))
        sizes[payload] = sum(f.length for f in d.features if f.in_cassette)
        assert not [m for lvl, m in d.messages
                    if lvl == "error" and "packaging limit" in m], \
            "%s alone must package; capacity is not this regimen's constraint" % payload
    # each has real headroom, so "spends the whole packaging budget" is not true of either
    assert max(sizes.values()) < 4000, sizes


def test_the_pair_really_would_not_fit_in_one_genome():
    """The claim that justifies two vectors must itself hold."""
    cds = sum(PAYLOADS[k]["cds"] for k in REGIMENS["disaggregase"]["payloads"])
    assert cds == 3600
    # one genome would also need two promoters, a polyA and both ITRs
    from pvd.parts.elements import AAV_LIMIT, ITR_LEN, POLYA, PROMOTERS
    minimum = cds + 2 * PROMOTERS["hSyn1"] + POLYA["synthetic"] + 2 * ITR_LEN
    assert minimum > AAV_LIMIT, "if this ever fits, the two-vector rationale changes"


def test_readme_no_longer_claims_the_pair_fills_one_genome():
    with open(os.path.join(ROOT, "README.md")) as fh:
        text = fh.read()
    assert "the pair spends the whole packaging budget" not in text
    assert "co-transduction" in text.lower()


# ------------------------------------------------- standing correctness checks
# Not regressions: claims the tool makes that are externally checkable, pinned so
# a later edit cannot quietly corrupt them.

def test_every_restriction_site_is_palindromic():
    """check_insert searches the forward strand only, which is valid only for palindromes."""
    for enzyme, site in RESTRICTION_SITES.items():
        assert revcomp(site) == site, "%s (%s) is not palindromic: the forward-only " \
                                      "search would miss reverse-strand sites" % (enzyme, site)


def test_restriction_sites_are_the_real_recognition_sequences():
    known = {"EcoRI": "GAATTC", "BamHI": "GGATCC", "HindIII": "AAGCTT", "XhoI": "CTCGAG",
             "NotI": "GCGGCCGC", "XbaI": "TCTAGA", "SalI": "GTCGAC", "KpnI": "GGTACC",
             "NheI": "GCTAGC", "AgeI": "ACCGGT", "BsrGI": "TGTACA", "AscI": "GGCGCGCC"}
    assert RESTRICTION_SITES == known


def test_payload_cds_and_aa_lengths_agree():
    """cds must be aa*3 + 3 for the stop, or the capacity arithmetic is wrong."""
    for key, p in PAYLOADS.items():
        if not p.get("verified_length"):
            continue
        assert p["cds"] == p["aa"] * 3 + 3, \
            "%s: %d bp does not encode %d residues plus a stop" % (key, p["cds"], p["aa"])


def test_region_maps_are_contiguous_and_cover_the_protein():
    for key, p in PAYLOADS.items():
        regions = p["regions"]
        if not regions:
            continue
        assert regions[0][0] == 1, "%s region map does not start at residue 1" % key
        assert regions[-1][1] == p["aa"], "%s region map does not reach residue %d" % (key, p["aa"])
        for (_lo, hi, _n), (lo2, _hi2, _n2) in zip(regions, regions[1:]):
            assert lo2 == hi + 1, "%s has a gap or overlap at %d/%d" % (key, hi, lo2)
