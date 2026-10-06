#!/bin/bash
# PG-D389 / HEALTH001..003, FULLBOM011..013. Fresh selected group, not formal/native.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg483-api-bom-selected-v1
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=ns > "$task_base.started"
git rev-parse HEAD > "$task_base.source"
git diff -- src pom.xml > "$task_base.source-diff.private"
task_exit=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api clean spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Djunit.jupiter.execution.parallel.enabled=false -Dtest=MessageCodecTest,ResourceScopeTest,FixedServiceIdentityTest,ReleasePayloadVerificationTest,NativeCoveragePrivateFileTest,FixedNativeCoverageCheckpointTest,FixedNativeCoverageStopHoldTest,ApiReadinessPredicateTest,ApiProcessMainTest,ApiProcessLifetimeTest,ApiManagementServerTest,ApiDependencyReadinessTest
) > "$task_base.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=ns > "$task_base.completed"
git diff -- src pom.xml > "$task_base.completed-source-diff.private"
printf 'PG483_API_BOM_SELECTED actualExit=%s formal=false nativeNotReused=true\n' "$task_exit"
exit "$task_exit"
