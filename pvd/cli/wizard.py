"""Text prompts, for when the graphical window is unavailable."""

from typing import Tuple

from ..model import Config
from ..parts.elements import CAPSIDS, PROMOTERS
from ..parts.payloads import PAYLOADS
from ..parts.programs import PROGRAMS
from ..patient.parse import read_arg, read_bins, read_classifications


def _ask(label: str, default: str = "") -> str:
    prompt = "%s%s: " % (label, " [%s]" % default if default else "")
    return input(prompt).strip() or default


def _ask_choice(label: str, options, default: str) -> str:
    print("  %s" % ", ".join(options))
    while True:
        value = _ask(label, default)
        for opt in options:
            if str(opt).lower() == value.lower():
                return opt
        print("  Not one of the options.")


def _ask_bool(label: str, default: bool = False) -> bool:
    value = _ask("%s (y/n)" % label, "y" if default else "n").lower()
    return value.startswith("y")


def _ask_path(label: str, reader=read_arg, default: str = "") -> str:
    """Prompt until the answer is usable, rather than aborting the whole session.

    read_arg now rejects a path that does not exist instead of treating it as a
    sequence. Letting that propagate would discard every answer given so far over
    one typo near the end of the run.
    """
    while True:
        value = _ask(label, default)
        try:
            return reader(value)
        except (ValueError, OSError) as exc:
            print("  %s" % exc)


def wizard() -> Tuple[Config, str]:
    print("pvd - patient-sequence driven vector designer\n")
    program = _ask_choice("Arm", list(PROGRAMS), "clearance")
    payloads = PROGRAMS[program]["payloads"]
    payload = _ask_choice("Payload", payloads, PROGRAMS[program]["default"])
    p = PAYLOADS[payload]
    print("\n%s\n" % p["note"])

    patient = reference = target = target_ref = ""
    if p["synthetic"]:
        print("%s is a synthetic binder: there is no patient allele to insert." % payload)
        print("Supply the patient's SNCA to verify the epitope (residues %d-%d)." % p["epitope"])
        target = _ask_path("Patient SNCA CDS (file or sequence)")
        target_ref = _ask_path("Reference SNCA CDS (file or sequence)")
    else:
        print("Reference to fetch for %s: %s" % (payload, p["refseq"]))
        patient = _ask_path("Patient %s CDS (file or sequence, blank to skip the gate)" % p["gene"])
        if patient:
            reference = _ask_path("Reference %s CDS (file or sequence)" % p["gene"])

    classify = _ask_path("Classification TSV (blank for none; unclassified variants fail the gate)",
                         read_classifications)
    bins = _ask_path("Haplotype bin TSV (blank for none)", read_bins)
    sex = _ask_choice("Patient sex", ["male", "female", "unknown"], "unknown")
    route = _ask_choice("Route", ["in-vivo", "autologous"], "in-vivo")

    capsid = _ask_choice("Capsid", list(CAPSIDS), "TfR1-CapX")
    promoter = _ask_choice("Promoter", list(PROMOTERS), PROGRAMS[program]["promoter"])
    detarget = _ask("Detargeting cassettes, comma separated or none", "miR-122x2")
    riboswitch = _ask_bool("Add the K19 riboswitch", False)
    name = _ask("Vector name (blank to generate)")
    out = _ask("Output folder", ".")

    cfg = Config(program=program, payload=payload, capsid=capsid, promoter=promoter,
                 detarget=[] if detarget.lower() in ("none", "") else
                 [x.strip() for x in detarget.split(",") if x.strip()],
                 riboswitch=riboswitch, route=route, sex=sex,
                 patient_seq=patient, reference_seq=reference,
                 target_seq=target, target_reference=target_ref,
                 classifications=classify, bins=bins,
                 name=name)
    return cfg, out
