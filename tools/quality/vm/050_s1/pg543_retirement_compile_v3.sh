#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg543-retirement-tools-v3
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg498-pending-tools-v3:$task_work/pg464-code-tools-v2:$task_work/pg490-migration-tools-v4:$task_work/pg481-pending-tools-v2:$task_work/pg456-tools-v7:$task_work/pg495-host/api/classes:$task_work/pg495-host/batch/classes:$task_work/pg495-host/bootstrap/classes:$task_work/pg495-host/storage/classes:$task_work/pg495-host/protocol/classes:$task_work/pg495-release-v1/api/lib/*:$task_work/pg495-release-v1/operations/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg543RuntimeRetirement.java > "$task_work/pg543-retirement-compile-v3.private.log" 2>&1

python3 -B tools/quality/vm/050_s1/pg543_retirement_contract_test.py > "$task_work/pg543-retirement-oracle-v3.private.log" 2>&1
printf 'PG543_COMPILED Werror0=true managementOnly=true\n'
