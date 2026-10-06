#!/bin/bash
# Read-only observer before the one reserved external parent start; no budget renewal.
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg474-parent-observer-v1
test ! -e "$task_base.started"
test ! -e "$task_work/pg474-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_base.started"
task_exit=0
ssh -i "$task_private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg474-observer-v1/pg474_watch_parent.py 09b448644cfe70c87df9c89aa5c0c1bf6efdeeea 3f6b837c12282baca8b2c5fc79c85916421b6940471cca5d544381072120af18 PG474' > "$task_work/pg474-parent-watch-private-v1.jsonl" 2> "$task_base.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG474_OBSERVER actualExit=%s starts0=true noBudgetRenewal=true\n' "$task_exit"
exit "$task_exit"
