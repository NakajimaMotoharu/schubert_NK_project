#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
case "$1" in red|fixed|faults) ;; *) exit 2 ;; esac
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg469-scenario-$1-v3
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=/home/mini/codex/project1/work/toolchain/node-v34.19.0/bin:$JAVA_HOME/bin:$PATH
task_controls=MessageCodecTest,ResourceScopeTest,FixedServiceIdentityTest
task_tests=$task_controls,ScenarioApplicationServiceTest
if test "$1" = red; then task_tests="$task_controls,ScenarioApplicationServiceTest#successAuditIsAtomicAndNotRepeatedForSavedSearchAndDetail+criticalAuditFailureRollsBackInboxAndCanBeRetried"; fi
if test "$1" = faults; then task_tests=$task_controls,ScenarioApplicationServiceTest,ScenarioAuditWriterTest,ScenarioRequestTest,ScenarioReplayServiceTest; fi
date --iso-8601=seconds > "$task_base.started"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report "-Dtest=$task_tests"
) > "$task_base.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG469_SCENARIO actualExit=%s run=%s\n' "$task_result" "$1"
exit "$task_result"
