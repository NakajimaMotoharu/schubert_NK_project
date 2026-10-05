#!/bin/bash
# New-only Root readback tools. No services, deployment, DB or startup mutation.
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test -f "$task_work/pg471-readback-tools-v3/Pg471CompletedReadback.class"
test ! -e "$task_work/pg471-readback-stage-v2.private.log"
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg471-readback-stage-v2 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg471-readback-tools-v2 && mkdir -m 700 /home/ubuntu/pg471-readback-stage-v2'
scp "${task_scp[@]}" "$task_work/pg471-readback-tools-v3/"*.class ubuntu@127.0.0.1:/home/ubuntu/pg471-readback-stage-v2/ > "$task_work/pg471-readback-stage-v2.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -o root -g root -m 700 /var/lib/pgpt-s1-preservation/pg471-readback-tools-v2 && sudo -n install -o root -g root -m 400 /home/ubuntu/pg471-readback-stage-v2/*.class /var/lib/pgpt-s1-preservation/pg471-readback-tools-v2/' >> "$task_work/pg471-readback-stage-v2.private.log" 2>&1
for task_class in "$task_work/pg471-readback-tools-v3/"*.class; do
 task_name=${task_class##*/}; task_hash=$(sha256sum "$task_class" | cut -d' ' -f1)
 test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg471-readback-tools-v2/'$task_name'" | cut -d' ' -f1)" = "$task_hash"
done
printf 'PG471_READBACK_STAGED exactClassBytes=true newOnly=true productionMutation0=true\n'
