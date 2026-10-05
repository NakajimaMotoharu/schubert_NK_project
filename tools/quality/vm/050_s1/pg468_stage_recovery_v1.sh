#!/bin/bash
# New-only current known30 tools; does not stop/start or mutate original/namespace/current.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test -f "$task_work/pg468-recovery-tools-v2/Pg468OwnedIsolation.class"
test "$(sha256sum "$task_work/pg467-parent-watch-private-v1.jsonl" | cut -d' ' -f1)" = 316f75d991e646b8b77e49288abf632d6bfd0b12e1544a21bf284f80d8d0fa8e
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg468-recovery-stage && mkdir -m 700 /home/ubuntu/pg468-recovery-stage && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg468-binding-v1'
scp "${task_scp[@]}" "$task_work/pg468-recovery-tools-v2/"*.class "$task_work/pg467-parent-watch-private-v1.jsonl" ubuntu@127.0.0.1:/home/ubuntu/pg468-recovery-stage/ > "$task_work/pg468-recovery-stage-copy-v1.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -o root -g root -m 700 /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2 /var/lib/pgpt-s1-preservation/pg468-binding-v1 && sudo -n install -o root -g root -m 400 /home/ubuntu/pg468-recovery-stage/*.class /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2/ && sudo -n install -o root -g root -m 600 /home/ubuntu/pg468-recovery-stage/pg467-parent-watch-private-v1.jsonl /var/lib/pgpt-s1-preservation/pg468-binding-v1/external-watch.private.jsonl' > "$task_work/pg468-recovery-stage-place-v1.private.log" 2>&1
for task_class in "$task_work/pg468-recovery-tools-v2/"*.class; do
  task_name=${task_class##*/}
  task_hash=$(sha256sum "$task_class" | cut -d' ' -f1)
  test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2/$task_name" | cut -d' ' -f1)" = "$task_hash"
done
printf 'PG468_RECOVERY_STAGED sameClassByte=true sourcePG465=true starts0=true stops0=true namespaceMutations0=true\n'
