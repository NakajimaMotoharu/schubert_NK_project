#!/bin/bash
# SSC193 closed profile/owned entry group; BUG751 parent-private vs native-test umask.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 0
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg470-profile-selected-v4
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base.started"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Dtest=MessageCodecTest,ResourceScopeTest,PrivateDirectoryEntryTest,FixedServiceIdentityTest,FixedServiceExecArgumentsTest,FixedNativeCoverageProfileTest
) > "$task_base.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG470_PROFILE actualExit=%s\n' "$task_result"
exit "$task_result"
