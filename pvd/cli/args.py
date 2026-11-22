"""Argument parsing, the catalogue listing, and Config construction."""

import argparse
from typing import List

from ..model import Config
from ..parts.elements import CAPSIDS, DETARGET, POLYA, PROMOTERS
from ..parts.payloads import PAYLOADS, TARGET
from ..parts.programs import PROGRAMS, REGIMENS
from ..patient.parse import read_arg, read_bins, read_classifications
from ..version import __version__


def print_catalog() -> None:
    print("Arms and their payloads:")
    for k, v in PROGRAMS.items():
        print("  %-10s %s\n             payloads: %s (default %s)\n             %s"
              % (k, v["name"], ", ".join(v["payloads"]), v["default"], v["tip"]))
    print("\nTwo-vector regimens (--regimen):")
    for k, v in REGIMENS.items():
        print("  %-14s %s\n                 %s" % (k, v["name"], v["tip"]))
    print("\nPayload library:")
    for k, p in PAYLOADS.items():
        flag = "synthetic" if p["synthetic"] else p["locus"]
        approx = "" if p.get("verified_length") else " approx"
        print("  %-11s %-10s %-9s %5s bp / %4d aa%s   %s"
              % (k, p["arm"], flag, format(p["cds"], ","), p["aa"], approx, p["refseq"]))
    print("\nTarget for epitope checks: %s, %s bp / %d aa. NAC %d-%d."
          % (TARGET["gene"], format(TARGET["cds"], ","), TARGET["aa"], TARGET["nac"][0], TARGET["nac"][1]))
    print("\nCapsids:")
    for k, c in CAPSIDS.items():
        print("  %-13s %-14s %s" % (k, c["receptor"], c["route"]))
    for label, opts in (("Promoters", PROMOTERS), ("PolyA", POLYA), ("Detargeting", DETARGET)):
        print("%s: %s" % (label, ", ".join(opts)))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pvd",
        description="Patient-sequence driven AAV vector designer for Parkinson's proteostasis programs.",
        epilog="Run with no arguments to open the graphical window. Use --list to see the catalogue.")
    p.add_argument("--gui", action="store_true", help="open the graphical window (the default with no arguments)")
    p.add_argument("--wizard", action="store_true", help="answer text prompts instead of using the window")
    p.add_argument("--list", action="store_true", help="list arms, payloads, capsids and parts, then exit")
    p.add_argument("--gate", action="store_true",
                   help="run the eligibility gate and print the decision trail without building a vector")

    p.add_argument("--program", default="clearance", help="clearance, barrier or chaperone (default: clearance)")
    p.add_argument("--payload", default="", help="payload key (default depends on the arm)")
    p.add_argument("--regimen", default="",
                   help="build a whole two-vector regimen: " + ", ".join(REGIMENS))

    p.add_argument("--patient", default="", metavar="FILE",
                   help="patient CDS for the payload gene, as a FASTA/text file or a sequence")
    p.add_argument("--reference", default="", metavar="FILE", help="reference CDS for the payload gene")
    p.add_argument("--target", default="", metavar="FILE",
                   help="patient SNCA CDS, for barrier epitope verification")
    p.add_argument("--target-reference", default="", metavar="FILE", help="reference SNCA CDS")
    p.add_argument("--classify", default="", metavar="FILE",
                   help="TSV of 'variant<TAB>classification' (benign, likely-benign, vus, "
                        "likely-pathogenic, pathogenic); unclassified variants fail the gate")
    p.add_argument("--bins", default="", metavar="FILE",
                   help="TSV of 'bin_id<TAB>variant[,variant...]' defining the qualified haplotype panel")
    p.add_argument("--sex", default="unknown", choices=["male", "female", "unknown"],
                   help="patient sex; hemizygous males default to the reference allele for X-linked genes")
    p.add_argument("--route", default="in-vivo", choices=["in-vivo", "autologous"],
                   help="in-vivo vector, or autologous ex vivo engineering of the patient's own cells")
    p.add_argument("--shared-end", type=int, default=0, metavar="N",
                   help="override the last residue of the shared region in the payload's region map")

    p.add_argument("--capsid", default="TfR1-CapX", help="capsid (default: TfR1-CapX)")
    p.add_argument("--promoter", help="promoter (default depends on the arm)")
    p.add_argument("--polya", help="polyadenylation signal: synthetic, bGH, SV40 or none")
    p.add_argument("--detarget", default="miR-122x2",
                   help="comma-separated detargeting cassettes, or 'none' (default: miR-122x2)")
    p.add_argument("--riboswitch", action="store_true", help="add the K19 tetracycline riboswitch")
    p.add_argument("--sc", action="store_true",
                   help="self-complementary AAV; halves the packaging capacity to about 2.4 kb")
    p.add_argument("--no-kozak", action="store_true", help="leave out the Kozak sequence")
    p.add_argument("--override", action="append", default=[], metavar="ID=SEQ",
                   help="replace a placeholder element with a verified sequence or file (repeatable)")

    p.add_argument("--name", default="", help="vector name (default: generated)")
    p.add_argument("--out", default=".", help="output folder (default: current folder)")
    p.add_argument("--example", metavar="DIR",
                   help="write a runnable example patient set to DIR and exit")
    p.add_argument("--strict", action="store_true", help="exit with status 1 if any design check reports an error")
    p.add_argument("--version", action="version", version="%(prog)s " + __version__)
    return p


def _detarget_list(raw: str) -> List[str]:
    if not raw or raw.strip().lower() in ("none", "off", ""):
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def config_from_args(a: argparse.Namespace) -> Config:
    overrides = {}
    for item in a.override:
        if "=" not in item:
            raise ValueError("--override needs ID=SEQUENCE, got %r" % item)
        key, val = item.split("=", 1)
        overrides[key.strip()] = read_arg(val.strip())
    return Config(program=a.program, payload=a.payload, capsid=a.capsid,
                  promoter=a.promoter, polya=a.polya, kozak=not a.no_kozak, sc=a.sc,
                  detarget=_detarget_list(a.detarget), riboswitch=a.riboswitch,
                  route=a.route, sex=a.sex,
                  patient_seq=read_arg(a.patient), reference_seq=read_arg(a.reference),
                  target_seq=read_arg(a.target), target_reference=read_arg(a.target_reference),
                  classifications=read_classifications(a.classify), bins=read_bins(a.bins),
                  name=a.name, overrides=overrides)
