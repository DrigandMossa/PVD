"""Mode dispatch and the process entry point."""

import os
import sys
from dataclasses import replace
from typing import List, Optional

from ..design.builder import build_design, resolve_parts
from ..export.files import write_outputs
from ..export.gatereport import to_gate_report
from ..gui import launch_gui
from ..model import Config, Design
from ..parts.programs import PROGRAMS, REGIMENS
from ..patient.gate import run_gate
from .args import build_parser, config_from_args, print_catalog
from .example import write_example
from .wizard import wizard


def report(d: Design, paths: List[str]) -> None:
    print("\n%s  |  %s bp  |  %s arm  |  payload %s" % (d.name, format(d.total, ","), d.program, d.payload))
    if d.gate:
        print("allele: %s   tier: %s%s" % (d.gate.allele, d.gate.tier,
                                           ("  bin %s" % d.gate.bin_id) if d.gate.bin_id else ""))
    print("-" * 70)
    for f in d.features:
        print("%-10s %5d..%-6d %6d bp  %s" % (f.id, f.start, f.end, f.length, f.name))
    print("\nDesign checks")
    for level, text in d.messages:
        print("  [%s] %s" % (level, text))
    if paths:
        print("\nFiles written:")
        for p in paths:
            print("  " + p)


def _build_one(cfg: Config, program: str, payload: str, out: str, shared_end: int,
               gate_only: bool) -> Design:
    if program not in PROGRAMS:
        raise ValueError("Unknown program %r. Choose from: %s" % (program, ", ".join(PROGRAMS)))
    payload = payload or PROGRAMS[program]["default"]
    cfg = replace(cfg, program=program, payload=payload)
    if gate_only:
        # Validate the catalogue choices even though no cassette is laid out, so --gate
        # rejects anything the build would reject. A dry run that passes where the real
        # run fails is worse than no dry run.
        resolve_parts(cfg)
        gate = run_gate(cfg, payload, shared_end)
        design = Design(cfg.name or payload, program, payload, cfg.capsid, [], "", list(gate.findings), gate)
        print(to_gate_report(design, shared_end))
        return design
    design = build_design(cfg, shared_end)
    paths = write_outputs(design, out, shared_end)
    report(design, paths)
    return design


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    no_arguments = argv is None and len(sys.argv) == 1
    args = parser.parse_args(argv)

    if args.list:
        print_catalog()
        return 0
    if args.example:
        try:
            paths = write_example(args.example)
        except OSError as exc:
            print("Error: %s" % exc, file=sys.stderr)
            return 2
        print("Wrote an example patient set to %s:" % args.example)
        for p in paths:
            print("  " + p)
        print("\nStart with %s" % os.path.join(args.example, "README.txt"))
        return 0

    wizard_mode = args.wizard
    if not wizard_mode and not args.gate and (args.gui or no_arguments):
        status = launch_gui()
        if status == 0 or args.gui:
            return status
        print("Falling back to text prompts.\n", file=sys.stderr)
        wizard_mode = True

    try:
        if wizard_mode:
            cfg, out = wizard()
        else:
            cfg, out = config_from_args(args), args.out

        designs: List[Design] = []
        if args.regimen:
            if args.regimen not in REGIMENS:
                raise ValueError("Unknown regimen %r. Choose from: %s" % (args.regimen, ", ".join(REGIMENS)))
            R = REGIMENS[args.regimen]
            print("Regimen: %s\n%s\n" % (R["name"], R["tip"]))
            from ..parts.payloads import PAYLOADS
            for payload in R["payloads"]:
                arm = PAYLOADS[payload]["arm"]
                print("\n=== %s (%s arm) ===" % (payload, arm))
                sub = replace(cfg, name="")
                designs.append(_build_one(sub, arm, payload, out, args.shared_end, args.gate))
        else:
            designs.append(_build_one(cfg, cfg.program, cfg.payload, out, args.shared_end, args.gate))
    except (ValueError, OSError) as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.", file=sys.stderr)
        return 130

    if args.strict and any(level == "error" for d in designs for level, _ in d.messages):
        return 1
    return 0
