#!/bin/sh
exp=$(cat "$3"); got=$(tr -d ' \n\r`' < "$1/answer.txt" 2>/dev/null)
[ "$got" = "$exp" ] && { echo "correct: $got"; exit 0; }
echo "got '$got', expected '$exp'"; exit 1
