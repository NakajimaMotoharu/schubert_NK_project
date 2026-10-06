#!/bin/bash
# Read-only observer before the one reserved external parent start; no budget renewal.
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg473-parent-observer-v1
test ! -e "$task_base.started"
test ! -e "$task_work/pg473-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_base.started"
task_exit=0
ssh -i "$task_private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg473-observer-v1/pg473_watch_parent.py a5f9e6a54427ff356626245230496d8667082465 ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d PG473' > "$task_work/pg473-parent-watch-private-v1.jsonl" 2> "$task_base.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG473_OBSERVER actualExit=%s starts0=true noBudgetRenewal=true\n' "$task_exit"
exit "$task_exit"
