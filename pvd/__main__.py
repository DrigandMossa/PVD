"""Entry point for `python -m pvd`."""

import sys

from .cli.run import main

if __name__ == "__main__":
    sys.exit(main())
