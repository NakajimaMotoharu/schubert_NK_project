#!/bin/bash
# Corrected endpoint/date fixtures; failed v1 exec is preserved, never appended.
set -eu
test "$#" = 1
exec bash /home/mini/codex/project1/work/pgpt-foundation/tools/quality/vm/050_s1/pg587_access_returns_v1.sh "$1" PG588V2
