# Six Gene-Therapy Levers for Parkinson's Proteostasis

> Research design notes. Not a clinical protocol, not medical advice, and not a
> substitute for IND-enabling work. Effect sizes are quoted from the literature as
> published, in models that mostly do not resemble idiopathic Parkinson's disease.

Soluble α-synuclein is **metastable**, not stable. The amyloid fibril appears to be the
thermodynamically favoured state; the monomer persists because the route to the fibril is
slow, not because the monomer is the bottom of the energy landscape. What keeps a healthy
neuron on the soluble side of that landscape is three things, and ageing erodes all three:

1. **High kinetic barriers** — nucleation is slow because the barrier to forming the first
   ordered oligomer is high.
2. **Chaperone buffering** — the species that do form are bound, remodelled or
   disassembled before they can template more.
3. **Clearance** — what gets past the first two is degraded, by chaperone-mediated
   autophagy, macroautophagy or the proteasome.

The useful consequence is that each arm is separately addressable, and gene therapy can act
in either direction on each one: **supply the effector**, or **remove what suppresses it**.
Six intervention points follow.

---

## Arm 1 — Raise the kinetic barrier

The barrier is set by how often a monomer finds itself in a conformation and a local
concentration that permit ordered nucleation. Two things dominate: how much substrate there
is, and whether the aggregation-prone stretch is accessible.

### Lever 1 — Lower the substrate

Nucleation is steeply superlinear in monomer concentration, so a modest reduction in
α-synuclein buys a disproportionate reduction in nucleation rate. This is the only lever
that attacks primary nucleation directly.

**Tools.** AAV-delivered shRNA or miRNA against *SNCA*; CRISPRi or a zinc-finger repressor
at the *SNCA* promoter; antisense is the non-viral comparator and is already in clinical
development.

**The hard constraint: how much is too much.** α-Synuclein is not dispensable. It has a
real presynaptic function in SNARE-complex assembly and vesicle trafficking, and
*SNCA*-null animals show blood–brain barrier abnormalities. Published knockdown experiments
have produced dopaminergic neuron loss when reduction went too deep — the therapeutic
window is bounded on **both** sides, and the upper bound is not well characterised in
humans.

A partial knockdown, titrated to perhaps 30–50%, is the defensible target. That is a
dose-finding problem for a gene therapy that cannot be withdrawn, which is the central
argument for a regulated construct (see *Regulation*, below).

### Lever 2 — Mask the aggregation-prone stretch

Rather than lowering the amount of substrate, change its availability. The **NAC domain**
(residues 61–95) is the stretch that must become accessible and ordered for the fibril core
to form. An intrabody or binder that occupies it raises the barrier without touching
expression level.

**Tools.** Intracellularly expressed single-domain binders — the best characterised is
**VH14**, directed at the NAC domain, usually expressed as a **VH14–PEST** fusion so that
bound α-synuclein is routed to the proteasome rather than merely sequestered. NAC-directed
nanobodies are the same idea from a different scaffold.

**Why this one is attractive.** It is small (well under 1 kb), it does not require
transcriptional repression machinery, and the PEST fusion converts binding into clearance —
making it a barrier intervention and a clearance intervention at once.

**Why it is not simple.** An intrabody must fold and remain soluble in the reducing
cytosol, which disqualifies most conventional antibody formats. Expression level has to be
high enough for stoichiometric occupancy of a very abundant protein, which pushes against
promoter strength and dose. And the epitope must actually be present in the patient's
α-synuclein — which is the single clearest case for sequencing the patient before choosing
the binder.

---

## Arm 2 — Restore chaperone buffering

This is the arm the earlier programs in this project were built on, and it is, on the
published evidence, **the weakest of the three**. That is worth stating plainly rather than
defending.

### Lever 3 — Supply a specific anti-amyloid chaperone

**DNAJB6b** is the standout. It suppresses amyloid formation **substoichiometrically** —
inhibition has been observed at concentrations around 7.8 nM against micromolar substrate,
roughly 0.04% molar ratio. It does not work by mass action; it appears to bind and poison
the growing nucleus, acting on primary nucleation specifically. Its serine-rich G/F domain
(approximately residues 77–100) is required.

*In vivo*, AAV-DNAJB6 delivered to rat substantia nigra reduced α-synuclein pathology
(Arkan et al., *Neurobiology of Disease*, 2021). The effect is real; it is not a cure, and
the paper does not claim it is.

**The safety constraint is specific and dominant.** Dominant missense mutations in the
*DNAJB6* G/F domain — **F89I, F93L, F93I** — cause **limb-girdle muscular dystrophy type
1D**. The mutant protein is not merely non-functional; it is actively toxic through a
dominant-negative mechanism. A construct carrying a G/F-domain variant would be delivering
a disease allele at supraphysiological dose into cells that cannot clear it. This is why
the gate blocks any patient variant mapping into 77–100 outright rather than classifying
it.

### Lever 4 — Supply a disaggregase, or lift the brake on HSF1

Two sub-levers, neither strong.

**The HSP70 disaggregase** — Hsc70 (*HSPA8*) + DNAJB1 + Apg2 (*HSPH1*) — is the only
mammalian system shown to fragment and depolymerise pre-formed α-synuclein fibrils. It is
mechanistically unique and, as a gene therapy, defeated by packaging arithmetic: the three
CDSs total roughly 5.54 kb against an AAV limit near 4.7 kb. See
[`disaggregase-program.md`](disaggregase-program.md) for the full treatment, including why
overexpressing *HSPA8* alone is not a neutral act.

**HSF1**, the master heat-shock transcription factor, is the upstream alternative: raise one
transcription factor and the whole chaperone network follows. The brake on it is the
**NEDD4/CK2 axis** acting through phosphorylation of **S303 and S307**; a constitutively
active HSF1 (S303A/S307A, or a regulatory-domain deletion) escapes it.

**Why it is ranked last.** In the published nigral work, constitutively active HSF1 gave
roughly **20% dopaminergic neuron survival benefit — no better than HSP70 alone**. The
network-level intervention did not beat its own single downstream component. And HSF1 is an
oncogenicity-class transcription factor: constitutive activation in long-lived,
non-dividing cells is a liability that a 20% effect does not pay for. See
[`hsf1-program.md`](hsf1-program.md).

---

## Arm 3 — Restore clearance

**This arm has the strongest published effects**, and the ranking in these notes was
revised to say so.

### Lever 5 — Restore chaperone-mediated autophagy

α-Synuclein is a **CMA substrate**: it carries a KFERQ-like motif, is recognised by
**HSC70**, and is translocated into the lysosome through **LAMP2A**. Both arms of that
pathway decline with age, and LAMP2A is reduced in Parkinson's substantia nigra. Worse,
aggregated α-synuclein **binds LAMP2A without being translocated**, blocking the receptor
for every other CMA substrate — a feed-forward failure.

**Tools.** AAV-*LAMP2A*, optionally with *HSPA8*.

**Why it leads.** Published LAMP2A overexpression work is the strongest of the six and the
only candidate here with **nonhuman-primate data**. It is the lead payload in `pvd` for
that reason.

**The safety constraint is genetic and unusual.** *LAMP2* is **X-linked, at Xq24**. Loss of
function causes **Danon disease** — cardiomyopathy, myopathy, intellectual disability — and
the clinically significant phenotype in males is severe. Three isoforms (2A, 2B, 2C) arise
from alternative splicing of exon 9; residues 1–375 are shared, and only the C-terminal
~35 residues are isoform-specific.

Two consequences, both encoded in the gate:

* A variant in the **shared lumenal region (1–375)** affects all three isoforms, not just
  the one being delivered. It is an automatic block.
* A **hemizygous male** has no second allele to compare against, so a novel variant cannot
  be called benign by inspection. Also an automatic block.

### Lever 6 — Release TFEB

*TFEB* is the master transcriptional regulator of lysosomal biogenesis and autophagy — raise
it and the clearance network coordinately rises. In Parkinson's models, α-synuclein
**sequesters TFEB in the cytoplasm**, preventing nuclear translocation; the brake and the
disease are the same lesion.

**Reported effect.** AAV-*TFEB* in the rat nigral α-synuclein model has been described as
giving **almost complete protection** of dopaminergic neurons. That is the largest effect
size in this document by a wide margin.

**The constraint that keeps it out of the lead.** Like HSF1, TFEB is an
oncogenicity-class transcription factor — *TFEB* translocations define a recognised renal
cell carcinoma subtype. Constitutive, unregulated overexpression delivered by a vector that
cannot be withdrawn is the wrong shape for that risk profile. **TFEB is the strongest
argument in the whole portfolio for a regulated construct**, not for abandoning the target.

---

## Comparative ranking

Ordered by published effect size, with the constraint that actually governs each.

| | Lever | Mechanism | Published effect | Governing constraint |
|---|---|---|---|---|
| 1 | **TFEB** | Clearance network | Reported near-complete nigral protection | Oncogenicity class; needs regulation |
| 2 | **LAMP2A (± HSPA8)** | CMA receptor | Strong, with NHP data | X-linked; Danon; shared lumenal region |
| 3 | **SNCA knockdown** | Substrate ↓ | Robust, but two-sided window | Essential gene; irreversible dosing |
| 4 | **VH14-PEST / NAC binder** | Barrier ↑ + clearance | Moderate | Cytosolic folding; stoichiometry; epitope must exist |
| 5 | **DNAJB6b** | Primary nucleation ↓ | Moderate (rat SN) | G/F-domain alleles are dominantly toxic |
| 6 | **HSF1 / disaggregase** | Chaperone network | ~20% DA survival; trio unpackageable | Oncogenicity class; AAV capacity |

### The regimen the code implements

No single lever addresses more than one arm. A defensible combination takes one from each:

* **Barrier:** VH14-PEST (small, dual-mechanism) or titrated *SNCA* knockdown
* **Chaperone:** DNAJB6b (substoichiometric, smallest real effect-per-kb)
* **Clearance:** LAMP2A (strongest evidence with primate data), TFEB held as the
  high-ceiling, high-regulation option

This is the `--regimen` default in `pvd`. Each arm is a separate vector; none of them fit
together, and the staging is a packaging consequence rather than a preference.

---

## Delivery

Everything above is moot without getting the vector to nigral and striatal neurons.

**Crossing the barrier, rather than going around it.** The modern option is a capsid
engineered to bind **human transferrin receptor 1** and transcytose — **BI-hTFR1**,
**TfR1-CapX**, **BI-TfR1 CapX** — which gives broad, non-surgical CNS delivery after
intravenous dosing. **AAV-PHP.eB must not be used in a human program**: it works through
**LY6A**, which is a mouse-strain-specific allele with no human orthologue serving that
function. The `pvd` checks flag this explicitly, because it is the single most common way a
promising mouse result fails to translate.

**Physical and local alternatives.** MR-guided focused ultrasound can open the barrier
transiently and focally; intraputaminal convection-enhanced delivery bypasses it entirely
at the cost of a neurosurgical procedure and a limited volume of distribution.

**Restricting expression to the right cells.** A broad capsid needs a narrow promoter.
`hSyn1` for neurons, `gfaABC1D` for astrocytes, `MBP` for oligodendrocytes, `CD68` or
`hHexB` for microglia. Off-target expression is further suppressed by **miRNA detargeting**
— `miR-122` binding sites to silence hepatic expression, `miR-124` or a `4x6T` cassette to
restrict within the CNS.

**Regulation.** For TFEB and HSF1 in particular, and for any irreversibly dosed essential
gene, a **K19 tetracycline-responsive riboswitch** gives a ligand-controlled off switch. It
costs cassette space and adds a drug dependency, and it is the only answer currently
available to "what if the dose is wrong and the vector is permanent".

**Eligibility.** Pre-existing anti-AAV neutralising antibodies exclude a substantial
fraction of patients from systemic dosing, and titre must be measured before assignment,
not after.

---

## Patient sequence: what it is actually for

The request that produced the software was to build vectors *from* sequenced patient code.
Working through it, that turns out to be **two different things**, and only one of them is
construction.

### Sequence for construction — narrower than it sounds

For an **augmentation** payload, the reference sequence is usually the **better molecule**.
If the patient's *LAMP2* allele is hypomorphic, copying it delivers the defect at higher
dose. The patient allele earns its place in the construct only when it is demonstrably
equivalent to reference, and the point of checking is to decide **eligibility**, not to
source the insert.

For **synthetic** payloads — VH14-PEST, NAC32, any engineered binder — there is no patient
allele at all. The patient's sequence does not supply the construct; it validates that the
construct will work.

This is why `pvd` defaults to the reference allele, treats a patient allele as something
that must pass the gate to be used, and refuses to put a patient *LAMP2* CDS into a
synthetic binder's cassette just because it was the sequence on the command line.

### Sequence for selection — where the real value is

1. **Epitope verification.** A NAC-directed binder requires the epitope to be intact. A
   patient variant inside residues 61–95 may abolish binding. The right response is not to
   proceed and hope; it is to switch to a binder whose window excludes the variant. The gate
   does exactly this, offering an alternative payload whose epitope window the variant falls
   outside.
2. **Eligibility and exclusion.** The *LAMP2* shared-lumenal rule, the *DNAJB6* G/F-domain
   rule, the hemizygous-male rule, and the watch-list rule are all sequence-driven
   exclusions. They are the main reason to sequence.
3. **Germline framework matching.** For an expressed binder, matching the IGHV framework to
   the patient's germline repertoire reduces the chance of an anti-drug response to a
   protein the neuron will express for the rest of the patient's life.

### Manufacturing reality: the three-tier model

**N-of-1 AAV is not N-of-1 ASO.** A bespoke antisense oligonucleotide is a chemical
synthesis. A bespoke AAV is a plasmid build, a production run, a release-testing panel and
a regulatory filing. The per-patient cost is not comparable, and a programme that promises a
unique vector per patient is promising something the manufacturing model cannot deliver at
scale.

What *is* deliverable is a **haplotype-binned panel**: a small number of pre-manufactured
vectors covering the common allele combinations, with patients assigned to a bin by
sequence. `pvd` implements three tiers:

| Tier | Meaning | Manufacturing |
|---|---|---|
| **stock** | Synthetic payload, or reference allele with no patient-specific requirement | One lot serves everyone |
| **binned** | Patient's variant set matches a pre-defined bin exactly | Pre-manufactured lot per bin |
| **n-of-1** | Variant set matches no bin | Bespoke build; the expensive path, and the one to minimise |

The tiering is the point. A programme's economics are set by what fraction of patients land
in **stock** and **binned**, and the gate's job is to make that fraction as large as it can
honestly be.

---

## What this does not solve

Target engagement has repeatedly not been enough in Parkinson's. α-Synuclein
immunotherapy has engaged its target and missed its clinical endpoint twice; LRRK2 kinase
inhibition engaged its target and missed once. Every effect size above comes from a model,
and most of those models create pathology by **AAV-overexpressing α-synuclein** — flooding
the neuron with substrate, which is precisely the design most likely to flatter a clearance
or substrate-lowering intervention and least likely to resemble the slow, multifactorial
failure of an ageing human nigra.

There is also a problem no proteostasis lever touches: **host-to-graft propagation**.
Lewy pathology appears in grafted embryonic neurons years after transplantation, which means
the pathological species moves between cells. An intervention that protects the
transduced population does nothing for the untransduced one, and the therapeutic window for
all six levers is bounded by how much nigra remains at diagnosis — by which point a
substantial fraction is already gone.

None of that argues against the work. It argues for honesty about what a positive preclinical
result means.
