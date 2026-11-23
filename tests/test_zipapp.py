"""The committed pvd.pyz must match the tree it ships with.

A zipapp is a zip of the package with a shebang: it carries whatever was under
pvd/ at the moment it was built, and nothing warns you when the two drift. The
failure is quiet and nasty - someone downloads the executable, runs it against a
patient FASTA, and gets the gate rules from three commits ago.

Comparing module source bytes rather than the archive's own bytes keeps this
independent of the Python version and zlib build that produced it.
"""

import os
import zipfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYZ = os.path.join(ROOT, "pvd.pyz")
PKG = os.path.join(ROOT, "pvd")

needs_pyz = pytest.mark.skipif(not os.path.exists(PYZ), reason="pvd.pyz is not built")


def tree_sources():
    """Every .py under pvd/, keyed by its archive-style path."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(PKG):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            full = os.path.join(dirpath, name)
            key = os.path.relpath(full, ROOT).replace(os.sep, "/")
            with open(full, "rb") as fh:
                out[key] = fh.read()
    return out


@needs_pyz
def test_zipapp_has_a_shebang_and_is_a_zip():
    with open(PYZ, "rb") as fh:
        assert fh.read(2) == b"#!", "pvd.pyz must start with a shebang to be executable"
    assert zipfile.is_zipfile(PYZ)


@needs_pyz
def test_zipapp_carries_every_module_in_the_tree():
    tree = tree_sources()
    with zipfile.ZipFile(PYZ) as zf:
        names = set(zf.namelist())
    missing = sorted(k for k in tree if k not in names)
    assert not missing, "pvd.pyz is missing modules; rebuild it: %s" % missing


@needs_pyz
def test_zipapp_sources_are_identical_to_the_tree():
    tree = tree_sources()
    stale = []
    with zipfile.ZipFile(PYZ) as zf:
        for key, src in sorted(tree.items()):
            if key not in zf.namelist():
                continue
            if zf.read(key) != src:
                stale.append(key)
    assert not stale, (
        "pvd.pyz is out of date with the tree; run tools/build-zipapp.sh. Stale: %s" % stale
    )


@needs_pyz
def test_zipapp_timestamps_are_pinned():
    """Every entry must carry the fixed build stamp, not a checkout time.

    zipapp records each file's mtime, and `git clone` stamps the tree with the time of
    the clone. Without pinning, two builds of the same commit differ in bytes and
    `git status` reports pvd.pyz dirty for anyone who runs the build script. A stray
    real timestamp here means the archive was built without tools/build-zipapp.sh.
    """
    with zipfile.ZipFile(PYZ) as zf:
        stamps = {i.date_time for i in zf.infolist()}
    assert stamps == {(2020, 1, 1, 0, 0, 0)}, (
        "unpinned timestamps in pvd.pyz: %s; rebuild with tools/build-zipapp.sh"
        % sorted(stamps)
    )


@needs_pyz
def test_zipapp_entry_point_is_present():
    with zipfile.ZipFile(PYZ) as zf:
        assert "__main__.py" in zf.namelist()
        assert b"pvd.cli.run" in zf.read("__main__.py")
