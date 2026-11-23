"""Verify that a barrier payload's epitope is intact in this patient's SNCA.

An intrabody is a selected synthetic binder, so there is no patient version of it to
insert.  The patient's sequence still decides whether the stock binder will work: a coding
variant inside the epitope can cost it its target.  This is the highest-value use of the
same sequencing data and it is cheap.
"""

from typing import Dict, List, Optional, Tuple

from ..model import Variant
from ..parts.payloads import PAYLOADS, TARGET
from ..seqops import translate


def verify(payload: str, patient_snca: str, reference_snca: str,
           classifications: Dict[str, str]
           ) -> Tuple[List[Variant], List[Variant], List[Tuple[str, str]]]:
    """Return (hits_in_window, all_coding_variants, findings).

    The second list matters: a variant outside *this* binder's window can sit inside
    another binder's, so choosing an alternative needs every coding change, not just
    the ones that compromise the current payload.
    """
    findings: List[Tuple[str, str]] = []
    window = PAYLOADS[payload].get("epitope")
    if not window:
        return [], [], findings
    lo, hi = window
    name = PAYLOADS[payload].get("epitope_name", "epitope")

    if not patient_snca or not reference_snca:
        findings.append(("warn", "No patient %s sequence supplied, so the %s (residues %d-%d) could not be "
                         "verified. A coding variant there can cost the binder its target: sequence %s "
                         "before dosing, not after."
                         % (TARGET["gene"], name, lo, hi, TARGET["gene"])))
        return [], [], findings

    p_prot, r_prot = translate(patient_snca), translate(reference_snca)
    if len(r_prot) != TARGET["aa"]:
        findings.append(("warn", "%s reference translates to %d residues; expected %d."
                         % (TARGET["gene"], len(r_prot), TARGET["aa"])))
    if len(p_prot) != len(r_prot):
        findings.append(("error", "Patient %s is %d residues and the reference is %d; epitope positions "
                         "cannot be compared across a length difference."
                         % (TARGET["gene"], len(p_prot), len(r_prot))))
        return [], [], findings

    hits: List[Variant] = []
    everything: List[Variant] = []
    for i, (r_aa, p_aa) in enumerate(zip(r_prot, p_prot), start=1):
        if r_aa == p_aa:
            continue
        inside = lo <= i <= hi
        v = Variant(pos=i, ref_aa=r_aa, alt_aa=p_aa, region="epitope" if inside else "other")
        v.classification = classifications.get(v.label, "unclassified")
        everything.append(v)
        if inside:
            hits.append(v)
    outside = len(everything) - len(hits)

    if hits:
        findings.append(("error", "Patient %s carries %d coding change(s) inside the %s: %s. The stock "
                         "binder may bind this patient's alpha-synuclein poorly. Re-select or re-engineer "
                         "the binder, or choose a payload whose epitope is intact."
                         % (TARGET["gene"], len(hits), name, ", ".join(v.label for v in hits))))
    else:
        findings.append(("info", "%s %s (residues %d-%d) is intact in this patient: the stock binder's "
                         "epitope is unchanged." % (TARGET["gene"], name, lo, hi)))
    if outside:
        findings.append(("info", "%d coding change(s) in %s lie outside the %s, so they do not compromise "
                         "this binder. They are still weighed when suggesting an alternative, because "
                         "another binder's window may contain them: %s."
                         % (outside, TARGET["gene"], name,
                            ", ".join(v.label for v in everything if v not in hits))))
    return hits, everything, findings


def alternative_payloads(payload: str, hits: List[Variant],
                         all_variants: Optional[List[Variant]] = None) -> List[str]:
    """Other barrier payloads whose epitope window contains none of the patient's changes.

    Judged against *every* coding change in the target, not only the ones inside the
    current payload's window. Checking the hits alone would recommend a binder whose own
    epitope carries a variant that simply fell outside the window being reported on - the
    exact failure the epitope check exists to prevent.
    """
    if not hits:
        return []
    considered = hits if all_variants is None else all_variants
    out = []
    for key, p in PAYLOADS.items():
        if key == payload or p["arm"] != "barrier" or not p.get("epitope"):
            continue
        lo, hi = p["epitope"]
        if all(not (lo <= v.pos <= hi) for v in considered):
            out.append(key)
    return out
