#!/bin/bash
# SSC187/BUG704 same stopped Backup cycle + existing owner/DB/receipt/launch controls. Not formal.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg464-stopcomp-selected-v3
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin:$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base.started"
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Dtest=MessageCodecTest,ResourceScopeTest,FixedServiceIdentityTest,QuestionQueryRequestTest,WebSecurityHeaderTest,MorningCompletionChecksTest,MorningCompletionEvidenceTest,StoppedBackupCompletionTest,MorningStartupLaunchOwnerTest,MorningDatabaseSessionTest,BackupUnitReceiptGateTest,MorningBackupUnitCycleTest,MorningParentBudgetTest
) > "$task_base.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base.exit"
date --iso-8601=seconds > "$task_base.completed"
printf 'PG464_SELECTED_V3 actual exit=%s\n' "$task_result"
exit "$task_result"
