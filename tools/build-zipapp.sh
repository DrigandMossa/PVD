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

# Pin every mtime before zipping. zipapp stores each file's modification time in the
# archive, and a fresh `git clone` stamps the working tree with the checkout time, so
# without this the artifact is reproducible in content but not in bytes: two builds of
# the same commit differ, and `git status` reports pvd.pyz dirty after anyone runs this
# script. Honours SOURCE_DATE_EPOCH if the caller sets it.
if [ -n "${SOURCE_DATE_EPOCH:-}" ]; then
  STAMP="$(date -u -d "@${SOURCE_DATE_EPOCH}" +%Y%m%d%H%M.%S 2>/dev/null || echo 202001010000.00)"
else
  STAMP="202001010000.00"
fi
find build/zapp -exec touch -t "$STAMP" {} +

python3 -m zipapp build/zapp -o pvd.pyz -p "/usr/bin/env python3" -c
chmod +x pvd.pyz
rm -rf build/zapp

./pvd.pyz --version
./pvd.pyz --list > /dev/null
echo "pvd.pyz rebuilt: $(wc -c < pvd.pyz) bytes"
