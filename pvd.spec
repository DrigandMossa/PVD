# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe for a single-file pvd executable.

    pip install -r requirements-dev.txt
    pyinstaller pvd.spec

The result is dist/pvd (dist/pvd.exe on Windows).

console=True is deliberate.  pvd is both a window and a command-line tool: a windowed
(--noconsole) build opens the designer fine but silently discards the output of --list,
--gate and one-shot design runs, which makes the command-line modes useless.  With a
console build both modes work; the cost is a console window behind the designer.
"""

a = Analysis(
    ["pvd/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    # The GUI classes are imported inside launch_gui() so that the command-line modes
    # never touch tkinter.  Named here so the analysis cannot miss them.
    hiddenimports=["pvd.gui.app"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="pvd",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
