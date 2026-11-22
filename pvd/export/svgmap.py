"""Linear SVG map of the cassette."""

from ..model import Design
from ..parts.elements import KINDS

W, H, PAD, BAR = 900, 240, 40, 34


def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def to_svg(d: Design) -> str:
    span = max(d.total, 1)
    inner = W - 2 * PAD
    y = 86
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
           'font-family="sans-serif">' % (W, H, W, H),
           '<title>%s</title>' % _esc(d.name),
           '<text x="%d" y="30" font-size="16" fill="#1a1a1a">%s</text>' % (PAD, _esc(d.name)),
           '<text x="%d" y="52" font-size="12" fill="#555">%s bp | %s arm | %s | capsid %s</text>'
           % (PAD, format(d.total, ","), d.program, _esc(d.payload), _esc(d.capsid))]
    if d.gate:
        out.append('<text x="%d" y="68" font-size="12" fill="#555">allele: %s | tier: %s%s</text>'
                   % (PAD, d.gate.allele, d.gate.tier,
                      (" | bin %s" % _esc(d.gate.bin_id)) if d.gate.bin_id else ""))
    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#f1efe8" stroke="#c9c6bb"/>'
               % (PAD, y, inner, BAR))
    flip = False
    for f in d.features:
        x = PAD + inner * (f.start - 1) / span
        w = max(inner * f.length / span, 1.2)
        color = KINDS[f.kind][0]
        out.append('<rect x="%.2f" y="%d" width="%.2f" height="%d" fill="%s" stroke="#ffffff" '
                   'stroke-width="0.5"><title>%s (%d..%d, %d bp)</title></rect>'
                   % (x, y, w, BAR, color, _esc(f.name), f.start, f.end, f.length))
        if w >= 6:
            ty = y + BAR + (34 if flip else 18)
            flip = not flip
            out.append('<line x1="%.2f" y1="%d" x2="%.2f" y2="%d" stroke="#b4b2a9" stroke-width="0.5"/>'
                       % (x + w / 2, y + BAR, x + w / 2, ty - 10))
            out.append('<text x="%.2f" y="%d" font-size="10" fill="#444" text-anchor="middle">%s</text>'
                       % (x + w / 2, ty, _esc(f.name[:28])))
    out.append('<text x="%d" y="%d" font-size="10" fill="#777">Elements drawn to scale. Runs of N have a '
               'typical length only.</text>' % (PAD, H - 12))
    out.append("</svg>")
    return "\n".join(out) + "\n"
