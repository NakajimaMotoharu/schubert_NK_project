#!/bin/bash
# SSC191/DEPLOY006..008. New-only private output; no repeated mutating phases.
set -eu
umask 077
test "$#" = 1
case "$1" in inspect|isolate|terminate) ;; *) exit 70 ;; esac
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_log="$task_work/pg466-$1-native-v1.private.log"
test ! -e "$task_log"
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
date --iso-8601=seconds > "$task_log.started"
task_result=0
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n /usr/bin/python3 -B /var/lib/pgpt-s1-preservation/pg466-tool-v2/pg466_handoff.py $1" > "$task_log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_log.exit"
date --iso-8601=seconds > "$task_log.completed"
printf 'PG466_%s actualExit=%s\n' "$1" "$task_result"
exit "$task_result"
