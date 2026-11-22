# pvd — patient-sequence driven vector designer

Build AAV cassettes for the three Parkinson's proteostasis arms — **clearance**, **barrier**
and **chaperone** — from a patient's own sequenced coding sequence, with an eligibility gate
applied *before* the patient allele is allowed into a payload.

Standard library only, Python 3.8+. Same shape as [CVD](https://github.com/DrigandMossa/CVD):
a window and a command-line tool in one, with GenBank/FASTA/SVG/summary exports and a
single-file PyInstaller build.

> **Research design tool.** Library elements use typical lengths and are written as runs of
> `N` until verified sequences are supplied. Producing virus requires institutional
> biosafety approval; a clinical product requires GMP manufacturing, preclinical safety
> data and regulatory authorization. Nothing here is a clinical protocol.

---

## Why the gate is the point of the tool

"Patient-derived vector" sounds unambiguously safer. For an **augmentation** payload it is
not. The arm works by supplying more functional protein, so if the patient's own allele is
part of why their clearance capacity is low, copying it delivers the defect at higher dose.
The reference sequence is frequently the better molecule.

That hazard is sharpest for `LAMP2A`, the recommended clearance payload:

* `LAMP2` is at **Xq24** and its loss causes **Danon disease**, with pathogenic variants
  reported across every exon.
* **Male patients are hemizygous** — one allele, no comparison, no mosaic rescue.
* Exon 9 splicing produces isoforms **2A / 2B / 2C**, and Danon is mainly 2B-driven. A
  variant restricted to the 2B-specific tail does not touch a 2A payload; a variant in the
  **shared lumenal domain** does.

So pvd's default answer is *reference*, and a patient allele is delivered only when **all**
of these hold:

1. the payload is a human gene the patient actually carries (not a synthetic binder)
2. a reference CDS was supplied and both translate to the same length
3. at least one coding difference exists (otherwise reference is the same molecule)
4. no difference falls in a region the payload's rule excludes
5. the gene is not X-linked in a male patient carrying a coding variant
6. every difference carries an explicit **benign** or **likely-benign** classification

**Unclassified means reference.** Without rule 6, "patient-derived" would mean
"risk-allele-amplifying" for some fraction of patients, and the sequencing step meant to add
safety would remove it. pvd enforces the gate; it does **not** classify variants for you.

### Match at the amino-acid level only

Synonymous variants create no new peptide, so matching the patient's codons buys nothing
immunologically and costs the cassette its codon optimisation. pvd compares **translations**,
not nucleotides, reports the synonymous codon count for information, and keeps the optimised
cassette.

---

## Install

```bash
git clone https://github.com/DrigandMossa/PVD
cd PVD
pip install -e .          # optional; `python -m pvd` works from the source tree
```

No runtime dependencies. `tkinter` is needed only for the window and is not pip-installable
— it ships with CPython on Windows and macOS; on Debian/Ubuntu `sudo apt install python3-tk`.
Every command-line mode works without it.

### Stand-alone executable

```bash
pip install -r requirements-dev.txt
pyinstaller pvd.spec       # -> dist/pvd  (dist/pvd.exe on Windows)
```

`console=True` is deliberate: a windowed build opens the designer but silently discards the
output of `--list`, `--gate` and one-shot runs.

---

## Quick start

```bash
python -m pvd --example demo     # synthetic patient set that exercises every gate branch
cat demo/README.txt
python -m pvd --list             # arms, payloads, capsids, parts
python -m pvd                    # graphical window
```

The recommended two-vector regimen, gated, in one run:

```bash
python -m pvd --regimen lamp2a+vh14 \
    --patient demo/lamp2a_patient_eligible.fasta \
    --reference demo/lamp2a_reference.fasta \
    --target demo/snca_patient_intact.fasta \
    --target-reference demo/snca_reference.fasta \
    --classify demo/classifications.tsv \
    --bins demo/bins.tsv \
    --sex female --out out
```

Gate only, no vector:

```bash
python -m pvd --program clearance --patient pt.fasta --reference ref.fasta \
    --classify calls.tsv --sex male --gate
```

---

## The three arms

| Arm | Payloads | Default | Why it sits where it does |
|---|---|---|---|
| `clearance` | LAMP2A, TFEB, Beclin-1 | `LAMP2A` | Strongest published effects; LAMP2A has nonhuman-primate data and no transcription-factor liability |
| `barrier` | VH14-PEST, NAC32 | `VH14-PEST` | Acts **inside** the neuron, where nucleation happens and extracellular antibody drugs could not reach. Smallest payload |
| `chaperone` | DNAJB6b, DNAJB1, HSPH1, HSPA8 | `DNAJB6b` | Weakest published effect sizes in Parkinson's; sequenced second |

Two-vector regimens via `--regimen`:

* `lamp2a+vh14` — clearance + barrier. Two points on the same kinetic curve rather than one
  node pushed harder. Both payloads are small, so each vector keeps headroom for
  detargeting and dose control.
* `disaggregase` — DNAJB1 + HSPH1, relying on endogenous HSPA8 as the motor. 3.6 kb of CDS:
  the pair spends the whole packaging budget.

### Synthetic payloads have no patient allele

`VH14-PEST` and `NAC32` are **selected synthetic binders**, not genes the patient carries.
There is nothing to insert from their genome. The patient's sequence still matters, and more
usefully: pvd verifies the **target epitope** in their `SNCA`, because a coding change inside
it can cost the stock binder its target. If a hit lands inside one binder's window but
outside another's, pvd names the alternative.

| Payload | Epitope window in SNCA |
|---|---|
| VH14-PEST | NAC domain, residues 61–95 |
| NAC32 | residues 53–87 |

pvd never lets a barrier cassette borrow the payload-gene FASTA on the command line as its
insert — supply the construct with `--override goi=FILE`.

---

## Input files

**Patient / reference CDS** — FASTA or bare sequence, as a path or inline. A multi-FASTA may
carry several genes: the first record whose header mentions the gene name wins, so one file
can hold the payload gene and `SNCA` together.

**`--classify FILE`** — one variant per line:

```
# variant<TAB>classification
A402K	benign
P120W	vus
```

Accepted: `benign`, `likely-benign`, `vus`, `likely-pathogenic`, `pathogenic`. Anything else
is rejected rather than silently treated as benign.

**`--bins FILE`** — the qualified haplotype panel:

```
# bin_id<TAB>variant[,variant...]   empty means the reference haplotype
BIN-REF	
BIN-01	A402K
```

A patient is assigned to the bin whose variant set matches theirs **exactly**.

---

## Tiers

Designing a patient-specific cassette is cheap; manufacturing it is not. An N-of-1 AAV is a
dedicated production campaign with a full release panel, months from sequence to dose — the
bespoke-ASO precedent does not transfer. So pvd reports a tier rather than assuming one:

| Tier | When | Meaning |
|---|---|---|
| `autologous` | `--route autologous` | Cassette engineered into the patient's own iPSC-derived progenitors during manufacturing. Immune matching is total, QC happens on the clone, and the capsid/BBB/serology constraints do not apply |
| `binned` | patient haplotype matches a qualified bin | A **stocked** vector covers this patient. Most of the matching benefit at conventional cost |
| `n-of-1` | eligible but no bin matches | Bespoke campaign. Consider adding the haplotype to the panel instead |
| `stock` | synthetic binder, in-vivo route | No allele question; the stock construct is used |
| `reference` | the gate blocked the patient allele | Not a fallback — often the better molecule |

---

## Options

| Option | Default | Notes |
|---|---|---|
| `--program` | `clearance` | `clearance`, `barrier`, `chaperone` |
| `--payload` | arm default | must belong to the chosen arm |
| `--regimen` | — | `lamp2a+vh14`, `disaggregase` |
| `--patient` / `--reference` | — | payload-gene CDS, file or sequence |
| `--target` / `--target-reference` | — | patient / reference `SNCA`, for epitope checks |
| `--classify` / `--bins` | — | side files above |
| `--sex` | `unknown` | `male` forces reference for X-linked genes with a variant |
| `--route` | `in-vivo` | or `autologous` |
| `--shared-end N` | library value | override the shared/isoform boundary in the region map |
| `--capsid` | `TfR1-CapX` | see `--list` |
| `--promoter` | arm default | glial promoters warn without neuronal detargeting |
| `--detarget` | `miR-122x2` | comma-separated, or `none` |
| `--riboswitch` | off | K19 tetracycline aptazyme in the 3′ UTR |
| `--sc` | off | self-complementary AAV; capacity drops to ~2.4 kb |
| `--no-kozak` | off | leave out the Kozak sequence |
| `--override ID=SEQ` | — | verified sequence for a placeholder element (repeatable) |
| `--out` | `.` | output folder |
| `--gate` | off | decision trail only, no vector |
| `--strict` | off | exit 1 if any check reports an error |

Exit codes: `0` success, `1` `--strict` with errors, `2` bad input, `130` cancelled.

---

## Outputs

Five files per vector, named from the generated or supplied vector name:

| File | Contents |
|---|---|
| `.gb` | GenBank with features, plus the allele/tier/variant decision in `COMMENT` lines |
| `.fasta` | full cassette sequence |
| `.svg` | linear map, elements to scale, hover titles |
| `.txt` | element table and all design checks |
| `.gate.txt` | the eligibility transcript: region map, every variant, the decision trail, the rules applied, and the RefSeq to confirm against |

---

## Caveats the tool states in its own output

* **Region boundaries are approximate.** They route a variant to the right rule but are not a
  substitute for the RefSeq exon table. Confirm them, or override with `--shared-end`.
* **Lengths marked `approx`** in `--list` are typical values; supply the real CDS and pvd uses
  its length instead.
* **`AAV-PHP.eB` is a mouse tool.** Its BBB crossing depends on LY6A, which has no human
  ortholog. pvd raises an error, not a warning.
* **The riboswitch is an on-switch above a leaky floor**, not an off-switch. It cannot retire
  an administered vector.
* **Patient-matching cannot be validated preclinically** — a model has no patient to match.
  Carry it as a secondary endpoint (IFN-γ ELISPOT, anti-drug antibody titre, durability of
  expression), not as a de-risked design choice. pvd prints this on every run.

---

## Tests

```bash
python -m pytest tests/ -q
```

Covers each gate branch: identical allele, eligible tail variant, bin matching, shared-domain
block, unclassified block, hemizygous male, watch-list position, length mismatch, DNAJB6 G/F
domain, synthetic-payload epitope handling, the borrow-prevention rule, AAV capacity and the
PHP.eB guard.
