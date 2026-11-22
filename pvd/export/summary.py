"""Human-readable text summary of a design."""

from ..model import Design
from ..parts.programs import PROGRAMS


def to_summary(d: Design) -> str:
    lines = [d.name, "=" * len(d.name),
             "Arm: %s" % PROGRAMS[d.program]["name"],
             "Payload: %s    Capsid: %s    Size: %s bp" % (d.payload, d.capsid, format(d.total, ",")),
             ""]
    if d.gate:
        lines += ["Allele delivered: %s    Tier: %s%s"
                  % (d.gate.allele, d.gate.tier, (" [%s]" % d.gate.bin_id) if d.gate.bin_id else ""), ""]
    lines += ["%-10s %-14s %7s  %s" % ("id", "position", "bp", "element")]
    for f in d.features:
        note = "  (your sequence)" if f.custom or (f.seq and "N" not in f.seq and f.id == "goi") else ""
        lines.append("%-10s %-14s %7d  %s%s" % (f.id, "%d..%d" % (f.start, f.end), f.length, f.name, note))
    lines += ["", "Design checks"] + ["  [%s] %s" % (lv, tx) for lv, tx in d.messages]
    if d.basis:
        lines += ["", "Design basis", d.basis]
    lines += ["",
              "Elements written as N have a typical length only. Supply verified sequences with",
              "--override ID=SEQUENCE (ids are in the first column), --reference for the payload CDS,",
              "or --override goi=FILE for a synthetic construct.",
              "",
              "Research design tool. Producing virus requires institutional biosafety approval; a",
              "clinical product requires GMP manufacturing, preclinical safety data and regulatory",
              "authorization."]
    return "\n".join(lines) + "\n"
