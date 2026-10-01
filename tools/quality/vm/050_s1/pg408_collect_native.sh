#!/usr/bin/env bash
# Genuine current-source samples only; Root exec replaces the JVM and may leave old dump intact.
set -euo pipefail
private=/home/mini/codex/project1/work/pgpt-vm/private
run=/home/mini/codex/project1/work/pgpt-runs/PG379
repo=/home/mini/codex/project1/work/pgpt-foundation
ssh_options=(-i "$private/vm-access" -p22222 -oBatchMode=yes -oIdentitiesOnly=yes -oStrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
test ! -e "$run/pg408-native"
mkdir -m700 "$run/pg408-native"
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n -u postgres psql -X -v ON_ERROR_STOP=1 -d schubert_nk -f - < /home/ubuntu/pg408-stage/pg393_readback_full.sql' > "$run/pg408-native-db-final-full.log" 2>&1
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n python3 /home/ubuntu/pg408-stage/pg403_backup_inventory.py' > "$run/pg408-backup-after-private.json"
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n systemctl show schubert-nk-morning-controller.service schubert-nk-api.service schubert-nk-web.service --property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,Result,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL' > "$run/pg408-native-full18-private.txt"
roles=(parent backup cleanup expiry)
for role in "${roles[@]}"; do
  ssh "${ssh_options[@]}" ubuntu@127.0.0.1 "sudo -n /usr/bin/cat /run/schubert-nk/pt-coverage/$role/$role.exec" > "$run/pg408-native/$role.exec"
  test -s "$run/pg408-native/$role.exec"
done
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n /usr/bin/cat /run/schubert-nk/pt-coverage/root-api/root-api.exec' > "$run/pg408-native/root-api-observed.exec"
observed=$(sha256sum "$run/pg408-native/root-api-observed.exec")
observed=${observed%% *}
if [[ -s "$run/pg408-native/root-api-observed.exec" && "$observed" != 37a53558821d53ff550a2d67dbcd522f0f24be4c70f78729197a5b5c6573486d ]]; then
  roles+=(root-api-observed)
else
  printf 'PG408 Root dump empty or previous-source: excluded, no Root coverage claim\n'
fi
cp="$run:/home/mini/codex/project1/work/toolchain/m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"
for name in asm asm-tree asm-commons; do cp="$cp:/home/mini/codex/project1/work/toolchain/m2/repository/org/ow2/asm/$name/9.10.1/$name-9.10.1.jar"; done
java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java
samples=()
for role in "${roles[@]}"; do samples+=("$run/pg408-native/$role.exec"); done
for module in protocol storage bootstrap api web batch; do
  "$java" -cp "$cp" NativeCoverage "$repo/src/schubert-nk-$module/target/classes" "$run/pg408-host/$module.exec" "${samples[@]}" > "$run/pg408-native/$module-union.json"
done
for name in MorningProcessMain MorningControlScope MorningPermitPublication RootServiceLauncher RootServiceExecutableAdmission RootServiceFacts RootServiceCredentialSource; do
  "$java" -cp "$cp" NativeReached "$run/pg408-native/parent.exec" "$repo/src/schubert-nk-batch/target/classes" "$name" > "$run/pg408-native/$name-parent-reached.txt"
  if [[ ${#roles[@]} == 5 ]]; then
    "$java" -cp "$cp" NativeReached "$run/pg408-native/root-api-observed.exec" "$repo/src/schubert-nk-batch/target/classes" "$name" > "$run/pg408-native/$name-root-reached.txt"
  fi
done
printf 'PG408 native collection complete actualSampleRoles=%s ordinaryCoverageClaimed=false wholeStartupAccepted=false\n' "${roles[*]}"
