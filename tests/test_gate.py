"""Gate behaviour: the branches that decide whether a patient allele may be delivered."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pvd.design.builder import build_design              # noqa: E402
from pvd.model import Config                             # noqa: E402
from pvd.parts.payloads import PAYLOADS                  # noqa: E402
from pvd.patient.gate import run_gate                    # noqa: E402
from pvd.seqops import CODONS, translate                 # noqa: E402

CODON_FOR = {}
for _c, _a in CODONS.items():
    CODON_FOR.setdefault(_a, _c)


def make_cds(n_aa, filler="GCT"):
    """ATG + n_aa-1 filler codons + TAA translates to n_aa residues."""
    return "ATG" + filler * (n_aa - 1) + "TAA"


def mutate(cds, pos, aa):
    i = (pos - 1) * 3
    return cds[:i] + CODON_FOR[aa] + cds[i + 3:]


def cfg_for(payload, patient, reference, **kw):
    base = dict(program=PAYLOADS[payload]["arm"], payload=payload,
                patient_seq=patient, reference_seq=reference)
    base.update(kw)
    return Config(**base)


REF = make_cds(PAYLOADS["LAMP2A"]["aa"])


def test_reference_translates_to_library_length():
    assert len(translate(REF)) == PAYLOADS["LAMP2A"]["aa"] == 410


def test_identical_allele_uses_reference():
    g = run_gate(cfg_for("LAMP2A", REF, REF), "LAMP2A")
    assert g.allele == "reference" and not g.variants


def test_tail_variant_benign_is_eligible():
    pat = mutate(REF, 402, "K")
    g = run_gate(cfg_for("LAMP2A", pat, REF, sex="female",
                         classifications={"A402K": "benign"}), "LAMP2A")
    assert g.allele == "patient", g.findings
    assert g.variants[0].region == "isoform-specific"
    assert g.tier == "n-of-1"          # no bin supplied


def test_bin_match_gives_binned_tier():
    pat = mutate(REF, 402, "K")
    g = run_gate(cfg_for("LAMP2A", pat, REF, sex="female",
                         classifications={"A402K": "benign"},
                         bins={"BIN-01": ["A402K"]}), "LAMP2A")
    assert g.tier == "binned" and g.bin_id == "BIN-01"


def test_shared_lumenal_variant_is_blocked():
    pat = mutate(REF, 120, "W")
    g = run_gate(cfg_for("LAMP2A", pat, REF, sex="female",
                         classifications={"A120W": "benign"}), "LAMP2A")
    assert g.allele == "reference"
    assert any("shared-lumenal" in t for _l, t in g.findings)


def test_unclassified_variant_is_blocked():
    pat = mutate(REF, 402, "K")
    g = run_gate(cfg_for("LAMP2A", pat, REF, sex="female"), "LAMP2A")
    assert g.allele == "reference"


def test_hemizygous_male_falls_back_to_reference():
    pat = mutate(REF, 402, "K")
    g = run_gate(cfg_for("LAMP2A", pat, REF, sex="male",
                         classifications={"A402K": "benign"}), "LAMP2A")
    assert g.allele == "reference"
    assert any("X-linked" in t for _l, t in g.findings)


def test_watch_list_position_is_blocked():
    pat = mutate(REF, 93, "R")
    g = run_gate(cfg_for("LAMP2A", pat, REF, sex="female",
                         classifications={"A93R": "benign"}), "LAMP2A")
    assert g.allele == "reference"
    assert any("watch list" in t for _l, t in g.findings)


def test_length_mismatch_refuses_to_align():
    g = run_gate(cfg_for("LAMP2A", make_cds(300), REF, sex="female"), "LAMP2A")
    assert g.allele == "reference"
    assert any("length difference" in t for _l, t in g.findings)


def test_dnajb6_gf_domain_variant_is_blocked():
    ref = make_cds(PAYLOADS["DNAJB6b"]["aa"])
    pat = mutate(ref, 85, "W")
    g = run_gate(cfg_for("DNAJB6b", pat, ref, classifications={"A85W": "benign"}), "DNAJB6b")
    assert g.allele == "reference"
    assert any("gf-domain" in t for _l, t in g.findings)


def test_synthetic_payload_has_no_allele_and_checks_epitope():
    snca_ref = make_cds(140)
    snca_pat = mutate(snca_ref, 91, "D")
    c = Config(program="barrier", payload="VH14-PEST",
               target_seq=snca_pat, target_reference=snca_ref)
    g = run_gate(c, "VH14-PEST")
    assert g.allele == "n/a"
    assert [v.pos for v in g.epitope] == [91]
    assert any("NAC32" in t for _l, t in g.findings)      # alternative offered


def test_synthetic_payload_never_borrows_the_reference_allele():
    """A barrier vector must not pick up the payload-gene FASTA as its insert."""
    c = Config(program="barrier", payload="VH14-PEST", reference_seq=REF, patient_seq=REF)
    d = build_design(c)
    goi = next(f for f in d.features if f.id == "goi")
    assert set(goi.seq) == {"N"}
    assert goi.length == PAYLOADS["VH14-PEST"]["cds"]


def test_aav_capacity_error_for_an_oversized_pair():
    """DNAJB1 + HSPH1 is 3.6 kb of CDS; HSPH1 alone still fits, sc does not."""
    ref = make_cds(PAYLOADS["HSPH1"]["aa"])
    d = build_design(cfg_for("HSPH1", ref, ref, sc=True))
    assert any(l == "error" and "packaging limit" in t for l, t in d.messages)


def test_php_eb_is_flagged_as_mouse_only():
    d = build_design(cfg_for("LAMP2A", REF, REF, capsid="AAV-PHP.eB"))
    assert any(l == "error" and "LY6A" in t for l, t in d.messages)
