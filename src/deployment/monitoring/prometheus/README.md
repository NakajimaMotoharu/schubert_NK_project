# Prometheus profiles — non-executing distribution data

NK-OPS-001/WBS-P018-09/C07; RD171 MON005010011012013; UI252 §5/253 §6;
SS342 §5.2/343 monitoring mode/351 §6/8. PG-D580; PT specification1730/result1731,
PROMCFG001..008. These files do not install, invoke, configure or stop a service.

- DEBUG: debug.yml.template describes only the two SS342 IPv4-loopback management
  targets, Web8081 and API8091 at /actuator/prometheus. No extra metrics endpoint,
  service discovery, proxy, credentials, remote-write, queries or alert receiver.
  All documents use JSON syntax within YAML; no variable expansion is required.
- STANDARD: standard.yml.template has no scrape targets. The monitoring daemon,
  Grafana and detailed exporters must independently be stopped per SS351.
  An empty scrape list is defense-in-depth, NOT proof of stopped services.
- debug-arguments.json.template is an argv DATA array, not a shell program or a
  launcher. Internal candidate paths are /etc/schubert-nk/monitoring/prometheus
  and /var/lib/schubert-nk/monitoring/prometheus; no such directory is created.
  The internal candidate listen address is127.0.0.1:9090, not an external listener.
  The 15s/5s scrape interval/timeout are initial technical values, not a performance
  acceptance. No approval to deploy or change any current service is implied.
- Retention uses15d and5000000000B (decimal5GB). Prometheus interprets GB as a
  power-of-two unit, so5GB would not mean5,000,000,000 bytes. Retention flags alone
  do NOT guarantee the UI253 total5GB: WAL/head, concurrent compaction, cleanup
  delay and all related monitoring storage need separate capacity/ownership
  design and real qualification. No existing data is deleted or moved.
  STANDARD must not run a daemon with retention size0 interpreted as unlimited.

Before any later permitted deployment, pin the actual Prometheus/promtool version,
source/checksum, installation, service identity, directories/permissions and total
capacity mechanism; parse the exact profiles with that binary without scrapes;
then validate same-source endpoint contents and registry compatibility, DEBUG
operation, STANDARD stop/no scrape and retention. Current artifact checks use
independent static semantics only; promtool and all daemon/runtime checks are
UNRUN/HOLD. Existing API readiness-only response does not prove all26 detailed
metrics. No new role, VM/native/Root/DB access or permission change is implemented.

Official primary references consulted2026-10-24 (latest docs, not installed-version
qualification):
https://prometheus.io/docs/prometheus/latest/configuration/configuration/
https://prometheus.io/docs/prometheus/latest/storage/
https://prometheus.io/docs/prometheus/latest/command-line/prometheus/
