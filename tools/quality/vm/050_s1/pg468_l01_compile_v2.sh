#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_target=$task_work/pg468-l01-tools-v2
test ! -e "$task_target"
task_cp="$task_work/pg468-auth-tools-v6:$task_work/pg460-chr-host/test-classes:$task_work/pg460-chr-host/classes:$(<"$task_work/pg459-chr-classpath.private")"
mkdir -m 700 "$task_target"
task_java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin
"$task_java/javac" -Xlint:all -Werror -cp "$task_cp" -d "$task_target" program/characterization/tests/java/dev/codex/schubert/characterization/NativeNkL01Capture.java > "$task_work/pg468-l01-compile-v2.private.log" 2>&1
printf 'PG468_L01_TOOLS Werror0=true nativeMutation=false comparisonNotAccepted=true currentBaselineUnchanged=true\n'
