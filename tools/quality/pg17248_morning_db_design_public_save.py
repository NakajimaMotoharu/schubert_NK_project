"""Exact read-only database runtime design mapping; no dynamic or formal promotion."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17248-morning-db-design-public-save-v1'
save.BEFORE = '6cda77a1667eec5812b076346b5e800734ac1cd8'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17246_', 'tools/quality/pg17248_')
if __name__ == '__main__':
    save.main()
