"""The three proteostasis arms, their payloads, defaults and guidance."""

PROGRAMS = {
    "clearance": dict(
        name="Clearance (autophagy-lysosome)",
        payloads=["LAMP2A", "TFEB", "Beclin-1"],
        default="LAMP2A", promoter="hSyn1",
        tip="Restores disposal of what has already formed. Strongest published effect of "
            "the three arms and the only one with nonhuman-primate data (LAMP2A). LAMP2A "
            "is preferred over TFEB: a structural lysosomal membrane protein rather than a "
            "growth-associated transcription factor."),
    "barrier": dict(
        name="Barrier (nucleation blockade)",
        payloads=["VH14-PEST", "NAC32"],
        default="VH14-PEST", promoter="hSyn1",
        tip="Raises the kinetic barrier to nucleation from inside the neuron, which is "
            "where the failed extracellular antibody drugs could not reach. Smallest "
            "payload in the set. Verify the SNCA epitope in this patient before dosing: a "
            "coding variant inside it can cost the binder its target."),
    "chaperone": dict(
        name="Chaperone buffering",
        payloads=["DNAJB6b", "DNAJB1", "HSPH1", "HSPA8"],
        default="DNAJB6b", promoter="hSyn1",
        tip="Buffers species that do form. Weakest published effect sizes of the three "
            "arms in Parkinson's, which is why it is sequenced second. DNAJB6b is the "
            "single-gene option; DNAJB1 plus HSPH1 reconstitutes the disaggregase but the "
            "pair uses the whole packaging budget."),
}

# Two-vector regimens the designer can emit in one run.
REGIMENS = {
    "lamp2a+vh14": dict(name="LAMP2A + VH14-PEST (recommended)",
                        payloads=["LAMP2A", "VH14-PEST"],
                        tip="Clearance plus barrier: two points on the same kinetic curve "
                            "rather than one node pushed harder. Both payloads are small, "
                            "so each vector keeps full headroom for detargeting and dose "
                            "control. Co-administer in one session; anti-capsid antibodies "
                            "make sequential dosing with the same capsid ineffective."),
    "disaggregase": dict(name="DNAJB1 + HSPH1 (disaggregase pair)",
                         payloads=["DNAJB1", "HSPH1"],
                         tip="Relies on endogenous HSPA8 as the motor. The machine only "
                             "works where both genomes reach the same neuron, so report "
                             "co-transduction fraction, not percent transduced."),
}
