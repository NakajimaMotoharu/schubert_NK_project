#!/bin/bash
set -euo pipefail
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_target=$task_work/pg508-broker-readonly-tools-v1
test ! -e "$task_target"
mkdir -m 700 "$task_target"
task_cp="$task_work/pg495-host/batch/classes:$task_work/pg495-host/bootstrap/classes:$task_work/pg495-host/storage/classes:$task_work/pg495-host/protocol/classes:$task_work/pg495-release-v1/api/lib/*:$task_work/pg495-release-v1/operations/lib/*"
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javac -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg508BrokerOpsReadonly.java > "$task_work/pg508-compile-v1.private.log" 2>&1
scp -i "$task_private/vm-access" -P22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o"UserKnownHostsFile=$task_private/known_hosts" "$task_target/Pg508BrokerOpsReadonly.class" ubuntu@127.0.0.1:/home/ubuntu/pg508-broker-readonly-v1.class
python3 -B tools/quality/vm/050_s1/pg508_broker_ops_readonly_v1.py
