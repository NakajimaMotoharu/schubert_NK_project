#!/bin/bash
# SSC191 exact identified old operator only. New metadata sender retains Ref on uncertainty.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test ! -e "$task_work/pg480-backup-handoff-v2.private.log"
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg480-backup-handoff-stage-v2 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg480-backup-handoff-tools-v2 && mkdir -m 700 /home/ubuntu/pg480-backup-handoff-stage-v2'
scp "${task_scp[@]}" tools/quality/vm/050_s1/pg480_backup_handoff_v2.py ubuntu@127.0.0.1:/home/ubuntu/pg480-backup-handoff-stage-v2/ > "$task_work/pg480-backup-handoff-stage-v2.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -m 700 /var/lib/pgpt-s1-preservation/pg480-backup-handoff-tools-v2 && sudo -n install -m 400 /home/ubuntu/pg480-backup-handoff-stage-v2/pg480_backup_handoff_v2.py /var/lib/pgpt-s1-preservation/pg480-backup-handoff-tools-v2/'
task_hash=$(sha256sum tools/quality/vm/050_s1/pg480_backup_handoff_v2.py | cut -d' ' -f1)
test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg480-backup-handoff-tools-v2/pg480_backup_handoff_v2.py' | cut -d' ' -f1)" = "$task_hash"
task_exit=0
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg480-backup-handoff-tools-v2/pg480_backup_handoff_v2.py handoff' > "$task_work/pg480-backup-handoff-v2.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg480-backup-handoff-v2.exit"
printf 'PG480_BACKUP_HANDOFF actualExit=%s historicalCloseNotInferred=true\n' "$task_exit"
exit "$task_exit"
