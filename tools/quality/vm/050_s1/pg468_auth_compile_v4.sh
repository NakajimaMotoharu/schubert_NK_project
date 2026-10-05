#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg468-auth-tools-v4
test ! -e "$task_target"
task_cp="$task_work/pg460-chr-host/test-classes:$task_work/pg460-chr-host/classes:$(<"$task_work/pg459-chr-classpath.private")"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" program/characterization/tests/java/dev/codex/schubert/characterization/CurrentCharacterizationTest.java program/characterization/tests/java/dev/codex/schubert/characterization/NativeNkBootstrapAuthentication.java program/characterization/tests/java/dev/codex/schubert/characterization/NativeNkBootstrapAuthenticationOracleTest.java > "$task_work/pg468-auth-compile-v4.private.log" 2>&1
"$task_java/java" -cp "$task_target:$task_cp" dev.codex.schubert.characterization.NativeNkBootstrapAuthenticationOracleTest > "$task_work/pg468-auth-oracle-v4.private.log" 2>&1
sha256sum program/characterization/tests/java/dev/codex/schubert/characterization/CurrentCharacterizationTest.java program/characterization/tests/java/dev/codex/schubert/characterization/NativeNkBootstrapAuthentication.java > "$task_work/pg468-auth-sources-v4.private.sha256"
printf 'PG468_AUTH_TOOLS_V4 Werror0=true independentOracle0=true productionPt0=true nativeMutation=false\n'
