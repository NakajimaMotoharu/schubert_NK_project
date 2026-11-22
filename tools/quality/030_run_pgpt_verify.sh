#!/bin/sh
# Run a new, same-day full PGPT gate without reusing an earlier run ID.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/../.." && pwd -P)
cd "$repo"
run_id=${1:?run ID required}
today=$(TZ=Asia/Tokyo date +%Y%m%d)
case "$run_id" in "PT-WEB-$today"-*) ;; *) exit 2 ;; esac
printf '%s\n' "$run_id" | rg -q '^PT-WEB-[0-9]{8}-[0-9]{2}$' || exit 2
state=$(git status --porcelain)
test -z "$state"
record="/tmp/$run_id"
for suffix in started commit log completed exit junit.json; do
    marker="$record.$suffix"
    test ! -e "$marker" && test ! -L "$marker" || exit 1
done
umask 077
# Keep the claim after any terminal outcome. An interrupted run ID is also spent.
mkdir "$record.claim"
source_commit=$(git rev-parse HEAD)
printf '%s\n' "$source_commit" > "$record.commit"
date --iso-8601=seconds > "$record.started"
result=0
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress clean verify > "$record.log" 2>&1 || result=$?
date --iso-8601=seconds > "$record.completed"
if [ "$result" -eq 0 ]; then
    final_commit=$(git rev-parse HEAD) || result=$?
    if [ "$result" -eq 0 ]; then
        test "$source_commit" = "$final_commit" || result=1
    fi
    if [ "$result" -eq 0 ]; then
        git diff --quiet "$source_commit" -- src pom.xml program/characterization tools/quality .mvn mvnw mvnw.cmd || result=$?
    fi
    if [ "$result" -eq 0 ]; then
        python3 -B tools/quality/pgpt_reactor_junit.py "$run_id" "$source_commit" || result=$?
    fi
fi
printf '%s\n' "$result" > "$record.claim/terminal"
mv "$record.claim/terminal" "$record.exit"
tail -24 "$record.log"
exit "$result"
