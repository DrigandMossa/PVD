"""FASTA export."""

from ..model import Design


def to_fasta(d: Design) -> str:
    head = ">%s %s bp | %s arm | payload %s | capsid %s" % (
        d.name, d.total, d.program, d.payload, d.capsid)
    body = "\n".join(d.seq[i:i + 70] for i in range(0, len(d.seq), 70))
    return head + "\n" + body + "\n"
