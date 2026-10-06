#!/bin/bash
# PG-D389/390 and SSC199: fresh changed-group all six; not native/formal acceptance.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
git diff --exit-code HEAD -- src tools pom.xml
test -z "$(git ls-files --others --exclude-standard -- src tools)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg485-six-full-v1
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin:$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base.started"
git rev-parse HEAD > "$task_base.source"
git ls-files -co --exclude-standard src tools | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base.source-files.sha256"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar org.apache.maven.plugins:maven-dependency-plugin:3.9.0:copy-dependencies org.apache.maven.plugins:maven-dependency-plugin:3.9.0:list -DincludeScope=runtime -DoutputDirectory=target/runtime-dependencies -DoutputFile=target/runtime-dependencies.txt -DappendOutput=false
) > "$task_base.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
sha256sum --check --status "$task_base.source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
git diff --exit-code HEAD -- src tools pom.xml
printf 'PG485_FULL actualExit=%s sourceUnchanged=true\n' "$task_result"
exit "$task_result"
