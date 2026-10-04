#!/bin/bash
# SSC185/BUG693 stateful TX owner PT + explicit six-module dependency controls; not formal.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg462-txowner-selected-v3
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=/home/mini/codex/project1/work/toolchain/node-v34.19.0/bin:$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base.started"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v34.19.0/bin/node -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Dtest=MessageCodecTest,ResourceScopeTest,FixedServiceIdentityTest,QuestionQueryRequestTest,WebSecurityHeaderTest,MorningCompletionChecksTest,MorningCompletionEvidenceTest,MorningStartupLaunchOwnerTest,MorningDatabaseSessionTest
) > "$task_base.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG462_SELECTED_V2 actual exit=%s\n' "$task_result"
exit "$task_result"
