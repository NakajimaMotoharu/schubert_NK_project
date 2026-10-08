#!/bin/bash
# SSC228 management tool only, no Production PT credit or VM operations.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg635-resume-tools-v1
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg633-pending-tools-v2:$task_work/pg498-pending-tools-v3:$task_work/pg464-code-tools-v2:$task_work/pg490-migration-tools-v4:$task_work/pg481-pending-tools-v2:$task_work/pg456-tools-v7:$task_work/pg630-retention-factory-six-host-v1/api/schubert-nk-api-0.1.0-SNAPSHOT.jar:$task_work/pg630-retention-factory-six-host-v1/batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar:$task_work/pg630-retention-factory-six-host-v1/bootstrap/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar:$task_work/pg630-retention-factory-six-host-v1/storage/schubert-nk-storage-0.1.0-SNAPSHOT.jar:$task_work/pg630-retention-factory-six-host-v1/protocol/schubert-nk-protocol-0.1.0-SNAPSHOT.jar:$task_work/pg631-release-v1/api/lib/*:$task_work/pg631-release-v1/operations/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg635ResumePreparation.java tools/quality/vm/050_s1/Pg635ResumePreparationTest.java > "$task_work/pg635-compile-v1.private.log" 2>&1
python3 -B tools/quality/vm/050_s1/pg635_resume_contract_test.py > "$task_work/pg635-oracle-v1.private.log" 2>&1
"$task_java/java" -cp "$task_target:$task_cp" Pg635ResumePreparationTest >> "$task_work/pg635-oracle-v1.private.log" 2>&1
printf 'PG635_COMPILED Werror0=true authority0=true\n'
