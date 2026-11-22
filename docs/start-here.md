# Start here — pvd explained in plain language

No biology class needed. If you can open a terminal, you can run this.

---

## 1. The problem this is about

Your cells are full of proteins. A protein is a long chain that has to fold into one exact
shape to do its job — like origami. Fold it right, it works. Fold it wrong, it's junk.

In **Parkinson's disease**, a protein called **alpha-synuclein** folds wrong. That alone
isn't the disaster. The disaster is that a wrongly-folded one **grabs its neighbours and
makes them fold wrong too**. One bad copy becomes two, two become four. The clump grows,
and the brain cells it grows inside — the ones that make a chemical called dopamine, which
you need to control movement — eventually die.

So it spreads a bit like a rumour. And like a rumour, the hard part isn't the first person
who said it. It's that everyone who hears it repeats it.

Here's the part that makes this fixable at all: **your cells already fight this**, all day,
your whole life. Three different ways:

| The cell's defence | What it does | Think of it as |
|---|---|---|
| **Barrier** | Makes it hard for the first clump to form | Not letting the rumour start |
| **Chaperone** | Grabs wrongly-folded proteins and refolds them | Correcting the rumour |
| **Clearance** | Shreds the bad ones and recycles the parts | Taking out the trash |

All three get weaker as you get older. That's a big part of why Parkinson's is a disease of
older people.

**pvd is a tool for designing medicines that try to make one of those three defences
stronger again.**

---

## 2. How do you make a defence stronger?

Each of those defences is run by proteins. Each protein is built from instructions in a
gene. So: **give the cell extra copies of the right gene**, and it builds more of that
protein, and that defence gets stronger.

That idea is called **gene therapy**. To do it you need two things.

**A delivery van.** You can't just sprinkle genes on someone. You use a hollowed-out virus
called **AAV** — a real virus with all its disease-causing parts removed, so all it can
still do is get inside a cell and drop off a package. Scientists have used AAV in approved
human medicines, so this part isn't science fiction.

**A way through the brain's security.** Your brain is wrapped in the **blood–brain
barrier**, a filter so strict that most drugs can't get in. Getting past it is one of the
hardest problems in all of medicine. The trick pvd uses: the barrier already has doors for
things the brain *needs*, like iron. One of those doors is a protein called **TfR1**. If you
redesign the virus's outer shell — its **capsid** — so it grabs TfR1, the barrier carries it
through, thinking it's doing its job. You inject into an arm vein and the medicine ends up in
the brain. No surgery.

**And a way to keep it in the right cells.** You don't want a brain gene switched on in
someone's liver. So the package includes a **promoter**, which is basically an address
label: an on-switch that only works in one cell type. `hSyn1` only works in neurons. You can
also add **detargeting** — short sequences that get the gene silenced in the wrong tissue,
like a "not for this address, return to sender" sticker.

Put it together and one finished design looks like this:

```
[ITR]—[promoter]—[the gene]—[stop]—[detargeting]—[polyA]—[ITR]
 ^^^     ^^^^^^^^   ^^^^^^^^           ^^^^^^^^^^^   ^^^^^^   ^^^^
 ends    on-switch  the payload        wrong-cell    "end     ends
 the                                   silencer      here"
 virus
 needs
```

That whole arrangement is a **cassette**, and designing one correctly is what pvd does.

---

## 3. So what does pvd actually do?

**pvd writes the blueprint.** It doesn't make medicine. Nothing you run on your laptop can
make medicine.

You tell it which defence you want to strengthen and give it some DNA sequence files. It
hands back a complete, labelled design — every piece in order, every length counted — plus
a list of warnings about things that could go wrong.

Think of it as the difference between designing a bridge and building one. pvd is the
drawing and the engineering check. The building happens in a lab, takes years, and needs
approval from a lot of people.

### The one rule that matters most

This is the real reason the program exists, so it's worth slowing down for.

You can use the **patient's own copy** of a gene, or the **standard reference copy** that
textbooks list. "Use the patient's own!" sounds obviously better and safer. Personalised!

It's often **wrong**, and here's why.

Everyone's genes have small differences. Mostly harmless. But sometimes a person's copy of a
gene is the *weak* copy — that's part of why they're sick. If you copy their weak version and
give them a thousand extra copies of it, you have carefully, expensively delivered **more of
the broken thing**.

It's like photocopying a page with a typo on it. Doing it a thousand times doesn't fix the
typo. You get a thousand typos.

So pvd has an **eligibility gate**: a safety checklist that runs *before* the patient's
sequence is allowed into the design. Six questions, and the patient's own copy has to pass
every single one:

1. Is this even a gene the patient has? (Some payloads are built from scratch in a lab — there's no personal version to use.)
2. Did you give me a reference copy to compare against?
3. Is the patient's copy actually *different* from the reference? (If it's identical, it's the same molecule — the question is meaningless.)
4. Is every difference outside the regions known to be dangerous?
5. Is this a gene on the X chromosome in a male patient? (Males have one X, so there's no second copy to compare against, and a difference can't be judged safe just by looking.)
6. Has a lab explicitly classified every difference as harmless?

**Fail any one, and pvd uses the reference copy instead and tells you exactly why.**

Rule 6 is the strict one. "Nobody has checked this difference yet" counts as a **fail**, not
a pass. It has to be unknown-until-proven-safe, because the alternative is treating "we
haven't looked" as "it's fine" — and the whole point of the gate is to catch exactly the
case where the patient's copy is the broken one.

---

## 4. Getting it running

Download one file:

```bash
curl -LO https://github.com/DrigandMossa/PVD/raw/main/pvd.pyz
chmod +x pvd.pyz
```

On Windows, download `pvd.pyz` from the repo and double-click it.

You need **Python 3.8 or newer** installed. Check with `python3 --version`. If you don't have
it, get it from [python.org](https://www.python.org/downloads/) — or grab a
[native binary](https://github.com/DrigandMossa/PVD/releases/latest) instead, which needs no
Python at all.

Then:

```bash
./pvd.pyz --help
```

Two ways to use it. `./pvd.pyz` with no arguments opens a **window** with menus — easier to
poke around in. Typing commands is better for following along here, and it's the only way to
get exactly the same result twice.

---

## 5. Your first run

pvd ships with fake practice data, so you don't need to find real DNA anywhere:

```bash
mkdir practice && cd practice
../pvd.pyz --example .
```

You now have a folder of pretend patient files. They're invented — made up specifically to
trip the safety rules so you can watch them work. Read `README.txt` in there; it lists what's
hidden in each one.

Now design something:

```bash
../pvd.pyz --program clearance \
  --patient lamp2a_patient_eligible.fasta \
  --reference lamp2a_reference.fasta \
  --classify classifications.tsv \
  --bins bins.tsv \
  --sex female \
  --out my-first-design
```

In English: *strengthen the trash-disposal defence, here's this patient's gene, here's the
standard one to compare against, here's the lab's verdict on their differences, they're
female, put the results in a folder called `my-first-design`.*

---

## 6. Reading what comes back

The first line is the answer:

```
pAAV-TfR1CapX-hSyn1>LAMP2A-pt-BIN-01  |  2,091 bp  |  clearance arm  |  payload LAMP2A
allele: patient   tier: binned  bin BIN-01
```

That name is a compressed description of the whole design:

| Part | Means |
|---|---|
| `pAAV` | It's an AAV design |
| `TfR1CapX` | The capsid that gets through the blood–brain barrier |
| `hSyn1>` | Switched on in neurons only |
| `LAMP2A` | The gene being delivered |
| `pt` | **The patient's own copy passed the gate** (`ref` would mean it didn't) |
| `BIN-01` | This patient matches pre-made batch #1 |

`2,091 bp` is the total length — 2,091 letters of DNA. Watch that number. **An AAV can only
carry about 4,700 letters.** Go over and it doesn't fail loudly; it packages a *cut-off*
version that looks fine and doesn't work. pvd warns at 4,400 and refuses past 4,700.

Then you get the parts list, each piece with its exact position, and a set of checks tagged
`[info]`, `[warn]` or `[error]`. **Read the errors.** They're the useful part.

### Why `bin` matters more than it looks

A genuinely custom medicine for one single person is called **n-of-1**. It is brutally
expensive — a custom-made virus means its own manufacturing run, its own safety testing, its
own paperwork. You can do that for a handful of people, not for a disease that affects
millions.

So pvd sorts patients into three buckets:

| Bucket | Meaning | Cost |
|---|---|---|
| `stock` | One standard design works for them | Cheapest. One batch, everyone |
| `binned` | They match a pre-made batch | Still cheap. Make a few batches, cover most people |
| `n-of-1` | They match nothing; needs a custom build | Very expensive. Keep this group small |

That's not a side feature. Whether a treatment reaches a million people or fifty comes down
to how many land in the first two buckets.

---

## 7. Watch the safety rules actually fire

This is the interesting part. `--gate` means *just run the checklist, don't build anything.*

**A dangerous difference gets caught:**

```bash
../pvd.pyz --program clearance \
  --patient lamp2a_patient_blocked.fasta \
  --reference lamp2a_reference.fasta \
  --classify classifications.tsv --gate
```

```
Allele delivered: reference
  [error] Q120W is in the shared-lumenal region ... Patient allele excluded.
  [error] Q120W is classified vus. Only benign or likely-benign variants may be
          delivered, so the patient allele is excluded.
```

It refused the patient's copy and said why, twice over. `vus` means "variant of uncertain
significance" — science's way of saying *we honestly don't know yet.* Which, per rule 6, is a
no.

(`Q120W` reads as: position 120 used to be a Q, now it's a W. That's how variants are
named — original letter, position, new letter. The practice files always plant the same
three, so you'll see the exact text above.)

**Being male changes the answer:**

```bash
../pvd.pyz --program clearance \
  --patient lamp2a_patient_eligible.fasta \
  --reference lamp2a_reference.fasta \
  --classify classifications.tsv --sex male --gate
```

Same patient file, same differences — now refused. The gene is on the X chromosome. A female
patient has a second copy to compare against; a male patient doesn't, so a difference can't
be called harmless just by looking at it.

**The medicine misses its target:**

```bash
../pvd.pyz --program barrier \
  --target snca_patient_epitope_hit.fasta \
  --target-reference snca_reference.fasta --gate
```

```
  [error] Patient SNCA carries 1 coding change(s) inside the NAC domain: A91D.
          The stock binder may bind this patient's alpha-synuclein poorly.
  [info]  Barrier payload(s) whose epitope window avoids every hit: NAC32.
```

The barrier medicine works by **grabbing** alpha-synuclein at one specific spot to stop it
clumping — like grabbing someone's wrist. This patient's alpha-synuclein is changed *at that
exact spot*. The grab won't hold.

And notice the second line: pvd doesn't just complain. It checked the other available
medicines and found one that grabs a different spot, which this patient's change doesn't
touch. **That** is what sequencing a patient is genuinely good for — not usually copying
their DNA into the medicine, but checking which medicine will actually work on them.

---

## 8. The five files you get

| File | What it's for |
|---|---|
| `.gb` | GenBank format — open it in real DNA software like SnapGene or Benchling |
| `.fasta` | Just the raw sequence, nothing else |
| `.svg` | A picture of the design. Open it in any browser |
| `.txt` | The parts list and all the warnings, as plain text |
| `.gate.txt` | The full safety-checklist decision and the reasoning |

Open the `.svg` first. Seeing the layout makes the rest click.

---

## 9. Things worth knowing

**The sequences in the library are placeholders.** Where pvd doesn't have a verified
sequence it writes runs of the letter `N`, which means "unknown base". That's deliberate — a
plausible-looking fake sequence would be far more dangerous than an obvious blank. The
lengths and the structure are real; some of the letters aren't yet.

**One capsid in the list is a trap, on purpose.** `AAV-PHP.eB` crosses the blood–brain
barrier brilliantly — **in mice**. It works by grabbing a mouse protein that humans don't
have in that role. It's in the list because it's famous and widely used in research, and pvd
reports it as an **error** for a human design. This is one of the most common ways a
beautiful mouse result turns out to mean nothing for people.

**None of these are cures.** Honestly: the strongest result in the research behind this tool
is in rats, in a model where scientists *caused* the problem artificially. The gap between
"worked in a rat" and "helps a person" has swallowed a lot of promising Parkinson's drugs
that did exactly what they were designed to do and still didn't make patients better.

**This is a design and teaching tool.** It can't make anything. Actually making a virus
needs a licensed lab and safety approval; actually treating a person needs years of testing
and government permission. If you want the real science behind every rule in the gate, it's
in the other files in this folder — [`proteostasis-levers.md`](proteostasis-levers.md) is
the place to start.

---

## 10. Quick reference

```bash
./pvd.pyz                       # the window
./pvd.pyz --help                # every option
./pvd.pyz --list                # every gene, capsid and part available
./pvd.pyz --example DIR         # practice files
./pvd.pyz --wizard              # asks you questions one at a time
./pvd.pyz --gate ...            # run the safety checklist only
./pvd.pyz --regimen lamp2a+vh14 # the recommended two-medicine combination
```

Stuck on a word? `--list` prints every available piece with a short description of what it
does and why it's there.
