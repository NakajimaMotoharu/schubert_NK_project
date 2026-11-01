"""Exact original fifteen data-only scopes; old fullSource/counter proofs retained."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17596-retained-audit-caddy-public-save-v1'
save.BEFORE = '705dc616f6beeb7438652ced4a237a5331c473e6'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1758', 'tools/quality/pg1759', 'tools/quality/architecture/RetainedAuditCaddyFifteenCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
