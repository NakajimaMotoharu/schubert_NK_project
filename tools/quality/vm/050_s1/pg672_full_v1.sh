#!/bin/bash
# 451 changed-source whole regression; global four100/native/formal are separate gates.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg672-entry-six-host-v1
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=ns > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
task_result=0
(
umask 0027
python3 -B tools/quality/qualified_nullable_check.py &&
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=ns > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
if test "$task_result" = 0; then
  for task_module in protocol storage bootstrap api web batch; do
    task_from="src/schubert-nk-$task_module/target"
    mkdir -m 700 "$task_base/$task_module"
    cp -a "$task_from/surefire-reports" "$task_base/$task_module/"
    cp "$task_from/jacoco.exec" "$task_base/$task_module/"
    cp "$task_from/spotbugsXml.xml" "$task_base/$task_module/"
    cp "$task_from/site/jacoco/jacoco.xml" "$task_base/$task_module/"
    cp "$task_from/schubert-nk-$task_module-0.1.0-SNAPSHOT.jar" "$task_base/$task_module/"
  done
fi
printf 'PG672_FULL actualExit=%s sameSource=true staticAndXmlQualificationPending=true globalFormalAccepted=false\n' "$task_result"
exit "$task_result"
