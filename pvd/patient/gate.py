"""The eligibility gate: may this patient's own allele go into the payload, and in which tier?

The default answer is no.  A patient allele is delivered only when every one of these holds:

  * the payload is a human gene the patient actually carries (not a synthetic binder)
  * a reference CDS was supplied, and patient and reference translate to the same length
  * at least one coding difference exists (otherwise reference is the same molecule)
  * no difference falls in a region the payload's rule excludes
  * the gene is not X-linked in a male patient with a coding variant, and where the gene is
    X-linked the patient's sex is known at all
  * every difference carries an explicit benign or likely-benign classification

Unclassified means reference.  Without that rule "patient-derived" would mean
"risk-allele-amplifying" for some fraction of patients, and the sequencing step that was
meant to add safety would remove it.
"""

from typing import List, Tuple

from ..model import Config, Gate
from ..parts.payloads import PAYLOADS, payload_regions
from . import epitope as epi
from .parse import looks_like_cds, select_cds
from .variants import call_variants

BENIGN = {"benign", "likely-benign"}
EXCLUDING_REGIONS = {
    "shared-lumenal": "a variant in the shared lumenal domain affects the 2A payload",
    "gf-domain": "a G/F-domain variant acts by a dominant toxic mechanism",
}


def run_gate(cfg: Config, payload: str, shared_end: int = 0) -> Gate:
    p = PAYLOADS[payload]
    g = Gate(payload=payload, gene=p["gene"],
             allele="n/a" if p["synthetic"] else "reference", tier="reference",
             binder=payload if p["arm"] == "barrier" else "")
    find: List[Tuple[str, str]] = g.findings

    # ---- barrier payloads: no patient allele exists, verify the target epitope instead
    if p["synthetic"]:
        find.append(("info", "%s is a selected synthetic binder, not a gene this patient carries: there is "
                     "no patient allele to insert. The sequence is used to verify the target epitope."
                     % payload))
        t_pat = select_cds(cfg.target_seq, "SNCA")[0]
        t_ref = select_cds(cfg.target_reference, "SNCA")[0]
        hits, every, f = epi.verify(payload, t_pat, t_ref, cfg.classifications)
        g.epitope = hits
        find.extend(f)
        if hits:
            alt = epi.alternative_payloads(payload, hits, every)
            if alt:
                find.append(("info", "Barrier payload(s) whose epitope window contains none of this "
                             "patient's coding changes: %s." % ", ".join(alt)))
            else:
                # Saying nothing here reads as "no alternative was considered". The patient
                # needs a re-engineered binder, which is a different and larger decision.
                find.append(("error", "No stocked barrier payload has an epitope window clear of this "
                             "patient's coding changes. A binder must be re-selected or re-engineered "
                             "against this patient's alpha-synuclein; no catalogue payload fits."))
        g.tier = "autologous" if cfg.route == "autologous" else "stock"
        _note_tier(g, cfg)
        return g

    # ---- human-gene payloads: the allele question is live
    pat = select_cds(cfg.patient_seq, p["gene"])[0]
    ref = select_cds(cfg.reference_seq, p["gene"])[0]

    if not pat:
        if (cfg.patient_seq or "").strip():
            # Something was supplied and nothing usable came out of it: a wrong path, a
            # binary file, a protein FASTA. Reporting that as "none supplied" at info level
            # lets a typo pass for a deliberate choice of the reference allele.
            find.append(("warn", "A patient sequence was supplied but no A, C, G, T or N could be read "
                         "from it, so the reference %s allele is used. Check the path and that the file "
                         "is nucleotide FASTA rather than protein or a binary format." % payload))
        else:
            find.append(("info", "No patient sequence supplied, so the reference %s allele is used. Supply "
                         "--patient and --reference to run the gate." % payload))
        g.tier = "autologous" if cfg.route == "autologous" else "reference"
        _note_tier(g, cfg)
        return g
    if not ref:
        find.append(("error", "A patient sequence was supplied without --reference, so no variant can be "
                     "called and the patient allele cannot be cleared. Reference allele is used. Fetch %s."
                     % p["refseq"]))
        g.tier = "autologous" if cfg.route == "autologous" else "reference"
        _note_tier(g, cfg)
        return g

    for label, seq in (("patient", pat), ("reference", ref)):
        ok, why = looks_like_cds(seq)
        if not ok:
            find.append(("error", "The %s %s sequence is not a usable CDS: %s. Reference allele is used."
                         % (label, p["gene"], why)))
            g.tier = "autologous" if cfg.route == "autologous" else "reference"
            _note_tier(g, cfg)
            return g

    variants, f = call_variants(pat, ref, payload, cfg.classifications, shared_end)
    g.variants = variants
    find.extend(f)

    blocked = False
    if any(level == "error" for level, _ in f):
        blocked = True
    if not variants:
        blocked = True

    for v in variants:
        if v.region in EXCLUDING_REGIONS:
            find.append(("error", "%s is in the %s region: %s. Patient allele excluded."
                         % (v.label, v.region, EXCLUDING_REGIONS[v.region])))
            blocked = True
        if v.known:
            find.append(("error", "%s is on the watch list: %s. Patient allele excluded."
                         % (v.label, v.known)))
            blocked = True
        if v.classification not in BENIGN:
            find.append(("error" if v.classification != "unclassified" else "warn",
                         "%s is classified %s. Only benign or likely-benign variants may be delivered, so "
                         "the patient allele is excluded." % (v.label, v.classification)))
            blocked = True

    if variants and p.get("x_linked") and cfg.sex == "male":
        find.append(("error", "%s is X-linked (%s) and this patient is male, so there is no second allele "
                     "to compare against and no mosaic rescue. Reference allele is used."
                     % (p["gene"], p["locus"])))
        blocked = True
    if variants and p.get("x_linked") and cfg.sex == "unknown":
        # Unknown sex on an X-linked gene is the same epistemic position as an unclassified
        # variant, so it gets the same answer. Warning and then delivering the patient allele
        # anyway would make the default path the unsafe one, and would contradict this
        # message. --sex female is the way to assert the second allele exists.
        find.append(("error", "%s is X-linked (%s) and the patient's sex was not given, so hemizygosity "
                     "cannot be ruled out and no second allele is known to exist. Reference allele is "
                     "used. Set --sex female to assert a second allele, or --sex male to confirm the "
                     "exclusion." % (p["gene"], p["locus"])))
        blocked = True

    if blocked:
        g.allele, g.tier = "reference", ("autologous" if cfg.route == "autologous" else "reference")
        _note_tier(g, cfg)
        return g

    g.allele = "patient"
    labels = {v.label for v in variants}
    match = next((b for b, vs in cfg.bins.items() if set(vs) == labels), "")
    if cfg.route == "autologous":
        g.tier = "autologous"
    elif match:
        g.tier, g.bin_id = "binned", match
        find.append(("info", "Patient coding haplotype matches qualified bin %s: a stocked vector covers "
                     "this patient, with no bespoke campaign." % match))
    else:
        g.tier = "n-of-1"
        find.append(("warn", "Patient haplotype (%s) matches no qualified bin. This routes to an N-of-1 "
                     "vector: a dedicated production campaign with a full release panel, months from "
                     "sequence to dose. Consider adding this haplotype to the panel instead."
                     % ", ".join(sorted(labels))))
    _note_tier(g, cfg)
    return g


def _note_tier(g: Gate, cfg: Config) -> None:
    if g.tier == "autologous":
        g.findings.append(("info", "Route is autologous ex vivo, so the product's genome is the patient's "
                           "and the allele question only concerns the engineered cassette. Immune matching "
                           "is total; QC happens on the clone before implantation."))
    elif g.tier == "reference" and g.allele == "reference" and not PAYLOADS[g.payload]["synthetic"]:
        g.findings.append(("info", "Reference allele is not a fallback here. For an augmentation payload the "
                           "goal is functional protein, so where the patient's own allele is unproven the "
                           "reference is often the better molecule."))


def gate_lines(g: Gate, shared_end: int = 0) -> List[str]:
    """Readable gate transcript for the report and the console."""
    p = PAYLOADS[g.payload]
    out = ["Payload: %s (%s)" % (g.payload, g.gene),
           "Allele delivered: %s" % g.allele,
           "Tier: %s%s" % (g.tier, (" [%s]" % g.bin_id) if g.bin_id else "")]
    if p["regions"]:
        out.append("Region map: " + ", ".join("%d-%d %s" % r for r in payload_regions(g.payload, shared_end)))
    if g.variants:
        out.append("Coding variants:")
        for v in g.variants:
            out.append("  %-10s %-18s %s%s" % (v.label, v.region, v.classification,
                                               "  <- " + v.known if v.known else ""))
    elif not p["synthetic"]:
        out.append("Coding variants: none")
    if g.epitope:
        out.append("Epitope variants: " + ", ".join(v.label for v in g.epitope))
    return out
