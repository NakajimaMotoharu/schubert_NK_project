#!/bin/bash
# PG-D401 / 546: one fresh API component run, no target-sharing parallel Maven.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg669-entry-component-v1
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=ns > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
if test -e src/schubert-nk-api/target/jacoco.exec; then
  mv src/schubert-nk-api/target/jacoco.exec "$task_base/preexisting-api.exec"
fi
task_result=0
(
umask 0027
python3 -B tools/quality/qualified_nullable_check.py &&
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-api spotless:check test-compile test spotbugs:check jacoco:report jar:jar -Dtest=BootstrapEntryBoundaryTest,BootstrapAdminMainTest,InspectorEntryBoundaryTest,InspectorLauncherTest,InspectorApplicationTest,InspectorProcessTest
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=ns > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
mkdir -m 700 "$task_base/surefire-reports"
for task_class in \
  dev.codex.schubert.nk.api.bootstrap.BootstrapEntryBoundaryTest \
  dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMainTest \
  dev.codex.schubert.nk.api.maintenance.InspectorEntryBoundaryTest \
  dev.codex.schubert.nk.api.maintenance.InspectorLauncherTest \
  dev.codex.schubert.nk.api.file.InspectorApplicationTest \
  dev.codex.schubert.nk.api.maintenance.InspectorProcessTest; do
  test -f "src/schubert-nk-api/target/surefire-reports/TEST-$task_class.xml"
  cp "src/schubert-nk-api/target/surefire-reports/TEST-$task_class.xml" "$task_base/surefire-reports/"
done
if test "$task_result" = 0; then
  cp src/schubert-nk-api/target/jacoco.exec "$task_base/api.exec"
  cp src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar "$task_base/"
  cp src/schubert-nk-api/target/spotbugsXml.xml "$task_base/"
  cp src/schubert-nk-api/target/site/jacoco/jacoco.xml "$task_base/"
fi
printf 'PG669_ENTRY_SELECTED actualExit=%s fixedSource=true nativeVmUnchanged=true formalAccepted=false\n' "$task_result"
exit "$task_result"
