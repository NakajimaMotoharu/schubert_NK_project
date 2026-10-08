#!/bin/bash
# P017-01.02 / BUG869: fresh same-source dependency reactor, six PT/static; old v1 preserved.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg585-access-reactor-v3
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin:$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=seconds > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
if test "$task_result" = 0; then
  for task_module in protocol storage bootstrap api web batch; do
    mkdir -m 700 "$task_base/$task_module"
    cp "src/schubert-nk-$task_module/target/jacoco.exec" "$task_base/$task_module/"
    cp "src/schubert-nk-$task_module/target/schubert-nk-$task_module-0.1.0-SNAPSHOT.jar" "$task_base/$task_module/"
    cp "src/schubert-nk-$task_module/target/spotbugsXml.xml" "$task_base/$task_module/"
    cp -a "src/schubert-nk-$task_module/target/surefire-reports" "$task_base/$task_module/"
    cp "src/schubert-nk-$task_module/target/site/jacoco/jacoco.xml" "$task_base/$task_module/"
  done
fi
printf 'PG585_ACCESS_PT actualExit=%s sourceUnchanged=true\n' "$task_result"
exit "$task_result"
