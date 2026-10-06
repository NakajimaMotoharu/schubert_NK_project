#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg477-stopped-tools-v4
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg475-readback-tools-v4:$task_work/pg474-readback-tools-v3:$task_work/pg473-readback-tools-v3:$task_work/pg471-readback-tools-v4:$task_work/pg471-completed-tools-v2:$task_work/pg469-current-tools-v3:$task_work/pg468-recovery-tools-v5:$task_work/pg468-recovery-tools-v2:$task_work/pg466-tool-v3:$task_work/pg465-completed-tool-v3:$task_work/pg464-completed-tools-v7:$task_work/pg464-code-tools-v2:$task_work/pg461-known30-tool-v3:$task_work/pg456-tools-v7:$task_work/pg477-host/api/classes:$task_work/pg477-host/batch/classes:$task_work/pg477-host/bootstrap/classes:$task_work/pg477-host/storage/classes:$task_work/pg477-host/protocol/classes:$task_work/pg477-release-v1/api/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg477UnitReferences.java tools/quality/vm/050_s1/Pg477StoppedDeployment.java tools/quality/vm/050_s1/Pg477StoppedDeploymentTest.java > "$task_work/pg477-stopped-compile-v4.private.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg477StoppedDeploymentTest > "$task_work/pg477-stopped-oracle-v4.private.log" 2>&1
printf 'PG477_STOPPED_TOOLS Werror0=true independentReadbackOracle0=true nativeMutation=false productionPT0=true\n'
