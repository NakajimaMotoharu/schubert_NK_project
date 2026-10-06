#!/bin/bash
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg493-parent-observer-v1
test ! -e "$task_base.started"
test ! -e "$task_work/pg493-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_base.started"
task_exit=0
ssh -i "$task_private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg493-observer-v1/pg493_watch_parent.py 38899a05b5c2daeecfc5af8ea5ae748e29954c60 652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c PG489' > "$task_work/pg493-parent-watch-private-v1.jsonl" 2> "$task_base.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG493_OBSERVER actualExit=%s starts0=true noBudgetRenewal=true\n' "$task_exit"
exit "$task_exit"
