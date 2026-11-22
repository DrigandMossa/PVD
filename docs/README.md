# Design notes

The scientific basis for the code. Every rule the eligibility gate enforces is justified in
one of these documents, and each is written to be read on its own.

| Document | What it covers | What in the code it justifies |
|---|---|---|
| [`proteostasis-levers.md`](proteostasis-levers.md) | The three-arm framework (barrier / chaperone / clearance), six intervention points, comparative ranking, and the patient-sequence architecture | `pvd/parts/programs.py`, the whole of `pvd/patient/`, the tier model, the recommended regimen |
| [`disaggregase-program.md`](disaggregase-program.md) | HSPA8 + DNAJB1 + HSPH1 as a disaggregase, the AAV packaging arithmetic that defeats it as one vector, and three mechanism-specific liabilities | the `disaggregase` regimen, the HSPA8 uncoating-ATPase note, `AAV_LIMIT` / `SC_LIMIT` checks |
| [`hsf1-program.md`](hsf1-program.md) | HSF1 upregulation across Alzheimer's, Parkinson's and prion disease; why its Parkinson's arm is the weakest of the three | the `chaperone` arm's payload ranking and the HSF1 entry in `pvd/parts/payloads.py` |

## The short version

Soluble α-synuclein is metastable, not stable — the amyloid state appears to be
thermodynamically favoured. What keeps a healthy neuron on the soluble side is three
things, all of which erode with age: **high kinetic barriers** to nucleation, **chaperone
buffering** of the species that do form, and **clearance** of what gets through.

Each is separately addressable, and gene therapy can work in two directions on each —
supply the effector, or remove what suppresses it.

Three conclusions from these notes drive the code:

1. **Clearance has the strongest published effects and the chaperone arm has the weakest.**
   LAMP2A is the lead payload and the only candidate with nonhuman-primate data; HSF1,
   which the earliest program was built on, gave roughly 20% dopaminergic neuron survival —
   no better than HSP70 alone.
2. **Patient sequence is worth collecting for assignment and epitope verification, not for
   payload construction.** This is why `pvd` defaults to the reference allele and treats a
   patient allele as something that must earn its way in.
3. **For an augmentation payload, the reference sequence is often the better molecule.**
   Copying a hypomorphic allele delivers the defect at higher dose. `LAMP2` makes this
   sharp: X-linked at Xq24, loss causes Danon disease, and hemizygous males have no
   comparison allele.

## Caveats that apply to all three

* **Region boundaries in the payload library are approximate.** They route a variant to the
  right rule but are not a substitute for the RefSeq exon table.
* **Published effect sizes come mostly from AAV–α-synuclein overexpression models**, which
  create pathology by flooding the neuron with substrate — precisely the design most likely
  to flatter a clearance or substrate-lowering intervention.
* **Target engagement has repeatedly not been enough in Parkinson's.** α-Synuclein
  immunotherapy twice and LRRK2 kinase inhibition once have all engaged their target and
  missed clinically. Nothing in these notes escapes that base rate.
* **Research design notes, not clinical protocols.** See the licence and the warning in the
  top-level [README](../README.md).
