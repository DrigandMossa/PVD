#!/usr/bin/env bash
# Rebuild the committed pvd.pyz from the current tree.
#
# A zipapp is a zip of the package with a shebang, so it carries whatever is
# under pvd/ at the moment it is built.  Run this after changing anything in
# pvd/, or the committed executable keeps running the old code.
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf build/zapp
mkdir -p build/zapp
cp -r pvd build/zapp/
find build/zapp -name __pycache__ -type d -exec rm -rf {} +
cat > build/zapp/__main__.py <<'PY'
"""Zipapp entry point: delegates to pvd.cli.run.main."""

import sys

from pvd.cli.run import main

if __name__ == "__main__":
    sys.exit(main())
PY

python3 -m zipapp build/zapp -o pvd.pyz -p "/usr/bin/env python3" -c
chmod +x pvd.pyz
rm -rf build/zapp

./pvd.pyz --version
./pvd.pyz --list > /dev/null
echo "pvd.pyz rebuilt: $(wc -c < pvd.pyz) bytes"
