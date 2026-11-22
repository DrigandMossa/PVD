"""Write a runnable example patient set.

The sequences are synthetic: a reference CDS is generated deterministically and the patient
copy carries three planted amino-acid changes, one per region, so each branch of the gate
can be exercised without downloading anything.  They are not real human sequences and must
never be used as a reference for a real design.
"""

import os
import random
from typing import List

from ..parts.payloads import PAYLOADS, TARGET
from ..seqops import CODONS

HEADERS = {"LAMP2A": "LAMP2 synthetic reference isoform A - NOT a real sequence",
           "SNCA": "SNCA synthetic reference - NOT a real sequence"}


def _codons_for(aa: str) -> List[str]:
    return [c for c, a in CODONS.items() if a == aa] or ["GCT"]


def _make_cds(n_aa: int, seed: int) -> str:
    rnd = random.Random(seed)
    # sorted(), not set() order: iteration order for a set of strings depends on hash
    # randomisation, which differs per process.  Without the sort, a fixed seed still
    # produced a different reference CDS on every run, so the planted variants the README
    # and classifications.tsv name changed each time --example was called.
    pool = sorted(a for a in set(CODONS.values()) if a != "*")
    # ATG plus n_aa-1 sense codons translates to n_aa residues; TAA is the terminator.
    out = ["ATG"]
    for _ in range(n_aa - 1):
        out.append(rnd.choice(_codons_for(rnd.choice(pool))))
    out.append("TAA")
    return "".join(out)


def _mutate(cds: str, pos: int, new_aa: str) -> str:
    i = (pos - 1) * 3
    return cds[:i] + _codons_for(new_aa)[0] + cds[i + 3:]


def _wrap(seq: str) -> str:
    return "\n".join(seq[i:i + 70] for i in range(0, len(seq), 70))


def write_example(outdir: str) -> List[str]:
    os.makedirs(outdir, exist_ok=True)
    paths = []

    lamp_ref = _make_cds(PAYLOADS["LAMP2A"]["aa"], seed=11)
    # one benign change in the isoform-specific tail, one in the shared lumenal domain
    lamp_pat = _mutate(lamp_ref, 402, "K")
    tail_label = "%s402%s" % (lamp_ref and _aa_at(lamp_ref, 402), "K")
    lamp_pat_bad = _mutate(lamp_pat, 120, "W")
    shared_label = "%s120%s" % (_aa_at(lamp_ref, 120), "W")

    snca_ref = _make_cds(TARGET["aa"], seed=23)
    snca_pat = _mutate(snca_ref, 120, "R")          # outside the NAC epitope
    # Residue 91 is inside the VH14 window (NAC 61-95) but outside NAC32's (53-87), so the
    # gate should block VH14-PEST and offer NAC32 as the alternative.
    snca_pat_bad = _mutate(snca_ref, 91, "D")
    epi_label = "%s91%s" % (_aa_at(snca_ref, 91), "D")

    files = {
        "lamp2a_reference.fasta": ">%s\n%s\n" % (HEADERS["LAMP2A"], _wrap(lamp_ref)),
        "lamp2a_patient_eligible.fasta":
            ">LAMP2 patient A - one tail change (%s)\n%s\n" % (tail_label, _wrap(lamp_pat)),
        "lamp2a_patient_blocked.fasta":
            ">LAMP2 patient B - tail change plus a shared lumenal change (%s)\n%s\n"
            % (shared_label, _wrap(lamp_pat_bad)),
        "snca_reference.fasta": ">%s\n%s\n" % (HEADERS["SNCA"], _wrap(snca_ref)),
        "snca_patient_intact.fasta": ">SNCA patient A - epitope intact\n%s\n" % _wrap(snca_pat),
        "snca_patient_epitope_hit.fasta":
            ">SNCA patient C - change inside VH14's epitope window (%s)\n%s\n"
            % (epi_label, _wrap(snca_pat_bad)),
        "classifications.tsv":
            "# variant<TAB>classification: benign, likely-benign, vus, likely-pathogenic, pathogenic\n"
            "%s\tbenign\n%s\tvus\n" % (tail_label, shared_label),
        "bins.tsv":
            "# bin_id<TAB>variant[,variant...]   empty means the reference haplotype\n"
            "BIN-REF\t\nBIN-01\t%s\n" % tail_label,
        "README.txt": _readme(tail_label, shared_label, epi_label),
    }
    for name, text in files.items():
        p = os.path.join(outdir, name)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        paths.append(p)
    return paths


def _aa_at(cds: str, pos: int) -> str:
    return CODONS.get(cds[(pos - 1) * 3:(pos - 1) * 3 + 3], "X")


def _readme(tail: str, shared: str, epi: str) -> str:
    return """Example patient set for pvd
===========================

SYNTHETIC SEQUENCES.  Generated deterministically to exercise the gate.  They are not real
human sequences: never use them as a reference for a real design.

Planted variants
  %s   isoform-specific tail, classified benign      -> patient allele should be ELIGIBLE
  %s   shared lumenal domain, classified vus         -> patient allele should be BLOCKED
  %s   inside VH14's NAC window but not NAC32's      -> VH14 FAILS, NAC32 offered

Try these, in order
  1. Patient allele clears the gate and matches a qualified bin:
     pvd --program clearance --patient lamp2a_patient_eligible.fasta \\
         --reference lamp2a_reference.fasta --classify classifications.tsv \\
         --bins bins.tsv --sex female --out out1

  2. Same patient, male: X-linked hemizygosity forces the reference allele:
     pvd --program clearance --patient lamp2a_patient_eligible.fasta \\
         --reference lamp2a_reference.fasta --classify classifications.tsv \\
         --bins bins.tsv --sex male --gate

  3. Shared lumenal variant blocks the patient allele whatever the classification:
     pvd --program clearance --patient lamp2a_patient_blocked.fasta \\
         --reference lamp2a_reference.fasta --classify classifications.tsv --gate

  4. Barrier arm, epitope intact:
     pvd --program barrier --target snca_patient_intact.fasta \\
         --target-reference snca_reference.fasta --out out4

  5. Barrier arm, epitope hit: the stock binder is reported as compromised and an
     alternative payload is suggested:
     pvd --program barrier --target snca_patient_epitope_hit.fasta \\
         --target-reference snca_reference.fasta --gate

  6. The recommended two-vector regimen in one run:
     pvd --regimen lamp2a+vh14 --patient lamp2a_patient_eligible.fasta \\
         --reference lamp2a_reference.fasta --target snca_patient_intact.fasta \\
         --target-reference snca_reference.fasta --classify classifications.tsv \\
         --bins bins.tsv --sex female --out out6
""" % (tail, shared, epi)
