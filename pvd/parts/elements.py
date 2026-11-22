"""Vector element catalogue: capsids, promoters, detargeting cassettes and their lengths.

Lengths are typical values in base pairs.  Elements without a built-in sequence are
written as runs of N until the user supplies a verified sequence with --override.
"""

# Capsid is annotated on the design but is not part of the packaged genome, so it has no
# length.  route: the administration route the capsid is intended for.
CAPSIDS = {
    "TfR1-CapX": dict(receptor="human TfR1", route="IV",
                      note="Engineered to bind the apical domain of human TfR1 for receptor-mediated "
                           "transcytosis. Requires humanised TFRC mice for preclinical evaluation."),
    "BI-hTFR1": dict(receptor="human TfR1", route="IV",
                     note="Earlier human TfR1-binding capsid in the same series."),
    "Dyno-9zh": dict(receptor="ALPL", route="IV",
                     note="Independent receptor mechanism; carry as a hedge against single-receptor failure."),
    "AAV9": dict(receptor="unspecified", route="ICV / intrathecal / FUS-assisted IV",
                 note="Use with focused-ultrasound BBB opening for focal delivery, or by CSF route."),
    "AAV2": dict(receptor="HSPG", route="intraparenchymal CED",
                 note="Clinically precedented for intraputaminal convection-enhanced delivery."),
    "AAV5": dict(receptor="unspecified", route="intraparenchymal",
                 note="Strong oligodendrocyte tropism with an MBP promoter."),
    "AAV-PHP.eB": dict(receptor="LY6A (mouse)", route="IV (mouse only)",
                       note="LY6A has no human ortholog. Mouse tool only: never load-bearing for a "
                            "translational claim."),
}

PROMOTERS = {"hSyn1": 469, "CaMKIIa": 1290, "gfaABC1D": 681, "MBP": 1300,
             "Sox10": 950, "CD68": 150, "hHexB": 134, "CBh": 800,
             "TH": 2500, "PITX3": 1000}
GLIAL_PROMOTERS = {"gfaABC1D", "MBP", "Sox10", "CD68", "hHexB"}

POLYA = {"bGH": 225, "SV40": 122, "synthetic": 49, "none": 0}

# 3' UTR detargeting cassettes.  miR-122 is hepatic; miR-124 and 4x6T suppress neuronal
# expression and belong only on a glial cassette.
DETARGET = {"miR-122x2": 44, "miR-122x4": 88, "miR-124x2": 44, "4x6T": 150}
NEURON_DETARGET = {"miR-124x2", "4x6T"}

RIBOSWITCH_LEN = 120          # tetracycline-responsive K19 aptazyme in the 3' UTR
ITR_LEN = 145
KOZAK_SEQ = "GCCACC"
STOP_SEQ = "TAA"

# AAV packaging capacity, ITR to ITR.
AAV_LIMIT = 4700
AAV_WARN = 4400
SC_LIMIT = 2400               # self-complementary genomes hold about half

# element kind -> (SVG color, GenBank feature key)
KINDS = {
    "itr": ("#6b7f90", "repeat_region"), "promoter": ("#e8a317", "promoter"),
    "cds": ("#1fa971", "CDS"), "reg": ("#7a63d1", "misc_feature"),
    "detarget": ("#18a5b8", "misc_feature"), "polya": ("#8497a5", "polyA_signal"),
    "stop": ("#c0392b", "misc_feature"), "link": ("#3b82d6", "misc_feature"),
}
# these elements take their sequence from the payload library or the patient input
BUILT_IN_IDS = {"goi", "kozak", "stop"}
