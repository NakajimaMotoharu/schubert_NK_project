#!/bin/bash
# Grouped regression trigger after Access9/MDB27 contract changes; existing success stays frozen.
set -eu
test "$#" = 1
exec bash /home/mini/codex/project1/work/pgpt-foundation/tools/quality/vm/050_s1/pg585_access_pt_v1.sh "$1" PG593
