#!/usr/bin/env bash
# Disposable VM feasibility only: NOT admitted production path/no-follow gate.
set -euo pipefail
test "$(id -u)" = 0
test "$(cat /var/lib/cloud/data/instance-id)" = pgpt-r2-20260927-01
test "$#" = 1
case "$1" in
  api) task_groups=schubert,schubert-read,schubert-web ;;
  web) task_groups=schubert,schubert-read ;;
  *) exit 70 ;;
esac
task_uid=$(id -u "schubert-$1")
task_gid=$(getent group "schubert-$1" | cut -d: -f3)
task_group_ids=
IFS=, read -r -a task_group_names <<< "$task_groups"
for task_group in "${task_group_names[@]}"; do
  task_id=$(getent group "$task_group" | cut -d: -f3)
  test -n "$task_id"
  task_group_ids+=${task_group_ids:+,}$task_id
done
# Root-controlled disposable fixture inode. Production must use retained NOFOLLOW admission,
# not this raw path open. Fixed descriptor 3 here is explicitly allocated by this test wrapper.
exec 3< /run/schubert-nk/pgpt-startup-admission.lock
/usr/bin/flock --nonblock 3
exec /usr/bin/setpriv --reuid="$task_uid" --regid="$task_gid" --groups="$task_group_ids" \
  --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
  /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED \
  -cp '/opt/pgpt-native/classes:/opt/pgpt-native/lib/*' NativeInheritedLockProbe "$1" "$task_uid" "$task_group_ids"
