#!/bin/bash
# SSC191/196 separate read-only new ownership; never replay the interrupted deployment.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_base=$task_work/pg477-completed-native-v1
test ! -e "$task_base.private.log"
task_exit=0
date --iso-8601=seconds > "$task_base.started"
ssh -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 'sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1:/var/lib/pgpt-s1-preservation/pg477-partial-tools-v3:/var/lib/pgpt-s1-preservation/pg475-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg474-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg473-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg471-readback-tools-v3:/var/lib/pgpt-s1-preservation/pg471-completed-tools-v2:/var/lib/pgpt-s1-preservation/pg469-current-tools-v3:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2:/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG477/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG477/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG477/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG477/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar" Pg477CompletedAcceptance verify' > "$task_base.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG477_COMPLETED_NATIVE actualExit=%s oldNormalCloseNotInferred=true\n' "$task_exit"
exit "$task_exit"
