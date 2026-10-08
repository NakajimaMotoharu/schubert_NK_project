#!/bin/bash
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg554-parent-observer-v1
test ! -e "$task_base.started"
test ! -e "$task_work/pg554-parent-watch-private-v1.jsonl"
date --iso-8601=seconds > "$task_base.started"
task_exit=0
ssh -i "$task_private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg554-observer-v1/pg554_watch_parent.py 969d8ded10c0bf5841d9e3a5c531e922caf4a24a a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b PG548' > "$task_work/pg554-parent-watch-private-v1.jsonl" 2> "$task_base.private.stderr" || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG554_OBSERVER actualExit=%s starts0=true noBudgetRenewal=true\n' "$task_exit"
exit "$task_exit"
