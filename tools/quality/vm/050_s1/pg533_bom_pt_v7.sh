#!/bin/bash
# BUG826/YKT595 / NK-OPS-001 / SS343354 / PT-OPS-FULLBOM001..019; limited, not formal.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
git diff --exit-code HEAD -- src tools pom.xml
test -z "$(git ls-files --others --exclude-standard -- src tools)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg533-bom-pt-v7
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base.started"
git rev-parse HEAD > "$task_base.source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base.source-files.sha256"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-storage,src/schubert-nk-bootstrap clean spotless:check test-compile org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar test spotbugs:check jacoco:report
) > "$task_base.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
sha256sum --check --status "$task_base.source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
git diff --exit-code HEAD -- src tools pom.xml
printf 'PG533_BOM_PT_V7 actualExit=%s sourceUnchanged=true\n' "$task_result"
exit "$task_result"
