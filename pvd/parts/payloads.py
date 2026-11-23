"""Payload library.

Each entry carries the reference CDS length (bp, including the stop codon), the protein
length, the RefSeq the user should fetch as --reference, and the region map the eligibility
gate uses to decide whether the patient's own allele may be delivered.

REGION BOUNDARIES ARE APPROXIMATE.  They place the split between the shared part of the
protein and the isoform-specific or disease-associated part at a residue number, which is
accurate enough to route a variant to the right rule but is not a substitute for the RefSeq
exon table.  Confirm every boundary against the transcript before any use beyond design,
or override it on the command line.  Where a length is marked unverified, paste the real
CDS with --reference and pvd will use its length instead.

synthetic=True marks a payload that is not a human gene the patient carries: there is no
patient allele to insert, so the gate skips the allele question and only verifies the
target epitope.
"""

from typing import Dict

PAYLOADS: Dict[str, dict] = {
    # ---------------- clearance arm ----------------
    "LAMP2A": dict(
        gene="LAMP2", arm="clearance", cds=1233, aa=410, synthetic=False,
        refseq="NM_002294.3 (transcript variant A) / NP_002285.1",
        locus="Xq24", x_linked=True,
        regions=[(1, 375, "shared-lumenal"), (376, 410, "isoform-specific")],
        watch={93: "LAMP2 p.G93R has been reported in mild Danon disease"},
        note="Rate-limiting receptor for chaperone-mediated autophagy. X-linked: LAMP2 "
             "loss of function causes Danon disease, and pathogenic variants have been "
             "reported in every exon. Exon 9 splicing gives isoforms 2A/2B/2C, and Danon "
             "is mainly 2B-driven, so a variant restricted to the 2B-specific tail does "
             "not affect a 2A payload while a variant in the shared lumenal domain does.",
        verified_length=True),
    "TFEB": dict(
        gene="TFEB", arm="clearance", cds=1431, aa=476, synthetic=False,
        refseq="fetch the RefSeq CDS for TFEB", locus="6p21", x_linked=False,
        regions=[(1, 476, "other")], watch={},
        note="Master regulator of the autophagy-lysosome programme and the strongest "
             "published effect in the clearance arm, but a growth-associated transcription "
             "factor: TFEB-rearranged renal cell carcinoma is a recognised entity. Needs "
             "the same oncogenicity workup as HSF1. Not recommended as a lead.",
        verified_length=False),
    "Beclin-1": dict(
        gene="BECN1", arm="clearance", cds=1353, aa=450, synthetic=False,
        refseq="fetch the RefSeq CDS for BECN1", locus="17q21", x_linked=False,
        regions=[(1, 450, "other")], watch={},
        note="Macroautophagy rather than CMA; worked comparably to TFEB in the same study.",
        verified_length=False),
    # ---------------- barrier arm ----------------
    "VH14-PEST": dict(
        gene="synthetic single-domain intrabody", arm="barrier", cds=483, aa=160,
        synthetic=True, refseq="n/a - supply the construct with --override goi=FILE",
        locus="n/a", x_linked=False, regions=[], watch={},
        epitope=(61, 95), epitope_name="NAC domain",
        note="Human single-domain intrabody against the NAC hydrophobic region, which is "
             "critical for initial aggregation, fused to a PEST degron. Acts inside the "
             "neuron, which is where nucleation happens and where extracellular antibody "
             "drugs could not reach. Length is approximate: paste your construct.",
        verified_length=False),
    "NAC32": dict(
        gene="synthetic scFv intrabody", arm="barrier", cds=750, aa=249,
        synthetic=True, refseq="n/a - supply the construct with --override goi=FILE",
        locus="n/a", x_linked=False, regions=[], watch={},
        epitope=(53, 87), epitope_name="residues 53-87 window",
        note="scFv intrabody against residues 53-87. AAV-NAC32 normalised behaviour and "
             "improved nigral dopaminergic survival in rats. Length is approximate.",
        verified_length=False),
    # ---------------- chaperone arm ----------------
    "DNAJB6b": dict(
        gene="DNAJB6", arm="chaperone", cds=726, aa=241, synthetic=False,
        refseq="NM_005494 (transcript variant II, isoform b)",
        locus="7q36", x_linked=False,
        regions=[(1, 76, "other"), (77, 100, "gf-domain"), (101, 241, "other")],
        watch={89: "DNAJB6 p.F89I causes LGMD1D by a dominant toxic mechanism",
               93: "DNAJB6 p.F93L / p.F93I cause LGMD1D by a dominant toxic mechanism"},
        note="Isoform b is the cytoplasmic one and the one that suppresses alpha-synuclein "
             "aggregation; isoform a is nuclear and was not responsible. G/F-domain "
             "missense variants cause limb-girdle muscular dystrophy type 1D by a dominant "
             "toxic effect mediated by this same cytoplasmic isoform, so a patient allele "
             "with a G/F-domain change is excluded.",
        verified_length=True),
    "DNAJB1": dict(
        gene="DNAJB1", arm="chaperone", cds=1023, aa=340, synthetic=False,
        refseq="fetch the RefSeq CDS for DNAJB1 (UniProt P25685)",
        locus="19p13", x_linked=False, regions=[(1, 340, "other")], watch={},
        note="Obligate targeting component of the HSP70 disaggregase; cannot be substituted "
             "by other J-domain proteins. Pairs with endogenous HSPA8 and with HSPH1.",
        verified_length=True),
    "HSPH1": dict(
        gene="HSPH1", arm="chaperone", cds=2577, aa=858, synthetic=False,
        refseq="fetch the RefSeq CDS for HSPH1 (UniProt Q92598, Hsp105 alpha)",
        locus="13q12", x_linked=False, regions=[(1, 858, "other")], watch={},
        note="Nucleotide exchange factor that accelerates disaggregation. With DNAJB1 this "
             "is 3.6 kb of coding sequence, so the pair only fits one AAV with no headroom.",
        verified_length=True),
    "HSPA8": dict(
        gene="HSPA8", arm="chaperone", cds=1941, aa=646, synthetic=False,
        refseq="fetch the RefSeq CDS for HSPA8 (UniProt P11142)",
        locus="11q24", x_linked=False, regions=[(1, 646, "other")], watch={},
        note="Disaggregase motor, but constitutively abundant in neurons already, and it is "
             "also the clathrin uncoating ATPase that releases clathrin from coated "
             "vesicles. Overexpressing it in presynaptic terminals risks the vesicle "
             "recycling the therapy is meant to protect. Lowest priority of the three.",
        verified_length=True),
}

# The aggregation target whose epitope the barrier payloads bind.
TARGET = dict(gene="SNCA", cds=423, aa=140,
              refseq="fetch the RefSeq CDS for SNCA",
              nac=(61, 95),
              note="Alpha-synuclein. 140 residues: N-terminal membrane-binding helix "
                   "(1-60), NAC aggregation core (61-95), acidic C-terminal tail (96-140).")


def shared_end_applies(key: str) -> bool:
    """Whether this payload has a shared/isoform boundary for --shared-end to move."""
    regions = PAYLOADS[key]["regions"]
    return len(regions) == 2 and regions[0][2] == "shared-lumenal"


def payload_regions(key: str, shared_end: int = 0):
    """Region map, with an optional override of the shared/isoform boundary.

    An out-of-range shared_end is rejected rather than applied. The old code accepted
    anything: a negative value produced regions like (1, -375) and (-374, 410), which
    matched no position for the first region and every position for the second, so every
    variant was relabelled isoform-specific and the shared-lumenal exclusion stopped
    firing. One mistyped flag turned a blocked allele into a delivered one.
    """
    p = PAYLOADS[key]
    regions = list(p["regions"])
    if not shared_end:
        return regions
    if not shared_end_applies(key):
        # No boundary to move. Silently dropping the flag is the caller's cue to say so;
        # see run_gate, which reports it rather than letting the user believe it applied.
        return regions
    if shared_end < 1 or shared_end >= p["aa"]:
        raise ValueError(
            "--shared-end %d is out of range for %s: give a residue between 1 and %d. "
            "A value outside the protein remaps the region boundaries nonsensically and "
            "can move a variant out of an excluding region."
            % (shared_end, key, p["aa"] - 1))
    return [(1, shared_end, "shared-lumenal"), (shared_end + 1, p["aa"], "isoform-specific")]


def region_of(key: str, pos: int, shared_end: int = 0) -> str:
    for lo, hi, name in payload_regions(key, shared_end):
        if lo <= pos <= hi:
            return name
    return "other"
