#!/bin/sh
cmp -s "$1/test_app.py" "$2/fixture/test_app.py" || { echo "tests modified"; exit 1; }
if grep -rn "fetch_user" "$1/app" >/dev/null; then echo "leftover fetch_user"; exit 1; fi
cd "$1" || exit 1
out=$(python3 -m unittest -q 2>&1); rc=$?
echo "$out" | tail -3; exit $rc
