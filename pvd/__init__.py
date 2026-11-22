"""Patient-sequence Driven Vector designer for Parkinson's proteostasis programs.

Build AAV cassettes for the three proteostasis arms (clearance, barrier, chaperone)
from a patient's own sequenced coding sequence, with the eligibility gate applied before
the patient allele is allowed into a payload.  Standard library only (Python 3.8+).

The gate is the point of the tool.  Delivering a patient's own allele of an augmentation
gene is only safe when that allele is functional, so pvd calls the amino-acid differences
against a reference CDS, maps each one to a region of the protein, and refuses the patient
allele unless an explicit benign classification is supplied.  Unclassified means reference.

Research design tool.  Library elements use typical lengths and are written as runs of N
until verified sequences are supplied.  Producing virus requires institutional biosafety
approval; a clinical product requires GMP manufacturing, preclinical safety data and
regulatory authorization.  Nothing here is a clinical protocol.

    python -m pvd                       open the graphical window
    python -m pvd --wizard              answer text prompts instead
    python -m pvd --list                show arms, payloads and parts
    python -m pvd --gate ...            run the eligibility gate only, no vector
    python -m pvd --program clearance --patient pt.fasta --reference ref.fasta

See README.md for the full option reference.
"""

from .version import __version__

__all__ = ["__version__"]
