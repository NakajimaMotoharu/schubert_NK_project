#!/bin/bash
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg616-missing-observer-host-v1
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
task_result=0
(
umask 0027
python3 -B tools/quality/qualified_nullable_check.py &&
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-bootstrap spotless:check test-compile test spotbugs:check jacoco:report jar:jar -Dtest=ChildStartupContextTest
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=seconds > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
if test "$task_result" = 0; then
  cp src/schubert-nk-bootstrap/target/jacoco.exec "$task_base/bootstrap.exec"
  cp src/schubert-nk-bootstrap/target/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar "$task_base/"
  cp src/schubert-nk-bootstrap/target/spotbugsXml.xml "$task_base/"
  cp src/schubert-nk-bootstrap/target/site/jacoco/jacoco.xml "$task_base/"
  cp src/schubert-nk-bootstrap/target/surefire-reports/TEST-dev.codex.schubert.nk.bootstrap.ChildStartupContextTest.xml "$task_base/"
fi
printf 'PG616_SELECTED actualExit=%s fixedSource=true nativeReplayed0=true formalAccepted=false\n' "$task_result"
exit "$task_result"
