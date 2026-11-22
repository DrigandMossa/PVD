"""The example patient set must be byte-identical on every run.

It is teaching material: the generated README.txt and classifications.tsv name the
planted variants, and docs/start-here.md quotes the gate output for them. If the
reference CDS is regenerated differently per process, every one of those names
changes and the walkthrough stops matching what the reader sees.

That is not hypothetical. `pool` was built from `set(CODONS.values())`, and set
iteration order for strings depends on per-process hash randomisation, so a fixed
random seed still produced a different CDS on every invocation.

These tests pin the planted labels to literals. Because pytest runs in a fresh
process with its own hash seed, a regression shows up here rather than in a
reader's terminal.
"""

import os
import tempfile

from pvd.cli.example import _make_cds, write_example
from pvd.parts.payloads import PAYLOADS, TARGET
from pvd.seqops import translate

# Planted by write_example: one benign tail change, one in the shared lumenal
# region, one inside VH14's epitope window.
EXPECTED_LABELS = ("H402K", "Q120W", "A91D")


def test_reference_cds_is_stable_across_processes():
    lamp = _make_cds(PAYLOADS["LAMP2A"]["aa"], seed=11)
    snca = _make_cds(TARGET["aa"], seed=23)
    # The residues the planted labels claim were there before mutation.
    assert translate(lamp)[401] == "H", "LAMP2A reference CDS drifted"
    assert translate(lamp)[119] == "Q", "LAMP2A reference CDS drifted"
    assert translate(snca)[90] == "A", "SNCA reference CDS drifted"


def test_generated_cds_lengths_match_the_library():
    lamp = _make_cds(PAYLOADS["LAMP2A"]["aa"], seed=11)
    snca = _make_cds(TARGET["aa"], seed=23)
    assert len(translate(lamp)) == PAYLOADS["LAMP2A"]["aa"]
    assert len(translate(snca)) == TARGET["aa"]
    assert lamp.startswith("ATG") and lamp.endswith("TAA")


def test_readme_and_classifications_name_the_same_variants():
    with tempfile.TemporaryDirectory() as d:
        write_example(d)
        with open(os.path.join(d, "README.txt")) as fh:
            readme = fh.read()
        with open(os.path.join(d, "classifications.tsv")) as fh:
            classify = fh.read()
        with open(os.path.join(d, "bins.tsv")) as fh:
            bins = fh.read()

    tail, shared, epitope = EXPECTED_LABELS
    for label in EXPECTED_LABELS:
        assert label in readme, "README.txt does not name %s; the example drifted" % label
    # The gate reads these two files, so a label here that README does not match
    # would make the walkthrough wrong even though nothing errors.
    assert "%s\tbenign" % tail in classify
    assert "%s\tvus" % shared in classify
    assert "BIN-01\t%s" % tail in bins
    assert epitope not in classify, "the epitope hit is verified, not classified"


def test_every_promised_file_is_written():
    with tempfile.TemporaryDirectory() as d:
        paths = write_example(d)
        names = {os.path.basename(p) for p in paths}
    for name in ("README.txt", "classifications.tsv", "bins.tsv",
                 "lamp2a_reference.fasta", "lamp2a_patient_eligible.fasta",
                 "lamp2a_patient_blocked.fasta", "snca_reference.fasta",
                 "snca_patient_intact.fasta", "snca_patient_epitope_hit.fasta"):
        assert name in names, "write_example no longer writes %s" % name
