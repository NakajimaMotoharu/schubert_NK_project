#!/bin/bash
# SSC204 / PT-OPS-REC204001..004. Independent host tool checks, NOT native recovery.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg496-timeout-tools-v3
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
test ! -e "$task_target"
mkdir -m700 "$task_target"
task_cp="$task_work/pg491-pending-tools-v1:$task_work/pg490-migration-tools-v4:$task_work/pg481-native-tools-v3:$task_work/pg481-pending-tools-v2:$task_work/pg456-tools-v7:$task_work/pg495-host/api/classes:$task_work/pg495-host/batch/classes:$task_work/pg495-host/bootstrap/classes:$task_work/pg495-host/storage/classes:$task_work/pg495-host/protocol/classes:$task_work/pg489-release-v1/api/lib/*:$task_work/pg489-release-v1/operations/lib/*:$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
date --iso-8601=ns > "$task_work/pg496-compile-v3.started"
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg496TimeoutRecovery.java tools/quality/vm/050_s1/Pg496TimeoutRecoveryTest.java > "$task_work/pg496-compile-v3.private.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg496TimeoutRecoveryTest > "$task_work/pg496-oracle-v3.private.log" 2>&1
date --iso-8601=ns > "$task_work/pg496-compile-v3.completed"
printf 'PG496_COMPILE actual0=true independentOracle0=true nativeNotRun=true\n'
