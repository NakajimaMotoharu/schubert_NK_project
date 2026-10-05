#!/bin/bash
# Single host-owned browser tunnel. Existing listener is never replaced.
set -eu
umask 077
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
test -z "$(ss -H -ltn 'sport = :55169')"
test ! -e "$task_work/pg469-socks-v1.pid"
printf '%s\n' "$BASHPID" > "$task_work/pg469-socks-v1.pid"
date --iso-8601=seconds > "$task_work/pg469-socks-v1.started"
exec ssh -N -D 127.0.0.1:55169 -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" -o ExitOnForwardFailure=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=2 ubuntu@127.0.0.1
