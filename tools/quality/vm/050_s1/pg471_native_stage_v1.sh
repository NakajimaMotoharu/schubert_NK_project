#!/bin/bash
set -eu
umask 077
task_tree=/home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test -f "$task_work/pg471-native-tools-v2/Pg471NativeStop.class"
test ! -e "$task_work/pg471-native-stage-v1.private.log"
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg471-native-stage-v1 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg471-native-tools-v1 && mkdir -m700 /home/ubuntu/pg471-native-stage-v1'
task_helpers=(pg471_native_owned_stop.py pg471_native_term_witness.py pg466_term_witness.py)
task_files=("$task_work/pg471-native-tools-v2/"*.class)
for task_name in "${task_helpers[@]}"; do task_files+=("$task_tree/tools/quality/vm/050_s1/$task_name"); done
scp "${task_scp[@]}" "${task_files[@]}" ubuntu@127.0.0.1:/home/ubuntu/pg471-native-stage-v1/ > "$task_work/pg471-native-stage-v1.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -o root -g root -m700 /var/lib/pgpt-s1-preservation/pg471-native-tools-v1 && sudo -n install -o root -g root -m400 /home/ubuntu/pg471-native-stage-v1/* /var/lib/pgpt-s1-preservation/pg471-native-tools-v1/' >> "$task_work/pg471-native-stage-v1.private.log" 2>&1
for task_file in "${task_files[@]}"; do
 task_name=${task_file##*/}; task_hash=$(sha256sum "$task_file" | cut -d' ' -f1)
 test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg471-native-tools-v1/'$task_name'" | cut -d' ' -f1)" = "$task_hash"
done
printf 'PG471_NATIVE_STAGED newOnly=true root400=true exactClassAndHelperBytes=true servicesUnchanged=true\n'
