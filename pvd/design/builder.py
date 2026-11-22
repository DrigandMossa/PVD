"""Assemble a Design from a Config: run the gate, lay out the cassette, run the checks."""

import re
from typing import List, Tuple

from ..model import Config, Design, Feature, Gate
from ..parts.elements import (AAV_LIMIT, AAV_WARN, BUILT_IN_IDS, CAPSIDS, DETARGET,
                              GLIAL_PROMOTERS, ITR_LEN, KOZAK_SEQ, NEURON_DETARGET, POLYA,
                              PROMOTERS, RIBOSWITCH_LEN, SC_LIMIT, STOP_SEQ)
from ..parts.payloads import PAYLOADS
from ..parts.programs import PROGRAMS
from ..patient.gate import run_gate
from ..patient.parse import select_cds
from ..seqops import clean_sequence, pick
from .checks import check_insert


def build_design(cfg: Config, shared_end: int = 0) -> Design:
    program = pick(cfg.program, PROGRAMS, "program")
    P = PROGRAMS[program]
    payload = pick(cfg.payload or P["default"], PAYLOADS, "payload")
    if PAYLOADS[payload]["arm"] != program:
        raise ValueError("Payload %s belongs to the %s arm, not %s. Payloads for %s: %s"
                         % (payload, PAYLOADS[payload]["arm"], program, program, ", ".join(P["payloads"])))
    capsid = pick(cfg.capsid, CAPSIDS, "capsid")
    prom = pick(cfg.promoter or P["promoter"], PROMOTERS, "promoter")
    polya = pick(cfg.polya or "synthetic", POLYA, "polyadenylation signal")
    detarget = [pick(d, DETARGET, "detargeting cassette") for d in cfg.detarget]

    pay = PAYLOADS[payload]
    gate: Gate = run_gate(cfg, payload, shared_end)
    msgs: List[Tuple[str, str]] = []

    # ---- choose the coding sequence that actually goes in -------------
    insert, bad = "", 0
    if pay["synthetic"]:
        # No patient or reference allele exists for a selected binder, and the payload-gene
        # FASTA on the command line belongs to a different payload: never borrow from it.
        # The construct arrives only via --override goi=FILE.
        source = "placeholder"
    elif gate.used_patient:
        insert, bad = clean_sequence(select_cds(cfg.patient_seq, pay["gene"])[0])
        source = "patient allele"
    elif cfg.reference_seq:
        insert, bad = clean_sequence(select_cds(cfg.reference_seq, pay["gene"])[0])
        source = "reference allele"
    else:
        source = "placeholder"

    feats: List[Feature] = []
    cassette = False

    def add(fid, name, kind, length, seq=None):
        feats.append(Feature(fid, name, kind, length, seq, cassette))

    add("itr5", "5' ITR", "itr", ITR_LEN)
    cassette = True
    add("prom", prom + " promoter", "promoter", PROMOTERS[prom])
    if cfg.kozak:
        add("kozak", "Kozak", "reg", len(KOZAK_SEQ), KOZAK_SEQ)
    label = "%s (%s)" % (payload, source if source != "placeholder" else "typical length")
    add("goi", label, "cds", len(insert) or pay["cds"], insert or None)
    if not insert or insert[-3:] not in ("TAA", "TAG", "TGA"):
        add("stop", "Stop (TAA)", "stop", len(STOP_SEQ), STOP_SEQ)
    for d in detarget:
        add("dt_" + re.sub(r"\W+", "", d).lower(), d + " target sites", "detarget", DETARGET[d])
    if cfg.riboswitch:
        add("k19", "K19 tetracycline riboswitch", "reg", RIBOSWITCH_LEN)
    if polya != "none":
        add("pa", polya + " polyA", "polya", POLYA[polya])
    cassette = False
    add("itr3", "3' ITR", "itr", ITR_LEN)

    # ---- user overrides (verified sequences for placeholder elements) --
    ids = {f.id for f in feats}
    for fid, raw in cfg.overrides.items():
        if fid in BUILT_IN_IDS and fid != "goi":
            raise ValueError("Element %r is built in and cannot be overridden." % fid)
        if fid not in ids:
            raise ValueError("No element with id %r in this design. Ids: %s"
                             % (fid, ", ".join(sorted(ids))))
        s, _ = clean_sequence(raw)
        if not s:
            raise ValueError("Override for %r contains no A, C, G, T or N." % fid)
        f = next(f for f in feats if f.id == fid)
        f.seq, f.length, f.custom = s, len(s), True
        if fid == "goi":
            insert = s

    pos, parts = 1, []
    for f in feats:
        if not f.seq:
            f.seq = "N" * f.length
        f.start, f.end = pos, pos + f.length - 1
        pos += f.length
        parts.append(f.seq)
    seq = "".join(parts)

    # ---- design checks -----------------------------------------------
    msgs.extend(gate.findings)
    if bad:
        msgs.append(("warn", "%d non-nucleotide character(s) were removed from the supplied sequence." % bad))
    if not insert:
        msgs.append(("warn", "No sequence supplied for %s, so a %s bp placeholder (typical length) is used. "
                     "Supply --reference, or --override goi=FILE for a synthetic construct."
                     % (payload, format(pay["cds"], ","))))
    else:
        check_insert(msgs, insert, payload)
        if not pay.get("verified_length", False) and len(insert) != pay["cds"]:
            msgs.append(("info", "Library length for %s (%s bp) is approximate; the supplied sequence "
                         "(%s bp) is used instead." % (payload, format(pay["cds"], ","), format(len(insert), ","))))
    if pay["note"]:
        msgs.append(("info", pay["note"]))

    # capacity
    cas = sum(f.length for f in feats if f.in_cassette)
    limit, what = (SC_LIMIT, "self-complementary AAV (about 2.4 kb)") if cfg.sc else (AAV_LIMIT, "AAV (about 4.7 kb)")
    n = format(cas, ",")
    if cas > limit:
        msgs.append(("error", "Cassette between the ITRs is %s bp, above the %s packaging limit. Oversized "
                     "genomes are truncated rather than packaged intact." % (n, what)))
    elif not cfg.sc and cas > AAV_WARN:
        msgs.append(("warn", "Cassette between the ITRs is %s bp, close to the %s limit. No headroom left "
                     "for further regulatory elements." % (n, what)))
    else:
        msgs.append(("info", "Cassette between the ITRs: %s bp (%s limit); %s bp spare."
                     % (n, what, format(limit - cas, ","))))

    # capsid and promoter sanity
    cap = CAPSIDS[capsid]
    msgs.append(("info", "Capsid %s binds %s, intended route %s. %s"
                 % (capsid, cap["receptor"], cap["route"], cap["note"])))
    if capsid == "AAV-PHP.eB":
        msgs.append(("error", "AAV-PHP.eB crossing depends on LY6A, which has no human ortholog. Any "
                     "efficacy shown with it must be re-established with a translational capsid."))
    if prom in GLIAL_PROMOTERS and not any(d in NEURON_DETARGET for d in detarget):
        msgs.append(("warn", "%s is a glial promoter without a neuronal detargeting cassette. Promoter "
                     "alone leaves substantial neuronal expression: add miR-124x2 or 4x6T." % prom))
    if prom not in GLIAL_PROMOTERS and any(d in NEURON_DETARGET for d in detarget):
        msgs.append(("warn", "A neuronal detargeting cassette (%s) on a neuronal promoter (%s) will "
                     "suppress the payload in the cells you are targeting."
                     % (", ".join(d for d in detarget if d in NEURON_DETARGET), prom)))
    if not any(d.startswith("miR-122") for d in detarget):
        msgs.append(("info", "No hepatic detargeting. miR-122 target sites reduce liver expression, which "
                     "matters most for the proliferative compartment."))
    if cfg.riboswitch:
        msgs.append(("info", "The K19 riboswitch is an on-switch above a leaky floor, not an off-switch: it "
                     "cannot retire an administered vector."))

    # tier consequences
    if gate.tier == "n-of-1":
        msgs.append(("warn", "N-of-1 tier: designing this cassette is cheap, manufacturing it is not. One "
                     "dedicated campaign with a full release panel per patient."))
    if gate.tier == "autologous":
        msgs.append(("info", "Autologous ex vivo route: this cassette is engineered into the patient's own "
                     "iPSC-derived progenitors during manufacturing rather than delivered by vector, so the "
                     "capsid, BBB and anti-AAV serology constraints do not apply."))
    msgs.append(("info", "Patient-matching cannot be validated preclinically: a model has no patient to "
                 "match. Carry it as a secondary endpoint (IFN-gamma ELISPOT, anti-drug antibody titre, "
                 "durability of expression), not as a de-risked design choice."))

    msgs.sort(key=lambda m: ("error", "warn", "info").index(m[0]))

    allele = {"patient": "pt", "reference": "ref"}.get(gate.allele, "na")
    tier = {"autologous": "auto", "binned": gate.bin_id or "bin", "n-of-1": "n1",
            "reference": "ref", "stock": "stock"}.get(gate.tier, gate.tier)
    auto = "pAAV-%s-%s>%s-%s-%s" % (capsid.replace("-", ""), prom, payload.replace("-", ""), allele, tier)
    return Design(cfg.name.strip() or auto, program, payload, capsid, feats, seq, msgs, gate, cfg.basis)
