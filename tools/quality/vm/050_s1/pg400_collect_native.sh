#!/usr/bin/env bash
set -euo pipefail
private=/home/mini/codex/project1/work/pgpt-vm/private
run=/home/mini/codex/project1/work/pgpt-runs/PG379
repo=/home/mini/codex/project1/work/pgpt-foundation
ssh_options=(-i "$private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
test ! -e "$run/pg400-native"
mkdir -m 700 "$run/pg400-native"
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n -u postgres psql -X -v ON_ERROR_STOP=1 -d schubert_nk -f - < /home/ubuntu/pg400-stage/pg393_readback_full.sql' > "$run/pg400-native-db-final-full.log" 2>&1
for role in parent backup cleanup expiry; do
  ssh "${ssh_options[@]}" ubuntu@127.0.0.1 "sudo -n /usr/bin/cat /run/schubert-nk/pt-coverage/$role/$role.exec" > "$run/pg400-native/$role.exec"
  test -s "$run/pg400-native/$role.exec"
done
cp="$run:/home/mini/codex/project1/work/toolchain/m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"
for name in asm asm-tree asm-commons; do
  cp="$cp:/home/mini/codex/project1/work/toolchain/m2/repository/org/ow2/asm/$name/9.10.1/$name-9.10.1.jar"
done
java=/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java
for name in MorningProcessMain MorningGateEvidence MorningBrokerExecution MorningDatabaseSession; do
  "$java" -cp "$cp" NativeReached "$run/pg400-native/parent.exec" "$repo/src/schubert-nk-batch/target/classes" "$name" > "$run/pg400-native/$name-reached.txt"
done
for module in protocol storage bootstrap api web batch; do
  "$java" -cp "$cp" NativeCoverage "$repo/src/schubert-nk-$module/target/classes" "$run/pg400-host/$module.exec" "$run/pg400-native/parent.exec" "$run/pg400-native/backup.exec" "$run/pg400-native/cleanup.exec" "$run/pg400-native/expiry.exec" > "$run/pg400-native/$module-union.json"
done
printf 'PG400 actual native exec collection and same-byte union completed\n'
