#!/bin/bash
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test -f "$task_work/pg468-recovery-tools-v4/Pg468Known30PairRecovery.class"
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg468-tools-stage-v4 && mkdir -m 700 /home/ubuntu/pg468-tools-stage-v4 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4'
scp "${task_scp[@]}" "$task_work/pg468-recovery-tools-v4/"*.class ubuntu@127.0.0.1:/home/ubuntu/pg468-tools-stage-v4/ > "$task_work/pg468-tools-stage-copy-v4.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -o root -g root -m 700 /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4 && sudo -n install -o root -g root -m 400 /home/ubuntu/pg468-tools-stage-v4/*.class /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4/' > "$task_work/pg468-tools-stage-place-v4.private.log" 2>&1
for task_class in "$task_work/pg468-recovery-tools-v4/"*.class; do
 task_name=${task_class##*/}; task_hash=$(sha256sum "$task_class" | cut -d' ' -f1)
 test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4/$task_name" | cut -d' ' -f1)" = "$task_hash"
done
printf 'PG468_TOOLS_STAGED_V4 exactClassBytes=true starts0=true stops0=true namespace0=true\n'
