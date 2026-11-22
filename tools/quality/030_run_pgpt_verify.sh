#!/bin/sh
# Run a new, same-day full PGPT gate without reusing an earlier run ID.
set -eu
cd /home/mini/codex/project1/work/pgpt-foundation
run_id=${1:?run ID required}
today=$(TZ=Asia/Tokyo date +%Y%m%d)
case "$run_id" in "PT-WEB-$today"-*) ;; *) exit 2 ;; esac
printf '%s\n' "$run_id" | rg -q '^PT-WEB-[0-9]{8}-[0-9]{2}$' || exit 2
test -z "$(git status --porcelain)"
test ! -e "/tmp/$run_id.started"
test ! -e "/tmp/$run_id.commit"
test ! -e "/tmp/$run_id.log"
test ! -e "/tmp/$run_id.completed"
test ! -e "/tmp/$run_id.exit"
test ! -e "/tmp/$run_id.junit.json"
source_commit=$(git rev-parse HEAD)
printf '%s\n' "$source_commit" > "/tmp/$run_id.commit"
date --iso-8601=seconds > "/tmp/$run_id.started"
result=0
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress clean verify > "/tmp/$run_id.log" 2>&1 || result=$?
date --iso-8601=seconds > "/tmp/$run_id.completed"
if [ "$result" -eq 0 ]; then
    git diff --quiet "$source_commit" -- src pom.xml program/characterization tools/quality .mvn mvnw mvnw.cmd || result=$?
    if [ "$result" -eq 0 ]; then
        python3 -B tools/quality/pgpt_reactor_junit.py "$run_id" "$source_commit" || result=$?
    fi
fi
printf '%s\n' "$result" > "/tmp/$run_id.exit"
tail -24 "/tmp/$run_id.log"
exit "$result"
