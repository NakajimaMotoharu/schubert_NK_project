#!/usr/bin/env bash
# Same frozen PG400 source; fixed signed candidate and preserved old Unit bases.
set -euo pipefail
repo=/home/mini/codex/project1/work/pgpt-foundation
run=/home/mini/codex/project1/work/pgpt-runs/PG379
private=/home/mini/codex/project1/work/pgpt-vm/private
jdk=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
source=bb003f2b8bca09456cd8bb856dbdd22f4a09f872
ssh_options=(-i "$private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
scp_options=(-i "$private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
cd "$repo"
git merge-base --is-ancestor "$source" HEAD
git diff --exit-code "$source" -- src pom.xml
git diff --exit-code HEAD -- src tools pom.xml
test ! -e "$private/pg400-release"
if test ! -e "$run/pg400-host"; then mkdir -m 700 "$run/pg400-host"; fi
for module in protocol storage bootstrap api web batch; do
  if test -e "$run/pg400-host/$module.exec"; then
    cmp "src/schubert-nk-$module/target/jacoco.exec" "$run/pg400-host/$module.exec"
  else
    cp "src/schubert-nk-$module/target/jacoco.exec" "$run/pg400-host/$module.exec"
  fi
done
"$jdk/bin/java" -cp "$run/pg390-tools:src/schubert-nk-batch/target/classes:src/schubert-nk-bootstrap/target/classes:src/schubert-nk-storage/target/classes:src/schubert-nk-api/target/dependency/*:/home/mini/codex/project1/work/toolchain/m2/repository/org/flywaydb/flyway-core/13.4.0/flyway-core-13.4.0.jar" AssembleReleaseFixture "$repo" "$private/pg400-release" "$source" 0.1.0-PG400 "$private/pg381-backup-profile.json" "$private/pg381-backup-age-recipient"
openssl pkeyutl -sign -rawin -inkey "$private/pg381-release-signing.pem" -in "$private/pg400-release/RELEASE-MANIFEST.json" -out "$private/pg400-manifest.sig"
test "$(stat -c %s "$private/pg400-manifest.sig")" = 64
tar -C "$private/pg400-release" -cf "$private/pg400-release.tar" .
digest=$(sha256sum "$private/pg400-release/RELEASE-MANIFEST.json")
digest=${digest%% *}
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg400-stage && mkdir -m 700 /home/ubuntu/pg400-stage'
scp "${scp_options[@]}" "$private/pg400-release.tar" "$private/pg400-manifest.sig" tools/quality/vm/050_s1/place_followup.py "$run/pg390-tools/Pg387TrustedDeployment.class" "$run/pg390-tools/Pg387TrustedDeployment\$Checked.class" ubuntu@127.0.0.1:/home/ubuntu/pg400-stage/
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 "sudo -n python3 /home/ubuntu/pg400-stage/place_followup.py PG400 $digest" > "$run/pg400-place.log" 2>&1
# Before deployment: exact prior signed Source bases, not the two new definitions yet.
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n python3 -' > "$run/pg400-old-unit-base.log" 2>&1 <<'PY'
import hashlib, pathlib
release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG399/systemd')
for name in ('schubert-nk-morning-controller.service','schubert-nk-backup.service',
             'schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service',
             'schubert-nk-expiry-cleanup.service','schubert-nk-api.service',
             'schubert-nk-web.service','artemis.service'):
    actual=pathlib.Path('/etc/systemd/system')/name
    assert actual.is_file() and not actual.is_symlink()
    assert actual.read_bytes()==(release/name).read_bytes(),name
    print(name,hashlib.sha256(actual.read_bytes()).hexdigest(),'OLD_SOURCE_IDENTICAL')
print('PRIOR_UNIT_BASE_OK count=8 dropInsPreserved=true')
PY
for mode in verify activate; do
  ssh "${ssh_options[@]}" ubuntu@127.0.0.1 "sudo -n /usr/bin/java --enable-native-access=ALL-UNNAMED -cp '/home/ubuntu/pg400-stage:/opt/schubert-nk/releases/0.1.0-PG400/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG400/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG400/api/lib/*' Pg387TrustedDeployment $mode 0.1.0-PG400 $source" > "$run/pg400-$mode.log" 2>&1
done
printf 'PG400 deployment complete manifest=%s source=%s permitsIssued=0\n' "$digest" "$source"
