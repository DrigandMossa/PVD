# Disaggregase Gene Therapy for Parkinson's Disease — HSPA8 / DNAJB1 / HSPH1

> Research design notes. Not a clinical protocol and not medical advice.

## The target

Mammals have no Hsp104. What they have instead is a three-component system that is the only
one shown to take **pre-formed** α-synuclein amyloid apart:

| Component | Gene | Role |
|---|---|---|
| **Hsc70** | *HSPA8* | The ATPase that binds and pulls |
| **DNAJB1** | *DNAJB1* | J-domain cochaperone; targets Hsc70 to the fibril surface |
| **Apg2** | *HSPH1* | Hsp110 nucleotide-exchange factor; recycles Hsc70 for repeated cycles |

The mechanism has two phases. **Fragmentation** breaks long fibrils into shorter ones;
**depolymerisation** then removes monomers from fibril ends. All three components are
required — the trio is not a sum of three independent activities, and leaving any one out
collapses the reaction.

This distinguishes it from every other lever in this project. DNAJB6b, LAMP2A, TFEB and
substrate reduction all act on what has not yet aggregated, or on what can be swept into a
lysosome. The disaggregase acts on the deposit itself.

## The arithmetic that defeats it

AAV packages roughly **4.7 kb** between the ITRs, including both ITRs, promoter, Kozak,
polyadenylation signal and any regulatory element. Oversized genomes do not simply fail —
they package **truncated**, producing vectors that look fine by titre and are useless or
worse by function.

| Component | CDS | Protein |
|---|---|---|
| *HSPA8* | ~1.95 kb | 646 aa |
| *DNAJB1* | ~1.02 kb | 340 aa |
| *HSPH1* | ~2.57 kb | 858 aa |
| **Total** | **~5.54 kb** | |

**~5.54 kb of coding sequence alone, against a ~4.7 kb total limit.** The trio does not fit
in one AAV with zero regulatory sequence, let alone with a promoter and a polyA.

| Configuration | Payload | Fits? |
|---|---|---|
| All three, single AAV | ~5.54 kb CDS + ~1.0 kb regulatory | **No** — over by ~1.8 kb |
| *HSPA8* + *DNAJB1*, one AAV | ~2.97 kb + regulatory | Tight; feasible with a minimal promoter |
| *DNAJB1* alone, scAAV | ~1.02 kb | Yes (scAAV limit ~2.4 kb) |
| *HSPA8* alone | ~1.95 kb | Yes |
| *HSPH1* alone | ~2.57 kb | Yes, with a compact cassette |

This is why `pvd` enforces `AAV_LIMIT = 4700` as an error, `AAV_WARN = 4400` as a warning,
and `SC_LIMIT = 2400` for self-complementary designs. The arithmetic is a design driver, not
a footnote.

### Three architectures, none of them clean

1. **Co-administration of separate vectors.** Three vectors, one per component, dosed
   together. The problem is that the mechanism requires all three **in the same cell**, and
   co-transduction efficiency is the product of three independent probabilities. At a
   realistic per-vector transduction fraction, the triply-transduced population is small —
   and cells transduced with only one or two components get the liabilities below without the
   benefit.
2. **Dual-vector with a multigene strategy.** Split the trio across two vectors (*HSPA8* +
   *DNAJB1* on one, *HSPH1* on the other) using a minimal promoter and an IRES or a
   self-cleaving 2A peptide. Halves the co-transduction penalty. Approaches such as AdAAV
   and AAVLINK exist for larger multigene payloads and carry their own manufacturing and
   immunogenicity questions.
3. **Single-component staging.** Deliver one component and rely on endogenous levels of the
   other two being sufficient. This is the honest option and also the weakest: if endogenous
   DNAJB1 or Apg2 were sufficient, the disaggregase would already be working.

`pvd` implements **option 1** as the `disaggregase` regimen: two separate vectors, one
carrying *DNAJB1* and one carrying *HSPH1*, co-administered, with endogenous *HSPA8* as the
motor. Each packages with room to spare — 1,594 bp and 3,148 bp between the ITRs against a
4,700 bp limit — so capacity is not what constrains this regimen. **Co-transduction is.**
Two vectors means the fraction of neurons receiving both is the product of two
probabilities, and a neuron that receives only one gets the liabilities below without the
mechanism. That is why the endpoint to report is co-transduction fraction rather than
percent transduced, and why the regimen prints exactly that warning.

Any single payload can still be built on its own (`--program chaperone --payload DNAJB1`),
which is option 3 and the weakest of the three for the reason given above.

## Three mechanism-specific liabilities

### HSPA8 is not a free upgrade

Hsc70 is the **uncoating ATPase** for clathrin-coated vesicles. Raising it in a presynaptic
terminal does not only add disaggregase capacity; it perturbs synaptic vesicle cycling in a
cell type whose entire function is synaptic vesicle cycling. This is a dose-dependent
on-target liability with no obvious engineering fix, and it is the reason the payload library
carries a note on *HSPA8* rather than treating it as the natural lead.

### Fragmentation generates seeds

The first phase of the mechanism breaks long fibrils into short ones. Short fibrils are
**better seeds** than long ones — more ends per unit mass, and more readily taken up by
neighbouring cells. A partial reaction, which is what a sub-saturating gene therapy
delivers, is a seed-generating machine. The *in vitro* work gets to net clearance because
the reaction runs to completion with all three components at saturating concentrations in a
cuvette. A neuron with one extra component and endogenous levels of the other two is in the
regime where fragmentation outruns depolymerisation.

This is the single strongest argument against the staged architecture, and against the
disaggregase as a first-in-human target at all.

### The deposit may not be the lesion

Lewy bodies are the pathological signature of Parkinson's, but the evidence that the mature
inclusion is the toxic species is weak; oligomeric intermediates are the leading candidate.
A therapy that dismantles mature deposits into oligomers would be converting the inert form
into the suspected toxic one. Disaggregation is only obviously good if what it produces is
cleared — which makes the disaggregase arm dependent on the **clearance** arm being intact,
and in Parkinson's nigra it is not.

## Delivery

Identical to the rest of the portfolio: a TfR1-binding capsid (**BI-hTFR1**, **TfR1-CapX**,
**BI-TfR1 CapX**) for non-surgical CNS access after intravenous dosing, `hSyn1` to restrict
expression to neurons, `miR-122` sites to silence hepatic expression, and
`miR-124`/`4x6T` for CNS compartment restriction. **AAV-PHP.eB is mouse-only** — it acts
through the LY6A allele, which does not serve that function in humans — and `pvd` flags it
as an error rather than a warning.

Local administration (intraputaminal CED) is more attractive here than elsewhere, because
the liabilities above are all dose- and distribution-dependent: a smaller, better-defined
transduced volume limits the seed-generation risk and the synaptic-vesicle risk at the same
time.

## Where this sits in the portfolio

Honest placement: **last**. The disaggregase is mechanistically the most interesting target
in this project and the least ready. It is the only system that acts on existing deposits;
it cannot be delivered whole; its staged form has a specific, plausible mechanism for making
things worse; and the one network-level alternative that would raise all three components at
once (HSF1) gave about 20% dopaminergic neuron survival, no better than HSP70 alone.

See [`proteostasis-levers.md`](proteostasis-levers.md) for the comparative ranking and
[`hsf1-program.md`](hsf1-program.md) for the HSF1 route.
