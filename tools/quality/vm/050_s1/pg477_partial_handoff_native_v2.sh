#!/bin/bash
# SSC191 / BUG766 exact partial-state handoff; old tool remains failed/interrupted.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg477-partial-handoff-native-v2
test ! -e "$task_base.private.log"
task_exit=0
date --iso-8601=seconds > "$task_base.started"
ssh -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n /usr/bin/python3 -B /var/lib/pgpt-s1-preservation/pg477-partial-tools-v2/pg477_partial_handoff.py handoff' > "$task_base.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG477_PARTIAL_HANDOFF actualExit=%s oldNormalCloseNotInferred=true\n' "$task_exit"
exit "$task_exit"
