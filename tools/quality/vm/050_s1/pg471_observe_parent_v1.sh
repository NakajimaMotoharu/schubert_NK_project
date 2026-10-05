#!/bin/bash
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
test ! -e "$task_work/pg471-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_work/pg471-parent-observer-v1.started"
task_exit=0
ssh -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n /usr/bin/python3 -u -B /var/lib/pgpt-s1-preservation/pg471-observer-v1/pg471_watch_parent.py 717d72dd844fff286b4c696b9d08c41b136f0a6c 47f7a338de848c83e96d2fc8208a9eade43e9d4e5218c79b3834603e27648b18 PG471' > "$task_work/pg471-parent-watch-private-v1.jsonl" 2> "$task_work/pg471-parent-observer-v1.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg471-parent-observer-v1.exit"
date --iso-8601=seconds > "$task_work/pg471-parent-observer-v1.completed"
printf 'PG471_PARENT_OBSERVER actualExit=%s parentSuccessNotInferred=true\n' "$task_exit"
exit "$task_exit"
