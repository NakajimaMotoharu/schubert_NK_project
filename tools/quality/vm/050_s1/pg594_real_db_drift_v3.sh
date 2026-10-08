#!/bin/bash
# New-only acknowledged fixture-lock release and independent retained-lock counterexample.
set -eu
test "$#" = 1
exec bash /home/mini/codex/project1/work/pgpt-foundation/tools/quality/vm/050_s1/pg587_access_returns_v1.sh "$1" PG594V3
