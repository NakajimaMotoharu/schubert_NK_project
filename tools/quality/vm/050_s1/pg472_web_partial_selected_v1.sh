#!/bin/bash
# Meaningful Web partial-owner/request identity negative group, not native acceptance.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg472-web-partial-selected-v1
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=ns > "$task_base.started"
task_exit=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Dtest=MessageCodecTest,ResourceScopeTest,PrivateDirectoryEntryTest,FixedServiceIdentityTest,ServiceCredentialSetTest,WebProcessMainTest,WebProcessLifetimeTest,WebNativeRuntimePartialTest,WebRequestIdentityConsistencyTest
) > "$task_base.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=ns > "$task_base.completed"
printf 'PG472_WEB_PARTIAL_SELECTED actualExit=%s formal=false nativeNotReused=true\n' "$task_exit"
exit "$task_exit"
