set -eu
export LC_ALL=C
printf 'host=%s\n' "$(hostname -s)"
printf 'user=%s\n' "$(id -un)"
printf 'uid=%s\n' "$(id -u)"
printf 'kernel=%s\n' "$(uname -sr)"
printf 'cpu=%s\n' "$(getconf _NPROCESSORS_ONLN)"
printf 'memory_kib=%s\n' "$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
printf 'boot_sha256=%s\n' "$(sha256sum /proc/sys/kernel/random/boot_id | cut -d ' ' -f 1)"
case "$(id -un)" in mini) ;; *) exit 21;; esac
base=/home/mini/schubert-nk-pgpt
if [ -d "$base" ] && [ -r "$base" ] && [ -x "$base" ]; then
  printf 'workspace_uid=%s\n' "$(stat -c '%u' "$base")"
  printf 'workspace_available_kib=%s\n' "$(df -Pk "$base" | awk 'END {print $4}')"
else
  printf 'workspace_uid=unavailable\n'
  printf 'workspace_available_kib=unavailable\n'
fi
for item in java maven artemis caddy; do
  case "$item" in
    java) file=/opt/schubert-nk-test-tools/jdk-25.0.4/bin/java ;;
    maven) file=/opt/schubert-nk-test-tools/maven/bin/mvn ;;
    artemis) file=/opt/schubert-nk-test-tools/apache-artemis-2.56.0/bin/artemis ;;
    caddy) file=/usr/bin/caddy ;;
  esac
  if [ -r "$file" ] && [ -x "$file" ]; then
    printf '%s=read_execute\n' "$item"
  else
    printf '%s=unavailable\n' "$item"
  fi
done
