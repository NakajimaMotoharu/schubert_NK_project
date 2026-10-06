#!/bin/bash
# SS355/BUG742: one shared-Current business observation, no password reset or PASS substitution.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
test "$(<"$task_work/pg474-readback-native-v1.exit")" = 0
test ! -e "$task_work/pg474-l01-native-v1.private.log"
test ! -e "$task_work/pg474-l01-v1"
test -n "$(ss -H -ltn 'sport = :55169')"
task_cp="$task_work/pg474-l01-tools-v1:$task_work/pg468-auth-tools-v6:$task_work/pg460-chr-host/test-classes:$task_work/pg460-chr-host/classes:$(<"$task_work/pg459-chr-classpath.private")"
export PLAYWRIGHT_BROWSERS_PATH=/home/mini/codex/project1/work/characterization-tools/playwright-browsers
export PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64
export LD_LIBRARY_PATH=/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu
date --iso-8601=seconds > "$task_work/pg474-l01-native-v1.started"
task_exit=0
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java -cp "$task_cp" dev.codex.schubert.characterization.NativeNkL01Capture474 "$task_work/pg474-l01-v1" 09b448644cfe70c87df9c89aa5c0c1bf6efdeeea /home/mini/codex/project1/work/pgpt-vm/private/pg468-active-account.private.json > "$task_work/pg474-l01-native-v1.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg474-l01-native-v1.exit"
date --iso-8601=seconds > "$task_work/pg474-l01-native-v1.completed"
printf 'PG474_L01_OBSERVATION actualExit=%s comparisonAccepted=false resets0=true\n' "$task_exit"
exit "$task_exit"
