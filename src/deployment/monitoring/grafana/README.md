# Grafana distribution candidates — no service or account operations

NK-OPS-001/WBS-P018-09/C07; RD171 MON010..013/UI252253/SS351; PG-D582.
PT1735/result1736; GRAFCFG001..008. Profiles are public non-executing data.
No installer, shell launcher, dashboard importer, role or credential is supplied.

grafana.ini.template uses a candidate loopback127.0.0.1:3000 HTTP listener, console
INFO, and candidate data/provisioning paths under the NK monitoring directories.
Anonymous access, signup, org creation and initial default-admin creation are off.
auto_assign_org=true/Viewer retains the official default; setting it false would
create a new organization for a new user even with allow_org_create=false.
Usage reporting and version/plugin update checks are explicitly disabled.
These declarations do not prove all egress stopped, valid accounts or a secure
complete runtime configuration. Actual version/parser/defaults/overrides remain
UNRUN/HOLD. In particular an independently supplied private secret key, managed
admin access and actual ownership/permissions must be qualified before any start.
Do not put passwords, session material or secret keys into these templates/Git.

DEBUG provisioning is JSON-syntax YAML with one immutable-in-UI datasource:
the candidate Prometheus endpoint http://127.0.0.1:9090, proxy mode, organization1,
stable UID/version, GET and15s initial interval. It matches the candidate
Prometheus data in ../prometheus, not a verified listener or current datasource.
No credential, arbitrary query, business data or remote target is included.

STANDARD lists no new datasources and keeps prune=false/deleteDatasources=[].
That deliberately does not delete or disable an old datasource already stored in
Grafana. The daemon and detailed exporters must separately be stopped per SS351;
an empty profile is NOT proof of no activity. Existing Grafana storage/dashboards
must be preserved, never reset to make a test pass.

Before any later permitted deployment, pin binary/version/source/checksum and
native parser behavior, intended config precedence, actual role/credentials,
data ownership and aggregate monitoring capacity. Qualify the retained-source/
same-owner delivery and signed BOM inclusion separately; this change does not
edit the existing Root/BOM allowlist or authorize placement/start/reload.
Grafana database/plugin/log storage and Prometheus together still need the UI253
total5GB assessment. Java coverage, real sockets/scrapes, DEBUG visualization,
STANDARD service stop, retention and full451 remain unaccepted.

Official primary references read2026-10-24 (latest docs, not product qualification):
https://grafana.com/docs/grafana/latest/administration/provisioning/
https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/
https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/
