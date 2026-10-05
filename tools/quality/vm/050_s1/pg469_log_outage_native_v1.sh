#!/bin/bash
# New-only test-private communication-fault tool. No process start/stop or Production edit.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
test "$(<"$task_work/pg469-readback-native-v1.exit")" = 0
test "$(<"$task_work/pg469-l01-native-v1.exit")" = 0
test ! -e "$task_work/pg469-log-outage-native-v1.private.log"
PYTHONDONTWRITEBYTECODE=1 python3 tools/quality/vm/050_s1/pg469_log_network_outage_test.py > "$task_work/pg469-log-outage-oracle-v1.log"
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg469-log-network-outage-v1.py && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg469-log-network-tools-v1 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg469-log-network-outage-v1'
scp "${task_scp[@]}" tools/quality/vm/050_s1/pg469_log_network_outage.py ubuntu@127.0.0.1:/home/ubuntu/pg469-log-network-outage-v1.py > "$task_work/pg469-log-outage-stage-v1.private.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n install -d -m 700 -o root -g root /var/lib/pgpt-s1-preservation/pg469-log-network-tools-v1 && sudo -n install -m 400 -o root -g root /home/ubuntu/pg469-log-network-outage-v1.py /var/lib/pgpt-s1-preservation/pg469-log-network-tools-v1/pg469_log_network_outage.py' >> "$task_work/pg469-log-outage-stage-v1.private.log" 2>&1
task_hash=$(sha256sum tools/quality/vm/050_s1/pg469_log_network_outage.py | cut -d' ' -f1)
test "$(ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg469-log-network-tools-v1/pg469_log_network_outage.py' | cut -d' ' -f1)" = "$task_hash"
date --iso-8601=seconds > "$task_work/pg469-log-outage-native-v1.started"
task_exit=0
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'sudo -n /usr/bin/python3 -B /var/lib/pgpt-s1-preservation/pg469-log-network-tools-v1/pg469_log_network_outage.py' > "$task_work/pg469-log-outage-native-v1.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg469-log-outage-native-v1.exit"
date --iso-8601=seconds > "$task_work/pg469-log-outage-native-v1.completed"
printf 'PG469_LOG_LINK_OUTAGE actualExit=%s brokerProcessStop0=true chrPass=false\n' "$task_exit"
exit "$task_exit"
