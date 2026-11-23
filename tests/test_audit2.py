"""Regression tests for the second audit round.

The first round covered the gate and the builder. This round covered the region
mapping and the CLI, and found the worst bug in the program: a single mistyped
numeric flag silently disabled a hard safety exclusion and the tool reported
success.
"""

import pytest

from pvd.cli.example import _make_cds, _mutate
from pvd.cli.run import main
from pvd.design.builder import resolve_parts
from pvd.model import Config
from pvd.parts.payloads import PAYLOADS, payload_regions, region_of, shared_end_applies
from pvd.patient.gate import run_gate
from pvd.seqops import translate

LAMP_REF = _make_cds(PAYLOADS["LAMP2A"]["aa"], seed=11)


# --------------------------------------------------------------- finding G
# payload_regions applied any shared_end it was given. A negative value produced
# (1, -375) and (-374, 410): the first region matched no position, the second
# matched every position, so every variant was relabelled isoform-specific and the
# shared-lumenal exclusion stopped firing. With the variant classified benign, the
# gate went from "reference" to "patient" - a Danon-relevant region delivered.

@pytest.mark.parametrize("bad", [-375, -1, 0 - 410, 410, 411, 5000])
def test_out_of_range_shared_end_is_rejected(bad):
    if bad == 0:
        pytest.skip("0 means 'no override'")
    with pytest.raises(ValueError, match="out of range"):
        payload_regions("LAMP2A", bad)


def test_negative_shared_end_cannot_relabel_a_shared_lumenal_variant():
    with pytest.raises(ValueError):
        region_of("LAMP2A", 120, -375)


def test_shared_lumenal_variant_stays_blocked_whatever_the_classification():
    patient = _mutate(LAMP_REF, 120, "W")
    label = "%s120W" % translate(LAMP_REF)[119]
    cfg = Config(program="clearance", payload="LAMP2A", patient_seq=patient,
                 reference_seq=LAMP_REF, sex="female",
                 classifications={label: "benign"})
    # honest run: blocked by the region rule even though the variant is benign
    assert run_gate(cfg, "LAMP2A").allele == "reference"
    # and the override cannot be used to move it out of that region
    with pytest.raises(ValueError):
        run_gate(cfg, "LAMP2A", -375)


def test_valid_shared_end_still_works():
    regions = payload_regions("LAMP2A", 300)
    assert regions == [(1, 300, "shared-lumenal"), (301, 410, "isoform-specific")]
    assert region_of("LAMP2A", 120, 300) == "shared-lumenal"
    assert region_of("LAMP2A", 350, 300) == "isoform-specific"


def test_boundary_values_are_accepted():
    assert payload_regions("LAMP2A", 1)[0] == (1, 1, "shared-lumenal")
    assert payload_regions("LAMP2A", 409)[1] == (410, 410, "isoform-specific")


# --------------------------------------------------------------- finding I
# --shared-end was silently discarded for a payload with no shared/isoform
# boundary, so the user believed a safety-relevant override had applied.

def test_shared_end_that_cannot_apply_is_reported_not_dropped():
    assert shared_end_applies("LAMP2A") is True
    assert shared_end_applies("DNAJB6b") is False
    g = run_gate(Config(program="chaperone", payload="DNAJB6b"), "DNAJB6b", 50)
    assert any(lvl == "warn" and "was ignored" in msg for lvl, msg in g.findings)


def test_dnajb6b_region_map_is_untouched_by_the_override():
    assert payload_regions("DNAJB6b", 50) == PAYLOADS["DNAJB6b"]["regions"]
    assert region_of("DNAJB6b", 89, 50) == "gf-domain", "the LGMD1D rule must still fire"


# ----------------------------------------------------------- findings M, N
# --gate validated only the gate, so a payload on the wrong arm or a misspelt
# capsid gave a clean report and exit 0 while the real build rejected it. A dry
# run that passes where the real run fails is worse than no dry run.

@pytest.mark.parametrize("argv", [
    ["--program", "clearance", "--payload", "DNAJB6b", "--gate"],
    ["--capsid", "NOPE", "--gate"],
    ["--promoter", "NOPE", "--gate"],
    ["--polya", "NOPE", "--gate"],
    ["--detarget", "NOPE", "--gate"],
])
def test_gate_mode_rejects_what_the_build_would_reject(argv, capsys):
    assert main(argv) == 2
    capsys.readouterr()


def test_gate_mode_still_succeeds_on_a_valid_command(capsys):
    assert main(["--program", "clearance", "--payload", "LAMP2A", "--gate"]) == 0
    capsys.readouterr()


def test_resolve_parts_is_the_single_source_of_truth():
    program, payload, capsid, prom, polya, detarget = resolve_parts(
        Config(program="clearance", payload="LAMP2A"))
    assert (program, payload) == ("clearance", "LAMP2A")
    assert capsid in PAYLOADS or capsid == "TfR1-CapX"
    assert prom and polya
    with pytest.raises(ValueError, match="belongs to the chaperone arm"):
        resolve_parts(Config(program="clearance", payload="DNAJB6b"))
