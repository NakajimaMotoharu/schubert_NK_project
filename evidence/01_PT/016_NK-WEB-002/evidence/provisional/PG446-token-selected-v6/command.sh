#!/bin/bash
set -eu
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH="/home/mini/codex/project1/work/toolchain/node-v24.19.0-linux-x64/bin:$JAVA_HOME/bin:$PATH"
task_run=/home/mini/codex/project1/work/pgpt-runs/PG379
git rev-parse HEAD > "$task_run/pg446-token-selected-v6.source"
git ls-files -co --exclude-standard src tools | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_run/pg446-token-selected-v6.source-files.sha256"
set +e
./mvnw -o --no-transfer-progress -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0-linux-x64/bin/node -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch -Dtest=FieldCodecTest,StorageAttributeGuardTest,FixedServiceIdentityTest,OperationFingerprintTest,MaintenanceRecordsTest,SessionAttributeCodecTest,SessionOperationTokenV2Test,SessionOperationTokenLifecycleTest,SessionPayloadCodecTest,EncryptedWebSessionRepositoryTest,SpringWebSessionTest,WebCsrfIntegrationTest,ApiSessionInvalidTest,SessionSecurityContextTest,SessionSavedRequestTest,SessionFormLoginTest clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report > "$task_run/pg446-token-selected-v6.log" 2>&1
task_exit=$?
printf '%s\n' "$task_exit" > "$task_run/pg446-token-selected-v6.exit"
printf 'PG446_TOKEN_SELECTED_V6 actualExit=%s log=WorkPG379/pg446-token-selected-v6.log\n' "$task_exit"
exit "$task_exit"
