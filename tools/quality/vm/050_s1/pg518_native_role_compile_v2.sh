#!/bin/bash
set -euo pipefail
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg518-native-role-tools-v2
test ! -e "$task_target"
task_repo=/home/mini/codex/project1/work/toolchain/m2/repository
task_annotations="$task_repo/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar:$task_repo/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar:$task_repo/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
task_junit="$task_repo/org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar:$task_repo/org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar:$task_repo/org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar"
task_cp="$task_work/pg498-pending-tools-v3:$task_work/pg464-code-tools-v2:$task_work/pg490-migration-tools-v4:$task_work/pg481-pending-tools-v2:$task_work/pg456-tools-v7:$task_work/pg495-host/api/classes:$task_work/pg495-host/batch/classes:$task_work/pg495-host/batch/test-classes:$task_work/pg495-host/bootstrap/classes:$task_work/pg495-host/storage/classes:$task_work/pg495-host/protocol/classes:$task_work/pg495-release-v1/api/lib/*:$task_work/pg495-release-v1/operations/lib/*:$task_annotations:$task_junit"
mkdir -m 700 "$task_target"
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javac -Xlint:all -Werror -cp "$task_cp" -d "$task_target" tools/quality/vm/050_s1/Pg513SingleApiIntent.java tools/quality/vm/050_s1/Pg513SingleApiIntentTest.java tools/quality/vm/050_s1/Pg515IssuedApiRecovery.java tools/quality/vm/050_s1/Pg515IssuedApiRecoveryTest.java tools/quality/vm/050_s1/Pg518NativeRoleDirectory.java tools/quality/vm/050_s1/Pg518NativeRoleDirectoryTest.java tools/quality/vm/050_s1/Pg518NativeRolePreparation.java > "$task_work/pg518-native-role-compile-v2.private.log" 2>&1
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" dev.codex.schubert.nk.batch.file.Pg513SingleApiIntentTest > "$task_work/pg518-native-role-java-oracle-v2.private.log" 2>&1
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" dev.codex.schubert.nk.batch.file.Pg515IssuedApiRecoveryTest > "$task_work/pg518-native-role-issued-oracle-v2.private.log" 2>&1
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "$task_target:$task_cp" dev.codex.schubert.nk.batch.file.Pg518NativeRoleDirectoryTest > "$task_work/pg518-native-role-directory-oracle-v2.private.log" 2>&1
python3 -B tools/quality/vm/050_s1/pg518_native_role_refs_test.py > "$task_work/pg518-native-role-reference-oracle-v2.private.log" 2>&1
python3 -B tools/quality/vm/050_s1/pg506_native_namespace_contract_test.py > "$task_work/pg518-native-role-broker-oracle-v2.private.log" 2>&1
printf 'PG518_COMPILED independentOperatorTests=true Werror0=true nativeActions0=true productionPT0=true\n'
