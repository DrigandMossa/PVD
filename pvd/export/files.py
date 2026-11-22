"""Write every export format for a design to a folder."""

import os
import re
from typing import List

from ..model import Design
from .fasta import to_fasta
from .gatereport import to_gate_report
from .genbank import to_genbank
from .summary import to_summary
from .svgmap import to_svg


def write_outputs(d: Design, outdir: str, shared_end: int = 0) -> List[str]:
    os.makedirs(outdir, exist_ok=True)
    stem = re.sub(r"[^\w.-]+", "_", d.name).strip("_") or "vector"
    items = ((".gb", to_genbank(d)), (".fasta", to_fasta(d)), (".svg", to_svg(d)),
             (".txt", to_summary(d)), (".gate.txt", to_gate_report(d, shared_end)))
    paths = []
    for ext, text in items:
        p = os.path.join(outdir, stem + ext)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        paths.append(p)
    return paths
