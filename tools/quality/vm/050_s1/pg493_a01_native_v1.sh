#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_base=$task_work/pg493-a01-native-v1
test ! -e "$task_base.log"
date --iso-8601=seconds > "$task_base.started"
task_exit=0
python3 -B tools/quality/vm/050_s1/pg493_capture_a01_when_ready.py 38899a05b5c2daeecfc5af8ea5ae748e29954c60 > "$task_base.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG493_A01 actualExit=%s wholeMorningAccepted=false\n' "$task_exit"
exit "$task_exit"
