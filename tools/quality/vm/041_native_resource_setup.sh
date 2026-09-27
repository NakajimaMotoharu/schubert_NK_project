#!/usr/bin/env bash
# Disposable VM-only PGPT fixture, never host provisioning or a Production startup gate.
# PT-OPS-NATIVE-001/002; SS331/342/343; SSC084; PG290. No password/key argv or output.
set -euo pipefail
test "$(id -u)" = 0
test "$(cat /var/lib/cloud/data/instance-id)" = pgpt-r2-20260927-01
test -d /opt/pgpt-native/source
task_source=/opt/pgpt-native/source
for group in schubert schubert-read schubert-api schubert-web; do
  getent group "$group" >/dev/null || groupadd --system "$group"
done
for service in api web; do
  getent passwd "schubert-$service" >/dev/null || useradd --system --gid "schubert-$service" --groups schubert,schubert-read --home-dir /nonexistent --shell /usr/sbin/nologin "schubert-$service"
done
usermod -a -G schubert-web schubert-api
install -d -o root -g schubert -m 0750 /etc/schubert-nk
install -d -o root -g root -m 0700 /etc/schubert-nk/credentials
install -d -o root -g root -m 0700 /opt/pgpt-native/private
for name in common api web; do
  install -o root -g schubert -m 0640 "$task_source/src/deployment/config/$name.yml.template" "/etc/schubert-nk/$name.yml"
done
for service in api web; do
  install -o root -g "schubert-$service" -m 0600 "$task_source/src/deployment/config/$service.env.template" "/etc/schubert-nk/$service.env"
done
for name in db-api db-web mq-api mq-web; do
  if test ! -f "/etc/schubert-nk/credentials/$name"; then
    openssl rand -hex -out "/etc/schubert-nk/credentials/$name" 32
    chmod 0600 "/etc/schubert-nk/credentials/$name"
  fi
done
for name in api-context-aes-current api-inbox-response-aes-current operation-hmac-current web-session-aes-current web-revoke-aes-current web-log-aes-current; do
  if test ! -f "/etc/schubert-nk/credentials/$name"; then
    openssl rand -base64 -out "/etc/schubert-nk/credentials/$name" 32
    sed -i '1iNKKEY1\nv1' "/etc/schubert-nk/credentials/$name"
    chmod 0600 "/etc/schubert-nk/credentials/$name"
  fi
done
if test "$(runuser -u postgres -- psql -Atqc "select 1 from pg_database where datname='schubert_nk'")" != 1; then
  runuser -u postgres -- createdb schubert_nk
fi
runuser -u postgres -- psql -v ON_ERROR_STOP=1 -d schubert_nk -f "$task_source/src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql" >/dev/null
install -d -o postgres -g postgres -m 0700 /var/lib/postgresql/pgpt-passwords
for name in db-api db-web; do
  install -o postgres -g postgres -m 0400 "/etc/schubert-nk/credentials/$name" "/var/lib/postgresql/pgpt-passwords/$name"
done
test "$(runuser -u postgres -- psql -Atqc 'show log_statement')" = none
if ! runuser -u postgres -- psql -v ON_ERROR_STOP=1 -d schubert_nk -f "$task_source/tools/quality/vm/042_native_passwords.sql" > /opt/pgpt-native/private/password-setup.log 2>&1; then
  printf '%s\n' 'fixture password setup failed (private diagnostic retained)' >&2
  exit 1
fi
for service in api web; do
  install -o root -g root -m 0644 "$task_source/tools/quality/vm/pgpt-native-$service.service" "/etc/systemd/system/pgpt-native-$service.service"
done
systemctl daemon-reload
printf '%s\n' 'fixture.ready=true productionStartupGate=false'
