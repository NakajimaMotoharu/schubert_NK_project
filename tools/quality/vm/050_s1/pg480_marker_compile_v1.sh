#!/bin/bash
# SSC198 / BREC198001..008, immutable full Production inputs + separate operator-tool assertions.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg480-marker-tools-v5
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_testlib="$task_repo/org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar:$task_repo/org/junit/platform/junit-platform-commons/1.13.4/junit-platform-commons-1.13.4.jar:$task_repo/org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar:$task_repo/org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar"
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg479-host/batch/classes:$task_work/pg479-host/batch/test-classes:$task_work/pg479-host/api/classes:$task_work/pg479-host/bootstrap/classes:$task_work/pg479-host/storage/classes:$task_work/pg479-host/protocol/classes:$task_work/pg479-release-v1/api/lib/*:$task_testlib:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/BackupInterruptedStartRecovery.java tools/quality/vm/050_s1/BackupInterruptedStartRecoveryTest.java > "$task_work/pg480-marker-compile-v5.private.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" dev.codex.schubert.nk.batch.file.BackupInterruptedStartRecoveryTest > "$task_work/pg480-marker-oracle-v5.private.log" 2>&1
printf 'PG480_MARKER_TOOLS Werror0=true independentMarkerOracle0=true nativeVMmutation0=true productionPT0=true\n'
