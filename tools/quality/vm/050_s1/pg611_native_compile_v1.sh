#!/bin/bash
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg611-native-tools-v1
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_candidate=$task_work/pg599-candidate-bootstrap-six-host-v1
task_cp="$task_work/pg498-pending-tools-v3:$task_work/pg464-code-tools-v2:$task_work/pg490-migration-tools-v4:$task_work/pg481-pending-tools-v2:$task_work/pg456-tools-v7:$task_candidate/api/schubert-nk-api-0.1.0-SNAPSHOT.jar:$task_candidate/batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar:$task_candidate/bootstrap/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar:$task_candidate/storage/schubert-nk-storage-0.1.0-SNAPSHOT.jar:$task_candidate/protocol/schubert-nk-protocol-0.1.0-SNAPSHOT.jar:$task_work/pg548-release-v1/api/lib/*:$task_work/pg548-release-v1/operations/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg611NativeStop.java tools/quality/vm/050_s1/Pg611NativeArgumentTest.java > "$task_work/pg611-native-compile-v1.private.log" 2>&1
"$task_java/java" -cp "$task_target:$task_cp" Pg611NativeArgumentTest > "$task_work/pg611-argument-oracle-v1.private.log" 2>&1
printf 'PG611_COMPILE Werror0=true cli6=true guestOperations0=true ProductionPT0=true\n'
