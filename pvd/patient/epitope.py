"""Verify that a barrier payload's epitope is intact in this patient's SNCA.

An intrabody is a selected synthetic binder, so there is no patient version of it to
insert.  The patient's sequence still decides whether the stock binder will work: a coding
variant inside the epitope can cost it its target.  This is the highest-value use of the
same sequencing data and it is cheap.
"""

from typing import Dict, List, Tuple

from ..model import Variant
from ..parts.payloads import PAYLOADS, TARGET
from ..seqops import translate


def verify(payload: str, patient_snca: str, reference_snca: str,
           classifications: Dict[str, str]) -> Tuple[List[Variant], List[Tuple[str, str]]]:
    """Return (epitope_variants, findings) for the payload's epitope window."""
    findings: List[Tuple[str, str]] = []
    window = PAYLOADS[payload].get("epitope")
    if not window:
        return [], findings
    lo, hi = window
    name = PAYLOADS[payload].get("epitope_name", "epitope")

    if not patient_snca or not reference_snca:
        findings.append(("warn", "No patient %s sequence supplied, so the %s (residues %d-%d) could not be "
                         "verified. A coding variant there can cost the binder its target: sequence %s "
                         "before dosing, not after."
                         % (TARGET["gene"], name, lo, hi, TARGET["gene"])))
        return [], findings

    p_prot, r_prot = translate(patient_snca), translate(reference_snca)
    if len(r_prot) != TARGET["aa"]:
        findings.append(("warn", "%s reference translates to %d residues; expected %d."
                         % (TARGET["gene"], len(r_prot), TARGET["aa"])))
    if len(p_prot) != len(r_prot):
        findings.append(("error", "Patient %s is %d residues and the reference is %d; epitope positions "
                         "cannot be compared across a length difference."
                         % (TARGET["gene"], len(p_prot), len(r_prot))))
        return [], findings

    hits: List[Variant] = []
    outside = 0
    for i, (r_aa, p_aa) in enumerate(zip(r_prot, p_prot), start=1):
        if r_aa == p_aa:
            continue
        if lo <= i <= hi:
            v = Variant(pos=i, ref_aa=r_aa, alt_aa=p_aa, region="epitope")
            v.classification = classifications.get(v.label, "unclassified")
            hits.append(v)
        else:
            outside += 1

    if hits:
        findings.append(("error", "Patient %s carries %d coding change(s) inside the %s: %s. The stock "
                         "binder may bind this patient's alpha-synuclein poorly. Re-select or re-engineer "
                         "the binder, or choose a payload whose epitope is intact."
                         % (TARGET["gene"], len(hits), name, ", ".join(v.label for v in hits))))
    else:
        findings.append(("info", "%s %s (residues %d-%d) is intact in this patient: the stock binder's "
                         "epitope is unchanged." % (TARGET["gene"], name, lo, hi)))
    if outside:
        findings.append(("info", "%d coding change(s) in %s lie outside the epitope window and do not "
                         "affect binder selection." % (outside, TARGET["gene"])))
    return hits, findings


def alternative_payloads(payload: str, hits: List[Variant]) -> List[str]:
    """Other barrier payloads whose epitope window misses every hit."""
    if not hits:
        return []
    out = []
    for key, p in PAYLOADS.items():
        if key == payload or p["arm"] != "barrier" or not p.get("epitope"):
            continue
        lo, hi = p["epitope"]
        if all(not (lo <= v.pos <= hi) for v in hits):
            out.append(key)
    return out
