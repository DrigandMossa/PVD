"""Graphical window.

The GUI class is imported inside launch_gui() so that the command-line modes never touch
tkinter: pvd is both a window and a command-line tool, and --list, --gate and one-shot
design runs must work on a machine with no display and no python3-tk.
"""

import sys


def launch_gui() -> int:
    """Open the designer window.  Returns an exit status, or 1 if tkinter is unavailable."""
    try:
        from .app import App
    except ImportError as exc:
        print("The graphical window needs tkinter, which is not available (%s)." % exc, file=sys.stderr)
        print("On Debian/Ubuntu: sudo apt install python3-tk", file=sys.stderr)
        return 1
    try:
        App().run()
    except Exception as exc:                      # a dead display is not a crash worth a traceback
        print("Could not open the window: %s" % exc, file=sys.stderr)
        return 1
    return 0
