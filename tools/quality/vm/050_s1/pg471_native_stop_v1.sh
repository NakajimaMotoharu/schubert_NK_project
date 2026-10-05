#!/bin/bash
# One same-source completed cohort stop, never start/repair/permit/epoch/DDL.
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
test ! -e "$task_work/pg471-native-stop-v1.private.log"
test "$(<"$task_work/pg471-readback-native-v3.exit")" = 0
test "$(<"$task_work/pg471-l01-native-v1.exit")" = 0
git diff --quiet 717d72dd844fff286b4c696b9d08c41b136f0a6c -- src pom.xml
task_cp='/var/lib/pgpt-s1-preservation/pg471-native-tools-v1:/var/lib/pgpt-s1-preservation/pg471-readback-tools-v3:/var/lib/pgpt-s1-preservation/pg471-completed-tools-v2:/var/lib/pgpt-s1-preservation/pg469-current-tools-v3:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2:/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG471/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG471/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG471/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG471/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
date --iso-8601=seconds > "$task_work/pg471-native-stop-v1.started"
task_exit=0
ssh -i "$task_private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 "sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp '$task_cp' Pg471NativeStop stop" > "$task_work/pg471-native-stop-v1.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg471-native-stop-v1.exit"
date --iso-8601=seconds > "$task_work/pg471-native-stop-v1.completed"
printf 'PG471_NATIVE_STOP actualExit=%s starts0=true oldUnknownNormalized=false nativeFilesNotYetAccepted=true\n' "$task_exit"
exit "$task_exit"
