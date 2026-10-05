#!/bin/bash
# Actual PG463 timeout143/321 rows/31 -> 29; independent tools only, Production PT credit0.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg464-timeout-tool-v2
test ! -e "$task_target"
mkdir "$task_target"
task_cp="$task_work/pg461-known30-tool-v3:$task_work/pg456-tools-v7:$task_work/pg463-host/batch/target/classes:$task_work/pg463-host/bootstrap/target/classes:$task_work/pg463-host/storage/target/classes:$task_work/pg463-host/protocol/target/classes:$task_work/pg463-host/api/target/classes:$task_work/pg463-release-v3/api/lib/*:/home/mini/codex/project1/work/toolchain/m2/repository/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:/home/mini/codex/project1/work/toolchain/m2/repository/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:/home/mini/codex/project1/work/toolchain/m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg464TimeoutIsolation.java tools/quality/vm/050_s1/Pg464TimeoutIsolationTest.java tools/quality/vm/050_s1/Pg464TimeoutRetirement.java tools/quality/vm/050_s1/Pg464TimeoutRetirementTest.java tools/quality/vm/050_s1/Pg464CapturedPeers.java tools/quality/vm/050_s1/Pg464CapturedPeersTest.java > "$task_work/pg464-timeout-compile-v2.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg464CapturedPeersTest "$task_work/pg463-parent-watch-private-v1.jsonl" > "$task_work/pg464-timeout-peers-v2.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg464TimeoutIsolationTest > "$task_work/pg464-timeout-isolation-tests-v2.log" 2>&1
"$task_java/java" --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" Pg464TimeoutRetirementTest > "$task_work/pg464-timeout-retirement-tests-v2.log" 2>&1
printf 'PG464_TIMEOUT_TOOLS compileWerror0=true independentTests0=true productionPt0=true nativeMutation=false\n'
