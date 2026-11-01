"""Exact API default-bind scope and finite metadata repair save; no Production change."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17556-api-default-public-save-v1'
save.BEFORE = '68c3b944ad41441a5df0d149268aefc85e3a66b4'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg175', 'tools/quality/scoped_prometheus_owned_api_default_loopback_host_v1.py', 'tools/quality/owned_api_default_loopback_environment_step_v1.py', 'tools/quality/architecture/ApiManagementDefaultBindCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
