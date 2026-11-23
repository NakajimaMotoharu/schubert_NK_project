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

The two tracked profile templates match the bytes checked on the host with the
pinned Prometheus LTS 3.13.5 `promtool check config --syntax-only`. The six
syntax test IDs and the separate eight offline parser checks retain their original
results. [Host syntax results and toolchain](../../../../evidence/01_PT/018_NK-OPS-001/1738_Prometheus公式構文parser_結果・toolchain記録.md)
[Independent offline parser results](../../../../evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8654-prometheus-profile-parser-post-v1/manifest.json)

Deployment validation still requires the target binary and rendered profiles,
service identity, directory permissions and total capacity mechanism. Same-source
endpoint and registry checks, DEBUG scrapes, STANDARD service stop and retention
remain pending on the approved target environment.

Official primary references consulted2026-10-24 (latest docs, not installed-version
qualification):
https://prometheus.io/docs/prometheus/latest/configuration/configuration/
https://prometheus.io/docs/prometheus/latest/storage/
https://prometheus.io/docs/prometheus/latest/command-line/prometheus/
