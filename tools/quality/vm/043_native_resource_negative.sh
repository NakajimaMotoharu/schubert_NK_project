#!/usr/bin/env bash
# PT-OPS-NATIVE-003..006. Exact disposable VM secrets only; reversible fixture perturbation.
set -euo pipefail
test "$(id -u)" = 0
test "$(cat /var/lib/cloud/data/instance-id)" = pgpt-r2-20260927-01
task_private=/opt/pgpt-native/private
task_credential=/etc/schubert-nk/credentials
test ! -e "$task_private/mq-api.held"
test ! -e "$task_private/api-context-aes-current.held"
test ! -e "$task_private/db-api.held"
restore() {
  for name in mq-api api-context-aes-current db-api; do
    if test -f "$task_private/$name.held"; then
      mv -f -- "$task_private/$name.held" "$task_credential/$name"
    fi
  done
}
trap restore EXIT
require_failed() {
  if systemctl start pgpt-native-api.service > "$task_private/negative-command.log" 2>&1; then
    printf '%s\n' 'negative probe unexpectedly succeeded' >&2
    exit 1
  fi
  test "$(systemctl show pgpt-native-api.service -p Result --value)" != success
  printf '%s\n' "$1 PASS startupRefused=true"
  systemctl reset-failed pgpt-native-api.service
}
mv -- "$task_credential/mq-api" "$task_private/mq-api.held"
require_failed PT-OPS-NATIVE-003
restore
mv -- "$task_credential/api-context-aes-current" "$task_private/api-context-aes-current.held"
install -o root -g root -m 0600 /opt/pgpt-native/source/tools/quality/vm/invalid-key.fixture "$task_credential/api-context-aes-current"
require_failed PT-OPS-NATIVE-004
restore
mv -- "$task_credential/db-api" "$task_private/db-api.held"
install -o root -g root -m 0600 "$task_credential/mq-api" "$task_credential/db-api"
require_failed PT-OPS-NATIVE-005
restore
for service in api web; do
  for name in db-api db-web; do
    if runuser -u "schubert-$service" -- test -r "$task_credential/$name"; then
      printf '%s\n' 'service can read private source credential' >&2
      exit 1
    fi
  done
done
printf '%s\n' 'PT-OPS-NATIVE-006 PASS privateSourceDenied=true'
systemctl start pgpt-native-api.service pgpt-native-web.service
test "$(systemctl show pgpt-native-api.service -p Result --value)" = success
test "$(systemctl show pgpt-native-web.service -p Result --value)" = success
printf '%s\n' 'restoredPositiveRetest=true productionStartupGate=false'
