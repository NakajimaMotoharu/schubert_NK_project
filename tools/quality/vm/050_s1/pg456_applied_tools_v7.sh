#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_run=/home/mini/codex/project1/work/pgpt-runs/PG379
task_m2=/home/mini/codex/project1/work/toolchain/m2/repository
task_jdk=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
task_cp="src/schubert-nk-protocol/target/classes:src/schubert-nk-storage/target/classes:src/schubert-nk-bootstrap/target/classes:src/schubert-nk-api/target/classes:src/schubert-nk-web/target/classes:src/schubert-nk-batch/target/classes:$task_run/pg456-host/api/dependency/*:$task_run/pg456-host/batch/dependency/*:$task_m2/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar:$task_m2/org/ow2/asm/asm/9.10.1/asm-9.10.1.jar:$task_m2/org/ow2/asm/asm-tree/9.10.1/asm-tree-9.10.1.jar:$task_m2/org/ow2/asm/asm-commons/9.10.1/asm-commons-9.10.1.jar:$task_m2/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar"
mkdir "$task_run/pg456-tools-v7"
"$task_jdk/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_run/pg456-tools-v7" tools/quality/vm/050_s1/*.java tools/quality/vm/AssembleReleaseFixture.java > "$task_run/pg456-compile-v7.log" 2>&1
for task_test in Pg455ReleaseSchemaToolTest Pg421ReleaseSchemaToolTest Pg456SignedMigrationTest Pg456AppliedCompletionTest; do
  "$task_jdk/java" --enable-native-access=ALL-UNNAMED -cp "$task_run/pg456-tools-v7:$task_cp" "$task_test" > "$task_run/pg456-$task_test-v7.log" 2>&1
done
python3 tools/quality/vm/050_s1/pg456_stage_applied_tools.py > "$task_run/pg456-applied-stage-v7.log" 2>&1
printf 'PG456_APPLIED_TOOLS_V7 actual0 warnings0 tools4 productionPt0 staged16\n'
