#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg481-retirement-tools-v3
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg481-pending-tools-v2:$task_work/pg480-backup-tools-v6:$task_work/pg477-completed-tools-v1:$task_work/pg477-partial-tools-v1:$task_work/pg475-readback-tools-v4:$task_work/pg474-readback-tools-v3:$task_work/pg473-readback-tools-v3:$task_work/pg471-readback-tools-v4:$task_work/pg471-completed-tools-v2:$task_work/pg469-current-tools-v3:$task_work/pg468-recovery-tools-v5:$task_work/pg468-recovery-tools-v2:$task_work/pg466-tool-v3:$task_work/pg465-completed-tool-v3:$task_work/pg464-completed-tools-v7:$task_work/pg464-code-tools-v2:$task_work/pg461-known30-tool-v3:$task_work/pg456-tools-v7:$task_work/pg479-host/api/classes:$task_work/pg479-host/batch/classes:$task_work/pg479-host/bootstrap/classes:$task_work/pg479-host/storage/classes:$task_work/pg479-host/protocol/classes:$task_work/pg479-release-v1/api/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg481RuntimeRetirement.java > "$task_work/pg481-retirement-compile-v3.private.log" 2>&1
python3 -B tools/quality/vm/050_s1/pg481_runtime_retirement_test.py > "$task_work/pg481-retirement-oracle-v3.private.log"
printf 'PG481_RESUME_TOOLS Werror0=true independentOracle0=true nativeMutation0=true productionPT0=true\n'
