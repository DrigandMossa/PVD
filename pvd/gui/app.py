"""Tkinter designer window: pick an arm and a payload, load the patient files, run the gate."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..design.builder import build_design
from ..export.files import write_outputs
from ..export.gatereport import to_gate_report
from ..model import Config
from ..parts.elements import CAPSIDS, DETARGET, PROMOTERS
from ..parts.payloads import PAYLOADS
from ..parts.programs import PROGRAMS
from ..patient.parse import read_arg, read_bins, read_classifications
from ..version import __version__


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("pvd %s - patient-sequence driven vector designer" % __version__)
        self.vars = {}
        self._build()

    # ---- layout -------------------------------------------------------
    def _build(self) -> None:
        pad = dict(padx=8, pady=4, sticky="w")
        frm = ttk.Frame(self.root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        r = 0
        ttk.Label(frm, text="Design", font=("TkDefaultFont", 11, "bold")).grid(row=r, column=0, **pad)
        r += 1
        self.program = self._combo(frm, r, "Arm", list(PROGRAMS), "clearance", self._on_program)
        r += 1
        self.payload, self.payload_box = self._combo(
            frm, r, "Payload", PROGRAMS["clearance"]["payloads"], "LAMP2A", self._on_payload,
            want_widget=True)
        r += 1
        self.note = ttk.Label(frm, text="", wraplength=620, foreground="#555")
        self.note.grid(row=r, column=0, columnspan=3, padx=8, pady=(0, 8), sticky="w")
        r += 1

        ttk.Label(frm, text="Patient sequence", font=("TkDefaultFont", 11, "bold")).grid(row=r, column=0, **pad)
        r += 1
        self.patient = self._file(frm, r, "Patient payload CDS")
        r += 1
        self.reference = self._file(frm, r, "Reference payload CDS")
        r += 1
        self.target = self._file(frm, r, "Patient SNCA CDS")
        r += 1
        self.target_ref = self._file(frm, r, "Reference SNCA CDS")
        r += 1
        self.classify = self._file(frm, r, "Classification TSV")
        r += 1
        self.bins = self._file(frm, r, "Haplotype bin TSV")
        r += 1
        self.sex = self._combo(frm, r, "Patient sex", ["male", "female", "unknown"], "unknown")
        r += 1
        self.route = self._combo(frm, r, "Route", ["in-vivo", "autologous"], "in-vivo")
        r += 1

        ttk.Label(frm, text="Cassette", font=("TkDefaultFont", 11, "bold")).grid(row=r, column=0, **pad)
        r += 1
        self.capsid = self._combo(frm, r, "Capsid", list(CAPSIDS), "TfR1-CapX")
        r += 1
        self.promoter = self._combo(frm, r, "Promoter", list(PROMOTERS), "hSyn1")
        r += 1
        self.detarget = self._combo(frm, r, "Detargeting", ["none"] + list(DETARGET), "miR-122x2")
        r += 1
        self.ribo = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="K19 riboswitch", variable=self.ribo).grid(row=r, column=1, **pad)
        self.sc = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="self-complementary", variable=self.sc).grid(row=r, column=2, **pad)
        r += 1
        self.out = self._file(frm, r, "Output folder", directory=True, default=".")
        r += 1

        bar = ttk.Frame(frm)
        bar.grid(row=r, column=0, columnspan=3, padx=8, pady=8, sticky="w")
        ttk.Button(bar, text="Run gate only", command=self._run_gate).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(bar, text="Build vector", command=self._build_vector).grid(row=0, column=1)
        r += 1

        self.log = tk.Text(frm, height=18, width=96, wrap="word")
        self.log.grid(row=r, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        frm.rowconfigure(r, weight=1)
        scroll = ttk.Scrollbar(frm, command=self.log.yview)
        scroll.grid(row=r, column=3, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)
        self._on_payload()

    def _combo(self, frm, row, label, values, default, command=None, want_widget=False):
        ttk.Label(frm, text=label).grid(row=row, column=0, padx=8, pady=4, sticky="w")
        var = tk.StringVar(value=default)
        box = ttk.Combobox(frm, textvariable=var, values=list(values), state="readonly", width=28)
        box.grid(row=row, column=1, padx=8, pady=4, sticky="w")
        if command:
            box.bind("<<ComboboxSelected>>", lambda _e: command())
        return (var, box) if want_widget else var

    def _file(self, frm, row, label, directory=False, default=""):
        ttk.Label(frm, text=label).grid(row=row, column=0, padx=8, pady=4, sticky="w")
        var = tk.StringVar(value=default)
        ttk.Entry(frm, textvariable=var, width=52).grid(row=row, column=1, padx=8, pady=4, sticky="we")

        def browse():
            path = filedialog.askdirectory() if directory else filedialog.askopenfilename()
            if path:
                var.set(path)
        ttk.Button(frm, text="Browse", command=browse).grid(row=row, column=2, padx=8, pady=4)
        return var

    # ---- events -------------------------------------------------------
    def _on_program(self) -> None:
        P = PROGRAMS[self.program.get()]
        self.payload_box.configure(values=P["payloads"])
        self.payload.set(P["default"])
        self.promoter.set(P["promoter"])
        self._on_payload()

    def _on_payload(self) -> None:
        key = self.payload.get()
        if key not in PAYLOADS:
            return
        p = PAYLOADS[key]
        bits = ["%s | %s | %s bp / %d aa" % (p["gene"], p["arm"], format(p["cds"], ","), p["aa"])]
        if p["synthetic"]:
            bits.append("Synthetic binder: no patient allele to insert. Epitope %d-%d of SNCA."
                        % p["epitope"])
        else:
            bits.append("Reference to fetch: %s" % p["refseq"])
        self.note.configure(text="\n".join(bits) + "\n" + p["note"])

    # ---- actions ------------------------------------------------------
    def _config(self) -> Config:
        d = self.detarget.get()
        return Config(program=self.program.get(), payload=self.payload.get(),
                      capsid=self.capsid.get(), promoter=self.promoter.get(),
                      detarget=[] if d == "none" else [d], riboswitch=self.ribo.get(),
                      sc=self.sc.get(), route=self.route.get(), sex=self.sex.get(),
                      patient_seq=read_arg(self.patient.get()),
                      reference_seq=read_arg(self.reference.get()),
                      target_seq=read_arg(self.target.get()),
                      target_reference=read_arg(self.target_ref.get()),
                      classifications=read_classifications(self.classify.get()),
                      bins=read_bins(self.bins.get()))

    def _write(self, text: str) -> None:
        self.log.delete("1.0", "end")
        self.log.insert("1.0", text)

    def _run_gate(self) -> None:
        try:
            design = build_design(self._config())
            self._write(to_gate_report(design))
        except (ValueError, OSError) as exc:
            messagebox.showerror("pvd", str(exc))

    def _build_vector(self) -> None:
        try:
            cfg = self._config()
            design = build_design(cfg)
            paths = write_outputs(design, self.out.get() or ".")
            lines = ["%s | %s bp | payload %s" % (design.name, format(design.total, ","), design.payload)]
            if design.gate:
                lines.append("allele: %s   tier: %s" % (design.gate.allele, design.gate.tier))
            lines += [""] + ["  [%s] %s" % m for m in design.messages]
            lines += ["", "Files written:"] + ["  " + os.path.abspath(p) for p in paths]
            self._write("\n".join(lines))
        except (ValueError, OSError) as exc:
            messagebox.showerror("pvd", str(exc))

    def run(self) -> None:
        self.root.mainloop()
