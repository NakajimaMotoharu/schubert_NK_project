#!/bin/bash
# SSC190/DEPLOY001..005. One source-pinned verify/activation; never repeat a started action.
set -eu
umask 077
test "$#" = 1
case "$1" in verify|activate) ;; *) exit 70 ;; esac
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_log="$task_work/pg465-completed-native-$1-v2-script.log"
test ! -e "$task_log"
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_cp='/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG465/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG465/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG465/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG465/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
test "$(sha256sum "$task_work/pg465-completed-tool-v3/Pg465CompletedDeployment.class" | cut -d' ' -f1)" = fcbd363e811e45dbb9bf3cd7bfef1a9c47f5199dcb7e1ac0dbd7c1bec6651ed8
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg465-completed-tool-v2/Pg465CompletedDeployment.class /opt/schubert-nk/releases/0.1.0-PG465/RELEASE-MANIFEST.json' > "$task_log.preflight"
test "$(sed -n '1s/ .*//p' "$task_log.preflight")" = fcbd363e811e45dbb9bf3cd7bfef1a9c47f5199dcb7e1ac0dbd7c1bec6651ed8
test "$(sed -n '2s/ .*//p' "$task_log.preflight")" = 8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e
date --iso-8601=seconds > "$task_log.started"
task_result=0
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp '$task_cp' Pg465CompletedDeployment $1" > "$task_log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_log.exit"
date --iso-8601=seconds > "$task_log.completed"
printf 'PG465_COMPLETED_%s actualExit=%s\n' "$1" "$task_result"
exit "$task_result"
