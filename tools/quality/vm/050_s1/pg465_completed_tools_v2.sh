#!/bin/bash
# SSC190/BUG716717/YKT510; host paths are not guest preservation names. ProductionPT0.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg465-completed-tool-v2
test ! -e "$task_target"
for task_pair in pg464-completed-tools-v7/Pg464CompletedReadback.class pg464-code-tools-v2/Pg464CodeOnlyDeployment.class pg461-known30-tool-v3/Pg461Known30PairRecovery.class pg456-tools-v7/Pg387TrustedDeployment.class pg465-host/batch/classes/dev/codex/schubert/nk/batch/file/StartupPermitFiles.class; do test -f "$task_work/$task_pair"; done
for task_module in protocol storage bootstrap api web batch; do test -d "$task_work/pg465-host/$task_module/classes"; done
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
for task_jar in "$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar" "$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar" "$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"; do test -f "$task_jar"; done
task_cp="$task_work/pg464-completed-tools-v7:$task_work/pg464-code-tools-v2:$task_work/pg461-known30-tool-v3:$task_work/pg456-tools-v7:$task_work/pg465-host/batch/classes:$task_work/pg465-host/bootstrap/classes:$task_work/pg465-host/storage/classes:$task_work/pg465-host/protocol/classes:$task_work/pg465-host/api/classes:$task_work/pg465-release-v2/api/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg465CompletedDeployment.java tools/quality/vm/050_s1/Pg465CompletedDeploymentTest.java > "$task_work/pg465-completed-compile-v2.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg465CompletedDeploymentTest > "$task_work/pg465-completed-tests-v2.log" 2>&1
printf 'PG465_COMPLETED_HOST compileWerror0=true independentTools0=true nativeMutation=false productionPT0=true\n'
