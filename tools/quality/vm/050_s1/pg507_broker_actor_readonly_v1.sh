#!/bin/bash
set -euo pipefail
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_target=$task_work/pg507-broker-readonly-tools-v1
test ! -e "$task_target"
mkdir -m 700 "$task_target"
task_cp="$task_work/pg495-host/bootstrap/classes:$task_work/pg495-host/storage/classes:$task_work/pg495-host/protocol/classes:$task_work/pg495-release-v1/api/lib/*"
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javac -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg507BrokerActorReadonly.java > "$task_work/pg507-compile-v1.private.log" 2>&1
scp -i "$task_private/vm-access" -P22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" "$task_target/Pg507BrokerActorReadonly.class" ubuntu@127.0.0.1:/home/ubuntu/pg507-broker-readonly-v1.class
python3 -B tools/quality/vm/050_s1/pg507_broker_actor_readonly_v1.py
