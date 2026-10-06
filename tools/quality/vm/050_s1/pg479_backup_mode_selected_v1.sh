#!/bin/bash
# SSC197/BUG771, independent mode oracle; optional red invocation retained separately.
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
case "$1" in red|green) ;; *) exit 64;; esac
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg479-backup-mode-selected-$1-v2
test ! -e "$task_base.log"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=ns > "$task_base.started"
git rev-parse HEAD > "$task_base.source"
git diff -- src pom.xml > "$task_base.source-diff.private"
task_exit=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-batch spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report -Djunit.jupiter.execution.parallel.enabled=false -Dtest=MessageCodecTest,ResourceScopeTest,FixedServiceIdentityTest,ApiProcessMainTest,MorningBackupInputModeTest,MorningBackupCatalogTest,InspectorEnvironmentReaderTest,BackupProfileTest
) > "$task_base.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_base.exit"
date --iso-8601=ns > "$task_base.completed"
printf 'PG479_MODE_SELECTED phase=%s actualExit=%s native=false formal=false\n' "$1" "$task_exit"
exit "$task_exit"
