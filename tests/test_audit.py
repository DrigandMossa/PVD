"""Regression tests for the findings of the 2026-11-22 audit.

Each test here failed before its fix. They are kept together because they share a
theme: every one is a place where the tool gave a confident answer that was wrong,
rather than crashing. A crash gets noticed; a plausible wrong recommendation does not.
"""

from pvd.cli.example import _make_cds, _mutate
from pvd.design.builder import build_design
from pvd.model import Config
from pvd.parts.payloads import PAYLOADS, TARGET
from pvd.patient import epitope as epi
from pvd.patient.gate import run_gate

SNCA_REF = _make_cds(TARGET["aa"], seed=23)
LAMP_REF = _make_cds(PAYLOADS["LAMP2A"]["aa"], seed=11)


def _levels(findings, text):
    return [lvl for lvl, msg in findings if text.lower() in msg.lower()]


# --------------------------------------------------------------- finding A
# alternative_payloads judged candidates against the hits inside the *current*
# payload's window only, so a variant that fell outside it was invisible - even
# when it sat squarely inside the window of the binder being recommended.

def test_alternative_binder_is_rejected_when_its_own_epitope_is_hit():
    vh_lo, vh_hi = PAYLOADS["VH14-PEST"]["epitope"]      # 61-95
    n32_lo, n32_hi = PAYLOADS["NAC32"]["epitope"]        # 53-87
    # 91 is inside VH14 only; 58 is inside NAC32 only. Both binders are compromised.
    assert vh_lo <= 91 <= vh_hi and not (n32_lo <= 91 <= n32_hi)
    assert n32_lo <= 58 <= n32_hi and not (vh_lo <= 58 <= vh_hi)

    patient = _mutate(_mutate(SNCA_REF, 91, "D"), 58, "W")
    hits, every, _f = epi.verify("VH14-PEST", patient, SNCA_REF, {})

    assert [v.pos for v in hits] == [91]
    assert sorted(v.pos for v in every) == [58, 91], "verify must return every coding change"
    assert epi.alternative_payloads("VH14-PEST", hits, every) == [], \
        "NAC32 carries the 58 change and must not be offered"


def test_alternative_binder_is_offered_when_it_really_is_clear():
    patient = _mutate(SNCA_REF, 91, "D")                 # inside VH14 only
    hits, every, _f = epi.verify("VH14-PEST", patient, SNCA_REF, {})
    assert epi.alternative_payloads("VH14-PEST", hits, every) == ["NAC32"]


def test_gate_says_so_when_no_catalogue_binder_fits():
    patient = _mutate(_mutate(SNCA_REF, 91, "D"), 58, "W")
    g = run_gate(Config(program="barrier", payload="VH14-PEST",
                        target_seq=patient, target_reference=SNCA_REF), "VH14-PEST")
    assert "error" in _levels(g.findings, "no stocked barrier payload"), \
        "silence here reads as 'no alternative was considered'"
    # and it must not claim an alternative at the same time
    assert not _levels(g.findings, "contains none of this patient")


def test_out_of_window_changes_are_not_called_irrelevant():
    patient = _mutate(_mutate(SNCA_REF, 91, "D"), 58, "W")
    _h, _e, f = epi.verify("VH14-PEST", patient, SNCA_REF, {})
    joined = " ".join(m for _l, m in f).lower()
    assert "do not affect binder selection" not in joined, \
        "they are exactly what decides the alternative"


# --------------------------------------------------------------- finding B
# An X-linked gene with --sex unspecified warned that hemizygous males default to
# reference, and then delivered the patient allele anyway. The default path was the
# unsafe one, and the message described behaviour the code did not have.

def _lamp_gate(sex):
    patient = _mutate(LAMP_REF, 402, "K")                # isoform-specific tail
    label = "%s402K" % epi.translate(LAMP_REF)[401]
    return run_gate(Config(program="clearance", payload="LAMP2A", patient_seq=patient,
                           reference_seq=LAMP_REF, sex=sex,
                           classifications={label: "benign"},
                           bins={"BIN-01": [label]}), "LAMP2A")


def test_x_linked_with_unknown_sex_uses_the_reference_allele():
    g = _lamp_gate("unknown")
    assert g.allele == "reference", "unknown sex must not be treated as female"
    assert "error" in _levels(g.findings, "sex was not given")


def test_x_linked_male_still_blocked_and_female_still_eligible():
    assert _lamp_gate("male").allele == "reference"
    female = _lamp_gate("female")
    assert female.allele == "patient" and female.tier == "binned"


# --------------------------------------------------------------- finding C
# A patient file that cleaned to nothing - wrong path, protein FASTA, a binary -
# was reported as "no patient sequence supplied", at info level.

def test_unreadable_patient_input_is_not_reported_as_absent():
    g = run_gate(Config(program="clearance", payload="LAMP2A",
                        patient_seq="!!! ??? ^^^", reference_seq=LAMP_REF), "LAMP2A")
    assert "warn" in _levels(g.findings, "no a, c, g, t or n could be read")
    assert not _levels(g.findings, "no patient sequence supplied")


def test_genuinely_absent_patient_input_stays_informational():
    g = run_gate(Config(program="clearance", payload="LAMP2A",
                        patient_seq="", reference_seq=LAMP_REF), "LAMP2A")
    assert _levels(g.findings, "no patient sequence supplied") == ["info"]


# --------------------------------------------------------------- findings D, E
# --override goi was applied after the cassette was laid out, so the stop-codon
# decision and the feature label were both made against the pre-override insert.

def test_override_ending_in_a_stop_gets_no_second_stop():
    d = build_design(Config(program="barrier", payload="VH14-PEST",
                            overrides={"goi": "ATG" + "GCT" * 20 + "TAA"}))
    ids = [f.id for f in d.features]
    assert "stop" not in ids, "the construct already terminates; a second stop wastes 3 bp"
    goi = next(f for f in d.features if f.id == "goi")
    assert goi.seq.endswith("TAA")
    assert goi.length == 3 + 3 * 20 + 3 == 66


def test_override_without_a_stop_still_gets_one():
    d = build_design(Config(program="barrier", payload="VH14-PEST",
                            overrides={"goi": "ATG" + "GCT" * 20}))
    assert "stop" in [f.id for f in d.features]


def test_override_is_not_labelled_a_placeholder():
    d = build_design(Config(program="barrier", payload="VH14-PEST",
                            overrides={"goi": "ATG" + "GCT" * 20 + "TAA"}))
    goi = next(f for f in d.features if f.id == "goi")
    assert "typical length" not in goi.name, "the label is exported to GenBank /label="
    assert "supplied construct" in goi.name
    assert goi.custom is True
