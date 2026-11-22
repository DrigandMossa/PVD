"""Patient and reference sequence intake, plus the classification and bin side files."""

import os
from typing import Dict, List, Tuple

from ..seqops import clean_sequence, read_fasta


def read_arg(value: str) -> str:
    """A path to a text/FASTA file, or the sequence itself."""
    if not value:
        return ""
    if os.path.isfile(value):
        with open(value, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    return value


def select_cds(text: str, gene: str) -> Tuple[str, str]:
    """Pick the CDS for a gene from FASTA text.

    One record is used as-is.  With several records the first whose header mentions the
    gene name wins, so a single multi-FASTA can carry the payload gene and SNCA together.
    Returns (sequence, header).
    """
    records = read_fasta(text)
    if not records:
        return "", ""
    if len(records) == 1:
        return records[0][1], records[0][0]
    key = (gene or "").lower()
    for header, seq in records:
        if key and key in header.lower():
            return seq, header
    return records[0][1], records[0][0]


def read_classifications(path: str) -> Dict[str, str]:
    """TSV or CSV of `variant<TAB>classification`, one per line; # comments allowed.

    Accepted classifications: benign, likely-benign, vus, likely-pathogenic, pathogenic.
    Anything else is rejected rather than silently treated as benign.
    """
    allowed = {"benign", "likely-benign", "vus", "likely-pathogenic", "pathogenic"}
    out: Dict[str, str] = {}
    if not path:
        return out
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.replace(",", "\t").split("\t") if p.strip()]
            if len(parts) < 2:
                raise ValueError("%s line %d: need 'variant<TAB>classification'." % (path, n))
            label, call = parts[0], parts[1].lower().replace("_", "-").replace(" ", "-")
            if call not in allowed:
                raise ValueError("%s line %d: classification %r is not one of %s."
                                 % (path, n, parts[1], ", ".join(sorted(allowed))))
            out[label] = call
    return out


def read_bins(path: str) -> Dict[str, List[str]]:
    """TSV of `bin_id<TAB>variant[,variant...]`; an empty variant field means the reference
    haplotype.  A patient is assigned to the bin whose variant set matches theirs exactly.
    """
    out: Dict[str, List[str]] = {}
    if not path:
        return out
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) == 1:
                parts = line.split(None, 1)
            bin_id = parts[0].strip()
            if not bin_id:
                raise ValueError("%s line %d: missing bin id." % (path, n))
            raw = parts[1] if len(parts) > 1 else ""
            out[bin_id] = [v.strip() for v in raw.replace(";", ",").split(",") if v.strip()]
    return out


def looks_like_cds(seq: str) -> Tuple[bool, str]:
    """Cheap sanity check before the gate bothers translating."""
    s = clean_sequence(seq)[0]
    if not s:
        return False, "no A, C, G, T or N found"
    if len(s) % 3:
        return False, "length %d bp is not a multiple of 3" % len(s)
    return True, ""
