#!/bin/bash
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg557-native-tools-v1
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_cp="$task_work/pg498-pending-tools-v3:$task_work/pg464-code-tools-v2:$task_work/pg490-migration-tools-v4:$task_work/pg481-pending-tools-v2:$task_work/pg456-tools-v7:$task_work/pg548-release-v1/api/api.jar:$task_work/pg548-release-v1/operations/batch.jar:$task_work/pg548-release-v1/api/lib/*:$task_work/pg548-release-v1/operations/lib/*:$task_annotations"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg557NativeStop.java tools/quality/vm/050_s1/Pg557NativeArgumentTest.java > "$task_work/pg557-native-compile-v1.private.log" 2>&1

python3 -B tools/quality/vm/050_s1/pg557_native_owned_stop_test.py > "$task_work/pg557-native-oracle-v1.private.log"
"$task_java/java" -cp "$task_target:$task_cp" Pg557NativeArgumentTest > "$task_work/pg557-argument-oracle-v1.private.log"
python3 -B tools/quality/vm/050_s1/pg557_reference_protocol_test.py > "$task_work/pg557-reference-oracle-v1.private.log"
python3 -B tools/quality/vm/050_s1/pg556_parent_receipt_test.py > "$task_work/pg557-batch-oracle-v1.private.log" 2>&1
printf 'PG557_NATIVE_TOOL Werror0=true pureOracle0=true guestMutations0=true productionPT0=true\n'
