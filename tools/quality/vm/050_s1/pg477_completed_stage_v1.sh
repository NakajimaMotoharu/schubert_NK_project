#!/bin/bash
# New-only immutable Root operator. No service, current, DB, permit or /run mutation.
set -eu
umask 077
task_repo=/home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test -f "$task_work/pg477-completed-tools-v1/Pg477CompletedAcceptance.class"
test ! -e "$task_work/pg477-completed-stage-v1.private.log"
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg477-completed-stage-v1 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg477-completed-tools-v1 && mkdir -m 700 /home/ubuntu/pg477-completed-stage-v1'
scp "${task_scp[@]}" "$task_work/pg477-completed-tools-v1/"*.class "$task_repo/tools/quality/vm/050_s1/pg477_completed_refs.py" "$task_repo/tools/quality/vm/050_s1/pg477_completed_native.py" "$task_repo/tools/quality/vm/050_s1/pg477_unit_references.py" ubuntu@127.0.0.1:/home/ubuntu/pg477-completed-stage-v1/ > "$task_work/pg477-completed-stage-v1.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -o root -g root -m 700 /var/lib/pgpt-s1-preservation/pg477-completed-tools-v1 && sudo -n install -o root -g root -m 400 /home/ubuntu/pg477-completed-stage-v1/* /var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/' >> "$task_work/pg477-completed-stage-v1.private.log" 2>&1
for task_file in "$task_work/pg477-completed-tools-v1/"*.class "$task_repo/tools/quality/vm/050_s1/pg477_completed_refs.py" "$task_repo/tools/quality/vm/050_s1/pg477_completed_native.py" "$task_repo/tools/quality/vm/050_s1/pg477_unit_references.py"; do
 task_name=${task_file##*/}; task_hash=$(sha256sum "$task_file" | cut -d' ' -f1)
 test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n sha256sum '/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/$task_name'" | cut -d' ' -f1)" = "$task_hash"
done
printf 'PG477_COMPLETED_STAGED exactClassAndHelperBytes=true newOnly=true servicesUnchanged=true\n'
