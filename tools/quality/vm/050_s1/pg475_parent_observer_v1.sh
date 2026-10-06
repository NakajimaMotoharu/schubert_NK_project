#!/bin/bash
# Read-only observer before the one reserved external parent start; no budget renewal.
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg475-parent-observer-v1
test ! -e "$task_base.started"
test ! -e "$task_work/pg475-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_base.started"
task_exit=0
ssh -i "$task_private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg475-observer-v1/pg475_watch_parent.py 979c5ac3e9c28ae76363adacdf9f0736f5a59df1 9183662292299cc86412c31a551bf140c8b32ccd9b2d6dcdd414b14e4bcd4806 PG475' > "$task_work/pg475-parent-watch-private-v1.jsonl" 2> "$task_base.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG475_OBSERVER actualExit=%s starts0=true noBudgetRenewal=true\n' "$task_exit"
exit "$task_exit"
