"""Amino-acid level comparison of a patient CDS against a reference CDS.

Only coding differences matter.  Synonymous variants produce no new peptide, so matching
the patient's codons buys nothing immunologically and costs the codon optimisation of the
cassette; pvd therefore compares translations, not nucleotides, and reports the synonymous
count for information only.
"""

from typing import Dict, List, Tuple

from ..model import Variant
from ..parts.payloads import PAYLOADS, region_of
from ..seqops import CODONS, translate


def call_variants(patient: str, reference: str, payload: str,
                  classifications: Dict[str, str], shared_end: int = 0
                  ) -> Tuple[List[Variant], List[Tuple[str, str]]]:
    """Return (variants, findings).  An empty variant list means the proteins match."""
    findings: List[Tuple[str, str]] = []
    p_prot, r_prot = translate(patient), translate(reference)
    watch = PAYLOADS[payload].get("watch", {})

    if not p_prot or not r_prot:
        findings.append(("error", "Could not translate the patient or reference CDS."))
        return [], findings

    expected = PAYLOADS[payload]["aa"]
    if len(r_prot) != expected:
        findings.append(("warn", "Reference translates to %d residues; the library expects %d for %s. "
                         "Check that the reference is the right isoform (%s)."
                         % (len(r_prot), expected, payload, PAYLOADS[payload]["refseq"])))

    if len(p_prot) != len(r_prot):
        findings.append(("error", "Patient protein is %d residues and the reference is %d. A length "
                         "difference means an indel, a frameshift or a different isoform; pvd will "
                         "not align across it. Reference allele will be used."
                         % (len(p_prot), len(r_prot))))
        return [], findings

    variants: List[Variant] = []
    for i, (r_aa, p_aa) in enumerate(zip(r_prot, p_prot), start=1):
        if r_aa == p_aa:
            continue
        if "X" in (r_aa, p_aa):
            findings.append(("warn", "Residue %d could not be read (N in a codon); treated as a difference." % i))
        v = Variant(pos=i, ref_aa=r_aa, alt_aa=p_aa, region=region_of(payload, i, shared_end))
        v.classification = classifications.get(v.label, "unclassified")
        if i in watch:
            v.known = watch[i]
        variants.append(v)

    # Count codons that differ in nucleotides but encode the same residue.
    syn = 0
    for i in range(0, min(len(patient), len(reference)) - 2, 3):
        pc, rc = patient[i:i + 3], reference[i:i + 3]
        if pc != rc and CODONS.get(pc) == CODONS.get(rc) and "N" not in pc + rc:
            syn += 1
    if syn:
        findings.append(("info", "%d codon(s) differ without changing the protein. Synonymous changes create "
                         "no new peptide, so they are not matched: the cassette keeps its codon "
                         "optimisation." % syn))
    if not variants:
        findings.append(("info", "Patient protein is identical to the reference. Patient-derived and "
                         "reference payloads would be the same molecule, so reference is used."))
    return variants, findings


def summarise(variants: List[Variant]) -> str:
    return ", ".join("%s [%s/%s]" % (v.label, v.region, v.classification) for v in variants) or "none"
