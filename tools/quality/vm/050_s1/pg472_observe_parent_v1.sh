#!/bin/bash
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
test ! -e "$task_work/pg472-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_work/pg472-parent-observer-v1.started"
task_exit=0
ssh -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n /usr/bin/python3 -u -B /var/lib/pgpt-s1-preservation/pg472-observer-v1/pg472_watch_parent.py c8ad413437be409f70ec37bdba33c5e3cd21790b 8e6bc3c26c1d707b5873dd14c229d41fa129bf7e5547dacc2bbc3780a90df3f1 PG472' > "$task_work/pg472-parent-watch-private-v1.jsonl" 2> "$task_work/pg472-parent-observer-v1.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg472-parent-observer-v1.exit"
date --iso-8601=seconds > "$task_work/pg472-parent-observer-v1.completed"
printf 'PG472_PARENT_OBSERVER actualExit=%s parentSuccessNotInferred=true\n' "$task_exit"
exit "$task_exit"
