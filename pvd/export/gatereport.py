"""The eligibility-gate transcript: why this allele, in this tier, for this patient."""

from typing import List

from ..model import Design
from ..parts.payloads import PAYLOADS, TARGET
from ..patient.gate import gate_lines

RULES = [
    "the payload is a human gene the patient actually carries (not a synthetic binder)",
    "a reference CDS was supplied and both translate to the same length",
    "at least one coding difference exists (otherwise reference is the same molecule)",
    "no difference falls in a region the payload's rule excludes",
    "the gene is not X-linked in a male patient carrying a coding variant",
    "every difference carries an explicit benign or likely-benign classification",
]


def to_gate_report(d: Design, shared_end: int = 0) -> str:
    g = d.gate
    title = "Eligibility gate - %s" % d.name
    out: List[str] = [title, "=" * len(title), ""]
    if g is None:
        return "\n".join(out + ["No gate was run for this design.", ""]) + "\n"

    out += gate_lines(g, shared_end) + ["", "Decision trail"]
    for level, text in g.findings:
        out.append("  [%s] %s" % (level, text))

    p = PAYLOADS[g.payload]
    out += ["", "Rules applied", "A patient allele is delivered only when all of these hold:"]
    out += ["  %d. %s" % (i, r) for i, r in enumerate(RULES, 1)]
    out += ["", "Unclassified means reference. Without that rule, 'patient-derived' would mean",
            "'risk-allele-amplifying' for some fraction of patients."]

    out += ["", "Payload reference", "  Gene:    %s (%s)" % (p["gene"], p["locus"]),
            "  RefSeq:  %s" % p["refseq"],
            "  CDS:     %s bp / %d aa%s"
            % (format(p["cds"], ","), p["aa"], "" if p.get("verified_length") else "  (approximate)")]
    if p.get("epitope"):
        out.append("  Epitope: %s residues %d-%d" % (p.get("epitope_name", ""), p["epitope"][0], p["epitope"][1]))
        out.append("  Target:  %s, %s bp / %d aa. %s"
                   % (TARGET["gene"], format(TARGET["cds"], ","), TARGET["aa"], TARGET["note"]))

    out += ["", "Region boundaries in the library are approximate: they route a variant to the right",
            "rule but are not a substitute for the RefSeq exon table. Confirm them, or override with",
            "--shared-end, before any use beyond design.", ""]
    return "\n".join(out) + "\n"
