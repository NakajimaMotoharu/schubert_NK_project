#!/bin/bash
set -eu
umask 077
test "$#" = 1
case "$1" in
  isolate) task_class=Pg468OwnedIsolation; task_args= ;;
  verify) task_class=Pg468Known30PairRecovery; task_args=verify ;;
  retire) task_class=Pg468Known30PairRecovery; task_args= ;;
  *) exit 2 ;;
esac
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_log=$task_work/pg468-recovery-native-$1-v1.private.log
test ! -e "$task_log"
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_cp='/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2:/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG465/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG465/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG465/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG465/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
date --iso-8601=seconds > "$task_log.started"
task_result=0
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp '$task_cp' $task_class $task_args" > "$task_log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_log.exit"
date --iso-8601=seconds > "$task_log.completed"
printf 'PG468_RECOVERY action=%s actualExit=%s\n' "$1" "$task_result"
exit "$task_result"
