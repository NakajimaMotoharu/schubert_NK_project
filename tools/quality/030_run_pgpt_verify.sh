#!/bin/sh
# Run a new, same-day full PGPT gate without reusing an earlier run ID.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/../.." && pwd -P)
cd "$repo"
run_id=${1:?run ID required}
today=$(TZ=Asia/Tokyo date +%Y%m%d)
case "$run_id" in "PT-WEB-$today"-*) ;; *) exit 2 ;; esac
printf '%s\n' "$run_id" | rg -q '^PT-WEB-[0-9]{8}-[0-9]{2}$' || exit 2
umask 077
export GIT_NO_REPLACE_OBJECTS=1
git_dir=$(git rev-parse --absolute-git-dir)
exec 9>"$git_dir/pgpt-verify.lock"
flock -n 9
require_clean_checkout() {
    state=$(git status --porcelain --untracked-files=normal) || return $?
    test -z "$state" || return 1
    visibility=$(git ls-files -v -- .mvn mvnw mvnw.cmd pom.xml src program/characterization tools/quality) || return $?
    # Lowercase marks assume-unchanged and S marks skip-worktree.
    printf '%s\n' "$visibility" | LC_ALL=C awk '/^[a-zS] / { hidden = 1 } END { exit hidden }'
}
require_recorded_checkout() {
    current_commit=$(git rev-parse HEAD) || return $?
    current_branch=$(git branch --show-current) || return $?
    test "$source_commit" = "$current_commit" || return 1
    test "$source_branch" = "$current_branch" || return 1
    require_clean_checkout
}
require_clean_checkout
source_branch=$(git branch --show-current)
test -n "$source_branch"
record="/tmp/$run_id"
for suffix in started commit branch log completed exit junit.json; do
    marker="$record.$suffix"
    test ! -e "$marker" && test ! -L "$marker" || exit 1
done
# Keep the claim after any terminal outcome. An interrupted run ID is also spent.
mkdir "$record.claim"
source_commit=$(git rev-parse HEAD)
printf '%s\n' "$source_commit" > "$record.commit"
printf '%s\n' "$source_branch" > "$record.branch"
date --iso-8601=seconds > "$record.started"
result=0
# HotSpot applies this inherited variable after the fixed JVM arguments.
unset MAVEN_ARGS _JAVA_OPTIONS
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress clean verify > "$record.log" 2>&1 || result=$?
date --iso-8601=seconds > "$record.completed"
if [ "$result" -eq 0 ]; then
    require_recorded_checkout || result=$?
fi
if [ "$result" -eq 0 ]; then
    python3 -B tools/quality/pgpt_reactor_junit.py "$run_id" "$source_commit" || result=$?
fi
if [ "$result" -eq 0 ]; then
    require_recorded_checkout || result=$?
fi
printf '%s\n' "$result" > "$record.claim/terminal"
mv "$record.claim/terminal" "$record.exit"
tail -24 "$record.log"
exit "$result"
