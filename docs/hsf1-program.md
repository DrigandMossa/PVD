# HSF1 Upregulation Gene Therapy Program — Alzheimer's, Parkinson's and Prion Disease

> Research design notes. Not a clinical protocol and not medical advice.

## Rationale

HSF1 is the master transcriptional regulator of the heat-shock response. One transcription
factor raises the whole chaperone network — HSP70 family, HSP40/J-domain cochaperones,
HSP90, small HSPs — rather than a single component. For a class of diseases in which the
failure is network-wide proteostatic collapse rather than loss of one chaperone, the
upstream regulator is the obvious target.

Across the three indications the shared logic is that each is a protein-misfolding disease
with a distinct substrate and a distinct dominant cell type, and the chaperone network acts
on all of them:

| Disease | Substrate | Dominant cell type | Promoter |
|---|---|---|---|
| Alzheimer's | Tau, Aβ | Neurons; microglia for clearance | `hSyn1`; `CD68` / `hHexB` |
| Parkinson's | α-Synuclein | Nigral dopaminergic neurons | `hSyn1` |
| Prion disease | PrP^Sc | Neurons; astrocytes amplify | `hSyn1`; `gfaABC1D` |

## Construct design

### Escaping the brake

Wild-type HSF1 is held inactive by phosphorylation of **S303 and S307** in its regulatory
domain, which recruits the **NEDD4/CK2** degradation axis. Overexpressing wild-type HSF1
therefore buys much less than the copy number suggests — the cell has a mechanism for
putting it back down.

Two constitutively active designs escape it:

* **S303A / S307A** — point substitutions that remove the phosphosites while leaving the
  protein otherwise intact. The conservative choice.
* **ΔRD** — deletion of the regulatory domain. Stronger, and correspondingly less
  controllable.

Both are small enough to package comfortably: HSF1 is 529 aa, ~1.6 kb of CDS, leaving room
for a full promoter, Kozak, polyA and a regulatory element inside the ~4.7 kb AAV limit.

### Cell-type restriction

A broad capsid needs a narrow promoter. `hSyn1` for neurons, `gfaABC1D` for astrocytes,
`MBP` for oligodendrocytes, `CD68` or `hHexB` for microglia, with `miR-122` sites to silence
hepatic expression after intravenous dosing and `miR-124` or a `4x6T` cassette for CNS
compartment restriction.

### Regulation is not optional here

HSF1 is an **oncogenicity-class transcription factor**. Constitutive activation is a known
feature of tumour biology, and the construct is being delivered permanently into long-lived
post-mitotic cells by a vector that cannot be withdrawn. A **K19 tetracycline-responsive
riboswitch** gives a ligand-controlled off switch at the cost of cassette space and a drug
dependency. For this payload the cost is worth paying.

## Delivery

A **TfR1-binding capsid** — BI-hTFR1, TfR1-CapX, BI-TfR1 CapX — transcytoses the human
blood–brain barrier after intravenous dosing, giving broad CNS distribution without
neurosurgery. **AAV-PHP.eB must not be carried into a human program**: it works through
**LY6A**, a mouse-strain-specific allele with no human orthologue serving that function.
`pvd` reports PHP.eB as an error.

Alternatives: Dyno-9zh and ALPL-directed capsids; MR-guided focused ultrasound for
transient focal barrier opening; intraputaminal convection-enhanced delivery where a
restricted volume of distribution is acceptable or desirable.

Pre-existing anti-AAV neutralising antibody titre must be measured before assignment —
seropositivity excludes a substantial fraction of patients from systemic dosing.

## Evidence, and why this program ranks last

In published nigral work, constitutively active HSF1 gave roughly **20% dopaminergic neuron
survival benefit — no better than HSP70 alone**. The network-level intervention did not beat
its own single downstream component. In tauopathy models the direction of effect is
favourable (Kim et al., *PLoS Genetics*, 2017), and an HSF1 variant termed **H-BH** was
characterised in *Molecular Therapy* 2008;16(6):1048-55 (PubMed 18398426).

Set against the clearance arm — LAMP2A with nonhuman-primate data, TFEB with reported
near-complete nigral protection — a 20% survival benefit carried by an oncogenicity-class
transcription factor is the weakest risk-adjusted position in the portfolio. This program
was built first in this project; the comparative work that followed moved it last, and
[`proteostasis-levers.md`](proteostasis-levers.md) records that reordering rather than
defending the original ranking.

What HSF1 retains is **breadth**. It is the only payload here that is substrate-agnostic:
the same construct is a plausible intervention in tauopathy, synucleinopathy and prion
disease, because what it raises is general folding capacity rather than a
substrate-specific activity. If the goal is one vector across three indications, this is
the only candidate. If the goal is the largest effect in Parkinson's, it is not.

## Prion disease is a special case

Two features set it apart. First, the substrate is **self-templating and transmissible**,
so the kinetics are dominated by secondary nucleation on existing PrP^Sc rather than by
primary nucleation — which favours interventions that lower substrate or clear seeds over
interventions that raise folding capacity. Second, **astrocytes amplify** prion
replication, so a neuron-only promoter leaves a replicating compartment untouched; a dual
`hSyn1` + `gfaABC1D` approach, or a broader promoter with miRNA detargeting, is the better
match.

Chaperone capacity alone is unlikely to be sufficient against a self-propagating substrate.
The strong preclinical results in prion disease have come from **lowering PrP** — the
substrate-reduction lever — which is the same conclusion the Parkinson's analysis reaches by
a different route.
