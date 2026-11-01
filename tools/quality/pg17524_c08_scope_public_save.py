"""Exact C08 inventory-only readiness and canonical-document metadata repair; no Product change."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17524-c08-scope-public-save-v1'
save.BEFORE = '4b95d1fab9cd6824a2e430232670c3afe54c0865'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17520_', 'tools/quality/pg17521_', 'tools/quality/pg17522_', 'tools/quality/pg17524_')
if __name__ == '__main__':
    save.main()
