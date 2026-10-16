#!/bin/sh
# $1 = workdir, $2 = task dir. Exit 0 = pass. Guard against edited tests.
cmp -s "$1/test_stats.py" "$2/fixture/test_stats.py" || { echo "tests modified"; exit 1; }
cd "$1" || exit 1
out=$(python3 -m unittest -q 2>&1); rc=$?
echo "$out" | tail -3; exit $rc
