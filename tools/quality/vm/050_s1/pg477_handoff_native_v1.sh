#!/bin/bash
# BUG764 / SSC191 exact holder interruption, never old close success.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg477-handoff-native-v1
test ! -e "$task_base.private.log"
task_exit=0
date --iso-8601=seconds > "$task_base.started"
ssh -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n /usr/bin/python3 -B /var/lib/pgpt-s1-preservation/pg477-handoff-tools-v1/pg477_handoff.py terminate' > "$task_base.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG477_HANDOFF actualExit=%s oldNormalCloseNotInferred=true\n' "$task_exit"
exit "$task_exit"
