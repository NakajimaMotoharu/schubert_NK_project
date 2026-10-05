#!/bin/bash
# Fresh actual PG463 timeout143 cohort; independent host tools only, no Production PT credit.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg464-code-tools-v1
test ! -e "$task_target"
mkdir "$task_target"
task_cp="$task_work/pg461-known30-tool-v3:$task_work/pg456-tools-v7:$task_work/pg463-host/batch/target/classes:$task_work/pg463-host/bootstrap/target/classes:$task_work/pg463-host/storage/target/classes:$task_work/pg463-host/protocol/target/classes:$task_work/pg463-host/api/target/classes:$task_work/pg463-release-v3/api/lib/*:/home/mini/codex/project1/work/toolchain/m2/repository/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:/home/mini/codex/project1/work/toolchain/m2/repository/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:/home/mini/codex/project1/work/toolchain/m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg464CodeOnlyDeployment.java tools/quality/vm/050_s1/Pg464CodeOnlyDeploymentTest.java > "$task_work/pg464-code-compile-v1.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg464CodeOnlyDeploymentTest > "$task_work/pg464-code-tests-v1.log" 2>&1
printf 'PG464_CODE_TOOLS compileWerror0=true independentTests0=true productionPt0=true nativeMutation=false\n'
