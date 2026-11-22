"""Pure sequence and option helpers.  No dependencies on the parts library."""

import re
from typing import List, Tuple

_COMP = {"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}

_BASES = "TCAG"
# Standard genetic code, in the canonical TCAG x TCAG x TCAG order.
_AAS = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODONS = dict(zip([a + b + c for a in _BASES for b in _BASES for c in _BASES], _AAS))


def clean_sequence(text: str) -> Tuple[str, int]:
    """Strip FASTA headers, whitespace and digits; U -> T. Returns (ACGTN, removed)."""
    text = re.sub(r"^>.*$", "", text or "", flags=re.M)
    text = re.sub(r"[\s\d]", "", text).upper().replace("U", "T")
    kept = re.sub(r"[^ACGTN]", "", text)
    return kept, len(text) - len(kept)


def read_fasta(text: str) -> List[Tuple[str, str]]:
    """Parse FASTA into [(header, cleaned_sequence)].  Headerless text becomes one record."""
    records: List[Tuple[str, List[str]]] = []
    for line in (text or "").splitlines():
        if line.startswith(">"):
            records.append((line[1:].strip(), []))
        elif line.strip():
            if not records:
                records.append(("", []))
            records[-1][1].append(line)
    return [(h, clean_sequence("".join(body))[0]) for h, body in records]


def revcomp(seq: str) -> str:
    return "".join(_COMP[c] for c in reversed(seq))


def gc_percent(seq: str) -> int:
    return round(100 * sum(c in "GC" for c in seq) / len(seq)) if seq else 0


def translate(seq: str, stop_at_stop: bool = True) -> str:
    """Translate a CDS from the first base.  X for any codon containing N."""
    out = []
    for i in range(0, len(seq) - len(seq) % 3, 3):
        codon = seq[i:i + 3]
        aa = "X" if "N" in codon else CODONS.get(codon, "X")
        if aa == "*" and stop_at_stop:
            break
        out.append(aa)
    return "".join(out)


def count_overlapping(seq: str, motif: str) -> int:
    n, i = 0, seq.find(motif)
    while i >= 0:
        n += 1
        i = seq.find(motif, i + 1)
    return n


def pick(value: str, options, what: str) -> str:
    """Case-insensitive choice from a dict/list, with a helpful error."""
    for opt in options:
        if str(opt).lower() == str(value).lower():
            return opt
    raise ValueError("Unknown %s %r. Choose from: %s" % (what, value, ", ".join(map(str, options))))
