#!/bin/bash
# PG-D379 / PT-OPS-API-REM001..004/FACT001; changed ownership group only.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg474-api-consumers-selected-v6
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=ns > "$task_base.started"
git rev-parse HEAD > "$task_base.source"
git diff -- src pom.xml > "$task_base.source-diff.private"
rg --files src -g '*.java' -g pom.xml | sort | xargs sha256sum > "$task_base.source-files.sha256"
task_exit=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Dtest=MessageCodecTest,ResourceScopeTest,PrivateDirectoryEntryTest,FixedServiceIdentityTest,ServiceCredentialSetTest,ApiMessagingRuntimeTest,WebLogConsumersTest,SyncRequestConsumersTest,QuestionWorkConsumersTest,ApiConsumerRemainderTest,ApiConsumerTerminalRemainderTest,ApiBrokerContextsTest,ApiBrokerContextsCredentialTest,ApiBrokerFactoryRemainderTest
) > "$task_base.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=ns > "$task_base.completed"
printf 'PG474_API_CONSUMERS_SELECTED actualExit=%s formal=false nativeNotReused=true\n' "$task_exit"
exit "$task_exit"
