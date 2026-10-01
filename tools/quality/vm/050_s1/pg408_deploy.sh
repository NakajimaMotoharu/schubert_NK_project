#!/usr/bin/env bash
# PG408 one activation: old genuine normal30 capture precedes stop; typed retirement under M/A.
set -euo pipefail
repo=/home/mini/codex/project1/work/pgpt-foundation
run=/home/mini/codex/project1/work/pgpt-runs/PG379
private=/home/mini/codex/project1/work/pgpt-vm/private
jdk=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
source=$(python3 -c 'import json; print(json.load(open("/home/mini/codex/project1/work/pgpt-foundation/evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG408-root-recovery-baseline/manifest.json"))["sourceCommit"])')
[[ "$source" =~ ^[0-9a-f]{40}$ ]]
ssh_options=(-i "$private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
scp_options=(-i "$private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
cd "$repo"
test "$(git rev-parse HEAD)" = "$source"
git diff --exit-code HEAD -- src tools pom.xml
test ! -e "$private/pg408-release"
test ! -e "$run/pg408-host"
mkdir -m 700 "$run/pg408-host"
for module in protocol storage bootstrap api web batch; do cp "src/schubert-nk-$module/target/jacoco.exec" "$run/pg408-host/$module.exec"; done
"$jdk/bin/java" -cp "$run/pg390-tools:src/schubert-nk-batch/target/classes:src/schubert-nk-bootstrap/target/classes:src/schubert-nk-storage/target/classes:src/schubert-nk-api/target/dependency/*:/home/mini/codex/project1/work/toolchain/m2/repository/org/flywaydb/flyway-core/13.4.0/flyway-core-13.4.0.jar" AssembleReleaseFixture "$repo" "$private/pg408-release" "$source" 0.1.0-PG408 "$private/pg381-backup-profile.json" "$private/pg381-backup-age-recipient"
openssl pkeyutl -sign -rawin -inkey "$private/pg381-release-signing.pem" -in "$private/pg408-release/RELEASE-MANIFEST.json" -out "$private/pg408-manifest.sig"
test "$(stat -c %s "$private/pg408-manifest.sig")" = 64
tar -C "$private/pg408-release" -cf "$private/pg408-release.tar" .
digest=$(sha256sum "$private/pg408-release/RELEASE-MANIFEST.json")
digest=${digest%% *}
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg408-stage && mkdir -m 700 /home/ubuntu/pg408-stage'
scp "${scp_options[@]}" "$private/pg408-release.tar" "$private/pg408-manifest.sig" tools/quality/vm/050_s1/place_followup.py "$run/pg408-tools/Pg387TrustedDeployment.class" "$run/pg408-tools/Pg387TrustedDeployment\$Checked.class" "$run/pg408-tools/Pg407FailedRootRecovery.class" ubuntu@127.0.0.1:/home/ubuntu/pg408-stage/
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 "sudo -n python3 /home/ubuntu/pg408-stage/place_followup.py PG408 $digest" > "$run/pg408-place.log" 2>&1
# Candidate signature/BOM verification is inside the same activate call, before old intent mutation.
# Separate verify/stop/start cannot overwrite the sole captured old receipt.
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 "sudo -n /usr/bin/java --enable-native-access=ALL-UNNAMED -cp '/home/ubuntu/pg408-stage:/opt/schubert-nk/releases/0.1.0-PG408/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG408/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG408/api/lib/*' Pg387TrustedDeployment activate 0.1.0-PG408 $source" > "$run/pg408-activate.log" 2>&1
printf 'PG408 deployment complete manifest=%s source=%s permitsIssued=0\n' "$digest" "$source"
