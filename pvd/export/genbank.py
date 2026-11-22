"""GenBank export."""

import datetime
import re

from ..model import Design
from ..parts.elements import KINDS


def _ascii(text: str) -> str:
    return text.encode("ascii", "replace").decode().replace('"', "")


def to_genbank(d: Design) -> str:
    today = datetime.date.today()
    mon = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()[today.month - 1]
    # re.ASCII keeps the LOCUS name ASCII: GenBank has no encoding for anything else.
    locus = re.sub(r"[^\w.-]", "_", d.name, flags=re.ASCII)[:16]
    out = ["LOCUS       %-16s %7d bp    DNA     linear   SYN %02d-%s-%d"
           % (locus, d.total, today.day, mon, today.year),
           "DEFINITION  %s, designed with pvd (patient-sequence driven vector designer)." % _ascii(d.name),
           "COMMENT     Arm: %s. Payload: %s. Capsid: %s." % (d.program, d.payload, d.capsid)]
    if d.gate:
        out.append("COMMENT     Allele delivered: %s. Tier: %s%s."
                   % (d.gate.allele, d.gate.tier, (" (%s)" % d.gate.bin_id) if d.gate.bin_id else ""))
        if d.gate.variants:
            out.append("COMMENT     Coding variants: %s."
                       % _ascii(", ".join(v.label for v in d.gate.variants)))
    out.append("FEATURES             Location/Qualifiers")
    for f in d.features:
        out.append("     %-16s%d..%d" % (KINDS[f.kind][1], f.start, f.end))
        out.append('                     /label="%s"' % _ascii(f.name))
    out.append("ORIGIN")
    s = d.seq.lower()
    for i in range(0, len(s), 60):
        line = s[i:i + 60]
        out.append("%9d %s" % (i + 1, " ".join(line[j:j + 10] for j in range(0, len(line), 10))))
    out.append("//")
    return "\n".join(out) + "\n"
