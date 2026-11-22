"""Dataclasses shared across the gate, the designer and the exports."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Config:
    program: str = "clearance"      # clearance / barrier / chaperone
    payload: str = ""               # payload key; default comes from the program
    capsid: str = "TfR1-CapX"
    promoter: Optional[str] = None
    polya: Optional[str] = None
    kozak: bool = True
    sc: bool = False                # self-complementary AAV (halves the capacity)
    detarget: List[str] = field(default_factory=lambda: ["miR-122x2"])
    riboswitch: bool = False
    route: str = "in-vivo"          # in-vivo / autologous
    sex: str = "unknown"            # male / female / unknown
    patient_seq: str = ""           # patient CDS for the payload gene (text or FASTA)
    reference_seq: str = ""         # reference CDS for the payload gene
    target_seq: str = ""            # patient SNCA CDS, for epitope verification
    target_reference: str = ""      # reference SNCA CDS
    classifications: Dict[str, str] = field(default_factory=dict)
    bins: Dict[str, List[str]] = field(default_factory=dict)
    name: str = ""
    basis: str = ""
    overrides: Dict[str, str] = field(default_factory=dict)


@dataclass
class Variant:
    """One amino-acid difference between the patient CDS and the reference CDS."""
    pos: int                        # 1-based residue position in the reference protein
    ref_aa: str
    alt_aa: str
    region: str                     # shared-lumenal / isoform-specific / gf-domain / other
    classification: str = "unclassified"
    known: str = ""                 # note if the position is in the built-in watch list

    @property
    def label(self) -> str:
        return "%s%d%s" % (self.ref_aa, self.pos, self.alt_aa)


@dataclass
class Gate:
    """The eligibility decision for using the patient allele as the payload."""
    payload: str
    gene: str
    allele: str                     # patient / reference
    tier: str                       # autologous / binned / n-of-1 / reference
    bin_id: str = ""
    variants: List[Variant] = field(default_factory=list)
    epitope: List[Variant] = field(default_factory=list)
    findings: List[Tuple[str, str]] = field(default_factory=list)
    binder: str = ""                # intrabody actually selected, barrier program only

    @property
    def used_patient(self) -> bool:
        return self.allele == "patient"


@dataclass
class Feature:
    id: str
    name: str
    kind: str
    length: int
    seq: Optional[str] = None
    in_cassette: bool = False
    custom: bool = False
    start: int = 0
    end: int = 0


@dataclass
class Design:
    name: str
    program: str
    payload: str
    capsid: str
    features: List[Feature]
    seq: str
    messages: List[Tuple[str, str]]     # (level, text); level: error / warn / info
    gate: Optional[Gate] = None
    basis: str = ""

    @property
    def total(self) -> int:
        return len(self.seq)
