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
        target = _ask("Patient SNCA CDS (file or sequence)")
        target_ref = _ask("Reference SNCA CDS (file or sequence)")
    else:
        print("Reference to fetch for %s: %s" % (payload, p["refseq"]))
        patient = _ask("Patient %s CDS (file or sequence, blank to skip the gate)" % p["gene"])
        if patient:
            reference = _ask("Reference %s CDS (file or sequence)" % p["gene"])

    classify = _ask("Classification TSV (blank for none; unclassified variants fail the gate)")
    bins = _ask("Haplotype bin TSV (blank for none)")
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
                 patient_seq=read_arg(patient), reference_seq=read_arg(reference),
                 target_seq=read_arg(target), target_reference=read_arg(target_ref),
                 classifications=read_classifications(classify), bins=read_bins(bins),
                 name=name)
    return cfg, out
