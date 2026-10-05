#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg468-recovery-tools-v2
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg466-tool-v3:$task_work/pg465-completed-tool-v3:$task_work/pg464-completed-tools-v7:$task_work/pg464-code-tools-v2:$task_work/pg461-known30-tool-v3:$task_work/pg456-tools-v7:$task_work/pg465-host/api/classes:$task_work/pg465-host/batch/classes:$task_work/pg465-host/bootstrap/classes:$task_work/pg465-host/storage/classes:$task_work/pg465-host/protocol/classes:$task_work/pg465-release-v2/api/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg468OwnedIsolation.java tools/quality/vm/050_s1/Pg468Known30PairRecovery.java tools/quality/vm/050_s1/Pg468CapturedPeers.java tools/quality/vm/050_s1/Pg468Known30PairRecoveryTest.java tools/quality/vm/050_s1/Pg468CapturedPeersTest.java > "$task_work/pg468-recovery-compile-v2.private.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg468Known30PairRecoveryTest > "$task_work/pg468-recovery-oracle-v2.private.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg468CapturedPeersTest "$task_work/pg467-parent-watch-private-v1.jsonl" > "$task_work/pg468-peer-oracle-v2.private.log" 2>&1
printf 'PG468_RECOVERY_TOOLS Werror0=true independentOracle0=true nativeMutation=false productionPT0=true\n'
